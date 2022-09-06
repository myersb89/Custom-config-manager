import logging
import pathlib
import yaml
from typing import Tuple
from .quipConfigFile import QuipConfigFile
from .quipConfigPackage import QuipConfigPackage

class QuipInvalidRoleConfigException(Exception):
    pass

def read_role_config(role: str) -> dict:
    path = pathlib.Path((pathlib.Path(__file__).resolve().parent).joinpath(f"configs\{role}_config.yml"))
    try:
        with open(path, 'r') as config_file:
            return yaml.safe_load(config_file)
    except FileNotFoundError:
        logging.error(f"Could not locate configuration for role: {role}. Please create the configuration file.")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Invalid yaml syntax for role config: {role}.")
        raise

def parse_role_config(config_data: str) -> Tuple[list[QuipConfigFile], list[QuipConfigPackage]]:
    files = config_data.get("files")
    packages = config_data.get("packages")

    for f in files:
        for required_attribute in ["path", "content", "owner", "group", "permissions", "restart"]:
            if required_attribute not in dir(f):
                raise(QuipInvalidRoleConfigException(f"Invalid configuration: File {f} is missing required attribute {required_attribute}"))

    for p in packages:
        for required_attribute in ["name", "version", "action", "restart"]:
            if required_attribute not in dir(p):
                raise(QuipInvalidRoleConfigException(f"Invalid configuration: Package {p} is missing required attribute {required_attribute}"))

    return files, packages