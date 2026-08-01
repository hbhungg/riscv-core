import pytest
from tests.conftest import rv64si_files


@pytest.mark.xfail(reason="RV64 not implemented", strict=False)
@pytest.mark.parametrize("fn", rv64si_files)
def test_rv64si(fn, cpu):
    cpu.exec(fn)
