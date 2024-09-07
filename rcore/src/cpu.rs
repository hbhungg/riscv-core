// 1MB at 0x80000000
const MEMSIZE: usize = 0x40000;
const REGSIZE: usize = 32;
pub const MAGIC_START: u32 = 0x80000000;

pub struct CPU {
  memory: [u8; MEMSIZE],
  register: [u32; REGSIZE],
}

pub enum DumpStyle {
  Hex,
  Bin,
}

impl CPU {
  // Init all 0s
  pub fn new() -> Self {
    Self {
      memory: [0; MEMSIZE],
      register: [0; REGSIZE],
    }
  }

  pub fn load(&mut self, addr: u32, data: &[u8]) {
    let start = usize::try_from(addr - MAGIC_START).unwrap();
    let end = start + usize::try_from(data.len()).unwrap();
    self.memory[start..end].copy_from_slice(data);
  }

  pub fn read32(&self, addr: u32) -> u32 {
    let start = usize::try_from(addr - MAGIC_START).unwrap();
    u32::from_le_bytes(self.memory[start..start + 4].try_into().unwrap())
  }

  pub fn coredump(&self, size: usize, style: DumpStyle) {
    let chunk_size: usize = 16;
    for (idx, chunk) in self.memory[0..size].chunks(chunk_size).enumerate() {
      let row = chunk
        .chunks(4)
        .enumerate()
        .fold(format!("0x{:08x}: ", MAGIC_START + (idx * chunk_size) as u32), |acc, (_, byte)| {
          let x = u32::from_le_bytes(byte.try_into().unwrap());
          let formatted_byte = match style {
            DumpStyle::Hex => format!("0x{:08x} ", x),
            DumpStyle::Bin => format!("0b{:032b} ", x),
          };
          acc + &formatted_byte
        });
      println!("{}", row);
    }
  }

  pub fn step(&self) {
    let ins: u32 = self.read32(self.register[32]);
  }
}
