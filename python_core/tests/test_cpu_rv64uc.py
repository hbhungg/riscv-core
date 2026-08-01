import pytest
from tests.conftest import rv64uc_files


@pytest.mark.xfail(reason="RV64 C extension not implemented", strict=False)
@pytest.mark.parametrize("fn", rv64uc_files)
def test_rv64uc(fn, cpu):
    cpu.exec(fn)
