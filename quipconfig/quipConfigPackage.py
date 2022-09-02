import yaml
import paramiko
import logging

from .quipRemoteExecutionException import QuipRemoteExecutionException

class QuipConfigPackage(yaml.YAMLObject):
    yaml_tag = u'!Package'
    yaml_loader = yaml.SafeLoader

    def __init__(self, name: str, version: str, action: str, restart: list[str]):
        self.name = name
        self.version = version
        self.action = action
        self.restart = restart

    def _remote_exec(self, client:paramiko.SSHClient, cmd: str) -> str:  
        stdin, stdout, stderr = client.exec_command(cmd)
        errors = stderr.readlines()

        ignore = ["debconf: delaying package configuration, since apt-utils is not installed"]
        for e in errors:
            if e.strip('\n') in ignore:
                errors.remove(e)

        if errors != []:
            raise QuipRemoteExecutionException(f"Error executing remote command: {errors}")
        return stdout

    def is_installed(self, client: paramiko.SSHClient) -> bool:
        logging.debug(f"{client.get_transport().getpeername()}: Checking {self.name} ...") 
        out = self._remote_exec(client, f"dpkg-query -W | grep {self.name}").readlines()

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
        out = self._remote_exec(client, f"apt-get install -y {self.name}={self.version}").readline().strip('\n')
        logging.debug(f"{client.get_transport().getpeername()}: Installed {self.name} ...")

    def uninstall(self, client: paramiko.SSHClient):
        logging.debug(f"{client.get_transport().getpeername()}: Uninstalling {self.name} ...") 
        out = self._remote_exec(client, f"apt-get remove -y {self.name}={self.version}").readline().strip('\n')
        logging.debug(f"{client.get_transport().getpeername()}: Uninstalled {self.name} ...")

