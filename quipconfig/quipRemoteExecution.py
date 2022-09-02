import paramiko

class QuipRemoteExecutionException(Exception):
    pass

def quip_remote_exec(self, client:paramiko.SSHClient, cmd: str) -> str:  
    errors = stderr.readlines()
    stdin, stdout, stderr = client.exec_command(cmd)

    ignore = ["debconf: delaying package configuration, since apt-utils is not installed"]
    for e in errors:
        if e.strip('\n') in ignore:
            errors.remove(e)

    if errors != []:
        raise QuipRemoteExecutionException(f"Error executing remote command: {errors}")
    return stdout
