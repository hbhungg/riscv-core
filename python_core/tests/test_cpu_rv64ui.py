import pytest
from tests.conftest import rv64ui_files


@pytest.mark.xfail(reason="RV64I not implemented", strict=False)
@pytest.mark.parametrize("fn", rv64ui_files)
def test_rv64ui(fn, cpu):
    cpu.exec(fn)
