import argparse
import yaml
import pathlib, os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("role", nargs='?', type=str, default="web", help="The role for the server. Determines which configuration to apply")
    args = parser.parse_args()
    role = args.role

    print(f"Configuring server of type: {role}")

    path = pathlib.Path(pathlib.Path(__file__).resolve().parent / f"configs\{role}_config.yml")
    with open(path, 'r') as config_file:
        data = config_file.read()
        content = yaml.safe_load(data)
        print(content)
        