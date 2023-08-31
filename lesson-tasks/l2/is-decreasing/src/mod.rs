//# Print last digit of a i64
//# ARGS: 123
fn main() {
    let x : i64 = 123;
    let tmp : i64 = last_digit(x);
    println!("{:?}", tmp);
}

fn last_digit(x: i64) -> i64 {
    return x % 10;
}