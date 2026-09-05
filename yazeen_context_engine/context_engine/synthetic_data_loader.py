"""
Synthetic data loader and validator for the Context Engine.
Loads, normalizes, and indexes messages, calendar events, files, and contacts.
"""

import json
import os
import logging
from typing import Dict, List, Optional
from .models import ContextItem

logger = logging.getLogger(__name__)

DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data")
)


class SyntheticDataLoader:
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self.items_by_source: Dict[str, List[ContextItem]] = {
            "messages": [],
            "calendar": [],
            "files": [],
            "contacts": [],
        }
        self.total_counts: Dict[str, int] = {}
        self._load_all()

    def _load_all(self):
        self._load_messages()
        self._load_calendar()
        self._load_files()
        self._load_contacts()
        for source, items in self.items_by_source.items():
            self.total_counts[source] = len(items)
        logger.info(f"Loaded synthetic data vault: {self.total_counts}")

    def _load_messages(self):
        filepath = os.path.join(self.data_dir, "messages.json")
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            search_text = (
                f"{item.get('sender_name', '')} {item.get('sender', '')} "
                f"{item.get('subject', '')} {item.get('body', '')} "
                f"{item.get('document_id', '')} {item.get('date_str', '')}"
            )
            self.items_by_source["messages"].append(
                ContextItem(
                    id=item["id"],
                    source="messages",
                    timestamp=item.get("timestamp"),
                    content=search_text,
                    metadata=item,
                )
            )

    def _load_calendar(self):
        filepath = os.path.join(self.data_dir, "calendar.json")
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            search_text = (
                f"{item.get('title', '')} {item.get('participant', '')} "
                f"{item.get('participant_email', '')} {item.get('location', '')} "
                f"{item.get('description', '')} {item.get('date_str', '')} {item.get('time_str', '')}"
            )
            self.items_by_source["calendar"].append(
                ContextItem(
                    id=item["id"],
                    source="calendar",
                    timestamp=item.get("start_time"),
                    content=search_text,
                    metadata=item,
                )
            )

    def _load_files(self):
        filepath = os.path.join(self.data_dir, "files.json")
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            tags_str = " ".join(item.get("tags", []))
            search_text = (
                f"{item.get('filename', '')} {item.get('project', '')} "
                f"{item.get('summary', '')} {tags_str} {item.get('last_modified_str', '')}"
            )
            self.items_by_source["files"].append(
                ContextItem(
                    id=item["id"],
                    source="files",
                    timestamp=item.get("last_modified"),
                    content=search_text,
                    metadata=item,
                )
            )

    def _load_contacts(self):
        filepath = os.path.join(self.data_dir, "contacts.json")
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            search_text = (
                f"{item.get('name', '')} {item.get('email', '')} "
                f"{item.get('relationship', '')} {item.get('organization', '')} "
                f"{item.get('notes', '')}"
            )
            self.items_by_source["contacts"].append(
                ContextItem(
                    id=item["id"],
                    source="contacts",
                    timestamp=None,
                    content=search_text,
                    metadata=item,
                )
            )

    def get_all_items(self, allowed_sources: Optional[List[str]] = None) -> List[ContextItem]:
        sources = allowed_sources if allowed_sources is not None else list(self.items_by_source.keys())
        result = []
        for src in sources:
            if src in self.items_by_source:
                result.extend(self.items_by_source[src])
        return result

    def get_source_counts(self) -> Dict[str, int]:
        return dict(self.total_counts)

    def get_item_by_id(self, source: str, item_id: str) -> Optional[ContextItem]:
        for item in self.items_by_source.get(source, []):
            if item.id == item_id:
                return item
        return None
