# Custom-config-manger
TODOS:
- Document how to create a config
    - bonus, add a wizard?
- invalid config file exception
- allow for latest version of package
- parallelization per host 
- integration test
- type hint consistency
- update log prefix with string repr

# Test Environment
docker build -t test-ssh .
docker run -d -p 2222:22 -p 8080:80 --name test-web-server1 test-ssh:latest
ssh root@127.0.0.1 -p 2222