import pytest
from yaml.scanner import ScannerError
from unittest.mock import patch, mock_open
from quipconfig.quipconfig import *

def test_read_config_happy_path():
    data = read_role_config("web")
    assert type(data) == dict
    assert data.get("files") != None and data.get("packages") != None

def test_read_config_not_exists():
    with pytest.raises(FileNotFoundError) as e:
        data = read_role_config("fake")
    assert e.type is FileNotFoundError

def test_read_config_invalid_yaml():
    yaml = """
    this: 
      is: "Invalid
    """
    with patch('builtins.open', mock_open(read_data=yaml)):
        with pytest.raises(ScannerError) as e:
            data = read_role_config("web")
            out, err = capsys.readouterr()
    assert e.type is ScannerError