"""
Demonstrates instantiating and using a PLL on an ECP5 platform.
"""

from nmigen import Signal, Module, Elaboratable, Instance, ClockDomain
from nmigen_boards.ulx3s import ULX3S_12F_Platform


class Top(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        # We'll need to create our own "sync" clock domain using the PLL's
        # output, since the default sync domain would use the 25MHz input.
        cd_sync = ClockDomain("sync")
        m.domains += cd_sync

        # We add a clock constraint so nmigen can tell nextpnr to check that
        # this clock domain meets timing.
        platform.add_clock_constraint(cd_sync.clk, 100e6)

        # Create an Instance with the required parameters, inputs, and outputs.
        # For the ECP5, this is EHXPLLL; refer to the "FPGA Libraries Reference
        # Guide" from Lattice for more details.
        m.submodules.pll = Instance(
            "EHXPLLL",

            # Parameters are taken from the `ecppll` output:
            # $ ecppll -i 25 -o 100 -f /dev/stdout
            a_FREQUENCY_PIN_CLKI="25",
            a_FREQUENCY_PIN_CLKOP="100",
            a_ICP_CURRENT="12",
            a_LPF_RESISTOR="8",
            p_CLKI_DIV=1,
            p_CLKOP_DIV=6,
            p_CLKFB_DIV=4,
            p_FEEDBK_PATH="CLKOP",
            p_CLKOP_ENABLE="ENABLED",

            # Input from the clk25 pin.
            i_CLKI=platform.request("clk25").i,

            # Output to the clock domain's clk signal.
            # We could also have written ClockSignal("sync").
            o_CLKOP=cd_sync.clk,

            # We also need to connect up the feedback signal, in this
            # case directly to the output.
            i_CLKFB=cd_sync.clk,
        )

        # Now our sync logic runs at 100MHz:
        cnt = Signal(24)
        m.d.sync += cnt.eq(cnt + 1)
        m.d.comb += platform.request("led", 0).o.eq(cnt[-1])

        return m


def test_pll_ecp5():
    top = Top()

    # The real ULX3S_12F_Platform inconsiderately requires openFPGAloader
    # present in the build environment, even if you're not programming.
    class FakeULX3SPlatform(ULX3S_12F_Platform):
        @property
        def required_tools(self):
            return super().required_tools[:-1]

    plat = FakeULX3SPlatform()
    plat.build(top, program=False)


if __name__ == "__main__":
    test_pll_ecp5()
