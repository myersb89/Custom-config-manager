import pytest
import paramiko
import logging
from unittest.mock import patch, MagicMock
from quipconfig.quipRemoteExecution import QuipRemoteExecutionException
from quipconfig.quipconfig import *
   
@patch('paramiko.SSHClient')
def test_service_restart_happy(mockSshClient, caplog):
    stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
    stdout.readlines.return_value = ["Restarting nginx"]
    stderr.readlines.return_value = []
    mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        
    with caplog.at_level(logging.DEBUG):
        restart_service(mockSshClient, 'nginx')

    assert "Restarted" in caplog.text

@patch('paramiko.SSHClient')
def test_service_restart_no_systemd(mockSshClient, caplog):
    stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
    stdout.readlines.return_value = []
    stderr.readlines.return_value = ["System has not been booted with systemd"]
    mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(QuipRemoteExecutionException) as e:
            restart_service(mockSshClient, 'nginx')

    assert "/etc/init.d" in caplog.text
    assert e.type is QuipRemoteExecutionException

@patch('paramiko.SSHClient')
def test_service_restart_error(mockSshClient, caplog):
    stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
    stdout.readlines.return_value = []
    stderr.readlines.return_value = ["Some other error encountered"]
    mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        
    with caplog.at_level(logging.DEBUG):
        with pytest.raises(QuipRemoteExecutionException) as e:
            restart_service(mockSshClient, 'nginx')

    assert "/etc/init.d" not in caplog.text
    assert e.type is QuipRemoteExecutionException