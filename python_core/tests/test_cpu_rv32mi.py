import pytest
from tests.conftest import rv32mi_files


@pytest.mark.xfail(reason="Machine-mode not implemented", strict=False)
@pytest.mark.parametrize("fn", rv32mi_files)
def test_rv32mi(fn, cpu):
    cpu.exec(fn)
