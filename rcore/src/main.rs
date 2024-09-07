use std::path::PathBuf;

use glob::glob;

use elf::endian::LittleEndian;
use elf::ElfBytes;

mod cpu;

fn read_elf(path: &PathBuf) {
  let buffer = std::fs::read(path).expect("Could not read file.");
  let elf = ElfBytes::<LittleEndian>::minimal_parse(buffer.as_slice()).expect("Failed to parse ELF");

  let mut cpu = cpu::CPU::new();

  for phdr in elf.segments().expect("Failed to get ELF segments") {
    let data = elf.segment_data(&phdr).unwrap();
    let offset: u32 = u32::try_from(phdr.p_vaddr).expect("could not cast u32?");
    if offset >= cpu::MAGIC_START {
      cpu.load(offset, data);
    }
  }
  cpu.coredump(400, cpu::DumpStyle::Hex);
}

fn main() {
  for f in glob("../riscv-tests/isa/rv32ui-p-*[!.dump]").expect("'riscv-tests' not found") {
    match f {
      Ok(ref path) => {
        println!("Read file: {:?}", path.display());
        read_elf(path);
      }
      Err(e) => println!("{:?}", e),
    }
    break;
  }
}
