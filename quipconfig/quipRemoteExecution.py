import paramiko
import getpass

class QuipRemoteExecutionException(Exception):
    pass

class QuipRemoteHost():

    def __init__(self, host: str, port: int, user: str):
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.client.WarningPolicy)
        self.host = host
        self.user = user
        self.port = port
        self.log_prefix = f"{self.host}:{self.port}: "

    def connect(self):
        self.client.connect(self.host, port=self.port, username=self.user, password=getpass.getpass(prompt=f"Input password for host {self.host}: "))

    def remote_exec(self, cmd: str) -> str:  
        stdin, stdout, stderr = self.client.exec_command(cmd)
        errors = stderr.readlines()

        # Ignore non-fatal errors
        ignore = ["debconf: delaying package configuration, since apt-utils is not installed"]
        for e in errors:
            if e.strip('\n') in ignore:
                errors.remove(e)

        if errors != []:
            raise QuipRemoteExecutionException(f"Error executing remote command: {errors}")
        return stdout

def quip_remote_exec(client:paramiko.SSHClient, cmd: str) -> str:  
    stdin, stdout, stderr = client.exec_command(cmd)
    errors = stderr.readlines()

    # Ignore non-fatal errors
    ignore = ["debconf: delaying package configuration, since apt-utils is not installed"]
    for e in errors:
        if e.strip('\n') in ignore:
            errors.remove(e)

    if errors != []:
        raise QuipRemoteExecutionException(f"Error executing remote command: {errors}")
    return stdout
