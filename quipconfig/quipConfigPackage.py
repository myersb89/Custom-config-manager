import yaml

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
        return False
    
    def install(self, client: paramiko.SSHClient):
        pass

    def uninstall(self, client: paramiko.SSHClient):
        pass

    def restart(self):
        pass