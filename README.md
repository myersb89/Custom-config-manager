# Custom-config-manger
TODOS:
- Document how to create a config
    - bonus, add a wizard?
- Tests for file class
- file class restart stuff
- invalid config file exception
- finish package functionality

# Test Environment
docker build -t test-ssh .
docker run -d -p 2222:22 --name test-web-server1 test-ssh:latest
ssh root@127.0.0.1 -p 2222