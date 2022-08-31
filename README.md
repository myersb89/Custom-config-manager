# Custom-config-manger
TODOS:
- Document how to create a config
    - bonus, add a wizard?
- Create exception for remote execution errors
- Tests for file class
- Finish file class functionality

# Test Environment
docker build -t test-ssh .
docker run -d -p 2222:22 --name test-web-server1 test-ssh:latest
ssh root@127.0.0.1 -p 2222