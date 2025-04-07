import pytest
import tempfile
import os
import yaml
from click.testing import CliRunner
from glassgen.cli import main, load_config, create_sink

def test_load_config():
    config_data = {
        "schema": {
            "name": "$string",
            "age": "$intrange(18, 65)"
        },
        "sink": {
            "type": "csv",
            "path": "output.csv"
        },
        "generation": {
            "count": 100,
            "rate": 10
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        yaml.dump(config_data, tmp)
        tmp_path = tmp.name
    
    try:
        loaded_config = load_config(tmp_path)
        assert loaded_config == config_data
    finally:
        os.unlink(tmp_path)

def test_create_sink():
    config = {
        "sink": {
            "type": "csv",
            "path": "test.csv"
        }
    }
    
    sink = create_sink(config)
    assert sink.filepath.name == "test.csv"
    sink.close()
    
    # Test invalid sink type
    config["sink"]["type"] = "invalid"
    with pytest.raises(ValueError, match="Unsupported sink type"):
        create_sink(config)

def test_cli_generate():
    runner = CliRunner()
    
    # Create a temporary config file
    config_data = {
        "schema": {
            "name": "$string",
            "age": "$intrange(18, 65)"
        },
        "sink": {
            "type": "csv",
            "path": "test_output.csv"
        },
        "generation": {
            "count": 5,
            "rate": 10
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        yaml.dump(config_data, tmp)
        tmp_path = tmp.name
    
    try:
        # Test successful generation
        result = runner.invoke(main, ["generate", "--config", tmp_path])
        assert result.exit_code == 0
        assert "Data generation completed successfully" in result.output
        
        # Test with non-existent config file
        result = runner.invoke(main, ["generate", "--config", "nonexistent.yaml"])
        assert result.exit_code != 0
        assert "Configuration file not found" in result.output
        
    finally:
        os.unlink(tmp_path)
        if os.path.exists("test_output.csv"):
            os.unlink("test_output.csv") 