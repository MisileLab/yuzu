import docker
import click
from misilelibpy import check_path

def setup_some():
    raise NotImplemented

def update_some():
    raise NotImplementedError

def link_some():
    raise NotImplementedError

def run_java():
    raise NotImplementedError

@click.option('--version', type=str, help="minecraft version")
@click.option('--mversion', type=str, default=None, help="modloader version, default is latest")
@click.option('--ram', type=int, default=8, help="minecraft ram, default is 8GB")
@click.option('--dir', type=str, help="dir of server")
def main():
    setup_some()
    update_some()
    link_some()
    run_java()

