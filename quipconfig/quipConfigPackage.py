import yaml

class QuipConfigPackage(yaml.YAMLObject):
    yaml_tag = u'!Package'
    yaml_loader = yaml.SafeLoader

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version

    def is_installed(self) -> bool: 
        pass
    
    def install(self):
        pass

    def restart(self):
        pass