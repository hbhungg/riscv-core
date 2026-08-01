import pytest
from tests.conftest import test_files

files = test_files("rv64ui-p-*")

@pytest.mark.parametrize("fn", files) 
def test_rv64ui(fn, cpu):
  cpu.exec(fn)
  assert True
