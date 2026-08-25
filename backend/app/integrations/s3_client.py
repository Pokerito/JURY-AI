import os
from pathlib import Path
import boto3
from app.config import get_settings

class StorageClient:
    """Singleton client for handling file storage operations (S3 or Local Fallback)."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StorageClient, cls).__new__(cls)
            cls._instance._init()
        return cls._instance
        
    def _init(self):
        self.settings = get_settings()
        if not self.settings.USE_LOCAL_STORAGE:
            self.s3_client = boto3.client('s3', region_name=self.settings.S3_REGION)
            
    def upload_file(self, org_id: str, doc_id: str, filename: str, content: bytes) -> str:
        """Upload a file to storage and return its key or path."""
        key = f"{org_id}/{doc_id}/{filename}"
        
        if self.settings.USE_LOCAL_STORAGE:
            file_path = Path(self.settings.LOCAL_STORAGE_DIR) / key
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(content)
            return str(file_path)
        else:
            self.s3_client.put_object(
                Bucket=self.settings.S3_BUCKET_NAME,
                Key=key,
                Body=content
            )
            return key

    def download_file(self, key: str) -> bytes:
        """Download a file's content by key or path."""
        if self.settings.USE_LOCAL_STORAGE:
            file_path = Path(key)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {key}")
            return file_path.read_bytes()
        else:
            response = self.s3_client.get_object(
                Bucket=self.settings.S3_BUCKET_NAME,
                Key=key
            )
            return response['Body'].read()
            
    def delete_file(self, key: str):
        """Delete a file from storage."""
        if self.settings.USE_LOCAL_STORAGE:
            file_path = Path(key)
            if file_path.exists():
                file_path.unlink()
        else:
            self.s3_client.delete_object(
                Bucket=self.settings.S3_BUCKET_NAME,
                Key=key
            )

storage_client = StorageClient()
