from enum import Enum
import binascii
import struct
import os
from itertools import count
from elftools.elf.elffile import ELFFile

from .utils import REGISTERS_NAME

MAGIC_START = 0x80000000
DEBUG = int(os.getenv("DEBUG", 0))

def bitrange(ins:int, s:int, e:int) -> int:
  """
  Slice ins[s, e], inclusive
  """
  return (ins >> e) & ((1 << (s - e + 1)) - 1)

def sign_ext(x:int, l:int):
  # Extend x to l length while preserving its sign
  # https://en.wikipedia.org/wiki/Sign_extension
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
  def __init__(self): self.regs = [0]*33
  def __getitem__(self, key): return self.regs[key]
  def __setitem__(self, key, val):
    # Write to reg 0 will have no effect since it is hardwire to 0
    if key == 0: return
    self.regs[key] = val & 0xFFFFFFFF
  def hexfmt(self, key): return f"{self.regs[key]:08x}" if self.regs[key] != 0 else " "*7 + "0" # Format hex 08x
  def __repr__(self):
    return "---- Register state ----\n" + "\n".join([" ".join([f"{REGISTERS_NAME[4*i+j]}: {self.hexfmt(4*i+j)}".rjust(16) for j in range(4)]) for i in range(8)]) + f"\nPC: {self.hexfmt(32)}\n"


