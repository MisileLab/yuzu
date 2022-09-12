use bollard::{Docker, errors::Error::DockerResponseServerError};
use futures_util::future::FutureExt;
use std::{
    time::Duration,
    thread::sleep,
    process::Command
};

fn main() {
  match Docker::connect_with_local_defaults() {
      Ok(_) => {},
      Err(a) => {
          match a {
              DockerResponseServerError{..} => {
                    println!("Docker does not response, Install docker please"); 
              },
              _ => {}
          }
      }
  }
}
