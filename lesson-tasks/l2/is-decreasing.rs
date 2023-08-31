//# Compute if an i64 contains digits in decreasing order
//# ARGS: 954320
fn main(x:i64) {
    let tmp : bool = is_decreasing(x);
    println!("{:?}", tmp);
}

fn is_decreasing(x: i64) -> bool {
    let mut tmp : i64 = x;
    let mut prev : i64 = -1;
    while tmp > 0 {
        let digit : i64 = last_digit(tmp);
        if digit < prev {
            return false;
        }
        prev = digit;
        tmp = tmp / 10;
    }
    return true;    
}

fn last_digit(x: i64) -> i64 {
    return x - (x / 10) * 10;
}