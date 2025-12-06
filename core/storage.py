"""Storage abstraction for multi-tenant data access in LienOS."""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import asyncio
import logging

# Try to import Google Cloud libraries, but allow local development without them
try:
    from google.cloud import firestore
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

logger = logging.getLogger(__name__)


class LocalStorageClient:
    """
    In-memory storage client for local development without Google Cloud.

    This is a drop-in replacement for FirestoreClient that stores data
    in memory dictionaries. Data is lost when the application restarts.
    """

    def __init__(self):
        """Initialize in-memory storage."""
        self.data: Dict[str, Dict[str, Dict[str, Any]]] = {}
        logger.info("LocalStorageClient initialized (in-memory storage)")

    def _get_collection(self, collection_name: str) -> Dict[str, Dict[str, Any]]:
        """Get or create a collection dictionary."""
        if collection_name not in self.data:
            self.data[collection_name] = {}
        return self.data[collection_name]

    async def create(
        self,
        collection_name: str,
        data: Dict[str, Any],
        tenant_id: str
    ) -> str:
        """
        Create a document in memory.

        Args:
            collection_name: Name of the collection
            data: Document data dictionary
            tenant_id: Tenant identifier

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

        # Store in memory
        collection = self._get_collection(collection_name)
        collection[doc_id] = data.copy()

        return doc_id

    async def get(
        self,
        collection_name: str,
        doc_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID from memory.

        Args:
            collection_name: Name of the collection
            doc_id: Document ID
            tenant_id: Tenant identifier for security verification

        Returns:
            Document data as dictionary, or None if not found or unauthorized
        """
        collection = self._get_collection(collection_name)
        doc_data = collection.get(doc_id)

        if doc_data is None:
            return None

        # Security check: Verify tenant_id matches
        if doc_data.get("tenant_id") != tenant_id:
            return None

        return doc_data.copy()

    async def update(
        self,
        collection_name: str,
        doc_id: str,
        updates: Dict[str, Any],
        tenant_id: str
    ) -> bool:
        """
        Update a document in memory.

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

        # Update in memory
        collection = self._get_collection(collection_name)
        collection[doc_id].update(updates)

        return True

    async def delete(
        self,
        collection_name: str,
        doc_id: str,
        tenant_id: str
    ) -> bool:
        """
        Delete a document from memory.

        Args:
            collection_name: Name of the collection
            doc_id: Document ID
            tenant_id: Tenant identifier for access verification

        Returns:
            True if delete successful, False if unauthorized or not found
        """
        # Security: First verify the tenant has access to this document
        existing_doc = await self.get(collection_name, doc_id, tenant_id)
        if existing_doc is None:
            return False

        # Delete from memory
        collection = self._get_collection(collection_name)
        del collection[doc_id]

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
        Query documents from memory.

        Args:
            collection_name: Name of the collection
            tenant_id: Tenant identifier (required for security)
            filters: Optional list of (field, operator, value) tuples
            order_by: Optional field name to order by
            limit: Optional maximum number of documents to return

        Returns:
            List of document dictionaries
        """
        collection = self._get_collection(collection_name)

        # Filter by tenant_id first (security)
        results = [
            doc.copy() for doc in collection.values()
            if doc.get("tenant_id") == tenant_id
        ]

        # Apply additional filters
        if filters:
            for field, operator, value in filters:
                if operator == "==":
                    results = [d for d in results if d.get(field) == value]
                elif operator == "!=":
                    results = [d for d in results if d.get(field) != value]
                elif operator == "<":
                    results = [d for d in results if d.get(field) is not None and d.get(field) < value]
                elif operator == "<=":
                    results = [d for d in results if d.get(field) is not None and d.get(field) <= value]
                elif operator == ">":
                    results = [d for d in results if d.get(field) is not None and d.get(field) > value]
                elif operator == ">=":
                    results = [d for d in results if d.get(field) is not None and d.get(field) >= value]

        # Apply ordering
        if order_by:
            reverse = False
            if order_by.startswith("-"):
                reverse = True
                order_by = order_by[1:]
            results.sort(key=lambda x: x.get(order_by, ""), reverse=reverse)

        # Apply limit
        if limit:
            results = results[:limit]

        return results


class FirestoreClient:
    """Firestore client with multi-tenant security enforcement."""

    def __init__(self, project_id: str = "local-dev"):
        """
        Initialize storage client.

        If project_id is "local-dev" or Google Cloud is not available,
        uses LocalStorageClient for in-memory storage.
        Otherwise, uses actual Firestore.

        Args:
            project_id: Google Cloud project ID or "local-dev" for local storage
        """
        self.project_id = project_id
        self._use_local = project_id == "local-dev" or not GOOGLE_CLOUD_AVAILABLE

        if self._use_local:
            self._local_client = LocalStorageClient()
            if not GOOGLE_CLOUD_AVAILABLE:
                logger.warning("Google Cloud libraries not installed. Using local storage.")
            else:
                logger.info("Using local in-memory storage (project_id='local-dev')")
        else:
            self.db = firestore.Client(project=project_id)
            logger.info(f"Connected to Firestore project: {project_id}")

        self.collections = {
            "liens": "liens",
            "payments": "payments",
            "interest_calculations": "interest_calculations",
            "deadlines": "deadlines",
            "notifications": "notifications",
            "portfolios": "portfolios",
            "documents": "documents",
            "email_queue": "email_queue",
            "sms_queue": "sms_queue"
        }

    def _sanitize_data(self, data: Any) -> Any:
        """Recursively convert Decimal to float for Firestore compatibility."""
        if isinstance(data, Decimal):
            return float(data)
        if isinstance(data, dict):
            return {k: self._sanitize_data(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._sanitize_data(i) for i in data]
        return data

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
        if self._use_local:
            return await self._local_client.create(collection_name, data, tenant_id)

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
        data = self._sanitize_data(data)
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
        if self._use_local:
            return await self._local_client.get(collection_name, doc_id, tenant_id)

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
        stored_tenant = doc_data.get("tenant_id")
        if stored_tenant != tenant_id:
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
        if self._use_local:
            return await self._local_client.update(collection_name, doc_id, updates, tenant_id)

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
        updates = self._sanitize_data(updates)
        await loop.run_in_executor(None, doc_ref.update, updates)

        return True

    async def delete(
        self,
        collection_name: str,
        doc_id: str,
        tenant_id: str
    ) -> bool:
        """
        Delete a document.

        First verify tenant has access.
        Return True if successful, False if unauthorized/not found.

        Args:
            collection_name: Name of the collection
            doc_id: Document ID
            tenant_id: Tenant identifier for access verification

        Returns:
            True if delete successful, False if unauthorized or not found
        """
        if self._use_local:
            return await self._local_client.delete(collection_name, doc_id, tenant_id)

        # Security: First verify the tenant has access to this document
        existing_doc = await self.get(collection_name, doc_id, tenant_id)
        if existing_doc is None:
            return False

        # Get collection reference
        collection_ref = self.db.collection(self.collections.get(collection_name, collection_name))

        # Delete document (run in thread pool since Firestore client is synchronous)
        loop = asyncio.get_event_loop()
        doc_ref = collection_ref.document(doc_id)
        await loop.run_in_executor(None, doc_ref.delete)

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
        if self._use_local:
            return await self._local_client.query(collection_name, tenant_id, filters, order_by, limit)

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
