#!/usr/bin/env python3
"""
สร้าง Pinecone Index with Integrated Embedding
สำหรับใช้งาน RAG ผ่าน MCP Tools
ใช้ Pinecone hosted embedding model (multilingual-e5-large)
"""

import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
INDEX_NAME = "test-rag-integrated"
EMBEDDING_MODEL = "multilingual-e5-large"  # Pinecone hosted model
DIMENSION = 1024  # multilingual-e5-large dimension (auto-configured)
METRIC = "cosine"  # For display only; actual metric is determined by the model
CLOUD = "aws"
REGION = "us-west-2"
FIELD_MAP = {"text": "content"}  # field ที่จะถูก embed อัตโนมัติ

def create_index_with_integrated_embedding():
    """
    สร้าง Pinecone index แบบ serverless พร้อม TRUE integrated embedding
    ใช้ Pinecone hosted model: multilingual-e5-large
    
    ข้อดี:
    - ไม่ต้องสร้าง embedding เอง
    - ใช้ MCP search-records ได้เต็มรูปแบบ (ค้นหาด้วย text โดยตรง)
    - Consistent embedding (ใช้ model เดียวกันตลอด)
    - ลด latency และ complexity
    """
    
    # Initialize Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("❌ PINECONE_API_KEY not found in environment variables")
    
    pc = Pinecone(api_key=api_key)
    
    print(f"🔍 ตรวจสอบ index ที่มีอยู่...")
    existing_indexes = pc.list_indexes()
    
    # Check if index already exists
    index_names = [idx.name for idx in existing_indexes.indexes]
    if INDEX_NAME in index_names:
        print(f"⚠️  Index '{INDEX_NAME}' มีอยู่แล้ว")
        
        # ถามว่าต้องการลบและสร้างใหม่หรือไม่
        response = input("ต้องการลบและสร้างใหม่หรือไม่? (y/N): ")
        if response.lower() == 'y':
            print(f"🗑️  กำลังลบ index '{INDEX_NAME}'...")
            pc.delete_index(INDEX_NAME)
            print("✅ ลบ index สำเร็จ")
            import time
            print("⏳ รอ 10 วินาที...")
            time.sleep(10)
        else:
            print("ℹ️  ใช้ index ที่มีอยู่ต่อไป")
            return
    
    print(f"\n📝 กำลังสร้าง index with INTEGRATED EMBEDDING: {INDEX_NAME}")
    print(f"   - Embedding Model: {EMBEDDING_MODEL}")
    print(f"   - Dimension: {DIMENSION}")
    print(f"   - Metric: {METRIC}")
    print(f"   - Cloud: {CLOUD}")
    print(f"   - Region: {REGION}")
    print(f"   - Type: Serverless with Integrated Inference")
    print(f"   - Field Map: {FIELD_MAP}")
    
    try:
        # สร้าง serverless index พร้อม integrated embedding
        # ใช้ create_index_for_model สำหรับ integrated inference
        # Note: metric จะถูกกำหนดโดย model โดยอัตโนมัติ (ไม่ต้องระบุ)
        
        index_config = pc.create_index_for_model(
            name=INDEX_NAME,
            cloud="aws",
            region="us-west-2",
            embed={
                "model": "multilingual-e5-large",
                "field_map": FIELD_MAP
            }
        )
        
        print(f"\n✅ สร้าง index '{INDEX_NAME}' สำเร็จ!")
        print(f"\n🎉 ข้อดีของ Integrated Embedding:")
        print(f"   ✅ ไม่ต้องสร้าง embedding เอง")
        print(f"   ✅ ใช้ MCP search-records ได้เต็มรูปแบบ")
        print(f"   ✅ ค้นหาด้วย text โดยตรง (ไม่ต้องส่ง vector)")
        print(f"   ✅ Consistent และ Maintainable")
        print(f"   ✅ รองรับภาษาไทยได้ดี (multilingual-e5-large)")
        
        # แสดงข้อมูล index
        print(f"\n🔍 ข้อมูล Index:")
        index_info = pc.describe_index(INDEX_NAME)
        print(f"   - Name: {index_info.name}")
        print(f"   - Dimension: {index_info.dimension}")
        print(f"   - Metric: {index_info.metric}")
        print(f"   - Host: {index_info.host}")
        print(f"   - Status: {index_info.status.state}")
        
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {str(e)}")
        raise

def main():
    """Main function"""
    print("=" * 80)
    print("🚀 Pinecone Index Creator with Integrated Embedding Support")
    print("=" * 80)
    print()
    
    try:
        create_index_with_integrated_embedding()
        print("\n" + "=" * 80)
        print("✅ Process completed successfully!")
        print("=" * 80)
        print("\n📖 Next steps:")
        print("   1. ใส่ข้อมูล sample ใน sample_data/")
        print("   2. รัน: python ingest_data.py")
        print("   3. รัน: python agent.py")
        
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ Process failed: {str(e)}")
        print("=" * 80)

if __name__ == "__main__":
    main()
