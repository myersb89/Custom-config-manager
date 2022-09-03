import pytest
import paramiko
import logging
from unittest.mock import patch, MagicMock
from quipconfig.quipRemoteExecution import QuipRemoteExecutionException, QuipRemoteHost
   
@patch('paramiko.SSHClient')
def test_remote_exec_ignore(mockSshClient):
    stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
    stdout.readlines.return_value = ["installed"]
    stderr.readlines.return_value = ["debconf: delaying package configuration, since apt-utils is not installed"]
    mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        
    result = quip_remote_exec(mockSshClient, 'apt-get install -y nginx')

    assert result.readlines() == ["installed"]

@patch('paramiko.SSHClient')
def test_remote_exec_ignore_with_error(mockSshClient):
    stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
    stdout.readlines.return_value = ["installed"]
    stderr.readlines.return_value = ["debconf: delaying package configuration, since apt-utils is not installed", "an actual error"]
    mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        
    with pytest.raises(QuipRemoteExecutionException) as e:
        result = quip_remote_exec(mockSshClient, 'apt-get install -y nginx')

    assert e.type is QuipRemoteExecutionException