from minio import Minio
from minio.error import S3Error
from app.core.config import settings
from typing import Optional, Dict, Any
from datetime import timedelta
import uuid

class MinIOClient:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self._ensure_buckets_exist()
    
    def _ensure_buckets_exist(self):
        """Create buckets if they don't exist"""
        buckets = [settings.MINIO_BUCKET_UPLOADS, settings.MINIO_BUCKET_EXPORTS]
        for bucket in buckets:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
    
    def generate_presigned_upload_url(
        self, 
        bucket: str, 
        object_key: Optional[str] = None,
        expires: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """Generate presigned URL for file upload"""
        if object_key is None:
            object_key = f"uploads/{uuid.uuid4()}"
        
        try:
            url = self.client.presigned_put_object(
                bucket_name=bucket,
                object_name=object_key,
                expires=expires
            )
            return {
                "upload_url": url,
                "object_key": object_key,
                "bucket": bucket
            }
        except S3Error as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def generate_presigned_download_url(
        self,
        bucket: str,
        object_key: str,
        expires: timedelta = timedelta(hours=1)
    ) -> str:
        """Generate presigned URL for file download"""
        try:
            url = self.client.presigned_get_object(
                bucket_name=bucket,
                object_name=object_key,
                expires=expires
            )
            return url
        except S3Error as e:
            raise Exception(f"Failed to generate download URL: {str(e)}")
    
    def upload_file(self, bucket: str, object_key: str, file_path: str) -> bool:
        """Upload file directly to MinIO"""
        try:
            self.client.fput_object(bucket, object_key, file_path)
            return True
        except S3Error as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def delete_object(self, bucket: str, object_key: str) -> bool:
        """Delete object from MinIO"""
        try:
            self.client.remove_object(bucket, object_key)
            return True
        except S3Error as e:
            raise Exception(f"Failed to delete object: {str(e)}")
    
    def get_object_info(self, bucket: str, object_key: str) -> Dict[str, Any]:
        """Get object metadata"""
        try:
            stat = self.client.stat_object(bucket, object_key)
            return {
                "size": stat.size,
                "etag": stat.etag,
                "last_modified": stat.last_modified,
                "content_type": stat.content_type
            }
        except S3Error as e:
            raise Exception(f"Failed to get object info: {str(e)}")

# Global MinIO client instance
minio_client = MinIOClient()