#!/usr/bin/env python3
import glob
from elftools.elf.elffile import ELFFile

from cpu import CPU, InvalidMemory

if __name__ == "__main__":
  riscv_tests = "riscv-tests/isa"
  files = glob.glob(f"{riscv_tests}/rv32ui-v-*[!.dump]")
  cpu = CPU()
  for fn in files:
    print(fn)
    with open(fn, "rb") as f:
      e = ELFFile(f)
      for s in e.iter_segments():
        try:
          cpu.load(s.header.p_paddr, s.data())
        except InvalidMemory:
          pass
    # cpu.coredump()
    cpu.run()
    break
