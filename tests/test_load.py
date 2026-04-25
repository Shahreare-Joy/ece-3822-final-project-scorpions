"""Large-load dataset tests.

Unit tests for the synthetic dataset loader.
Tests verify required files exist, minimum record counts are met,
and sample records contain required fields.
"""

from pathlib import Path
import unittest

from platform_server.data_ingest import DATASET_FILES, DataIngestService, REQUIRED_FIELDS


class TestLoad(unittest.TestCase):
    def setUp(self) -> None:
        """Create a dataset loader pointed at the committed synthetic dataset."""
        self.dataset_root = Path("data/synthetic_dataset")
        self.service = DataIngestService(self.dataset_root)

    def test_dataset_folder_and_required_files_exist(self) -> None:
        """Verify the dataset folder and required JSON files exist."""
        self.assertTrue(self.dataset_root.exists())
        for file_name in DATASET_FILES.values():
            self.assertTrue((self.dataset_root / file_name).exists(), file_name)

    def test_dataset_meets_minimum_counts(self) -> None:
        """Verify committed dataset sizes meet project requirements."""
        loaded = self.service.load_all()
        self.assertGreaterEqual(len(loaded["players"]), 10_000)
        self.assertGreaterEqual(len(loaded["sessions"]), 100_000)
        self.assertGreaterEqual(len(loaded["chat_messages"]), 50_000)
        self.assertGreaterEqual(len(loaded["game_catalog"]), 100)

    def test_sample_records_include_required_fields(self) -> None:
        """Verify sample records include all required fields."""
        loaded = self.service.load_all()
        for dataset_name, rows in loaded.items():
            self.assertTrue(rows, dataset_name)
            sample = rows[0]
            self.assertTrue(REQUIRED_FIELDS[dataset_name].issubset(sample.keys()))

    def test_ids_are_not_empty_in_sample_records(self) -> None:
        """Verify ID fields are present and non-empty in sample records."""
        loaded = self.service.load_all()
        id_fields = {
            "players": "player_id",
            "sessions": "session_id",
            "chat_messages": "message_id",
            "game_catalog": "game_id",
        }
        for dataset_name, id_field in id_fields.items():
            sample = loaded[dataset_name][0]
            self.assertTrue(sample[id_field])

    def test_validation_passes_for_committed_dataset(self) -> None:
        """Verify the committed dataset passes loader validation."""
        self.assertEqual(self.service.validate_all(), [])
