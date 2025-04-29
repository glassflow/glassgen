import pytest

from glassgen.config import (
    ConfigError,
    GlassGenConfig,
    validate_config,
)


def test_valid_config(basic_config):
    """Test validation of a valid configuration"""
    config = validate_config(basic_config)
    assert isinstance(config, GlassGenConfig)
    assert config.schema_config["name"] == "$name"
    assert config.sink.type == "csv"
    assert config.generator.rps == 100
    assert config.generator.num_records == 10


def test_invalid_rps():
    """Test validation of invalid RPS value"""
    invalid_config = {
        "schema": {"name": "$name"},
        "sink": {"type": "csv"},
        "generator": {"rps": -1, "num_records": 10},
    }

    with pytest.raises(ConfigError) as exc_info:
        validate_config(invalid_config)

    assert "rps" in str(exc_info.value.details["errors"][0]).lower()


def test_invalid_duplication_ratio():
    """Test validation of invalid duplication ratio"""
    invalid_config = {
        "schema": {"name": "$name", "email": "$email"},
        "sink": {"type": "csv"},
        "generator": {
            "rps": 100,
            "num_records": 10,
            "event_options": {
                "duplication": {
                    "enabled": True,
                    "ratio": 1.5,  # Invalid ratio > 1
                    "key_field": "email",
                    "time_window": "1h",
                }
            },
        },
    }

    with pytest.raises(ConfigError) as exc_info:
        validate_config(invalid_config)

    assert "ratio" in str(exc_info.value.details["errors"][0]).lower()


def test_missing_key_field():
    """Test validation when key_field is not in schema"""
    invalid_config = {
        "schema": {"name": "$name"},  # Missing email field
        "sink": {"type": "csv"},
        "generator": {
            "rps": 100,
            "num_records": 10,
            "event_options": {
                "duplication": {
                    "enabled": True,
                    "ratio": 0.2,
                    "key_field": "email",  # email not in schema
                    "time_window": "1h",
                }
            },
        },
    }

    with pytest.raises(ConfigError) as exc_info:
        validate_config(invalid_config)

    assert "key_field" in str(exc_info.value.details["errors"][0]).lower()


def test_extra_fields():
    """Test validation of configuration with extra fields"""
    config_with_extra = {
        "schema": {"name": "$name"},
        "sink": {"type": "csv", "extra_field": "value"},
        "generator": {"rps": 100, "num_records": 10},
    }

    with pytest.raises(ConfigError) as exc_info:
        validate_config(config_with_extra)

    assert "extra_field" in str(exc_info.value.details["errors"][0]).lower()


def test_valid_duplication_config(duplication_config):
    """Test validation of a valid duplication configuration"""
    config = validate_config(duplication_config)
    assert config.generator.event_options.duplication is not None
    assert config.generator.event_options.duplication.enabled is True
    assert config.generator.event_options.duplication.ratio == 0.2
    assert config.generator.event_options.duplication.key_field == "email"
    assert config.generator.event_options.duplication.time_window == "1h"
