import yaml
import paramiko
import logging

from .quipRemoteExecution import QuipRemoteExecutionException, quip_remote_exec

class QuipConfigPackage(yaml.YAMLObject):
    yaml_tag = u'!Package'
    yaml_loader = yaml.SafeLoader

    def __init__(self, name: str, version: str, action: str, restart: list[str]):
        self.name = name
        self.version = version
        self.action = action
        self.restart = restart

    def is_installed(self, client: paramiko.SSHClient) -> bool:
        logging.debug(f"{client.get_transport().getpeername()}: Checking {self.name} ...") 
        out = quip_remote_exec(client, f"dpkg-query -W | grep {self.name}").readlines()

        # Packages can have similar names. Grep narrows it down but need to check for exact match
        for pkg in out:
            pkg = pkg.strip('\n')
            if pkg.split('\t')[0] == self.name and pkg.split('\t')[1] == self.version:
                logging.debug(f"{client.get_transport().getpeername()}: {self.name} {self.version} is installed")
                return True
        logging.debug(f"{client.get_transport().getpeername()}: {self.name} {self.version} is not installed")
        return False
    
    def install(self, client: paramiko.SSHClient):
        logging.debug(f"{client.get_transport().getpeername()}: Installing {self.name} ...") 
        out = quip_remote_exec(client, f"DEBIAN_FRONTEND=noninteractive apt-get install -y {self.name}={self.version}").readline().strip('\n')
        logging.debug(f"{client.get_transport().getpeername()}: Installed {self.name} ...")

    def uninstall(self, client: paramiko.SSHClient):
        logging.debug(f"{client.get_transport().getpeername()}: Uninstalling {self.name} ...") 
        out = quip_remote_exec(client, f"DEBIAN_FRONTEND=noninteractive apt-get remove -y {self.name}={self.version}").readline().strip('\n')
        logging.debug(f"{client.get_transport().getpeername()}: Uninstalled {self.name} ...")

