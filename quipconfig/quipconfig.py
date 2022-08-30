import argparse
import yaml
import pathlib
import logging
from .quipConfigFile import QuipConfigFile
from .quipConfigPackage import QuipConfigPackage
from typing import Tuple

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("role", nargs='?', type=str, default="web", help="The role for the server. Determines which configuration to apply")
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s %(message)s')

    role = args.role

    files: list[QuipConfigFile]
    packages = list[QuipConfigPackage]

    print(f"Configuring server of type: {role}")

    # Read and Parse the Configuration
    data = read_role_config(role)
    files, packages = parse_role_config(data)

    logging.debug(files)
    logging.debug(packages)

def read_role_config(role: str) -> dict:
    path = pathlib.Path((pathlib.Path(__file__).resolve().parent).joinpath(f"configs\{role}_config.yml"))
    try:
        with open(path, 'r') as config_file:
            return yaml.safe_load(config_file)
    except FileNotFoundError:
        logging.error(f"Could not locate configuration for role: {role}. Please create the configuration file.")
        raise
    except yaml.YAMLError:
        logging.error(f"Invalid yaml syntax for role config: {role}.")
        raise

def parse_role_config(config_data: str) -> Tuple[list[QuipConfigFile], list[QuipConfigPackage]]:
    return config_data.get("files"), config_data.get("packages")