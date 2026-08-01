import pytest
import glob
from cpu import CPU

RISCV_TEST_PATH = "../riscv-tests/isa"


def _test_files(pattern):
    return [f for f in glob.glob(f"{RISCV_TEST_PATH}/{pattern}") if not f.endswith('.dump')]


@pytest.fixture
def cpu():
    return CPU()


# ── RV32I: base integer (implemented) ─────────────────────────────────────
rv32ui_files = _test_files("rv32ui-p-*")

# ── RV32SI: supervisor integer (partially implemented: ECALL works, CSR stubbed) ─
rv32si_files = _test_files("rv32si-p-*")

# ── RV64UI: 64-bit base integer (not implemented) ──────────────────────────
rv64ui_files = _test_files("rv64ui-p-*")

# ── RV64SI: 64-bit supervisor (not implemented) ────────────────────────────
rv64si_files = _test_files("rv64si-p-*")

# ── RV32MI: machine-mode integer (not implemented) ─────────────────────────
rv32mi_files = _test_files("rv32mi-p-*")

# ── RV64MI: 64-bit machine-mode (not implemented) ──────────────────────────
rv64mi_files = _test_files("rv64mi-p-*")

# ── RV32M / RV64M: multiply/divide extension (not implemented) ──────────────
rv32um_files = _test_files("rv32um-p-*")
rv64um_files = _test_files("rv64um-p-*")

# ── RV32A / RV64A: atomic extension (not implemented) ───────────────────────
rv32ua_files = _test_files("rv32ua-p-*")
rv64ua_files = _test_files("rv64ua-p-*")

# ── RV32C / RV64C: compressed instructions (not implemented) ────────────────
rv32uc_files = _test_files("rv32uc-p-*")
rv64uc_files = _test_files("rv64uc-p-*")
