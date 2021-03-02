# nmigen examples

This repository contains a variety of nmigen examples:

* [counter.py](nmigen_examples/counter.py): Simple logic example with a testbench
* [comb_test.py](nmigen_examples/comb_test.py): Testbench for a purely
    combinatorial Module, using Settle.
* [custom_board.py](nmigen_examples/custom_board.py): Demonstrates adding your
    own Platform for your own FPGA board and synthesising a bitstream for it.
* [connectors.py](nmigen_examples/connectors.py): Demonstrates using connectors
    defined in a Platform.
* [instance.py](nmigen_examples/instance.py): Using an Instance to instantiate
    a module (from Verilog or a platform primitive), and adding a Verilog file
    to the build process.
