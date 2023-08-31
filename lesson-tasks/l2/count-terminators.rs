use bril_rs::{load_program, load_program_from_read, Program};
use clap::Parser;

/// Count the number of terminators in the a .bril file
#[derive(Parser)]
struct CLI {
    /// The path to the file to read
    path: std::path::PathBuf,
}

fn main() {
    let args = CLI::parse();
    let program = load_program(&args.path).expect("Failed to load program");
    let count = count_terminators(&program);
    println!("{} terminators", count);
}

fn count_terminators(program: &Program) -> usize {
    program
        .functions
        .iter()
        .map(|f| f.instrs.iter().filter(|i| i.op == "jmp").count())
        .sum()
}