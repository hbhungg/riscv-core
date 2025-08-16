import glob
import pytest

riscv_test_path = "../riscv-tests/isa"
rv32ui_p = glob.glob(f"{riscv_test_path}/rv32ui-p-*[!.dump]")

@pytest.mark.parametrize("fn", rv32ui_p) 
def test_rv32ui(fn, cpu):
  cpu.exec(fn)
  assert True
