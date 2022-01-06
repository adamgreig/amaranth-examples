"""
A counter that generates a pulse on rollover.

Demonstrates basic modules and synchronous testbenches.
"""

from amaranth import Module, Signal, Elaboratable
from amaranth.sim import Simulator


class Counter(Elaboratable):
    def __init__(self, limit):
        self.limit = limit

        # Counter state.
        #
        # Using `range(limit)` means the signal will be wide enough to
        # represent any integer up to but excluding `limit`.
        #
        # For example, with limit=128, we'd get a 7-bit signal which can
        # represent the integers 0 to 127.
        self.counter = Signal(range(limit))

        # Rollover output will be pulsed high for one clock cycle
        # when the counter reaches `limit-1`.
        self.rollover = Signal()

    def elaborate(self, platform):
        m = Module()

        # Make the output `rollover` always equal to this comparison,
        # which will only be 1 for a single cycle every counter period.
        m.d.comb += self.rollover.eq(self.counter == self.limit - 1)

        # Conditionally reset the counter to 0 on rollover, otherwise
        # increment it. We could write the comparison out again here
        # to the same effect.
        with m.If(self.rollover):
            m.d.sync += self.counter.eq(0)
        with m.Else():
            m.d.sync += self.counter.eq(self.counter + 1)

        return m


def test_counter():
    """Simple testbench for the Counter above."""

    # Create a counter with a rollover at 18.
    # This awkward non-power-of-two value will help test that we're not
    # rolling over by accident of the bit width of the counter.
    counter = Counter(limit=18)

    # Test benches are written as Python generators, which yield
    # commands to the simulator such as "send me the current value of this
    # signal" or "advance the simulation by one clock cycle".
    def testbench():
        for step in range(20):
            # Check outputs are correct at each step.
            assert (yield counter.counter) == (step % 18)
            if step == 17:
                assert (yield counter.rollover)
            else:
                assert not (yield counter.rollover)

            # Advance simulation by one cycle.
            yield

    sim = Simulator(counter)

    # To test synchronous processes, we create a clock at some nominal
    # frequency (which only changes the displayed timescale in the output),
    # and add our testbench as a "synchronous" process.
    sim.add_clock(1/10e6)
    sim.add_sync_process(testbench)

    sim.run()
