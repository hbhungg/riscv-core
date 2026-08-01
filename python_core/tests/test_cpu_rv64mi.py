import pytest
from tests.conftest import rv64mi_files


@pytest.mark.xfail(reason="RV64 machine-mode not implemented", strict=False)
@pytest.mark.parametrize("fn", rv64mi_files)
def test_rv64mi(fn, cpu):
    cpu.exec(fn)
