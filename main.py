import docker
import click
from docker.models.containers import Container
from docker.models.images import Model
from docker.errors import NotFound
from misilelibpy import check_path, read_once, write_once
from os.path import isdir, isfile
from os import mkdir, remove
from tomli import loads
from json import loads, dumps

class Dockers:
    def __init__(self):
        self.client = docker.from_env()

    def setup_some(self):
        if isdir("yuzu") is False:
            mkdir("yuzu")
        if isfile("yuzu.toml"):
            config = loads(read_once("yuzu.toml"))
        else:
            container: Model = self.client.containers.run("eclipse-temurin:8-jre-jammy", detach=True, mounts=[docker.types.Mount("yuzu", "yuzu", type="bind")]) # type: ignore
            config = {"id": container.id_attribute}
            write_once("yuzu.toml", dumps(config))
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
            if isdir(check_path("yuzu/midori")) == False:
                c.exec_run("git clone https://github.com/misilelab/midori yuzu/midori && cd yuzu/midori && poetry install && cd -")
            else:
                c.exec_run("cd yuzu/midori && git pull && poetry install && cd -")

    def update_some(self):
        config = loads(read_once("yuzu.toml"))["id"]
        self.client.images.pull('eclipse-temurin:8-jre-jammy')
        self.client.images.pull('eclipse-temurin:17-jre-jammy')
        c: Container = self.client.containers.get(config) # type: ignore
        c.exec_run("sudo apt update && sudo apt dist-upgrade -y && sudo apt autoremove -y")
        c.exec_run("cd yuzu/midori && git pull && poetry install && cd -")

    def link_some(self, dicter: dict):
        c: Container = self.client.containers.get(loads(read_once("yuzu.toml"))["id"]) # type: ignore
        if isfile(check_path("yuzu/yuzu.json")) == False:
            write_once(check_path('yuzu/yuzu.json'), '{}')
        config: dict = loads(read_once(check_path('yuzu/yuzu.json')))
        if dicter["mversion"] is None:
            dicter["mversion"] = "latest"
        vstring = f"{dicter['version']}-{dicter['modloader']}-{dicter['mversion']}"
        if config.get(vstring) is None:
            string = "yuzu/midori/main.py "
            if dicter["modloader"] is not None:
                string = string + f"--modloader {dicter['modloader']} "
            string = string + f"--ram {dicter['ram']} --maindir yuzu/{vstring}"
            if dicter["mversion"] != "latest":
                string = string + f" --mversion {dicter['version']}"
            c.exec_run(string)
            config[vstring] = f"yuzu/{vstring}"
            write_once(check_path('yuzu/yuzu.json'), dumps(config))
            c.exec_run("'eula=true' > eula.txt")
        lpath = config[vstring]
        c.exec_run(f"mkdir server && ln -s {lpath}/libraries server/libraries && ln -s {lpath}/eula.txt server/eula.txt")

    def run_java(self, ram: int):
        c: Container = self.client.containers.get(loads(read_once("yuzu.toml"))["id"]) # type: ignore
        c.exec_run(f"java --Xms{ram}G -Xmx{ram}G -jar *.jar")

@click.option('--version', type=str, help="minecraft version")
@click.option('--modloader', type=str, default=None, help="modloader, default is vanilia")
@click.option('--mversion', type=str, default=None, help="modloader version, default is latest")
@click.option('--ram', type=int, default=8, help="minecraft ram, default is 8GB")
@click.option('--dir', type=str, help="dir of server")
@click.command("create")
def main(version: str, mversion: str | None, ram: int, dir: str | None, modloader: str | None):
    dockers = Dockers()
    dockers.setup_some()
    dockers.update_some()
    dockers.link_some({
        {
            "version": version,
            "mversion": mversion,
            "ram": ram,
            "dir": dir,
            "modloader": modloader
        }
    }) # type: ignore
    dockers.run_java(ram)

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

