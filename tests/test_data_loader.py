import json
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend import data_loader


def test_load_data_uses_mock_when_files_missing(tmp_path, monkeypatch):
    """When no data files are present, the loader should generate mock entries for each theme."""
    monkeypatch.setattr(data_loader, "DATA_DIR", tmp_path)

    result = data_loader.load_data()

    assert set(result) == {"tabac", "alcool", "drogue"}
    for theme, entries in result.items():
        assert len(entries) == 2
        assert all("question" in entry and "answer" in entry for entry in entries)


def test_load_data_reads_existing_files(tmp_path, monkeypatch):
    """Existing JSON files should be loaded as-is without being replaced by mock data."""
    real_entries = [
        {"question": "Quelle est la prévalence du tabagisme ?", "answer": "42%"},
        {"question": "Comment arrêter de fumer ?", "answer": "Consultez un professionnel."},
    ]
    tabac_file = tmp_path / "tabac.json"
    tabac_file.write_text(json.dumps(real_entries, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(data_loader, "DATA_DIR", tmp_path)

    result = data_loader.load_data()

    assert result["tabac"] == real_entries
    assert len(result["alcool"]) == 2
    assert len(result["drogue"]) == 2


def test_load_training_data_returns_mock_when_missing(tmp_path, monkeypatch, capsys):
    """If the training data file is missing, mocked examples should be returned."""
    monkeypatch.setattr(data_loader, "DATA_DIR", tmp_path)

    training_data = data_loader.load_training_data()

    assert len(training_data) == 2
    assert all("prompt" in item and "response" in item for item in training_data)

    captured = capsys.readouterr()
    assert "Mock training data" in captured.out


def test_load_training_data_reads_file(tmp_path, monkeypatch):
    """When the training data file exists, its content must be returned without alteration."""
    payload = [
        {"prompt": "Question A", "response": "Réponse A"},
        {"prompt": "Question B", "response": "Réponse B"},
    ]
    training_file = tmp_path / "training_data.json"
    training_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(data_loader, "DATA_DIR", tmp_path)

    assert data_loader.load_training_data() == payload