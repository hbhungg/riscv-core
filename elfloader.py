#!/usr/bin/env python3
import glob
from elftools.elf.elffile import ELFFile

from cpu import CPU

if __name__ == "__main__":
  riscv_tests = "riscv-tests/isa"
  files = glob.glob(f"{riscv_tests}/rv32ui-p-*[!.dump]")
  cpu = CPU()
  for fn in files:
    print(fn)
    with open(fn, "rb") as f:
      e = ELFFile(f)
      for s in e.iter_segments():
        cpu.load(s.header.p_paddr, s.data())
    cpu.coredump(0x00004200)
    break
