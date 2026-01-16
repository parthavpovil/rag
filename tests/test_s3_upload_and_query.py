#!/usr/bin/env python3
"""
Upload a test document to S3 and verify RAG processing with queries.
"""
import os
import boto3
import requests
import time

# Load environment variables
env_path = '/home/parthav/work/rag/.env'
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Configuration
TENANT_ID = "demo_tenant"
BUCKET = "chatbot-amzs3"
FILENAME = "coffee_guide.txt"
S3_KEY = f"rag/{FILENAME}"  # Upload to 'rag' folder in S3
LOCAL_FILE = "/home/parthav/work/rag/test_coffee_guide.txt"

print("="*60)
print("S3 + RAG INTEGRATION TEST - Coffee Guide")
print("="*60)

# Step 1: Upload to S3
print(f"\n📤 Step 1: Uploading to S3: s3://{BUCKET}/{S3_KEY}")
try:
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )
    
    with open(LOCAL_FILE, 'rb') as f:
        s3.put_object(Bucket=BUCKET, Key=S3_KEY, Body=f)
    print("✅ Upload successful!")
except Exception as e:
    print(f"❌ Upload failed: {e}")
    exit(1)

# Step 2: Start RAG service
print(f"\n🚀 Step 2: Starting RAG service on port 8006...")
os.system("cd /home/parthav/work/rag && uvicorn knowledge_svc.main:app --port 8006 --host 0.0.0.0 > /tmp/rag_service.log 2>&1 &")
os.system("echo $! > /tmp/rag_service_pid.txt")

BASE_URL = "http://localhost:8006"

# Wait for service to be ready
print("   Waiting for service to start...")
for i in range(15):
    time.sleep(1)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=1)
        if response.status_code == 200:
            print("   ✅ Service is ready!")
            break
    except:
        if i == 14:
            print("   ❌ Service failed to start. Check /tmp/rag_service.log")
            print("\n   Log contents:")
            os.system("cat /tmp/rag_service.log")
            exit(1)
        continue

# Step 3: Process document via RAG
print(f"\n🔄 Step 3: Processing document via RAG service...")
try:
    response = requests.post(
        f"{BASE_URL}/process-s3",
        data={
            "tenant_id": TENANT_ID,
            "s3_bucket": BUCKET,
            "s3_key": S3_KEY,
            "filename": FILENAME
        }
    )
    result = response.json()
    if result.get("status") == "success":
        print(f"✅ Processing successful!")
        print(f"   Chunks created: {result.get('chunks_created')}")
    else:
        print(f"❌ Processing failed: {result}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Step 4: Query the knowledge base
print(f"\n🔍 Step 4: Testing queries...")

queries = [
    "What is the ideal water temperature for pour-over coffee?",
    "How long should coffee steep in a French press?",
    "What is the golden ratio for coffee brewing?",
    "How much caffeine is in a cup of coffee?"
]

for i, query in enumerate(queries, 1):
    print(f"\n   Query {i}: {query}")
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"tenant_id": TENANT_ID, "query": query}
        )
        result = response.json()
        answer = result.get("answer", "No answer")
        print(f"   Answer: {answer}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Step 5: List documents
print(f"\n📋 Step 5: Listing documents for tenant...")
try:
    response = requests.get(f"{BASE_URL}/files/{TENANT_ID}")
    result = response.json()
    print(f"✅ Found {len(result.get('files', []))} document(s):")
    for doc in result.get('files', []):
        print(f"   - {doc.get('filename')} ({doc.get('chunk_count')} chunks)")
except Exception as e:
    print(f"❌ Error: {e}")

# Step 6: Cleanup
print(f"\n🗑️  Step 6: Cleanup...")
print("   Deleting from RAG...")
try:
    requests.delete(f"{BASE_URL}/documents/{TENANT_ID}/{FILENAME}")
    print("   ✅ Deleted from RAG")
except:
    pass

print("   Deleting from S3...")
try:
    s3.delete_object(Bucket=BUCKET, Key=S3_KEY)
    print("   ✅ Deleted from S3")
except:
    pass

print("   Stopping RAG service...")
os.system("kill $(cat /tmp/rag_service_pid.txt) 2>/dev/null")
os.system("rm /tmp/rag_service_pid.txt /tmp/rag_service.log 2>/dev/null")

print("\n" + "="*60)
print("🎉 TEST COMPLETE!")
print("="*60)
