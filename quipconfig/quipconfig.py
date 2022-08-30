import argparse
import yaml
import pathlib, os
from .quipConfigFile import QuipConfigFile
from .quipConfigPackage import QuipConfigPackage

from typing import Tuple

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("role", nargs='?', type=str, default="web", help="The role for the server. Determines which configuration to apply")
    args = parser.parse_args()
    role = args.role

    files: list[QuipConfigFile]
    packages = list[QuipConfigPackage]

    print(f"Configuring server of type: {role}")

    # Read and Parse the Configuration
    files, packages = read_role_config(role)

    print(files)
    print(packages)

def read_role_config(role: str) -> Tuple[list[QuipConfigFile], list[QuipConfigPackage]]:
    path = pathlib.Path(pathlib.Path(__file__).resolve().parent / f"configs\{role}_config.yml")
    with open(path, 'r') as config_file:
        data = config_file.read()
        content = yaml.safe_load(data)
        files = content.get("files")
        packages = content.get("packages")
        return content.get("files"), content.get("packages")