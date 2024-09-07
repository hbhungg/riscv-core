use std::path::PathBuf;

use glob::glob;

use elf::endian::LittleEndian;
use elf::ElfBytes;

struct CPU {
  memory: Vec<u8>,
  register: [u32; 33],
}

impl CPU {
  const MAGIC_START: u64 = 0x80000000;
  fn new() -> Self {
    Self {
      // 1MB at 0x80000000
      memory: vec![0; 0x40000],
      register: [0; 33],
    }
  }

  fn load(&mut self, addr: u64, data: &[u8]) {
    let start = usize::try_from(addr - CPU::MAGIC_START).unwrap();
    let end = start + usize::try_from(data.len()).unwrap();
    self.memory[start..end].copy_from_slice(data);
    // self.print_memory_chunk(start, end);
  }

  fn read32(&self, addr: u64) -> [u8; 4] {
    let start = usize::try_from(addr - CPU::MAGIC_START).unwrap();
    self.memory[start..start+4].try_into().expect("should be size 4")
  }

  fn reg_dump(&self) {
    println!("Registers: {:?}", self.register)
  }
  fn mem_dump(&self) {
    println!("{:?}", self.memory)
  }

  fn print_memory_chunk(&self, start: usize, end: usize) {
    // Ensure the slice bounds are within the valid range
    if start <= end && end <= self.memory.len() {
      println!("{:?}", &self.memory[start..end]);
    } else {
      eprintln!("Error: Slice bounds are out of range.");
    }
  }
}

fn read_elf(path: &PathBuf) {
  let buffer = std::fs::read(path).expect("Could not read file.");
  let elf = ElfBytes::<LittleEndian>::minimal_parse(buffer.as_slice()).expect("Failed to parse ELF");

  let mut cpu = CPU::new();

  for phdr in elf.segments().expect("Failed to get ELF segments") {
    let data = elf.segment_data(&phdr).unwrap();
    if phdr.p_vaddr >= CPU::MAGIC_START {
      cpu.load(phdr.p_vaddr, data);
    }
  }

  // cpu.reg_dump();
  cpu.mem_dump();
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
