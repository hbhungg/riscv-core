import binascii

class CPU:
  def __init__(self):
    self.PC = 32
    self.regs = [0]*33
    self.regs[self.PC] =  0x80000000
    self.memory = b'\x00'*0x4000
  
  def load(self, addr, data):
    self.memory = self.memory[:addr] + data + self.memory[addr+len(data):]
  
  def coredump(self, start_addr=0, filename=None):
    dump = [binascii.hexlify(self.memory[i:i+4][::-1]) for i in range(0,len(self.memory),4)]
    if filename is not None:
      with open(f"test-cache/{filename}") as f: f.write(b'\n'.join(dump))
    else:
      # Print core dump
      for i in range(start_addr//4, len(dump), 4):
        row = ' '.join(f"0x{chunk.decode('utf-8')}" for chunk in dump[i: i+4])
        print(f"0x{i*4:08x} {row}")


