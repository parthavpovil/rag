import os
import boto3
import requests
import time
import sys

# Configuration
BASE_URL = "http://localhost:8005"
TENANT_ID = "test_tenant_s3"
BUCKET = "chatbot-amzs3"
FILENAME = "s3_test_doc.txt"
S3_KEY = f"{TENANT_ID}/{FILENAME}"
CONTENT = """
This is a test document uploaded to S3 for RAG processing.
It confirms that the RAG service can successfully download files from AWS S3.
The integration uses boto3 and passes the S3 path to the knowledge service.
Plutonium is element 94.
"""

def setup_env():
    # Load env vars for local testing if .env exists
    env_path = '/home/parthav/work/rag/.env'
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def upload_to_s3():
    print(f"⬆️  Uploading test file to S3: s3://{BUCKET}/{S3_KEY}")
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
        
        s3.put_object(
            Bucket=BUCKET,
            Key=S3_KEY,
            Body=CONTENT.encode('utf-8')
        )
        print("✅ Upload complete")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def call_rag_process():
    print(f"\n🔄 Requesting RAG service to process s3://{BUCKET}/{S3_KEY}")
    url = f"{BASE_URL}/process-s3"
    
    data = {
        "tenant_id": TENANT_ID,
        "s3_bucket": BUCKET,
        "s3_key": S3_KEY,
        "filename": FILENAME
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print(f"✅ RAG processing successful!")
                print(f"   Chunks created: {result.get('chunks_created')}")
                return True
            else:
                print(f"❌ RAG processing error: {result}")
        else:
            print(f"❌ API call failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    return False

def verify_retrieval():
    print("\n🔍 Verifying retrieval...")
    url = f"{BASE_URL}/query"
    data = {
        "tenant_id": TENANT_ID,
        "query": "What element is plutonium?"
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        print(f"Answer: {result.get('answer')}")
        
        # Check if answer contains expected info
        if "94" in result.get("answer", ""):
            print("✅ Retrieval successful and answer correct!")
            return True
        else:
            print("⚠️ Answer might be incorrect (check manually)")
    except Exception as e:
        print(f"❌ Retrieval error: {e}")
    return False

def cleanup():
    print(f"\n🗑️ Cleaning up S3 and Database...")
    # Delete from RAG
    print("   Deleting from RAG...")
    requests.delete(f"{BASE_URL}/documents/{TENANT_ID}/{FILENAME}")
    
    # Delete from S3
    print("   Deleting from S3...")
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
        s3.delete_object(Bucket=BUCKET, Key=S3_KEY)
        print("✅ Cleanup complete")
    except Exception as e:
        print(f"⚠️ S3 cleanup failed: {e}")

if __name__ == "__main__":
    print("="*50)
    print("S3 INTEGRATION TEST")
    print("="*50)
    
    setup_env()
    
    if not upload_to_s3():
        sys.exit(1)
        
    time.sleep(2) # Give S3 a moment
    
    if call_rag_process():
        time.sleep(2)
        verify_retrieval()
        
    cleanup()
    print("\n🎉 Test Finished")
