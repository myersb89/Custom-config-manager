import yaml

class QuipConfigFile(yaml.YAMLObject):
    yaml_tag = u'!File'
    yaml_loader = yaml.SafeLoader

    def __init__(self, path, content):
        self.path = path
        self.content = content

    #def __repr__(self):
     #   return f"filepath: {self.path}"
