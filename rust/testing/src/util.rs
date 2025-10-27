
pub fn rec_sub(
    k:usize,
    subsets:&mut Vec<Vec<i32>> ,
    subset:Vec<i32>,
    i:Option<usize>
){
    let I = match i {
        Some(i) => i,
        None => 0
    };
    let mut Subset = subset.clone();
    // println!("{}",I);
    println!("{:?}",Subset);
    if subset.len() == k {
        subsets.push(subset.clone())
    }else if I<=k {
        Subset.remove(I);
        rec_sub(k, subsets, Subset, Some(I));
        rec_sub(k, subsets, subset.clone(), Some(I+1));
    }
}

pub fn n_set(n:i32)->Vec<i32> {
        if n==0{
            return vec![];
        }
        let mut res = n_set(n-1);
        let mut N = vec![n.clone()];
    res.append(&mut N);
    return res;
} 

pub fn fib(n:i64)->i64 {
    println!("{n}");
    if n == 0 || n==1{
        return 1;
    }
    return n + fib(n-1)
}
