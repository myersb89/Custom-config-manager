import pytest
import paramiko
import logging
from yaml import safe_load
from typing import Tuple
from unittest.mock import patch, MagicMock
from quipconfig.quipConfigPackage import QuipConfigPackage
from quipconfig.quipRemoteExecution import QuipRemoteExecutionException, QuipRemoteHost

class TestQuipConfigPackage():
    def setup(self):
        yaml = """
!Package
name: wget
version: '1.22'
action: install
"""
        yaml_uninstall = """
!Package
name: nginx
version: '1.14.0-0ubuntu1.10'
action: uninstall
"""
        self.testPackage = safe_load(yaml)
        self.testPackageUninstall = safe_load(yaml)
        self.testHost = QuipRemoteHost("127.0.0.1", 22, "root")

    @patch('paramiko.SSHClient')
    def test_is_installed_true(self, mockSshClient):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readlines.return_value = ["wget\t1.22"]
        stderr.readlines.return_value = []
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        self.testHost.client = mockSshClient
        
        result = self.testPackage.is_installed(self.testHost)

        assert result == True

    @patch('paramiko.SSHClient')
    def test_is_installed_false(self, mockSshClient):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readlines.return_value = [""]
        stderr.readlines.return_value = []
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        self.testHost.client = mockSshClient
        
        result = self.testPackage.is_installed(self.testHost)

        assert result == False

    @patch('paramiko.SSHClient')
    def test_is_installed_wrong_version(self, mockSshClient):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readlines.return_value = ["wget\t1.21"]
        stderr.readlines.return_value = []
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        self.testHost.client = mockSshClient
        
        result = self.testPackage.is_installed(self.testHost)

        assert result == False

    @patch('paramiko.SSHClient')
    def test_is_installed_similar_package(self, mockSshClient):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readlines.return_value = ["libwget\t1.22"]
        stderr.readlines.return_value = []
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        self.testHost.client = mockSshClient
        
        result = self.testPackage.is_installed(self.testHost)

        assert result == False
    
    @patch('paramiko.SSHClient')
    def test_install(self, mockSshClient, caplog):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readlines.return_value = ["Preparing to unpack .../nginx_1.14.0-0ubuntu1.10_all.deb ...\n", 
                                         "Unpacking nginx (1.14.0-0ubuntu1.10) ... \n",
                                         "Setting up nginx (1.14.0-0ubuntu1.10) ...\n"]
        stderr.readlines.return_value = []
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        self.testHost.client = mockSshClient
        
        with caplog.at_level(logging.DEBUG):
            self.testPackage.install(self.testHost)

        assert "Installed" in caplog.text

    @patch('paramiko.SSHClient')
    def test_uninstall(self, mockSshClient, caplog):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readlines.return_value = ["Removing nginx (1.14.0-0ubuntu1.10) ..."]
        stderr.readlines.return_value = []
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        
        with caplog.at_level(logging.DEBUG):
            self.testPackage.uninstall(mockSshClient)

        assert "Uninstalled" in caplog.text