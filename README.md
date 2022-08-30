# Custom-config-manger
TODOS:
- Add testing framework
- Errors and edge cases
- Decide on push or pull architecture
    push:
    - look into remote code execution with python
    - threading/parallelization?
    pull:
    - how to get it installed
    - should it actually connect and download config, or run a local copy?
- Document how to create a config
    - bonus, add a wizard?

# Test Environment
docker build -t test-ssh .
docker run -d -p 2222:22 --name test-web-server1 test-ssh:latest
ssh root@127.0.0.1 -p 2222