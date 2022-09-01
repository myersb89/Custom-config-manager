import pytest
import paramiko
import logging
from yaml import safe_load
from typing import Tuple
from unittest.mock import patch, MagicMock
from quipconfig.quipConfigFile import QuipConfigFile
from quipconfig.quipRemoteExecutionException import QuipRemoteExecutionException

class TestQuipConfigFile():
    def setup(self):
        yaml = """
!File
content: this is a config
path: nginx.conf
owner: root
group: root
permissions: -rw-r--r--
"""
        self.testFile = safe_load(yaml)

    # Provide various working return values for paramiko exec_commands
    def _exec_command_side_effect_happy(self, arg):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        cmd = arg.split()[0]

        if cmd == "chown" or cmd == "chgrp" or cmd == "chmod":
            stderr.readlines.return_value = []
        elif cmd == "[":
            stderr.readlines.return_value = []
            stdout.readline.return_value = "1"
        elif cmd == "ls":
            stderr.readlines.return_value = []
            stdout.readline.return_value = "-rw-r--r-- 1 root root 18 Aug 31 20:52 nginx.conf"
        elif cmd == "cat":
            stderr.readlines.return_value = []
            stdout.readlines.return_value = ["this is a config"]

        return stdin, stdout, stderr

    # Provide error casess for paramiko exec_commands
    def _exec_command_side_effect_sad(self, arg):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        cmd = arg.split()[0]

        if cmd == "cat" or cmd == "[":
            stderr.readlines.return_value = ["There was an error"]

        return stdin, stdout, stderr

    @patch('paramiko.SSHClient')
    def test_update_happy_path(self, mockSshClient, caplog):
        mockSshClient.exec_command.side_effect = self._exec_command_side_effect_happy

        with caplog.at_level(logging.DEBUG):
            self.testFile.update(mockSshClient)

       # captured = capsys.readouterr()
        print(caplog.text)
        assert "updated file" in caplog.text

    @patch('paramiko.SSHClient')
    def test_update_with_error(self, mockSshClient):
        mockSshClient.exec_command.side_effect = self._exec_command_side_effect_sad
        with pytest.raises(QuipRemoteExecutionException) as e:
            self.testFile.update(mockSshClient)

        assert e.type is QuipRemoteExecutionException

    @patch('paramiko.SSHClient')
    def test_needs_update_happy_path_false(self, mockSshClient):
        mockSshClient.exec_command.side_effect = self._exec_command_side_effect_happy
        
        result = self.testFile.needs_update(mockSshClient)

        assert result == False

    @patch('paramiko.SSHClient')
    def test_needs_update_happy_path_true(self, mockSshClient):
        stdin, stdout, stderr = MagicMock(), MagicMock(), MagicMock()
        stdout.readline.return_value = '0'
        stderr.readlines.return_value = []
        mockSshClient.exec_command.return_value = (stdin, stdout, stderr)
        
        result = self.testFile.needs_update(mockSshClient)

        assert result == True

    @patch('paramiko.SSHClient')
    def test_needs_update_with_error(self, mockSshClient):
        mockSshClient.exec_command.side_effect = self._exec_command_side_effect_sad
        
        with pytest.raises(QuipRemoteExecutionException) as e:
            self.testFile.needs_update(mockSshClient)

        assert e.type is QuipRemoteExecutionException

    def test_parse_ls(self):
        permissions, owner, group = self.testFile._parse_ls("-rw-r--r-- 1 root users 18 Aug 31 20:52 nginx.conf")
        assert permissions == "-rw-r--r--"
        assert owner == "root"
        assert group == "users"

    def test_xform_permissions(self):
        permissions = self.testFile._xform_permissions("drwxr-xr-x")
        assert permissions == "755"

    def test_restart_package(self):
        self.testFile.restart_package()
        pass