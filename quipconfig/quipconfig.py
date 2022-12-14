import argparse
import yaml
import pathlib
import logging
import paramiko
import getpass
from .quipConfigFile import QuipConfigFile
from .quipConfigPackage import QuipConfigPackage
from .quipRemoteHost import QuipRemoteExecutionException, QuipRemoteHost
from .quipRoleConfig import read_role_config, parse_role_config
from typing import Tuple
from multiprocessing import Pool

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("role", nargs='?', type=str, default="web", help="The role for the server. Determines which configuration to apply")
    parser.add_argument("hosts", nargs='*', default=["127.0.0.1:2222"], help="The hosts to apply the configuration to")
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.getLogger('paramiko').setLevel(logging.CRITICAL+1)
    else:
        logging.basicConfig(format='%(asctime)s %(message)s')

    role = args.role
    hosts = args.hosts

    files: list[QuipConfigFile]
    packages = list[QuipConfigPackage]

    print(f"Configuring server of type: {role}")

    # Read and Parse the Configuration
    data = read_role_config(role)
    files, packages = parse_role_config(data)

    logging.debug(f"Parsed out the following files and packages from {role} config")
    logging.debug(files)
    logging.debug(packages)

    password = getpass.getpass(prompt=f"Input root password for hosts: ")

    # Configure up to 4 hosts in parallel
    with Pool(4) as p:
        p.starmap(configure, [[host, password, files, packages] for host in hosts])


def configure(host: str, password: str, files: list[QuipConfigFile], packages: list[QuipConfigPackage]):
    hostip, port = parse_host(host)
    client = QuipRemoteHost(hostip, port, "root", password)
    print(f"Connecting to host {client}...")
    client.connect()

    # Main logic loop: Apply the configuration idempotently
    to_restart = set()
    for p in packages:
        installed = p.is_installed(client)
        if not installed and p.action == "install":
            p.install(client)
            to_restart.update(p.restart)
        elif installed and p.action == "uninstall":
            p.uninstall(client)
            to_restart.update(p.restart)

    for f in files:
        if f.needs_update(client):
            f.update(client)
            to_restart.update(f.restart)

    for service in to_restart:
        status = client.service_interface(service, 'status')
        if "is not running" in status:
            client.service_interface(service, 'start')
        else:
            client.service_interface(service, 'restart')

    client.close()

def parse_host(hoststr: str) -> Tuple[str, int]:
    # Better input validation goes here
    host = hoststr.split(":")
    port = 22
    if len(host) > 1:
        port = int(host[1])

    return host[0], port
