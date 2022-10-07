import docker
import click
from docker.models.containers import Container
from docker.models.images import Model
from docker.errors import APIError, NotFound
from misilelibpy import check_path
from os.path import isfile
from os import remove
from tomli import loads

class Dockers:
    def __init__(self):
        self.client = docker.from_env()

    def setup_some(self):
        if isfile("yuzu.toml"):
            config = loads(open("yuzu.toml", "r").read())
        else:
            container: Model = self.client.containers.run("eclipse-temurin:8-jre-jammy", detach=True) # type: ignore
            config = {"id": container.id_attribute}
        try:
            c: Container = self.client.containers.get(config["id"]) # type: ignore
        except (APIError, NotFound):
            remove("yuzu.toml")
            self.setup_some()
            return
        else:
            if c.status != "running":
                c.start()
            c.exec_run("sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt update && sudo apt dist-upgrade && sudo apt install python3.10")
            c.exec_run("curl -sSL example.sh | python -") # i'll change it

    def update_some(self):
        config = loads(open("yuzu.toml", "r").read())["id"]
        c = self.client.containers.get(config)
        c.exec_run("sudo apt update && sudo apt dist-upgrade") # type: ignore

    def link_some(self):
        raise NotImplementedError

    def run_java(self):
        raise NotImplementedError

@click.option('--version', type=str, help="minecraft version")
@click.option('--mversion', type=str, default=None, help="modloader version, default is latest")
@click.option('--ram', type=int, default=8, help="minecraft ram, default is 8GB")
@click.option('--dir', type=str, help="dir of server")
@click.command("create")
def main():
    dockers = Dockers()
    dockers.setup_some()
    dockers.update_some()
    dockers.link_some()
    dockers.run_java()

@click.command("list")
def show_list():
    raise NotImplementedError

@click.command("remove")
def remove_container():
    raise NotImplementedError

@click.command("start")
def start():
    raise NotImplementedError

@click.command("stop")
def stop():
    raise NotImplementedError

