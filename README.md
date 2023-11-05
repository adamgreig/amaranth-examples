# amaranth examples

This repository contains a variety of Amaranth examples:

* [comb_test.py](amaranth_examples/comb_test.py): Testbench for a purely combinatorial Module, using Settle.
* [connectors.py](amaranth_examples/connectors.py): Demonstrates using connectors defined in a Platform.
* [counter.py](amaranth_examples/counter.py): Simple logic example with a testbench
* [custom_board.py](amaranth_examples/custom_board.py): Demonstrates adding your own Platform for your own FPGA board and synthesising a bitstream for it.
* [ddr.py](amaranth_examples/ddr.py): Demonstrates use of DDR outputs on a custom ECP5 board
* [instance.py](amaranth_examples/instance.py): Using an Instance to instantiate a module (from Verilog or a platform primitive), and adding a Verilog file to the build process.
* [pll_ecp5.py](amaranth_examples/pll_ecp5.py): Use a platform PLL primitive on the ECP5.
* [pll_ice40.py](amaranth_examples/pll_ice40.py): Use a platform PLL primitive on the iCE40.
* [spi_oversampled.py](amaranth_examples/spi_oversampled.py): A toy SPI peripheral which oversamples SCLK/MOSI from a higher-frequency internal sync domain
