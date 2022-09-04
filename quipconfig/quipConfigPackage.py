import yaml
import paramiko
import logging

from .quipRemoteHost import QuipRemoteExecutionException, QuipRemoteHost

class QuipConfigPackage(yaml.YAMLObject):
    yaml_tag = u'!Package'
    yaml_loader = yaml.SafeLoader

    def __init__(self, name: str, version: str, action: str, restart: list[str]):
        self.name = name
        self.version = version
        self.action = action
        self.restart = restart

    def __repr__(self):
        return f"{self.__class__.__name__} {self.name} {self.version}"

    def is_installed(self, client: QuipRemoteHost) -> bool:
        print(f"{client.log_prefix} Checking {self.name} ...") 
        out = client.remote_exec(f"dpkg-query -W | grep {self.name}").readlines()
        logging.debug(f"{client.log_prefix} Installed packages for {self.name}\n {out}")

        # Packages can have similar names. Grep narrows it down but need to check for exact match
        for pkg in out:
            pkg = pkg.strip('\n')
            if pkg.split('\t')[0] == self.name and pkg.split('\t')[1] == self.version:
                print(f"{client.log_prefix} {self.name} {self.version} is installed")
                return True
        print(f"{client.log_prefix} {self.name} {self.version} is not installed")
        return False
    
    def install(self, client: QuipRemoteHost):
        print(f"{client.log_prefix} Installing {self.name} ...") 
        out = client.remote_exec(f"DEBIAN_FRONTEND=noninteractive apt-get install -y {self.name}={self.version}").readline().strip('\n')
        
        print(f"{client.log_prefix} Installed {self.name} ...")

    def uninstall(self, client: QuipRemoteHost):
        print(f"{client.log_prefix} Uninstalling {self.name} ...") 
        out = client.remote_exec(f"DEBIAN_FRONTEND=noninteractive apt-get remove -y {self.name}={self.version}").readline().strip('\n')
        print(f"{client.log_prefix} Uninstalled {self.name} ...")

