import pytest
from tests.conftest import rv64um_files


@pytest.mark.xfail(reason="RV64 M extension not implemented", strict=False)
@pytest.mark.parametrize("fn", rv64um_files)
def test_rv64um(fn, cpu):
    cpu.exec(fn)
