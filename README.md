# Custom-config-manger
TODOS:
- Document how to create a config
    - bonus, add a wizard?
- invalid config file exception
- allow for latest version of package
- str/print reprs for objects
- parallelization per host 
- on file creation if the directory doesn't exist we should make it
- integration test
- type hint consistency


# Test Environment
docker build -t test-ssh .
docker run -d -p 2222:22 -p 8080:80 --name test-web-server1 test-ssh:latest
ssh root@127.0.0.1 -p 2222