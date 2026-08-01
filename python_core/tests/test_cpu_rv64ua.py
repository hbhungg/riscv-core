import pytest
from tests.conftest import rv64ua_files


@pytest.mark.xfail(reason="RV64 A extension not implemented", strict=False)
@pytest.mark.parametrize("fn", rv64ua_files)
def test_rv64ua(fn, cpu):
    cpu.exec(fn)
