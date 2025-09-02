from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile, HTTPException
from urllib.parse import urlparse
import io
from ..core.config import settings


class MinIOService:
    def __init__(self):
        # Parse MinIO endpoint
        parsed_url = urlparse(settings.MINIO_ENDPOINT)
        self.client = Minio(
            parsed_url.netloc,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=parsed_url.scheme == 'https'
        )
        
        # Ensure buckets exist
        self._ensure_buckets()
    
    def _ensure_buckets(self):
        """Ensure required buckets exist."""
        buckets = [
            settings.MINIO_BUCKET_UPLOADS,
            settings.MINIO_BUCKET_EXPORTS
        ]
        
        for bucket_name in buckets:
            try:
                if not self.client.bucket_exists(bucket_name):
                    self.client.make_bucket(bucket_name)
            except S3Error as e:
                print(f"Error creating bucket {bucket_name}: {e}")
    
    async def upload_file(self, file: UploadFile, object_name: str, bucket_name: str = None) -> str:
        """Upload file to MinIO and return the file path."""
        if bucket_name is None:
            bucket_name = settings.MINIO_BUCKET_UPLOADS
        
        try:
            # Read file content
            file_content = await file.read()
            file_like = io.BytesIO(file_content)
            
            # Upload file
            self.client.put_object(
                bucket_name,
                object_name,
                file_like,
                length=len(file_content),
                content_type=file.content_type
            )
            
            return f"{bucket_name}/{object_name}"
            
        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {e}")
    
    async def delete_file(self, object_name: str, bucket_name: str = None):
        """Delete file from MinIO."""
        if bucket_name is None:
            # Extract bucket from object_name if it includes bucket
            if '/' in object_name:
                parts = object_name.split('/', 1)
                bucket_name = parts[0]
                object_name = parts[1]
            else:
                bucket_name = settings.MINIO_BUCKET_UPLOADS
        
        try:
            self.client.remove_object(bucket_name, object_name)
        except S3Error as e:
            print(f"Error deleting file {object_name}: {e}")
    
    def get_presigned_download_url(self, object_name: str, bucket_name: str = None, expires_in: int = 3600) -> str:
        """Generate presigned URL for downloading file."""
        if bucket_name is None:
            bucket_name = settings.MINIO_BUCKET_UPLOADS
        
        try:
            url = self.client.presigned_get_object(
                bucket_name,
                object_name,
                expires=expires_in
            )
            return url
        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate download URL: {e}")
    
    def get_presigned_upload_url(self, object_name: str, bucket_name: str = None, expires_in: int = 3600) -> str:
        """Generate presigned URL for uploading file."""
        if bucket_name is None:
            bucket_name = settings.MINIO_BUCKET_UPLOADS
        
        try:
            url = self.client.presigned_put_object(
                bucket_name,
                object_name,
                expires=expires_in
            )
            return url
        except S3Error as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate upload URL: {e}")
    
    async def get_file_content(self, object_name: str, bucket_name: str = None) -> bytes:
        """Get file content from MinIO."""
        if bucket_name is None:
            # Extract bucket from object_name if it includes bucket
            if '/' in object_name:
                parts = object_name.split('/', 1)
                bucket_name = parts[0]
                object_name = parts[1]
            else:
                bucket_name = settings.MINIO_BUCKET_UPLOADS
        
        try:
            response = self.client.get_object(bucket_name, object_name)
            return response.read()
        except S3Error as e:
            raise HTTPException(status_code=404, detail=f"File not found: {e}")
        finally:
            response.close()
            response.release_conn()