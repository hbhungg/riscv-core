import pytest
from tests.conftest import test_files

files = test_files("rv32ui-p-*")

@pytest.mark.parametrize("fn", files) 
def test_rv32ui(fn, cpu):
  cpu.exec(fn)
  assert True
