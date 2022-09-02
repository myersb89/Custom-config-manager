import paramiko

class QuipRemoteExecutionException(Exception):
    pass

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
