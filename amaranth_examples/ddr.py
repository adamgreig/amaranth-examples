"""
Demonstrate use of DDR outputs on a custom ECP5 board.
"""

from amaranth import Module, Elaboratable, ClockSignal
from amaranth.vendor.lattice_ecp5 import LatticeECP5Platform
from amaranth.build import Resource, Pins, Clock


class CustomPlatform(LatticeECP5Platform):
    """
    This CustomPlatform represents our particular custom FPGA board,
    where we've wired a 20MHz clock to pin P3, and want to use U1 and V1
    as DDR inputs and outputs.

    We use the Clock property to let amaranth know this signal is a clock at
    a particular frequency, which it in turn tells the placement software
    about, so that nextpnr can check the circuit is able to run at the
    specified frequency.

    By specifying `default_clk`, we tell amaranth to create a default clock
    domain named "sync" if none exists using the specified signal as the
    clock input. If we didn't specify default_clk we'd have to create the
    clock domain ourselves.
    """
    device = "LFE5U-25F"
    package = "BG381"
    speed = "6"
    default_clk = "clk"
    resources = [
        Resource("clk", 0, Pins("P3", dir="i"), Clock(20e6)),
        Resource("gpi", 0, Pins("U1", dir="i")),
        Resource("gpo", 0, Pins("V1", dir="o")),
    ]
    connectors = []


class Top(Elaboratable):
    """
    This simple Top module reads the input DDR and copies it to the output.
    """
    def elaborate(self, platform):
        m = Module()

        # Requesting the pins with `xdr=2` requests a DDR gearing.
        # Using `xdr=1` would be SDR - registered but only one data
        # connection. Higher values of `xdr` may be allowed on particular
        # hardware, for example `xdr=7` for video interfaces.
        # When `xdr` is greater than 0, the `i_clk`/`o_clk` signals
        # become available.
        gpi = platform.request("gpi", 0, xdr=2)
        gpo = platform.request("gpo", 0, xdr=2)

        # Hook up clock signals.
        m.d.comb += [
            gpi.i_clk.eq(ClockSignal()),
            gpo.o_clk.eq(ClockSignal()),
        ]

        # Connect inputs to outputs through a register.
        m.d.sync += [
            gpo.o0.eq(gpi.i0),
            gpo.o1.eq(gpi.i1),
        ]

        return m


def test_synthesise_custom_board():
    # All we need to do is create the top-level module, then call the
    # platform's `build()` method with it.
    top = Top()
    plat = CustomPlatform()
    plat.build(top)


if __name__ == "__main__":
    test_synthesise_custom_board()
