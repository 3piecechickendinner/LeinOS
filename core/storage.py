"""Firestore abstraction for multi-tenant data access in LienOS."""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio

from google.cloud import firestore


class FirestoreClient:
    """Firestore client with multi-tenant security enforcement."""

    def __init__(self, project_id: str):
        """
        Initialize Firestore client.

        Args:
            project_id: Google Cloud project ID
        """
        self.db = firestore.Client(project=project_id)
        self.collections = {
            "liens": "liens",
            "payments": "payments",
            "interest_calculations": "interest_calculations"
        }

    async def create(
        self,
        collection_name: str,
        data: Dict[str, Any],
        tenant_id: str
    ) -> str:
        """
        Create a document. Ensures tenant_id is in data for security.

        Generates uuid4 if no 'id' field in data.
        Adds created_at and updated_at timestamps.
        Returns the document ID.

        Args:
            collection_name: Name of the collection
            data: Document data dictionary
            tenant_id: Tenant identifier (will be enforced in data)

        Returns:
            Document ID (string)
        """
        # Security: Ensure tenant_id is always set in the document
        data["tenant_id"] = tenant_id

        # Generate document ID if not provided
        doc_id = data.get("id") or str(uuid.uuid4())
        if "id" not in data:
            data["id"] = doc_id

        # Add timestamps
        now = datetime.utcnow()
        data["created_at"] = now
        data["updated_at"] = now

        # Get collection reference
        collection_ref = self.db.collection(self.collections.get(collection_name, collection_name))

        # Create document (run in thread pool since Firestore client is synchronous)
        loop = asyncio.get_event_loop()
        doc_ref = collection_ref.document(doc_id)
        await loop.run_in_executor(None, doc_ref.set, data)

        return doc_id

    async def get(
        self,
        collection_name: str,
        doc_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.

        CRITICAL: Must verify document.tenant_id matches the provided tenant_id.
        Return None if not found OR if tenant_id doesn't match (security check).

        Args:
            collection_name: Name of the collection
            doc_id: Document ID
            tenant_id: Tenant identifier for security verification

        Returns:
            Document data as dictionary, or None if not found or unauthorized
        """
        # Get collection reference
        collection_ref = self.db.collection(self.collections.get(collection_name, collection_name))

        # Fetch document (run in thread pool since Firestore client is synchronous)
        loop = asyncio.get_event_loop()
        doc_ref = collection_ref.document(doc_id)
        doc = await loop.run_in_executor(None, doc_ref.get)

        # Check if document exists
        if not doc.exists:
            return None

        # Security check: Verify tenant_id matches
        # This prevents tenants from accessing other tenants' data
        doc_data = doc.to_dict()
        if doc_data.get("tenant_id") != tenant_id:
            return None

        return doc_data

    async def update(
        self,
        collection_name: str,
        doc_id: str,
        updates: Dict[str, Any],
        tenant_id: str
    ) -> bool:
        """
        Update a document.

        First call get() to verify tenant has access.
        Automatically add updated_at timestamp.
        Return True if successful, False if unauthorized/not found.

        Args:
            collection_name: Name of the collection
            doc_id: Document ID
            updates: Dictionary of fields to update
            tenant_id: Tenant identifier for access verification

        Returns:
            True if update successful, False if unauthorized or not found
        """
        # Security: First verify the tenant has access to this document
        existing_doc = await self.get(collection_name, doc_id, tenant_id)
        if existing_doc is None:
            return False

        # Add updated_at timestamp
        updates["updated_at"] = datetime.utcnow()

        # Ensure tenant_id cannot be changed (security)
        if "tenant_id" in updates:
            del updates["tenant_id"]

        # Get collection reference
        collection_ref = self.db.collection(self.collections.get(collection_name, collection_name))

        # Update document (run in thread pool since Firestore client is synchronous)
        loop = asyncio.get_event_loop()
        doc_ref = collection_ref.document(doc_id)
        await loop.run_in_executor(None, doc_ref.update, updates)

        return True

    async def query(
        self,
        collection_name: str,
        tenant_id: str,
        filters: Optional[List[tuple]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query documents.

        ALWAYS start with .where("tenant_id", "==", tenant_id) for security.
        filters is list of (field, operator, value) tuples.
        Return list of document dicts.

        Args:
            collection_name: Name of the collection
            tenant_id: Tenant identifier (required for security)
            filters: Optional list of (field, operator, value) tuples
            order_by: Optional field name to order by
            limit: Optional maximum number of documents to return

        Returns:
            List of document dictionaries
        """
        # Get collection reference
        collection_ref = self.db.collection(self.collections.get(collection_name, collection_name))

        # Security: ALWAYS filter by tenant_id first
        # This ensures tenants can only query their own data
        query = collection_ref.where("tenant_id", "==", tenant_id)

        # Apply additional filters
        if filters:
            for field, operator, value in filters:
                query = query.where(field, operator, value)

        # Apply ordering
        if order_by:
            query = query.order_by(order_by)

        # Apply limit
        if limit:
            query = query.limit(limit)

        # Execute query (run in thread pool since Firestore client is synchronous)
        loop = asyncio.get_event_loop()
        docs = await loop.run_in_executor(None, query.get)

        # Convert to list of dictionaries
        return [doc.to_dict() for doc in docs]

