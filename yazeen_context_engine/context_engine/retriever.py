"""
Context retriever module for Context Engine.
Enforces policy-permitted sources, performs semantic search, and caps context items.
"""

import logging
from typing import List, Dict, Any, Tuple
from .models import ContextItem, PolicyInput, TargetData
from .synthetic_data_loader import SyntheticDataLoader
from .vector_store import get_vector_store

logger = logging.getLogger(__name__)


class ContextRetriever:
    def __init__(self, data_loader: SyntheticDataLoader):
        self.data_loader = data_loader
        self.vector_store = get_vector_store()
        self._index_data()

    def _index_data(self):
        all_items = self.data_loader.get_all_items()
        docs = [
            {
                "id": item.id,
                "content": item.content,
                "source": item.source,
                "metadata": item.metadata,
            }
            for item in all_items
        ]
        self.vector_store.add_documents(docs)
        logger.info(f"Indexed {len(docs)} documents into Context Vector Store.")

    def build_query(self, action_type: str, target: Dict[str, Any]) -> str:
        recipient = str(target.get("recipient", "") or "")
        document_id = str(target.get("document_id", "") or "")
        amount = str(target.get("amount", "") or "")

        parts = [action_type]
        if recipient:
            parts.append(recipient)
        if document_id:
            parts.append(document_id)
        if amount and amount != "0":
            parts.append(f"${amount}")

        # Add domain semantic hints
        if action_type == "SEND_DOCUMENT":
            parts.append("request send document report attachment")
        elif action_type == "DELETE_FILE":
            parts.append("file project notes modified temporary")
        elif action_type == "CANCEL_APPT":
            parts.append("appointment consultation schedule doctor clinic")
        elif action_type == "TRANSFER":
            parts.append("money transfer dollars bank reimbursement")

        return " ".join(parts)

    def retrieve(
        self,
        action_type: str,
        target: Dict[str, Any],
        policy: PolicyInput,
    ) -> List[ContextItem]:
        query = self.build_query(action_type, target)
        logger.info(f"Retrieving context for query: '{query}' with allowed sources: {policy.allowedSources}")

        # Hard privacy check: Only allow sources explicitly permitted in policy
        results = self.vector_store.search(
            query=query,
            allowed_sources=policy.allowedSources,
            top_k=policy.maxContextItems,
            threshold=0.20,
        )

        retrieved_items = []
        for doc, score in results:
            item = ContextItem(
                id=doc["id"],
                source=doc["source"],
                timestamp=doc.get("metadata", {}).get("timestamp") or doc.get("metadata", {}).get("start_time") or doc.get("metadata", {}).get("last_modified"),
                content=doc["content"],
                metadata=doc.get("metadata", {}),
                similarity_score=round(score, 3),
            )
            retrieved_items.append(item)

        logger.info(f"Retrieved {len(retrieved_items)} context items.")
        return retrieved_items
