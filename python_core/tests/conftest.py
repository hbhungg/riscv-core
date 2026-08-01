import pytest
from cpu import CPU
import glob

RISCV_TEST_PATH = "../riscv-tests/isa"

def test_files(pattern):
  return [f for f in glob.glob(f"{RISCV_TEST_PATH}/{pattern}") if not f.endswith('.dump')]

@pytest.fixture
def cpu():
    return CPU()
