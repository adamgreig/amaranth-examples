"""
A simple SPI peripheral device which oversamples SCLK using a higher-frequency
internal sync domain.

This uses SPI mode 0: the clock idles low and rising edges are active;
data is sampled on the rising edge and changed on the falling edge.

This works when the external SPI clock is sufficiently slow (maybe 1/3 or less
of the sync frequency); for higher-speed SPI clocks it would be better to run
some logic directly from that external clock (which likely then needs to enter
the FPGA via a clock input pin) and synchronise the data internally.
"""

from amaranth import Module, Signal, Elaboratable, Cat
from amaranth.sim import Simulator


class SPIPeriph(Elaboratable):
    def __init__(self):
        # Data received from controller
        self.din = Signal(8)

        # Data to send to controller
        self.dout = Signal(8)

        # SPI interface
        self.csn = Signal()
        self.sck = Signal()
        self.sdi = Signal()
        self.sdo = Signal()

    def elaborate(self, platform):
        m = Module()

        # Detect edges on SCK
        last_sck = Signal()
        m.d.sync += last_sck.eq(self.sck)
        sck_rose = Signal()
        sck_fell = Signal()
        m.d.comb += sck_rose.eq(self.sck & ~last_sck)
        m.d.comb += sck_fell.eq(~self.sck & last_sck)

        # Always output the current most significant bit of `dout`.
        m.d.comb += self.sdo.eq(self.dout[-1])

        with m.If(~self.csn):
            # Capture SDI into `din` on rising edge.
            with m.If(sck_rose):
                m.d.sync += self.din.eq(Cat(self.sdi, self.din))
            # Shift `dout` into SDO on falling edge.
            with m.If(sck_fell):
                m.d.sync += self.dout.eq(self.dout.rotate_left(1))

        return m


def test_spi_periph():
    spi = SPIPeriph()

    # Test benches are written as Python generators, which yield commands
    # to the simulator such as "set this signal to this value" or
    # "read the value of this signal".
    def testbench():
        # Set up the starting conditions.
        # Start with CS not asserted and dout (data to send) 0xAB.
        yield spi.csn.eq(1)
        yield spi.dout.eq(0xAB)
        yield
        yield

        # Assert CS.
        yield spi.csn.eq(0)
        yield

        bits = []

        # Run 8 clock cycles.
        for clk in range(8):
            # On the rising edge, capture the output and set new input.
            bits.append((yield spi.sdo))
            yield spi.sdi.eq(clk & 1)
            yield spi.sck.eq(1)
            yield
            yield

            yield spi.sck.eq(0)
            yield
            yield

        # De-assert CS.
        yield spi.csn.eq(1)
        yield

        # Check the device received 0x55 from us, and we received 0xAB from it.
        assert (yield spi.din) == 0x55
        assert bits == [1, 0, 1, 0, 1, 0, 1, 1]

    # Run the simulator at a nominal 10MHz.
    sim = Simulator(spi)
    sim.add_clock(1/10e6)
    sim.add_sync_process(testbench)

    # Output a VCD file for visualisation.
    with sim.write_vcd("spi.vcd"):
        sim.run()