class CPU:
  def __init__(self, register=Register()):
    self.register = register
    self.register[Register.PC] = MAGIC_START
    # 1MB at 0x80000000
    self.memory = bytearray(b'\x00' * 0x40000)
  
  def load(self, addr, data):
    addr -= MAGIC_START
    if addr < 0 or addr >= len(self.memory): raise InvalidMemory(f"Address {addr:08x} is out of bound for {len(self.memory):08x}")
    self.memory[addr:addr+len(data)] = data
  
  def read32(self, addr):
    addr -= MAGIC_START
    if addr < 0 or addr >= len(self.memory): raise InvalidMemory(f"Address {addr:08x} is out of bound for {len(self.memory):08x}")
    return struct.unpack("<I", self.memory[addr:addr+4])[0]
  
  def condition(self, funct3:Funct3, x:int, y:int):
    if funct3 == Funct3.BEQ:
      return x == y
    elif funct3 == Funct3.BNE:
      return x != y
    elif funct3 == Funct3.BLT:
      return sign_ext(x, 32) < sign_ext(y, 32)
    elif funct3 == Funct3.BGE:
      return sign_ext(x, 32) >= sign_ext(y, 32)
    elif funct3 == Funct3.BLTU:
      return x < y
    elif funct3 == Funct3.BGEU:
      return x >= y
    else:
      raise NotImplementedError

  def alu(self, funct3:Funct3, x:int, y:int, alt:bool):
    """
    Arithmetic Logic Unit
    """
    if funct3 == Funct3.ADD:
      if alt:
        return x - y
      else:
        return x + y
    # (y & 0x1F) is because we use the shamt (lower 5 bits) part of imm
    elif funct3 == Funct3.SLLI:
      return x << (y & 0x1F)
    elif funct3 == Funct3.SRL:
      out = x >> (y & 0x1F)
      if alt:
        sign_bit = x >> 31
        fill_shift = (((0xFFFFFFFF * sign_bit) << (32 - (y & 0x1F))) & 0xFFFFFFFF)
        return out | fill_shift
      else:
        return out
    elif funct3 == Funct3.OR:
      return x | y
    elif funct3 == Funct3.AND:
      return x & y
    elif funct3 == Funct3.XOR:
      return x ^ y
    elif funct3 == Funct3.SLT:
      return int(sign_ext(x, 32) < sign_ext(y, 32))
    elif funct3 == Funct3.SLTU:
      return int((x & 0xFFFFFFFF) < (y & 0xFFFFFFFF))
    else:
      raise NotImplementedError
  
  
  def step(self):
    # -------------- FETCH -------------- 
    ins = self.read32(self.register[Register.PC])
    if DEBUG > 1: print(f"Raw instruction: {bin(ins)} ({hex(ins)})")


    # -------------- DECODE -------------- 
    opcode = Ops(bitrange(ins, 6, 0))
    # Immediate decode
    imm_i = sign_ext(bitrange(ins, 31, 20), 12)
    imm_s = sign_ext((bitrange(ins, 32, 25) << 5) | bitrange(ins, 11, 7), 12)
    imm_b = sign_ext((bitrange(ins, 32, 31) << 12) | (bitrange(ins, 30, 25) << 5) | (bitrange(ins, 11, 8) << 1) | (bitrange(ins, 8, 7) << 11), 13)
    imm_u = sign_ext(bitrange(ins, 31, 12) << 12, 32)
    imm_j = sign_ext((bitrange(ins, 32, 31) << 20) | (bitrange(ins, 19, 12) << 12) | (bitrange(ins, 21, 20) << 11) | (bitrange(ins, 30, 21) << 1), 21)
    funct3 = Funct3(bitrange(ins, 14, 12))
    funct7 = bitrange(ins, 31, 25)
    # Write back register
    rd = bitrange(ins, 11, 7)
    # Read register
    rs1 = bitrange(ins, 19, 15)
    rs2 = bitrange(ins, 24, 20)

    vs1 = self.register[rs1]
    vs2 = self.register[rs2]
    vpc = self.register[Register.PC]

    # Alternative mode for OP and IMM
    # For IMM, it is only SRAI
    alt = (funct7 == 0b0100000) and (opcode == Ops.OP or (opcode == Ops.IMM and funct3 == Funct3.SRAI))


    # -------------- EXECUTE -------------- 
    if opcode == Ops.JAL:
      if DEBUG > 0: print(self.register.hexfmt(32), opcode, REGISTERS_NAME[rd], hex(imm_j))
      self.register[rd] = vpc + 4  # Store the next instruction addr
      self.register[Register.PC] += imm_j # Perform a jump
      return True # HACK: REMOVE THIS
    elif opcode == Ops.JALR:
      if DEBUG > 0: print(self.register.hexfmt(32), opcode, REGISTERS_NAME[rd], REGISTERS_NAME[rs1], hex(imm_i))
      self.register[rd] = vpc + 4  # Store the next instruction addr
      self.register[Register.PC] = vs1 + imm_i
      return True # HACK: REMOVE THIS
    elif opcode == Ops.BRANCH:
      if DEBUG > 0: print(self.register.hexfmt(32), opcode, funct3, REGISTERS_NAME[rs1], REGISTERS_NAME[rs2], hex(imm_b))
      if self.condition(funct3, vs1, vs2): # Check condition
        self.register[Register.PC] += imm_b
        return True # HACK: REMOVE THIS

    elif opcode == Ops.IMM:
      if DEBUG > 0: print(self.register.hexfmt(32), opcode, funct3, REGISTERS_NAME[rd], REGISTERS_NAME[rs1], hex(imm_i), funct3, funct7)
      self.register[rd] = self.alu(funct3, vs1, imm_i, alt)
    elif opcode == Ops.AUIPC:
      self.register[rd] = self.alu(funct3.ADD, vpc, imm_u, alt)
      if DEBUG > 0: print(self.register.hexfmt(32), opcode, REGISTERS_NAME[rd], hex(imm_u))
    elif opcode == Ops.LUI:
      self.register[rd] = self.alu(funct3.ADD, 0, imm_u, alt)
      if DEBUG > 0: print(self.register.hexfmt(32), opcode, REGISTERS_NAME[rd], hex(imm_u))
    elif opcode == Ops.OP:
      if DEBUG > 0: print(self.register.hexfmt(32), opcode, funct3, REGISTERS_NAME[rd], REGISTERS_NAME[rs1], REGISTERS_NAME[rs2])
      self.register[rd] = self.alu(funct3, vs1, vs2, alt)
    
    elif opcode == Ops.LOAD:
      if DEBUG > 0: print(self.register.hexfmt(32), opcode, REGISTERS_NAME[rd], REGISTERS_NAME[rs1], hex(imm_i))
      addr = self.alu(funct3.ADD, vs1, imm_i, alt)
      if funct3 == Funct3.LB:
        self.register[rd] = sign_ext(self.read32(addr)&0xFF, 8)
      elif funct3 == Funct3.LH:
        self.register[rd] = sign_ext(self.read32(addr)&0xFFFF, 16)
      elif funct3 == Funct3.LW:
        self.register[rd] = self.read32(addr)
      # Load unsign
      elif funct3 == Funct3.LBU:
        self.register[rd] = self.read32(addr)&0xFF
      elif funct3 == Funct3.LHU:
        self.register[rd] = self.read32(addr)&0xFFFF
    elif opcode == Ops.STORE:
      if DEBUG > 0: print(self.register.hexfmt(32), opcode, funct3, REGISTERS_NAME[rs1], REGISTERS_NAME[rs2], hex(imm_s))
      addr = self.alu(funct3.ADD, vs1, imm_s, alt)
      if funct3 == Funct3.SB:
        self.load(addr, struct.pack("B", vs2&0xFF))
      elif funct3 == Funct3.SH:
        self.load(addr, struct.pack("H", vs2&0xFFFF))
      elif funct3 == Funct3.SW:
        self.load(addr, struct.pack("I", vs2))
      if DEBUG > 2: self.coredump(vs1+imm_s-4, l=32)

    elif opcode == Ops.SYSTEM:
      if funct3 == Funct3.ECALL:
        if DEBUG > 0: print(self.register.hexfmt(32), opcode, "ECALL", REGISTERS_NAME[rd], REGISTERS_NAME[rs1])
        if self.register[3] > 1:
          raise Exception("Fail")
        elif self.register[3] == 1:
          return False
      else:
        if DEBUG > 0: print(self.register.hexfmt(32), opcode, "SKIP")
    elif opcode == Ops.MISC:
      if DEBUG > 0: print(self.register.hexfmt(32), opcode, "SKIP")
    else:
      if DEBUG > 0: print(self.register.hexfmt(32), opcode, REGISTERS_NAME[rd])
      raise NotImplementedError

    if DEBUG > 1: print(self.register, end="\n")

    # Next instruction
    self.register[Register.PC] += 4
    return True
  

  def coredump(self, start_addr=MAGIC_START, l=16, filename=None):
    start_addr -= MAGIC_START
    dump = [binascii.hexlify(self.memory[i:i+4][::-1]) for i in range(0,len(self.memory),4)]
    # if filename is not None:
    #   with open(f"test-cache/{filename}") as f: f.write(b'\n'.join(dump))
    # else:
      # Print core dump
    for i in range(start_addr//4, start_addr//4+l, 4):
      row = ' '.join(f"0x{chunk.decode('utf-8')}" for chunk in dump[i: i+4])
      print(f"0x{i*4+MAGIC_START:08x}: {row}")

  def start(self):
    for _ in count():
      r = self.step()
      if not r:
        break

  def exec(self, fn: str):
    # Read .dump file
    with open(fn, "rb") as f:
      e = ELFFile(f)
      for s in e.iter_segments():
        try:
          self.load(s.header.p_paddr, s.data())
        except InvalidMemory:
          pass
    self.start()


