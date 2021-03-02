"""
Demonstrate synthesis for a custom board, using an iCE40UP5k FPGA.
"""

from nmigen import Module, Signal, Elaboratable
from nmigen.vendor.lattice_ice40 import LatticeICE40Platform
from nmigen.build import Resource, Pins, Clock, Attrs


class CustomPlatform(LatticeICE40Platform):
    """
    This CustomPlatform represents our particular custom FPGA board,
    where we've wired a 20MHz clock to pin 35, and put LEDs (active high)
    on pins 46-48.

    We use the Clock property to let nmigen know this signal is a clock at
    a particular frequency, which it in turn tells the placement software
    about, so that nextpnr can check the circuit is able to run at the
    specified frequency.

    We use the Attrs(GLOBAL=True) property to request that this clock input
    is immediately put into a global buffer on the iCE40 FPGA.

    By specifying `default_clk`, we tell nmigen to create a default clock
    domain named "sync" if none exists using the specified signal as the
    clock input. If we didn't specify default_clk we'd have to create the
    clock domain ourselves.
    """
    device = "iCE40UP5K"
    package = "sg48"
    default_clk = "clk"
    resources = [
        Resource("clk", 0, Pins("35", dir="i"), Clock(20e6), Attrs(GLOBAL=True)),
        Resource("led", 0, Pins("46", dir="o")),
        Resource("led", 1, Pins("47", dir="o")),
        Resource("led", 2, Pins("48", dir="o")),
    ]
    connectors = []


class Top(Elaboratable):
    """
    This simple Top module requests the three LED pins from the Platform.

    Output pins like this LEDs have an `o` attribute which we assign to
    to set the output. Other pins might have `i` and `oe` attributes, or
    for gearboxed pins (where xdr is specified), `i0`, `i1`, `i_clk`, etc.

    We'll make a 24-bit counter and just set the LEDs to the top bits.
    """
    def elaborate(self, platform):
        m = Module()

        ctr = Signal(24)
        m.d.sync += ctr.eq(ctr + 1)

        leds = [platform.request("led", i) for i in range(3)]
        m.d.comb += [
            leds[0].o.eq(ctr[-1]),
            leds[1].o.eq(ctr[-2]),
            leds[2].o.eq(ctr[-3]),
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
