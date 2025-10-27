mod util;
use std::fmt::Debug;

fn main() {
    let mut a : Node<i32> = Node::new(10);
    let mut b : Node<i32> = Node::new(5);
    let mut c : Node<i32> = Node::new(6);
    c.left_Node(a);
    c.right_Node(b);
    let val = c.right;
    if let Some(b_) = val.is_leaf() {
        print!("{}",b_)
    }
}    

#[derive(Debug, PartialEq)]
struct Node<T>{
    value : T,
    left : Option<Box<Node<T>>>,
    right : Option<Box<Node<T>>>,
}


impl<T> Node<T>{
    pub fn new(value : T) -> Self{
        Self{
            value,
            left:None,
            right:None
        }
    }
    pub fn left_Node(&mut self,l : Node<T>){
        self.left = Some(Box::new(l));
    }
    pub fn right_Node(&mut self,r : Node<T>){
        self.right = Some(Box::new(r));
    }
    pub fn is_leaf(&self)->bool{
        return self.right.is_none() && self.right.is_none();
    }
}

impl <T : Debug> Node<T>{
    pub fn print(&self){
        println!("{:?}",self)
    }
}