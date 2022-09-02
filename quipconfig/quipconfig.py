import argparse
import yaml
import pathlib
import logging
import paramiko
import getpass
from .quipConfigFile import QuipConfigFile
from .quipConfigPackage import QuipConfigPackage
from .quipRemoteExecution import QuipRemoteExecutionException, QuipRemoteHost, quip_remote_exec
from typing import Tuple

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("role", nargs='?', type=str, default="web", help="The role for the server. Determines which configuration to apply")
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
        logging.getLogger('paramiko').setLevel(logging.CRITICAL+1)
    else:
        logging.basicConfig(format='%(asctime)s %(message)s')

    role = args.role

    files: list[QuipConfigFile]
    packages = list[QuipConfigPackage]

    print(f"Configuring server of type: {role}")

    # Read and Parse the Configuration
    data = read_role_config(role)
    files, packages = parse_role_config(data)

    #logging.debug(files)
    #logging.debug(packages)

    # Connect to the host
    hostip = "127.0.0.1"
    client = QuipRemoteHost(hostip, 2222, "root")
    logging.debug(f"Connecting to host {hostip}...")
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

    #for service in to_restart:
    #    restart_service(client, service)
        

def read_role_config(role: str) -> dict:
    path = pathlib.Path((pathlib.Path(__file__).resolve().parent).joinpath(f"configs\{role}_config.yml"))
    try:
        with open(path, 'r') as config_file:
            return yaml.safe_load(config_file)
    except FileNotFoundError:
        logging.error(f"Could not locate configuration for role: {role}. Please create the configuration file.")
        raise
    except yaml.YAMLError:
        logging.error(f"Invalid yaml syntax for role config: {role}.")
        raise

def parse_role_config(config_data: str) -> Tuple[list[QuipConfigFile], list[QuipConfigPackage]]:
    return config_data.get("files"), config_data.get("packages")

def restart_service(client: paramiko.SSHClient, service: str):
    try:
        logging.debug(f"{client.get_transport().getpeername()}: Restarting {service} ...")
        out = quip_remote_exec(client, f"systemctl restart {service}").readline().strip('\n')
    except QuipRemoteExecutionException as e:
        if "System has not been booted with systemd" in str(e):
            logging.debug(f"{client.get_transport().getpeername()}: Systemd not configured on remote host, falling back to /etc/init.d script ...")
            out = quip_remote_exec(client, f"/etc/init.d/{service} restart")
        else:
            raise
    logging.debug(f"{client.get_transport().getpeername()}: Restarted {service}")
