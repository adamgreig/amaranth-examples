"""
Demonstrates instantiating and using a PLL on an iCE40 platform.
"""

from amaranth import Signal, Module, Elaboratable, Instance, ClockDomain
from amaranth_boards.icebreaker import ICEBreakerPlatform


class Top(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        # We'll need to create our own "sync" clock domain using the PLL's
        # output, since the default sync domain would use the 12MHz input.
        cd_sync = ClockDomain("sync")
        m.domains += cd_sync

        # We add a clock constraint so amaranth can tell nextpnr to check that
        # this clock domain meets timing.
        platform.add_clock_constraint(cd_sync.clk, 48e6)

        # A mystery errata on iCE40 devices means that BRAMs will read as
        # all-zero for ~3µs after configuration completes. If you use a "sync"
        # domain without creating it, Amaranth will create one for you and
        # ensure it is reset for 3µs after startup to avoid this issue.
        # However, if you create your own clock domain, you have to deal with
        # this manually if it's important. For this example there are no BRAMs
        # so it's not important, but for the sake of example, a suitable reset
        # is added, delaying for approx 15µs using the 48MHz PLL output clock.
        # Additionally, since we're running this timer off the PLL, we can
        # keep this domain in reset until the PLL is locked.
        # For more details, see create_missing_domain() in
        # amaranth/vendor/_lattice_ice40.py.
        cd_por = ClockDomain("por", local=True)
        m.domains += cd_por
        delay = int(5 * 3e-6 * 48e6)
        timer = Signal(range(delay))
        ready = Signal()
        pll_locked = Signal()
        with m.If(timer == delay):
            m.d.por += ready.eq(1)
        with m.Else():
            m.d.por += timer.eq(timer + 1)
        m.d.comb += cd_por.clk.eq(cd_sync.clk), cd_por.rst.eq(~pll_locked)
        m.d.comb += cd_sync.rst.eq(~ready)

        # Create an Instance with the required parameters, inputs, and outputs.
        # We have a choice of either SB_PLL40_CORE or SB_PLL40_PAD (or the _2F
        # versions of each, to have two output frequencies).
        # Use _CORE when the input signal comes from logic or routing or a
        # non-global pin or you need to use the input signal and have it
        # drive a PLL too; use _PAD when the clock input signal goes directly
        # to the PLL and is only used for the PLL. You also have to use _PAD
        # if the PLL is fed from the pin that the PLL is located on, as
        # otherwise the PLL disables that input signal (hope you spotted this
        # fun fact in the documentation!). For the ICEBreaker, that means we'll
        # have to use _PAD.
        m.submodules.pll = Instance(
            "SB_PLL40_PAD",

            # Parameters are taken from the `icepll` output:
            # $ icepll -i 12 -o 40 -m
            p_FEEDBACK_PATH="SIMPLE",
            p_DIVR=0,
            p_DIVF=52,
            p_DIVQ=4,
            p_FILTER_RANGE=1,

            # Input from the clk12 pin. Since we want the raw pin without
            # an input buffer, use `dir="-"` and then don't try to access
            # a `.i` attribute.
            i_PACKAGEPIN=platform.request("clk12", dir="-"),

            # Force RESET off.
            i_RESETB=1,

            # Output to the clock domain's clk signal.
            # We could also have written ClockSignal("sync").
            o_PLLOUTGLOBAL=cd_sync.clk,

            # We'll use the LOCK output to keep the POR domain in reset
            # until the PLL has locked.
            o_LOCK=pll_locked,
        )

        # Now our sync logic runs at 48MHz:
        cnt = Signal(24)
        m.d.sync += cnt.eq(cnt + 1)
        m.d.comb += platform.request("led_g", 0).o.eq(cnt[-1])

        return m


def test_pll_ice40():
    top = Top()
    plat = ICEBreakerPlatform()
    plat.build(top)


if __name__ == "__main__":
    test_pll_ice40()
