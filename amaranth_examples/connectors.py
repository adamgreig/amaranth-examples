"""
Demonstrate use of platform connectors.

Connectors require calling `platform.add_resources()` to create a new
resource which you can later request.
"""

from amaranth import Module, Signal, Elaboratable
from amaranth.build import Resource, Pins
from amaranth_boards.icebreaker import ICEBreakerPlatform


class Top(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        # Say we want to add some LEDs and switches to pmod 1, which
        # has pins 1-4 and 7-10 (plus 5/6 and 11/12 which are power and gnd).
        platform.add_resources([
            Resource("leds", 0, Pins("1 2 3 4", dir="o", conn=("pmod", 1))),
            Resource("sw", 0, Pins("7 8 9 10", dir="i", conn=("pmod", 1))),
        ])

        # Now we can request and use them.
        leds = platform.request("leds", 0)
        switches = platform.request("sw", 0)
        m.d.sync += leds.eq(~switches)

        return m


def test_connectors():
    top = Top()
    plat = ICEBreakerPlatform()
    plat.build(top)


if __name__ == "__main__":
    test_connectors()
