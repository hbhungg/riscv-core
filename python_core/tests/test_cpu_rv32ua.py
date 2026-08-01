import pytest
from tests.conftest import rv32ua_files


@pytest.mark.xfail(reason="A extension (atomics) not implemented", strict=False)
@pytest.mark.parametrize("fn", rv32ua_files)
def test_rv32ua(fn, cpu):
    cpu.exec(fn)
