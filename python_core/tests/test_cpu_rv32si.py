import pytest
from tests.conftest import rv32si_files


@pytest.mark.parametrize("fn", rv32si_files)
def test_rv32si(fn, cpu):
    cpu.exec(fn)
