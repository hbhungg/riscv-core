import pytest
from tests.conftest import rv32ui_files


@pytest.mark.parametrize("fn", rv32ui_files)
def test_rv32ui(fn, cpu):
    cpu.exec(fn)
