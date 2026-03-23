from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from glassgen.config import GeneratorConfig
from glassgen.generator.batch_controller import DynamicBatchController
from glassgen.generator.duplication import DuplicateController
from glassgen.generator.generator import Generator
from glassgen.schema.base import BaseSchema


class TestDynamicBatchController:
    def test_initial_batch_size(self):
        """Test initial batch size calculation"""
        max_batch_size = 100
        controller = DynamicBatchController(target_rps=100)
        batch_size = controller.get_batch_size(max_batch_size)
        assert 1 <= batch_size <= max_batch_size

    def test_batch_size_with_remaining_records(self):
        """Test batch size calculation with remaining records"""
        max_batch_size = 100
        controller = DynamicBatchController(target_rps=100)
        controller.records_sent = 50  # Half of target RPS used
        batch_size = controller.get_batch_size(max_batch_size)
        assert batch_size > 0
        assert batch_size <= max_batch_size  # Should not exceed remaining records

    def test_record_sent_updates_count(self):
        """Test that record_sent updates the count correctly"""
        controller = DynamicBatchController(target_rps=100)
        controller.record_sent(10)
        assert controller.records_sent == 10

    @patch("time.sleep")
    def test_sleep_if_needed(self, mock_sleep):
        """Test sleep behavior when needed"""
        controller = DynamicBatchController(target_rps=100)
        controller.records_sent = 100  # All records sent
        controller._sleep_if_needed()
        mock_sleep.assert_called_once()

    @patch("time.sleep")
    def test_sleep_until_next_window(self, mock_sleep):
        """Test sleep until next window behavior"""
        controller = DynamicBatchController(target_rps=100)
        controller._sleep_until_next_window()
        mock_sleep.assert_called_once()
        assert controller.records_sent == 0  # Should reset count


class TestDuplicateController:
    def test_time_window_parsing(self, generator_config):
        """Test time window string parsing"""
        controller = DuplicateController(generator_config)
        assert controller.time_window == timedelta(hours=1)

        # Test different time units
        config = generator_config.model_copy()
        config.event_options.duplication.time_window = "30m"
        controller = DuplicateController(config)
        assert controller.time_window == timedelta(minutes=30)

        config.event_options.duplication.time_window = "2d"
        controller = DuplicateController(config)
        assert controller.time_window == timedelta(days=2)

    def test_add_record(self, generator_config):
        """Test adding records to the controller"""
        controller = DuplicateController(generator_config)
        record = {"id": "123", "data": "test"}
        controller.add_record(record)
        assert len(controller.duplicates) == 1
        assert controller.total_generated == 1

    def test_cleanup_old_duplicates(self, generator_config):
        """Test cleanup of old duplicates"""
        controller = DuplicateController(generator_config)

        # Add an old record
        old_time = datetime.now() - timedelta(hours=2)
        controller.duplicates.append((old_time, {"id": "old"}))

        # Add a new record
        controller.add_record({"id": "new"})

        # Cleanup should remove the old record
        controller._cleanup_old_duplicates()
        assert len(controller.duplicates) == 1
        assert controller.duplicates[0][1]["id"] == "new"

    def test_duplication_ratio(self, generator_config):
        """Test duplication ratio calculation"""
        controller = DuplicateController(generator_config)

        # Add some records
        for i in range(10):
            controller.add_record({"id": str(i)})

        # Force some duplicates
        controller.total_duplicates = 2

        results = controller.get_results()
        assert results["total_generated"] == 10
        assert results["total_duplicates"] == 2
        assert results["duplication_ratio"] == 0.2

    def test_max_size_enforcement(self, generator_config):
        """Test that the controller enforces max size"""
        controller = DuplicateController(generator_config)

        # Add more records than max_size
        for i in range(controller.max_size + 10):
            controller.add_record({"id": str(i)})

        assert len(controller.duplicates) == controller.max_size

    def test_get_duplicate(self, generator_config):
        """Test getting a duplicate record"""
        controller = DuplicateController(generator_config)

        # Add some records
        records = [{"id": str(i)} for i in range(5)]
        for record in records:
            controller.add_record(record)

        # Get a duplicate
        duplicate = controller._get_duplicate()
        assert duplicate in records

    def test_duplication_target_ratio(self, generator_config):
        """Test that duplication respects target ratio"""
        controller = DuplicateController(generator_config)

        # Add records and force some duplicates
        for i in range(100):
            controller.add_record({"id": str(i)})
            if i < 20:  # Force 20% duplication ratio
                controller.total_duplicates += 1

        # Should not return more duplicates once target ratio is reached
        assert controller._get_if_duplication() is None

    def test_duplicated_event_immutability(self, generator_config):
        """Test that duplicated events maintain their original state"""
        controller = DuplicateController(generator_config)

        # Create and add an original event
        original_event = {
            "id": "123",
            "name": "John Doe",
            "email": "john@example.com",
            "data": {"score": 100},
        }
        controller.add_record(original_event)

        # Modify the original event
        original_event["name"] = "Modified Name"
        original_event["data"]["score"] = 200

        # Get a duplicate of the event
        duplicate = controller._get_duplicate()

        # Verify the duplicate has the original values
        assert duplicate["name"] == "John Doe"
        assert duplicate["data"]["score"] == 100
        assert duplicate["id"] == "123"
        assert duplicate["email"] == "john@example.com"


class TestGenerator:
    def test_generate_simple(self):
        """Test the generate_simple method of Generator with duplication disabled."""
        mock_duplication = MagicMock()
        mock_duplication.enabled = False
        mock_duplication.ratio = 0.4
        mock_duplication.key_field = "id"
        mock_duplication.time_window = "7s"

        mock_event_options = MagicMock()
        mock_event_options.duplication = mock_duplication

        mock_config = MagicMock(spec=GeneratorConfig)
        mock_config.rps = 3000
        mock_config.bulk_size = 10
        mock_config.num_records = 30
        mock_config.event_options = mock_event_options

        mock_schema = MagicMock(spec=BaseSchema)
        mock_schema._generate_record.return_value = {"id": "simple"}

        generator = Generator(mock_config, mock_schema)

        # Assert that duplicate_controller is None when duplication is disabled
        assert generator.duplicate_controller is None

        result = list(generator.generate_simple())

        # Verify the number of records generated
        assert len(result) == 3  # 30 records in batches of 10
        for batch in result:
            assert len(batch) == 10
            for record in batch:
                assert record == {"id": "simple"}

    def test_generate_optimized(self):
        """Test the generate_optimized method of Generator with duplication enabled."""
        mock_duplication = MagicMock()
        mock_duplication.enabled = True
        mock_duplication.ratio = 0.4
        mock_duplication.key_field = "id"
        mock_duplication.time_window = "7s"

        mock_event_options = MagicMock()
        mock_event_options.duplication = mock_duplication

        mock_config = MagicMock(spec=GeneratorConfig)
        mock_config.rps = 3000
        mock_config.bulk_size = 10
        mock_config.num_records = 30
        mock_config.event_options = mock_event_options

        mock_schema = MagicMock(spec=BaseSchema)
        mock_schema._generate_record.return_value = {"id": "simple"}

        generator = Generator(mock_config, mock_schema)

        # Assert that duplicate_controller is not None when duplication is enabled
        assert generator.duplicate_controller is not None

        result = list(generator.generate_simple())

        # Verify the number of records generated
        assert len(result) == 3  # 30 records in batches of 10
        for batch in result:
            assert len(batch) == 10
            for record in batch:
                assert record == {"id": "simple"}



