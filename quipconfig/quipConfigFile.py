import yaml
import paramiko
import logging
from typing import Tuple

class QuipConfigFile(yaml.YAMLObject):
    yaml_tag = u'!File'
    yaml_loader = yaml.SafeLoader

    def __init__(self, path: str, content: str):
        self.path = path
        self.content = content

    def __parse_ls(self, output: list[str]) -> Tuple[str,str,str]:
        fields = output[0].split()
        permissions = fields[0]
        owner = fields[2]
        group = fields[3]

        return permissions, owner, group

    def needs_update(self, client: paramiko.SSHClient) -> bool:
        # The file needs updating if it doesn't exist, content doesn't match, or permissions and owners are incorrect
        stdin, stdout, stderr = client.exec_command(f"ls -al {self.path}")

        errors = stderr.readlines()
        if any("No such file or directory" in e for e in errors):
            logging.debug(f"File {self.path} does not exist on remote server")
            return True

        permissions, owner, group = self.__parse_ls(stdout.readlines())
        logging.debug(f"File {self.path} permissions: {permissions} {owner} {group}")

        return False
        

    def update(self, client: paramiko.SSHClient):
        print(f"Updating file {self.path}")
        stdin, stdout, stderr = client.exec_command(f"""cat << 'EOF' > {self.path}
{self.content}
EOF""")

        errors = stderr.readlines()
        print(errors)
        if errors != []:
            logging.error(f"Error executing remote command: {errors}")
        

    def restart_package(self):
        pass