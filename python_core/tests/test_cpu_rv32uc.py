import pytest
from tests.conftest import rv32uc_files


@pytest.mark.xfail(reason="C extension (compressed) not implemented", strict=False)
@pytest.mark.parametrize("fn", rv32uc_files)
def test_rv32uc(fn, cpu):
    cpu.exec(fn)
