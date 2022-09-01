import yaml
import paramiko
import logging

from .quipRemoteExecutionException import QuipRemoteExecutionException

class QuipConfigPackage(yaml.YAMLObject):
    yaml_tag = u'!Package'
    yaml_loader = yaml.SafeLoader

    def __init__(self, name: str, version: str, action: str):
        self.name = name
        self.version = version
        self.action = action

    def _remote_exec(self, client:paramiko.SSHClient, cmd: str) -> str:
        stdin, stdout, stderr = client.exec_command(cmd)
        errors = stderr.readlines()
        if errors != []:
            raise QuipRemoteExecutionException(f"Error executing remote command: {errors}")
        return stdout

    def is_installed(self, client: paramiko.SSHClient) -> bool:
        logging.debug(f"{client.get_transport().getpeername()}: Checking {self.name} ...") 
        out = self._remote_exec(client, f"dpkg-query -W | grep {self.name}").readline().strip('\n')
        if out != "":
            version = out.split('\t')[1]
            if version == self.version:
                logging.debug(f"{client.get_transport().getpeername()}: {self.name} {self.version} is installed")
                return True
        logging.debug(f"{client.get_transport().getpeername()}: {self.name} {self.version} is not installed")
        return False
    
    def install(self, client: paramiko.SSHClient):
        pass

    def uninstall(self, client: paramiko.SSHClient):
        pass

    def restart(self):
        pass