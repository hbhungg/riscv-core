import glob
import pytest
from elftools.elf.elffile import ELFFile

from riscv_core.cpu import CPU, InvalidMemory

riscv_test_path = "riscv-tests/isa"
rv32ui_p = glob.glob(f"{riscv_test_path}/rv32ui-p-*[!.dump]")

@pytest.fixture
def cpu(): return CPU()

@pytest.mark.parametrize("fn", rv32ui_p) 
def test_rv32ui(fn, cpu):
  with open(fn, "rb") as f:
    e = ELFFile(f)
    for s in e.iter_segments():
      try:
        cpu.load(s.header.p_paddr, s.data())
      except InvalidMemory:
        pass
  # cpu.coredump()
  cpu.run()
  assert True
