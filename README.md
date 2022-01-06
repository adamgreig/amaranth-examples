# amaranth examples

This repository contains a variety of Amaranth examples:

* [counter.py](amaranth_examples/counter.py): Simple logic example with a testbench
* [comb_test.py](amaranth_examples/comb_test.py): Testbench for a purely
    combinatorial Module, using Settle.
* [custom_board.py](amaranth_examples/custom_board.py): Demonstrates adding your
    own Platform for your own FPGA board and synthesising a bitstream for it.
* [connectors.py](amaranth_examples/connectors.py): Demonstrates using connectors
    defined in a Platform.
* [instance.py](amaranth_examples/instance.py): Using an Instance to instantiate
    a module (from Verilog or a platform primitive), and adding a Verilog file
    to the build process.
* [pll_ecp5.py](amaranth_examples/pll_ecp5.py): Use a platform PLL primitive on
    the ECP5.
* [pll_ice40.py](amaranth_examples/pll_ice40.py): Use a platform PLL primitive on
    the iCE40.
