"""
Tests for Synthetic Data Vault.
Verifies data loading, schemas, completeness, unique IDs, and ethical labeling.
"""

import os
import json
import pytest
from context_engine.synthetic_data_loader import SyntheticDataLoader

DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data")
)


def test_data_files_exist():
    required_files = ["messages.json", "calendar.json", "files.json", "contacts.json", "README.md"]
    for f in required_files:
        path = os.path.join(DATA_DIR, f)
        assert os.path.exists(path), f"Missing data file: {f}"


def test_messages_dataset_integrity():
    with open(os.path.join(DATA_DIR, "messages.json"), "r", encoding="utf-8") as f:
        messages = json.load(f)

    assert len(messages) >= 50, f"Expected at least 50 messages, got {len(messages)}"
    ids = set()
    for m in messages:
        assert "id" in m and m["id"] not in ids, f"Duplicate or missing ID: {m.get('id')}"
        ids.add(m["id"])
        assert "sender" in m
        assert "subject" in m
        assert "body" in m
        assert m.get("label") == "SYNTHETIC_DATA_FOR_HACKATHON_DEMO"


def test_calendar_dataset_integrity():
    with open(os.path.join(DATA_DIR, "calendar.json"), "r", encoding="utf-8") as f:
        events = json.load(f)

    assert len(events) >= 15, f"Expected at least 15 events, got {len(events)}"
    ids = set()
    for e in events:
        assert "id" in e and e["id"] not in ids
        ids.add(e["id"])
        assert "title" in e
        assert "participant" in e
        assert e.get("label") == "SYNTHETIC_DATA_FOR_HACKATHON_DEMO"


def test_files_dataset_integrity():
    with open(os.path.join(DATA_DIR, "files.json"), "r", encoding="utf-8") as f:
        files = json.load(f)

    assert len(files) >= 20, f"Expected at least 20 files, got {len(files)}"
    ids = set()
    for file_item in files:
        assert "id" in file_item and file_item["id"] not in ids
        ids.add(file_item["id"])
        assert "filename" in file_item
        assert "project" in file_item
        assert file_item.get("label") == "SYNTHETIC_DATA_FOR_HACKATHON_DEMO"


def test_contacts_dataset_integrity():
    with open(os.path.join(DATA_DIR, "contacts.json"), "r", encoding="utf-8") as f:
        contacts = json.load(f)

    assert len(contacts) >= 15, f"Expected at least 15 contacts, got {len(contacts)}"
    ids = set()
    for c in contacts:
        assert "id" in c and c["id"] not in ids
        ids.add(c["id"])
        assert "name" in c
        assert "email" in c
        assert "trust_level" in c
        assert c.get("label") == "SYNTHETIC_DATA_FOR_HACKATHON_DEMO"


def test_loader_caches_and_aggregates():
    loader = SyntheticDataLoader(data_dir=DATA_DIR)
    counts = loader.get_source_counts()
    total = sum(counts.values())
    assert total >= 100
    all_items = loader.get_all_items()
    assert len(all_items) == total
