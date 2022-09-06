# Concept
Configuration management tools tend to either use a "push" architecture where the tool is run from a central location or management server and pushes the configuration to target server, or a "pull" architecture where a lightweight client is installed on each target server that pulls the configuration from a central location or management server. Out of the commercially available tools, I have the most experience with Chef which uses the "pull" model. One of my pain points with Chef is running into issues with the initial setup of the Chef client software. For this project, I thought it would be fun to write this tool using the "push" model to do something different than what I have experience with and avoid the same sort of issues I've seen with Chef.

# Architecture
This tool is designed to be run from any location with Python installed that has SSH connectivity to the target servers. It then leverages the Python Paramiko library to remotely execute commands to apply the desired configuration to the target servers over SSH. 

The tool also uses the Python multiprocessing library to create a pool of worker processes. The configuration for each target host is submitted as a job to the worker process pool. This gives us a few benefits
1. Configuration for multiple hosts can run in parallel
2. The tool can scale up by running from a machine with more CPU cores and increasing the number of workers in the pool
3. An exception encountered while configuring a host does not cause the whole tool to crash and all configuration to fail; it is isolated to the worker process that ran into the exception 

# Configuration
The configuration files for the tool are written in YAML and consist of a key for `packages` with a value of a list of package objects to install/remove and a key for `files` with a value of a list of file objects to create/override on the target server. See below for package and file object specifications.

The configuration should be placed in the `quipconfig/configs` directory and follow the naming convention `<role name>_config.yml` where `role_name` is a descriptive name for the type of role the target hosts are intended to fulfil. e.g. `web_config.yml` for a webserver.

## Packages
A package consists a yaml tag `!Package` and the following required attributes:
*  name - The name of the package. Must be a valid package name to run with `apt-get install <name>` 
* version - The version of the package to install. Must be a valid version to run with `apt-get install <name>=<version>`
* action - Either "install" or "remove"
* restart = A list of services to restart after applying the configuration. Each service name must be valid when called with `systemctl` or `/etc/init.d` 

```yaml
!Package
name: nginx
version: '1.14.0-0ubuntu1.10'
action: install
restart: []
```

## Files
A file consists a yaml tag `!File` and the following required attributes:
* path - The absolute file path for the file 
* content - The content of the file specified as a yaml multiline string
* owner - The owner of the file
* group - The group the file belongs to
* permissions - The file permissions specified as a standard unix filepermission string e.g. `-rw-r--r--`
* restart = A list of services to restart after applying the configuration. Each service name must be valid when called with `systemctl` or `/etc/init.d` 

```yaml
!File
content:
  |
  <?php
  header("Content-Type: text/plain");
  echo "Hello, world!\n";
path: app.php
owner: root
group: root
permissions: -rw-r--r--
restart: ["nginx"]
```

# Installation
The tool could eventually be published to pypi and installed with the pip package manager, but for now should be installed from source into a Python virtual environment.

Assuming Python3.9 and Virtualenv are already installed:

```
git clone git@github.com:myersb89/Custom-config-manger.git
cd Custom-config-manager
virtualenv -p python3.9 venv
source ./venv/bin/activate  # .\venv\Scripts\Activate for windows
pip install -r requirements.txt
pip install --editable .

quipconfig --help 
```

# Invoke
Once installed the tool can be invoked with `quipconfig <role> <host> ... <host>` where
* role - must be the first argument and corresponds to the role name of the configuration file for the role configuration to apply to the hosts e.g. `web` for `web_config.yml`
* host - quipconfig accepts any number of host arguments where each host is the IP address of the target server. It can either be specified as `x.x.x.x` which defaults to ssh over port 22 or you can override the port with `x.x.x.x:<port>` e.g. `127.0.0.1:2222`

See `quipconfig --help` for full usage

# Test Environment
```
docker build -t test-ssh .
docker run -d -p 2222:22 -p 8080:80 --name test-web-server1 test-ssh:latest
docker run -d -p 2223:22 -p 8081:80 --name test-web-server2 test-ssh:latest
ssh root@127.0.0.1 -p 2222

quipconfig web 127.0.0.1:2222 127.0.0.1:2223
```

# TODOS
- integration test
- type hint consistency
- input validation
- wizard for configuration