# riscv-core
A small RISC-V core in ~~Python~~ Rust (and Verilog, soon).

**UPDATE: The Python version is done, I am just porting over to Rust.**

# Prerequisite
RISC-V test suite: https://github.com/riscv-software-src/riscv-tests

# Notes
Some images and notes from the The RISC-V Instruction Set Manual causes its a pain everytime I tried to refer back after to it.

## RISC-V 32I Base instruction format
32I Decode
![alt text](docs/riscv_instruction_decode.jpg "32I decode scheme")

![alt text](docs/riscv_instruction_set_listing.jpg "32I binary instruction set")

# Run test
```
export PYTHONPATH=$(pwd)
pytest
```

## Overall goals (TODO)
- ~~Write a 32-bit core in Python~~
- Write a 32-bit core in Rust
- Instruction pipelining
- Port over to Verilog
- Syn on FPGA?
- ???
- Profit
