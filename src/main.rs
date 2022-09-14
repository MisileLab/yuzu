use bollard::{
    Docker, errors::Error::DockerResponseServerError,
    exec::CreateExecOptions, container::Config,
    image::CreateImageOptions
};
use futures_util::TryStreamExt;
use std::mem::drop;

#[tokio::main]
async fn main() {
  match Docker::connect_with_local_defaults() {
      Ok(_) => {},
      Err(a) => {
          match a {
              DockerResponseServerError{..} => {
                    panic!("Docker does not response, Install docker please");
              },
              _ => {}
          }
      }
  }
  let docker = Docker::connect_with_local_defaults().unwrap();
}

async fn create_image(version: JavaVersion, docker: Docker) -> String {
    let jversion = match version {
        JavaVersion::Java8 => { "openjdk8-jre" },
        JavaVersion::Java17 => { "openjdk17-jre" }
    };
    docker.create_image(
        Some(CreateImageOptions {
            from_image: "alpine:latest",
            ..Default::default()
        }),
        None,
        None,
    )
    .try_collect::<Vec<_>>()
    .await.unwrap();

    let alpine_config = Config {
        image: Some("alpine:latest"),
        tty: Some(true),
        ..Default::default()
    };

    let id = docker
        .create_container::<&str, &str>(None, alpine_config)
        .await.unwrap()
        .id;
    docker.start_container::<String>(&id, None).await.unwrap();
   
    let exec = docker.create_exec(
            &id,
            CreateExecOptions {
                attach_stdout: Some(true),
                attach_stderr: Some(true),
                cmd: Some(vec!["apk", "update"]),
                ..Default::default()
            },
        ).await.unwrap().id;
    docker.start_exec(&exec, None).await.unwrap();
    drop(exec);
    let exec = docker.create_exec(&id, CreateExecOptions{   
        attach_stderr: Some(true), attach_stdout: Some(true), cmd: Some(vec!["apk", "add", jversion]), ..Default::default()
    }).await.unwrap().id;
    docker.start_exec(&exec, None).await.unwrap();
    
    id
}

enum JavaVersion {
    Java8,
    Java17
}
