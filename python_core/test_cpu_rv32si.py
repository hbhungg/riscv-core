import glob
import pytest

riscv_test_path = "../riscv-tests/isa"
rv32si_p = glob.glob(f"{riscv_test_path}/rv32si-p-*[!.dump]")

@pytest.mark.parametrize("fn", rv32si_p) 
def test_rv32si(fn, cpu):
  cpu.exec(fn)
  assert True