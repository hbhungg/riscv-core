from enum import Enum
import binascii
import struct

MAGIC_START = 0x80000000

def bitrange(ins, s, e):
  return (ins >> e) & ((1 << (s - e + 1)) - 1)

def sign_extend(x, l):
  return -((1 << l) - x) if x >> (l-1) == 1 else x

class Ops(Enum):
  LUI = 0b0110111
  LOAD = 0b0000011
  STORE = 0b0100011
  AUIPC = 0b0010111

  JAL = 0b1101111
  JALR = 0b1100111
  BRANCH = 0b1100011

  OP = 0b0110011
  IMM = 0b0010011

  MISC = 0b0001111
  SYSTEM = 0b1110011

class Funct3(Enum):
  # OP and IMM
  ADD = SUB = ADDI = 0b000
  SLLI = 0b001
  SLT = SLTI = 0b010
  SLTU = SLTIU = 0b011

  XOR = XORI = 0b100
  SRL = SRLI = SRA = SRAI = 0b101
  OR = ORI = 0b110
  AND = ANDI = 0b111

  # BRANCH 
  BEQ = 0b000
  BNE = 0b001
  BLT = 0b100
  BGE = 0b101
  BLTU = 0b110
  BGEU = 0b111

  # LOAD and STORE
  LB = SB = 0b000
  LH = SH = 0b001
  LW = SW = 0b010
  LBU = 0b100
  LHU = 0b101

  # MISC (are we going to use these?)
  FENCE = 0b000
  FENCEI = 0b001

  # SYSTEM
  ECALL = 0b000
  CSRRW = 0b001
  CSRRS = 0b010
  CSRRC = 0b011
  CSRRWI = 0b101
  CSRRSI = 0b110
  CSRRCI = 0b111

class InvalidMemory(Exception):
  def __init__(self, message="Invalid memory address"):
    super(InvalidMemory, self).__init__(message)

class Register:
  PC = 32
  def __init__(self, *args, **kwargs):
    self.regs = [0]*33
  def __getitem__(self, key):
    return self.regs[key]
  def __setitem__(self, key, val):
    if key == 0: return
    self.regs[key] = val & 0xffffffff
  def __repr__(self):
    return f"PC: {self.regs[32]:08x}"


class CPU:
  def __init__(self):
    self.regs = Register()
    self.regs[Register.PC] = MAGIC_START
    # 16KB at 0x80000000
    self.memory = b'\x00'*0x4000
  
  def load(self, addr, data):
    addr -= MAGIC_START
    if addr < 0 and addr >= len(self.memory): raise InvalidMemory(f"Address {addr:08x} is out of bound for {len(self.memory):08x}")
    self.memory = self.memory[:addr] + data + self.memory[addr+len(data):]
  
  def read32(self, addr):
    addr -= MAGIC_START
    if addr < 0 and addr >= len(self.memory): raise InvalidMemory(f"Address {addr:08x} is out of bound for {len(self.memory):08x}")
    return struct.unpack("<I", self.memory[addr:addr+4])[0]
  
  # TOOD: For refractoring?
  def decode(self, ins):
    raise NotImplementedError
  
  def execute(self, opcode, *args):
    raise NotImplementedError
  
  def step(self):
    # Fetch
    ins = self.read32(self.regs[Register.PC])
    print(bin(ins), hex(ins))

    # Decode
    opcode = Ops(bitrange(ins, 6, 0))
    # Write back register
    rd = bitrange(ins, 11, 7)

    # J-type
    if opcode == Ops.JAL:
      imm = sign_extend((bitrange(ins, 32, 31) << 20 | bitrange(ins, 19, 12) << 12 | bitrange(ins, 21, 20) << 11 | bitrange(ins, 30, 21) << 1), 21)
      self.regs[Register.PC] += imm
      print(opcode, imm)
    # I-type
    if opcode == Ops.IMM:
      funct3 = Funct3(bitrange(ins, 14, 12))
      rs1 = bitrange(ins, 19, 15)
      imm = sign_extend(bitrange(ins, 31, 20), 12)
      print(opcode, funct3, rs1, imm)
    
    print(self.regs)
    print()
  

  def coredump(self, start_addr=MAGIC_START, l=16, filename=None):
    start_addr -= MAGIC_START
    dump = [binascii.hexlify(self.memory[i:i+4][::-1]) for i in range(0,len(self.memory),4)]
    if filename is not None:
      with open(f"test-cache/{filename}") as f: f.write(b'\n'.join(dump))
    else:
      # Print core dump
      for i in range(start_addr//4, start_addr//4+l, 4):
        row = ' '.join(f"0x{chunk.decode('utf-8')}" for chunk in dump[i: i+4])
        print(f"0x{i*4+MAGIC_START:08x} {row}")

  def run(self):
    # while True:
    for _ in range(2):
      self.step()
