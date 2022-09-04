import yaml
import paramiko
import logging
from typing import Tuple
from .quipRemoteHost import QuipRemoteExecutionException, QuipRemoteHost

class QuipConfigFile(yaml.YAMLObject):
    yaml_tag = u'!File'
    yaml_loader = yaml.SafeLoader

    def __init__(self, path: str, content: str, owner: str, group: str, permissions: str, restart: list[str]):
        self.path = path
        self.content = content
        self.owner = owner
        self.group = group
        self.permissions = permissions
        self.restart = restart

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

    def needs_update(self, client: QuipRemoteHost) -> bool:
        # The file needs updating if it doesn't exist, permissions/owner/group different, or content changed
        print(f"{client.log_prefix} Checking {self.path} ...")
        out = client.remote_exec(f'[ -e "{self.path}" ] && echo 1 || echo 0').readline().strip('\n')
        if out == '0':
            print(f"{client.log_prefix} {self.path} does not exist")
            return True

        # Check metadata with ls -al
        out = client.remote_exec(f"ls -al {self.path}").readline().strip('\n')
        permissions, owner, group = self._parse_ls(out)
        logging.debug(f"{client.log_prefix} {self.path} permissions: {permissions} {owner} {group}")
        if permissions != self.permissions or owner != self.owner or group != self.group:
            print(f"{client.log_prefix} {self.path} permissions have changed")
            return True

        # Check content with cat
        out = """""".join(client.remote_exec(f"cat {self.path}").readlines())
        logging.debug(f"{client.log_prefix} content\n {out}")
        if out.strip('\n') != self.content.strip('\n'):  
            print(f"{client.log_prefix} {self.path} content has changed")
            return True

        print(f"{client.log_prefix} {self.path} is up to date")
        return False
        
    def update(self, client: QuipRemoteHost):
        # Create/Update file, owner, group, permissions
        print(f"{client.log_prefix} Updating {self.path}")
        out = client.remote_exec(f"""cat << 'EOF' > {self.path}
{self.content}
EOF""") 
        out = client.remote_exec(f"chown {self.owner} {self.path}")
        out = client.remote_exec(f"chgrp {self.group} {self.path}")
        out = client.remote_exec(f"chmod {self._xform_permissions(self.permissions)} {self.path}")
        
        print(f"{client.log_prefix} Updated file {self.path}")       

