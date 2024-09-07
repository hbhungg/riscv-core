use std::path::PathBuf;

use glob::glob;

use elf::endian::LittleEndian;
use elf::ElfBytes;

// 1MB at 0x80000000
const MEM_SIZE: usize = 0x40000;
struct CPU {
  memory: [u8; MEM_SIZE],
  register: [u32; 33],
}

enum DumpStyle {
  Hex,
  Bin,
}

impl CPU {
  const MAGIC_START: u32 = 0x80000000;
  // Init all 0s
  fn new() -> Self {
    Self {
      memory: [0; MEM_SIZE],
      register: [0; 33],
    }
  }

  fn load(&mut self, addr: u32, data: &[u8]) {
    let start = usize::try_from(addr - CPU::MAGIC_START).unwrap();
    let end = start + usize::try_from(data.len()).unwrap();
    self.memory[start..end].copy_from_slice(data);
  }

  fn read32(&self, addr: u32) -> u32 {
    let start = usize::try_from(addr - CPU::MAGIC_START).unwrap();
    u32::from_le_bytes(self.memory[start..start + 4].try_into().unwrap())
  }

  fn reg_dump(&self) {
    println!("Registers: {:?}", self.register)
  }

  fn mem_dump(&self, size: usize, style: DumpStyle) {
    let chunk_size: usize = 16;
    for (idx, chunk) in self.memory[0..size].chunks(chunk_size).enumerate() {
      let row = chunk.iter().enumerate().fold(
        format!("{:08x}: ", idx * chunk_size),
        |acc, (_, &byte)| {
          let formatted_byte = match style {
            DumpStyle::Hex => format!("{:02x} ", byte),
            DumpStyle::Bin => format!("{:08b} ", byte),
          };
          acc + &formatted_byte
        }
      );
      println!("{}", row);
    }
  }

  fn step(&self) {
    let ins: u32 = self.read32(self.register[32]);
  }
}

fn read_elf(path: &PathBuf) {
  let buffer = std::fs::read(path).expect("Could not read file.");
  let elf = ElfBytes::<LittleEndian>::minimal_parse(buffer.as_slice()).expect("Failed to parse ELF");

  let mut cpu = CPU::new();

  for phdr in elf.segments().expect("Failed to get ELF segments") {
    let data = elf.segment_data(&phdr).unwrap();
    let offset: u32 = u32::try_from(phdr.p_vaddr).expect("could not cast u32?");
    if offset >= CPU::MAGIC_START {
      cpu.load(offset, data);
    }
  }

  // cpu.reg_dump();
  cpu.mem_dump(400, DumpStyle::Hex);
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
