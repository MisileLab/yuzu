import docker
import click
from docker.models.containers import Container
from docker.models.images import Model
from docker.errors import NotFound
from misilelibpy import check_path
from os.path import isdir, isfile
from os import mkdir, remove
from tomli import loads

class Dockers:
    def __init__(self):
        self.client = docker.from_env()

    def setup_some(self):
        if isdir("yuzu") is False:
            mkdir("yuzu")
        if isfile("yuzu.toml"):
            config = loads(open("yuzu.toml", "r").read())
        else:
            container: Model = self.client.containers.run("eclipse-temurin:8-jre-jammy", detach=True, mounts=[docker.types.Mount("yuzu", "yuzu", type="bind")]) # type: ignore
            config = {"id": container.id_attribute}
        try:
            c: Container = self.client.containers.get(config["id"]) # type: ignore
        except NotFound:
            remove("yuzu.toml")
            self.setup_some()
            return
        else:
            if c.status != "running":
                c.start()
            c.exec_run("sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt update && sudo apt dist-upgrade -y && sudo apt autoremove -y && sudo apt install python3.10")
            c.exec_run("curl -sSL https://install.python-poetry.org | python3 -")
            c.exec_run("git clone https://github.com/misilelab/midori yuzu/midori && cd yuzu/midori && poetry install && cd -")

    def update_some(self):
        config = loads(open("yuzu.toml", "r").read())["id"]
        self.client.images.pull('eclipse-temurin:8-jre-jammy')
        self.client.images.pull('eclipse-temurin:17-jre-jammy')
        c = self.client.containers.get(config)
        c.exec_run("sudo apt update && sudo apt dist-upgrade -y && sudo apt autoremove -y") # type: ignore

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

