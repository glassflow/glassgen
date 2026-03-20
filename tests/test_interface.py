from glassgen import generate
from glassgen.config import GlassGenConfig
from glassgen.sinks import CSVSink


def test_generate_with_dict_config(basic_config, mock_sink):
    """Test generating data with dictionary config"""
    result = generate(basic_config, sink=mock_sink)
    assert isinstance(result, dict)
    assert result["sink"] == "csv"
    assert len(mock_sink.events) == 10  # num_records
    assert mock_sink.closed


def test_generate_with_pydantic_config(basic_config, mock_sink):
    """Test generating data with Pydantic config"""
    config = GlassGenConfig.model_validate(basic_config)
    result = generate(config, sink=mock_sink)
    assert isinstance(result, dict)
    assert result["sink"] == "csv"
    assert len(mock_sink.events) == 10
    assert mock_sink.closed


def test_generate_with_yield_sink(yield_sink_config):
    """Test generating data with yield sink"""
    gen = generate(yield_sink_config)
    events = list(gen)
    assert len(events) == 5  # num_records
    for event in events:
        assert "name" in event
        assert "email" in event


def test_duplication_feature(duplication_config):
    """Test event duplication feature"""
    gen = generate(duplication_config)
    events = list(gen)

    # Check that we have the expected number of events
    assert len(events) == 10

    # Count unique emails
    unique_emails = set(event["email"] for event in events)

    # Verify that we have some duplicates (since ratio is 0.2)
    assert len(unique_emails) < len(events)

    # Verify that the duplication ratio is approximately correct
    expected_duplicates = int(10 * 0.2)  # 20% of 10 records
    assert len(events) - len(unique_emails) >= expected_duplicates


def test_predefined_schema_with_deduplication(predefined_schema_dedup_config):
    """Test generating data with pre-defined UserSchema and deduplication"""
    from glassgen.schema.user_schema import UserSchema

    gen = generate(predefined_schema_dedup_config, schema=UserSchema())
    events = list(gen)

    # Check total number of events
    assert len(events) == predefined_schema_dedup_config["generator"]["num_records"]

    # Count unique emails
    unique_emails = set(event["email"] for event in events)

    # Verify we have duplicates
    assert len(unique_emails) < len(events)


def test_generate_with_sink_instance(basic_config, temp_csv_file):
    """Test generating data with a CSVSink instance"""
    # Remove sink from config to pass it separately
    config_without_sink = {
        "schema": basic_config["schema"],
        "generator": basic_config["generator"],
    }

    # Pass an instance
    csv_sink = CSVSink({"path": temp_csv_file})

    result = generate(config_without_sink, sink=csv_sink)
    assert isinstance(result, dict)
    assert result["sink"] == "CSVSink"
    assert csv_sink.file is None or csv_sink.file.closed


def test_generate_with_dict_csv_sink(basic_config, temp_csv_file):
    """Test generating data with a dict containing csv sink configuration"""
    # Remove sink from config to pass it separately as a dict
    config_without_sink = {
        "schema": basic_config["schema"],
        "generator": basic_config["generator"],
    }

    # Pass sink as a dict
    sink_dict = {"type": "csv", "params": {"path": temp_csv_file}}

    result = generate(config_without_sink, sink=sink_dict)
    assert isinstance(result, dict)
    assert result["sink"] == "csv"
