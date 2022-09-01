import pytest
import paramiko
import logging
from yaml import safe_load
from typing import Tuple
from unittest.mock import patch, MagicMock
from quipconfig.quipConfigPackage import QuipConfigPackage
from quipconfig.quipRemoteExecutionException import QuipRemoteExecutionException

class TestQuipConfigPackage():
    def setup(self):
        yaml = """
!Package
name: wget
version: '1.22'
action: install
"""
        self.testPackage = safe_load(yaml)

    def _exec_command_side_effect_happy(self, arg):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        cmd = arg.split()[0]

        if cmd == "" :
            stderr.readlines.return_value = []
            stdout.readline.return_value = ""

        return stdin, stdout, stderr

    @patch('paramiko.SSHClient')
    def test_is_installed_true(self, mockSshClient):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readline.return_value = "wget\t1.22"
        stderr.readlines.return_value = []
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        
        result = self.testPackage.is_installed(mockSshClient)

        assert result == True

    @patch('paramiko.SSHClient')
    def test_is_installed_false(self, mockSshClient):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readline.return_value = ""
        stderr.readlines.return_value = []
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        
        result = self.testPackage.is_installed(mockSshClient)

        assert result == False

    @patch('paramiko.SSHClient')
    def test_is_installed_wrong_version(self, mockSshClient):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readline.return_value = "wget\t1.21"
        stderr.readlines.return_value = []
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        
        result = self.testPackage.is_installed(mockSshClient)

        assert result == False