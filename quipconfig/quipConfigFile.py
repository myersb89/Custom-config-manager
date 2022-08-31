import yaml
import paramiko
import logging
from typing import Tuple
from .quipRemoteExecutionException import QuipRemoteExecutionException

class QuipConfigFile(yaml.YAMLObject):
    yaml_tag = u'!File'
    yaml_loader = yaml.SafeLoader

    def __init__(self, path: str, content: str, owner: str, group: str, permissions: str):
        self.path = path
        self.content = content
        self.owner = owner
        self.group = group
        self.permissions = permissions

    def _remote_exec(self, client:paramiko.SSHClient, cmd: str) -> str:
        stdin, stdout, stderr = client.exec_command(cmd)
        errors = stderr.readlines()
        if errors != []:
            raise QuipRemoteExecutionException(f"Error executing remote command: {errors}")
        return stdout

    def _parse_ls(self, output: str) -> Tuple[str,str,str]:
        fields = output.split()
        permissions = fields[0]
        owner = fields[2]
        group = fields[3]

        return permissions, owner, group

    def _xform_permissions(self, permissions: str) -> str:
        xform = {"---": "0", "--x": "1", "-w-":"2", "-wx": "3",
                 "r--": "4", "r-x": "5", "rw-": "6", "rwx": "7"}
        return "".join([xform[permissions[1:4]], xform[permissions[4:7]], xform[permissions[7:]]])

    def needs_update(self, client: paramiko.SSHClient) -> bool:
        # The file needs updating if it doesn't exist, permissions/owner/group different, or content changed
        out = self._remote_exec(client, f'[ -e "{self.path}" ] && echo 1 || echo 0').readline().strip('\n')
        if out == '0':
            logging.debug(f"{client.get_transport().getpeername()}: {self.path} does not exist")
            return True

        # Check metadata with ls -al
        out = self._remote_exec(client, f"ls -al {self.path}").readline().strip('\n')
        permissions, owner, group = self._parse_ls(out)
        logging.debug(f"{client.get_transport().getpeername()}: {self.path} permissions: {permissions} {owner} {group}")
        if permissions != self.permissions or owner != self.owner or group != self.group:
            logging.debug(f"{client.get_transport().getpeername()}: {self.path} permissions have changed")
            return True

        # Check content with cat
        out = """""".join(self._remote_exec(client, f"cat {self.path}").readlines())
        if out.strip('\n') != self.content.strip('\n'):  
            logging.debug(f"{client.get_transport().getpeername()}: {self.path} content has changed")
            return True

        return False
        
    def update(self, client: paramiko.SSHClient):
        # Create/Update file, owner, group, permissions
        out = self._remote_exec(client, f"""cat << 'EOF' > {self.path}
{self.content}
EOF""") 
        out = self._remote_exec(client, f"chown {self.owner} {self.path}")
        out = self._remote_exec(client, f"chgrp {self.group} {self.path}")
        out = self._remote_exec(client, f"chmod {self._xform_permissions(self.permissions)} {self.path}")

        print(f"{client.get_transport().getpeername()}: updated file {self.path}")       

    def restart_package(self):
        pass