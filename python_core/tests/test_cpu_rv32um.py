import pytest
from tests.conftest import rv32um_files


@pytest.mark.xfail(reason="M extension (mul/div) not implemented", strict=False)
@pytest.mark.parametrize("fn", rv32um_files)
def test_rv32um(fn, cpu):
    cpu.exec(fn)
