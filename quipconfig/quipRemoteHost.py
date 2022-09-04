import paramiko
import getpass
import logging

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

    def service_interface(self, service: str, cmd: str) -> str:
        try:
            if cmd == 'status':
                print(f"{self.log_prefix} Checking status of {service} ...")
            else:
                print(f"{self.log_prefix} {''.join(cmd + 'p').capitalize() if cmd == 'stop' else cmd.capitalize()}ing {service} ...")
            out = self.remote_exec(f"systemctl {cmd} {service}").readline().strip('\n')
        except QuipRemoteExecutionException as e:
            if "System has not been booted with systemd" in str(e):
                logging.debug(f"{self.log_prefix} Systemd not configured on remote host, falling back to /etc/init.d script ...")
                out = self.remote_exec(f"/etc/init.d/{service} {cmd}").readline().strip('\n')
            else:
                raise
        print(f"{self.log_prefix} {out}")
        return out

