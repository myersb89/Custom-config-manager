# Custom-config-manger
TODOS:
- Document how to create a config
    - bonus, add a wizard?
- invalid config file exception
- allow for latest version of package
- str/print reprs for objects
- parallelization per host 
- actually configure the web service

# Test Environment
docker build -t test-ssh .
docker run -d -p 2222:22 --name test-web-server1 test-ssh:latest
ssh root@127.0.0.1 -p 2222