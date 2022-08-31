import pytest
import paramiko
from yaml import safe_load
from typing import Tuple
from unittest.mock import patch, MagicMock
from quipconfig.quipConfigFile import QuipConfigFile

class TestQuipConfigFile():
    def setup(self):
        yaml = """
!File
content: this is a config
path: nginx.conf
"""
        self.testFile = safe_load(yaml)

    def _exec_command_side_effect_happy(self, arg):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        cmd = arg.split()[0]

        if cmd == "cat":
            stderr.readlines.return_value = []

        return stdin, stdout, stderr

    def _exec_command_side_effect_sad(self, arg):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        cmd = arg.split()[0]

        if cmd == "cat":
            stderr.readlines.return_value = ["There was an error"]

        return stdin, stdout, stderr

    @patch('paramiko.SSHClient')
    def test_update_happy_path(self, mockSshClient, capsys):
        mockSshClient.exec_command.side_effect = self._exec_command_side_effect_happy

        self.testFile.update(mockSshClient)

        captured = capsys.readouterr()
        assert "Updating file" in captured.out

    @patch('paramiko.SSHClient')
    def test_update_with_error(self, mockSshClient, caplog):
        mockSshClient.exec_command.side_effect = self._exec_command_side_effect_sad

        self.testFile.update(mockSshClient)

        assert "Error executing remote command" in caplog.text
    
    def test_restart_package(self):
        self.testFile.restart_package()
        pass