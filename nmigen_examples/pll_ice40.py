"""
Demonstrates instantiating and using a PLL on an iCE40 platform.
"""

from nmigen import Signal, Module, Elaboratable, Instance, ClockDomain
from nmigen_boards.icebreaker import ICEBreakerPlatform


class Top(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        # We'll need to create our own "sync" clock domain using the PLL's
        # output, since the default sync domain would use the 12MHz input.
        cd_sync = ClockDomain("sync")
        m.domains += cd_sync

        # We add a clock constraint so nmigen can tell nextpnr to check that
        # this clock domain meets timing.
        platform.add_clock_constraint(cd_sync.clk, 48e6)

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

            # Output to the clock domain's clk signal.
            # We could also have written ClockSignal("sync").
            o_PLLOUTGLOBAL=cd_sync.clk,
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
