"""
Uses an Instance which could be a platform primitive but in this case is
an external Verilog file which we'll include in the build.
"""

from nmigen import Module, Signal, Elaboratable, Instance, ClockSignal
from nmigen_boards.icebreaker import ICEBreakerPlatform


class Top(Elaboratable):
    def elaborate(self, platform):
        m = Module()

        # First, we'll make up some simple Verilog.
        # We could have read this from a file or similar.
        v = """
        module counter ( clk, cnt );
            parameter WIDTH = 8;
            input clk;
            output reg [WIDTH-1:0] cnt;

            always @(posedge clk) begin
                cnt <= cnt + 1;
            end
        endmodule
        """

        # We use `platform.add_file()` to add the file to the build.
        platform.add_file("counter.v", v)

        # Now, we can use Instance to instantiate this module.
        count = Signal(8)
        counter = Instance(
            "counter",
            # Parameters starting with `p_` are Verilog parameters.
            p_WIDTH=count.width,
            # Parameters starting with `i_` are inputs.
            # In this case we get the clock signal using `ClockSignal()`,
            # although we could have assigned any signal.
            i_clk=ClockSignal("sync"),
            # Parameters starting with `o_` are outputs.
            # We assign the output of the module to our `count` Signal.
            o_cnt=count
            # We could also use `a_` for Verilog attributes and `io_`
            # for Verilog inouts.
        )

        # We have to add the instance to our submodules.
        # Often this is written `counter = m.submodules.counter = Instance(...`
        m.submodules.counter = counter

        # Finally, let's just bind the top count bit to an LED.
        led = platform.request("led_g", 0)
        m.d.comb += led.o.eq(count[-1])

        return m


def test_instance():
    top = Top()
    plat = ICEBreakerPlatform()
    plat.build(top)


if __name__ == "__main__":
    test_instance()
