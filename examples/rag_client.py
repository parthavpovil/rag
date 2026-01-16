"""
RAG Client - Drop this into your backend codebase
"""
import requests
from typing import Optional, Dict, List

class RAGClient:
    """Client for communicating with RAG service"""
    
    def __init__(self, base_url: str = "http://rag-service:8000"):
        """
        Initialize RAG client.
        
        Args:
            base_url: URL of RAG service
                - In Docker: "http://rag-service:8000"
                - Local testing: "http://localhost:8000"
        """
        self.base_url = base_url
        self.timeout = 30
    
    def process_s3_document(
        self, 
        tenant_id: str, 
        s3_bucket: str, 
        s3_key: str, 
        filename: str
    ) -> Dict:
        """Process a document from S3"""
        try:
            response = requests.post(
                f"{self.base_url}/process-s3",
                data={
                    "tenant_id": tenant_id,
                    "s3_bucket": s3_bucket,
                    "s3_key": s3_key,
                    "filename": filename
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def query(self, tenant_id: str, query: str, limit: int = 5) -> Dict:
        """Query the RAG system"""
        try:
            response = requests.post(
                f"{self.base_url}/query",
                json={
                    "tenant_id": tenant_id,
                    "query": query,
                    "limit": limit
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def list_documents(self, tenant_id: str) -> Dict:
        """List all documents for a tenant"""
        try:
            response = requests.get(
                f"{self.base_url}/files/{tenant_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def delete_document(self, tenant_id: str, filename: str) -> Dict:
        """Delete a specific document"""
        try:
            response = requests.delete(
                f"{self.base_url}/documents/{tenant_id}/{filename}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def delete_all_documents(self, tenant_id: str) -> Dict:
        """Delete all documents for a tenant"""
        try:
            response = requests.delete(
                f"{self.base_url}/documents/{tenant_id}/all",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def health_check(self) -> bool:
        """Check if RAG service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
