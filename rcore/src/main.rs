use std::path::PathBuf;

use glob::glob;

use elf::ElfBytes;
use elf::endian::AnyEndian;


fn read_elf(path: &PathBuf) {
  let file_data = std::fs::read(path).expect("Could not read file.");
  let slice = file_data.as_slice();
  let file = ElfBytes::<AnyEndian>::minimal_parse(slice).expect("Open test1");
  println!("{:?}", file);
}

fn main() {
  for f in glob("../riscv-tests/isa/rv32ui-p-*[!.dump]").expect("'../riscv-tests/isa' not found") {
    match f {
      Ok(ref path) => {
        println!("Read file: {:?}", path.display());
        read_elf(path);
      },
      Err(e) => println!("{:?}", e),
    }
    break;
  }
}
