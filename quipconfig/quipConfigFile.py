import yaml

class QuipConfigFile(yaml.YAMLObject):
    yaml_tag = u'!File'
    yaml_loader = yaml.SafeLoader

    def __init__(self, path: str, content: str):
        self.path = path
        self.content = content

    def needs_update(self) -> bool:
        pass

    def update(self):
        pass

    def restart_package(self):
        pass