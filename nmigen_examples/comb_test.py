"""
Example testbench for a combinatorial-only module.
"""

from nmigen import Module, Signal, Elaboratable
from nmigen.sim import Simulator, Settle


class ALU(Elaboratable):
    """
    A simple ALU that either adds or subtracts two inputs,
    but implemented only using combinatorial statements,
    without any synchronous logic.
    """
    def __init__(self):
        self.op = Signal()
        self.a = Signal(8)
        self.b = Signal(8)
        self.y = Signal(9)

    def elaborate(self, platform):
        m = Module()

        with m.If(self.op):
            m.d.comb += self.y.eq(self.a + self.b)
        with m.Else():
            m.d.comb += self.y.eq(self.a - self.b)

        return m


def test_comb_alu():
    alu = ALU()

    def testbench():
        for a in range(20):
            yield alu.a.eq(a)
            for b in range(20):
                yield alu.b.eq(b)

                # In this combinatorial testbench, we use `yield Settle()`
                # to request the simulator advance until all combinatorial
                # statements have been fully resolved.
                yield alu.op.eq(1)
                yield Settle()
                assert (yield alu.y) == a + b

                yield alu.op.eq(0)
                yield Settle()
                assert (yield alu.y) == (a - b) % 512

    sim = Simulator(alu)

    # Instead of `sim.add_sync_process`, which would try to use a clock domain
    # (by default, "sync") and error out saying it doesn't exist, we use
    # `sim.add_process`.
    sim.add_process(testbench)

    sim.run()
