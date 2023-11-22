import glob
from elftools.elf.elffile import ELFFile

def read_elf(fn):
  with open(fn, "rb") as f:
    e = ELFFile(f)
    data = e.get_section_by_name(".text").data()
  return data

if __name__ == "__main__":
  riscv_tests = "riscv-tests/isa"
  files = glob.glob(f"{riscv_tests}/*[!.dump]")
  for i in files:
    print(read_elf(files[0]))