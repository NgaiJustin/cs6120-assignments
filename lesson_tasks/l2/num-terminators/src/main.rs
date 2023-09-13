#![warn(clippy::pedantic, clippy::nursery)]
use bril_rs::{load_program_from_read, Program, Code, Instruction, EffectOps};
use clap::Parser;
use std::fs::File;

/// Count the number of terminators in the a .bril file
#[derive(Parser)]
struct CLI {
    /// The path to the file to read
    path: std::path::PathBuf,
}

fn main() {
    let args = CLI::parse();
    let bril_file = File::open(args.path).expect("Failed to open file");
    let program = load_program_from_read(bril_file);

    let count = count_terminators(&program);
    println!("{} terminators", count);
}

fn count_terminators(program: &Program) -> usize {
    program
        .functions
        .iter()
        .map(|f| f.instrs.iter().filter(|i| is_terminator(i)).count())
        .sum()
}

fn is_terminator(code: &Code) -> bool {
    match code {
        Code::Instruction(instr) => {
            match instr {
                Instruction::Effect {
                    op: EffectOps::Jump | EffectOps::Branch | EffectOps::Return,
                    ..
                } => true, 
                _ => false
            }
        }
        _ => false
    }
}