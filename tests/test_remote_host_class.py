import pytest
import paramiko
import logging
from unittest.mock import patch, MagicMock
from quipconfig.quipRemoteHost import QuipRemoteExecutionException, QuipRemoteHost

class TestQuipRemoteHost():
    def setup(self):
        self.testHost = QuipRemoteHost("127.0.0.1", 22, "root")

    @patch('paramiko.SSHClient')
    def test_remote_exec_ignore(self, mockSshClient):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readlines.return_value = ["installed"]
        stderr.readlines.return_value = ["debconf: delaying package configuration, since apt-utils is not installed"]
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        self.testHost.client = mockSshClient

        result = self.testHost.remote_exec('apt-get install -y nginx')

        assert result.readlines() == ["installed"]

    @patch('paramiko.SSHClient')
    def test_remote_exec_ignore_with_error(self, mockSshClient):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readlines.return_value = ["installed"]
        stderr.readlines.return_value = ["debconf: delaying package configuration, since apt-utils is not installed", "an actual error"]
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        self.testHost.client = mockSshClient

        with pytest.raises(QuipRemoteExecutionException) as e:
            result = self.testHost.remote_exec('apt-get install -y nginx')

        assert e.type is QuipRemoteExecutionException

    @patch('paramiko.SSHClient')
    def test_service_restart_happy(self, mockSshClient, caplog):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readlines.return_value = ["Restarting nginx"]
        stderr.readlines.return_value = []
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        self.testHost.client = mockSshClient

        with caplog.at_level(logging.DEBUG):
            self.testHost.service_interface('nginx', 'restart')

        assert "Restarted" in caplog.text

    @patch('paramiko.SSHClient')
    def test_service_stop_happy(self, mockSshClient, caplog):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readlines.return_value = ["Stopping nginx"]
        stderr.readlines.return_value = []
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        self.testHost.client = mockSshClient

        with caplog.at_level(logging.DEBUG):
            self.testHost.service_interface('nginx', 'stop')

        assert "Stopped" in caplog.text

    @patch('paramiko.SSHClient')
    def test_service_restart_no_systemd(self, mockSshClient, caplog):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readlines.return_value = []
        stderr.readlines.return_value = ["System has not been booted with systemd"]
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        self.testHost.client = mockSshClient

        with caplog.at_level(logging.DEBUG):
            with pytest.raises(QuipRemoteExecutionException) as e:
                self.testHost.service_interface('nginx', 'restart')

        assert "/etc/init.d" in caplog.text
        assert e.type is QuipRemoteExecutionException

    @patch('paramiko.SSHClient')
    def test_service_restart_error(self, mockSshClient, caplog):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readlines.return_value = []
        stderr.readlines.return_value = ["Some other error encountered"]
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        self.testHost.client = mockSshClient

        with caplog.at_level(logging.DEBUG):
            with pytest.raises(QuipRemoteExecutionException) as e:
                self.testHost.service_interface('nginx', 'restart')

        assert "/etc/init.d" not in caplog.text
        assert e.type is QuipRemoteExecutionException