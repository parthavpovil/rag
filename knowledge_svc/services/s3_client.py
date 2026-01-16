"""
S3 client for downloading documents from AWS S3.
"""
import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

_s3_client = None

def get_s3_client():
    """Get or create S3 client singleton."""
    global _s3_client
    if _s3_client is None:
        if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
            print("Warning: AWS credentials not set. S3 operations will fail.")
            print("Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
        
        _s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
    return _s3_client

def download_from_s3(bucket: str, key: str) -> Optional[bytes]:
    """
    Download file from S3.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key (path)
    
    Returns:
        File bytes if successful, None if failed
    
    Raises:
        ClientError: If S3 operation fails
    """
    client = get_s3_client()
    
    try:
        print(f"Downloading from S3: s3://{bucket}/{key}")
        response = client.get_object(Bucket=bucket, Key=key)
        file_bytes = response['Body'].read()
        print(f"✓ Downloaded {len(file_bytes)} bytes from S3")
        return file_bytes
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchKey':
            print(f"✗ File not found in S3: {key}")
        elif error_code == 'NoSuchBucket':
            print(f"✗ Bucket not found: {bucket}")
        else:
            print(f"✗ S3 error: {e}")
        raise

def check_file_exists(bucket: str, key: str) -> bool:
    """
    Check if file exists in S3.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key (path)
    
    Returns:
        True if file exists, False otherwise
    """
    client = get_s3_client()
    
    try:
        client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise

def list_tenant_files(bucket: str, tenant_id: str) -> list[dict]:
    """
    List all files for a tenant in S3.
    
    Args:
        bucket: S3 bucket name
        tenant_id: Tenant ID (used as prefix)
    
    Returns:
        List of file metadata dicts
    """
    client = get_s3_client()
    
    try:
        prefix = f"{tenant_id}/"
        response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        
        if 'Contents' not in response:
            return []
        
        files = []
        for obj in response['Contents']:
            # Skip the folder itself
            if obj['Key'] == prefix:
                continue
            
            files.append({
                'key': obj['Key'],
                'filename': obj['Key'].replace(prefix, ''),
                'size': obj['Size'],
                'last_modified': obj['LastModified'].isoformat()
            })
        
        return files
    except ClientError as e:
        print(f"Error listing S3 files: {e}")
        return []
