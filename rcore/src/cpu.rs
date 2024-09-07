use bitflags::bitflags;

// 1MB at 0x80000000
const MEMSIZE: usize = 0x40000;
// RISC-V have 32 register
const REGSIZE: usize = 33;
const PC: usize = 32;
pub const MAGIC_START: u32 = 0x80000000;

pub struct CPU {
  memory: [u8; MEMSIZE],
  register: [u32; REGSIZE],
}

enum DumpStyle {
  Hex,
  Bin,
}

bitflags! {
  struct Ops: u32 {
    // Load store
    const LUI = 0b0110111;
    const LOAD = 0b0000011;
    const STORE = 0b0100011;
    const AUIPC = 0b0010111;

    // Branch
    const JAL = 0b1101111;
    const JALR = 0b1100111;
    const BRANCH = 0b1100011;
    const OP = 0b0110011;
    const IMM = 0b0010011;

    // IDK
    const MISC = 0b0001111;
    const SYSTEM = 0b1110011;
  }

  struct Funct3: u8 {
    // OP and IMM
    const ADD = 0b000;
    const ADDI = 0b000;
    const SUB = 0b000;
    const SLLI = 0b001;
    const SLT = 0b010;
    const SLTI = 0b010;
    const SLTU = 0b011;
    const SLTIU = 0b011;
    const XOR = 0b100;
    const XORI = 0b100;
    const SRL = 0b101;
    const SRLI = 0b101;
    const SRA = 0b101;
    const SRAI = 0b101;
    const OR = 0b110;
    const ORI = 0b110;
    const AND = 0b111;
    const ANDI = 0b111;

    // BRANCH
    const BEQ = 0b000;
    const BNE = 0b001;
    const BLT = 0b100;
    const BGE = 0b101;
    const BLTU = 0b110;
    const BGEU = 0b111;

    // LOAD and STORE
    const LB = 0b000;
    const SB = 0b000;
    const LH = 0b001;
    const SH = 0b001;
    const LW = 0b010;
    const SW = 0b010;
    const LBU = 0b100;
    const LHU = 0b101;

    // MISC
    const FENCE = 0b000;
    const FENCEI = 0b001;

    // SYSTEM
    const ECALL = 0b000;
    const CSRRW = 0b001;
    const CSRRS = 0b010;
    const CSRRC = 0b011;
    const CSRRWI = 0b101;
    const CSRRSI = 0b110;
    const CSRRCI = 0b111;
  }
}

impl CPU {
  // Init all 0s
  pub fn new() -> Self {
    let mut register = [0; REGSIZE];
    register[32] = MAGIC_START;
    Self {
      memory: [0; MEMSIZE],
      register: register,
    }
  }

  /// Load data into memory at an address
  pub fn load(&mut self, addr: u32, data: &[u8]) {
    let start = usize::try_from(addr - MAGIC_START).unwrap();
    let end = start + usize::try_from(data.len()).unwrap();
    self.memory[start..end].copy_from_slice(data);
  }

  /// Read 32bit value from an address
  fn read32(&self, addr: u32) -> u32 {
    let start = usize::try_from(addr - MAGIC_START).unwrap();
    u32::from_le_bytes(self.memory[start..start + 4].try_into().unwrap())
  }

  fn setreg(&mut self, reg: usize, val: u32) {
    // Write to reg 0 will have no effect since it is hardwire to 0
    if reg != 0 {
      self.register[reg] = val;
    }
  }

  fn getreg(&self, reg: usize) -> u32 {
    // Just to be safe
    match reg {
      0 => 0,
      _ => self.register[reg],
    }
  }

  fn regdump(&self) {
    // Print a header
    println!("{:<5} {:>8}", "Reg", "Value");
    // Print each register with its value
    for idx in 0..31 {
      println!("{:<5} {:08x}", format!("x{}", idx), self.register[idx])
    }
    println!("{:<5} {:08x}", format!("{}", "PC"), self.register[32]);
  }

  /// Pretty print coredump
  fn coredump(&self, size: usize, style: DumpStyle) {
    let chunk_size: usize = 16;
    for (idx, chunk) in self.memory[0..size].chunks(chunk_size).enumerate() {
      let addr = MAGIC_START + (idx * chunk_size) as u32;
      let row = chunk.chunks(4).enumerate().fold(format!("0x{:08x}: ", addr), |acc, (_, byte)| {
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

  /// Main CPU loop
  pub fn step(mut self) {
    self.coredump(400, DumpStyle::Hex);
    loop {
      let vpc = self.getreg(PC);
      let ins: u32 = self.read32(vpc);
      println!("{:08x}: {:08x}", vpc, ins);
      self.setreg(PC, vpc + 4);
      break;
    }
    self.regdump();
  }
}
