#!/usr/bin/env python3
"""
Ingest Data to Pinecone Index with Integrated Embedding
- อ่านข้อมูลจาก sample_data/
- แบ่ง chunk
- Upsert เข้า Pinecone (Pinecone จะสร้าง embedding ให้อัตโนมัติ)
- ไม่ต้องเรียก OpenAI API เอง!
"""

import os
import json
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# Configuration
INDEX_NAME = "test-rag-integrated"
NAMESPACE = ""  # Empty string for default namespace (not "__default__")
CHUNK_SIZE = 500  # ขนาด chunk (characters)
CHUNK_OVERLAP = 50  # overlap ระหว่าง chunk

def load_sample_data() -> List[Dict[str, str]]:
    """โหลดข้อมูล sample จาก sample_data/"""
    sample_data_dir = Path(__file__).parent / "sample_data"
    
    if not sample_data_dir.exists():
        print(f"⚠️  ไม่พบโฟลเดอร์ {sample_data_dir}")
        print("📝 สร้างข้อมูล sample ตัวอย่าง...")
        sample_data_dir.mkdir(exist_ok=True)
        
        # สร้างข้อมูล sample
        sample_docs = [
            {
                "title": "ทักษะการขายที่สำคัญ",
                "content": """
                ทักษะการขายที่ดีประกอบด้วยหลายองค์ประกอบสำคัญ ได้แก่:
                
                1. การฟังอย่างตั้งใจ (Active Listening) - นักขายที่ดีต้องรู้จักฟังความต้องการของลูกค้าอย่างตั้งใจ 
                ไม่ใช่แค่พูดคนเดียว แต่ต้องรู้จักถามคำถามที่ถูกต้องและฟังคำตอบอย่างลึกซึ้ง
                
                2. การสร้างความไว้วางใจ (Building Trust) - ลูกค้าจะซื้อจากคนที่พวกเขาไว้วางใจ 
                การสร้างความไว้วางใจต้องอาศัยความซื่อสัตย์ ความรู้ในผลิตภัณฑ์ และการให้คำแนะนำที่เป็นประโยชน์
                
                3. ความรู้เกี่ยวกับผลิตภัณฑ์ (Product Knowledge) - นักขายต้องเข้าใจผลิตภัณฑ์หรือบริการของตนเองอย่างลึกซึ้ง 
                สามารถตอบคำถามได้อย่างมั่นใจและแนะนำสิ่งที่เหมาะสมกับลูกค้าได้
                """,
                "category": "sales_skills"
            },
            {
                "title": "เทคนิคการปิดการขาย",
                "content": """
                เทคนิคการปิดการขายที่มีประสิทธิภาพ:
                
                1. การปิดแบบสมมติฐาน (Assumptive Close) - ทำเสมือนว่าลูกค้าจะซื้อแน่นอน 
                เช่น "เราจะส่งสินค้าวันไหนดีครับ?" แทนที่จะถามว่า "คุณจะซื้อไหมครับ?"
                
                2. การปิดแบบทางเลือก (Alternative Close) - ให้ลูกค้าเลือกระหว่างตัวเลือก 
                เช่น "คุณต้องการรุ่น A หรือ B ครับ?" ไม่ใช่ "คุณจะซื้อไหมครับ?"
                
                3. การปิดแบบเร่งด่วน (Urgency Close) - สร้างความรู้สึกเร่งด่วน 
                เช่น "โปรโมชั่นนี้เหลือเพียง 3 วันเท่านั้น" หรือ "เหลือสินค้าอีกแค่ 2 ชิ้น"
                
                4. การปิดแบบลดความเสี่ยง (Risk Reversal Close) - ลดความกังวลของลูกค้า 
                เช่น "เรามีรับประกัน 30 วันคืนเงินเต็มจำนวน" หรือ "ทดลองใช้ฟรี 14 วัน"
                """,
                "category": "sales_techniques"
            },
            {
                "title": "การจัดการการคัดค้านของลูกค้า",
                "content": """
                การจัดการกับการคัดค้านของลูกค้าอย่างมีประสิทธิภาพ:
                
                1. ฟังและเข้าใจก่อน - อย่าพยายามโต้แย้งทันที ให้ฟังความกังวลของลูกค้าจนจบ
                
                2. แสดงความเห็นอกเห็นใจ - แสดงให้ลูกค้าเห็นว่าคุณเข้าใจความกังวลของเขา 
                เช่น "ผมเข้าใจครับว่าคุณกังวลเรื่องราคา"
                
                3. ชี้แจงและให้ข้อมูล - ตอบข้อกังวลด้วยข้อมูลที่ชัดเจน ไม่ใช่แค่ความคิดเห็น
                
                4. ยืนยันและดำเนินการต่อ - หลังจากตอบข้อกังวลแล้ว ให้ยืนยันกับลูกค้า 
                "คุณรู้สึกสบายใจขึ้นแล้วใช่ไหมครับ?" แล้วดำเนินการขายต่อ
                
                การคัดค้านที่พบบ่อย:
                - "แพงเกินไป" → เน้นคุณค่าและ ROI
                - "ต้องคิดก่อน" → สร้างความเร่งด่วนและลดความเสี่ยง
                - "มีของเดิมอยู่แล้ว" → แสดงความแตกต่างและข้อได้เปรียบ
                """,
                "category": "objection_handling"
            }
        ]
        
        # บันทึก sample data
        for i, doc in enumerate(sample_docs):
            file_path = sample_data_dir / f"sample_{i+1}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(doc, f, ensure_ascii=False, indent=2)
        
        print(f"✅ สร้างข้อมูล sample {len(sample_docs)} ไฟล์")
        
        # Return ข้อมูลที่เพิ่งสร้างทันที (Best Practice)
        return sample_docs
    
    # โหลดข้อมูลทั้งหมดจากไฟล์ที่มีอยู่
    documents = []
    for file_path in sample_data_dir.glob("*.json"):
        with open(file_path, 'r', encoding='utf-8') as f:
            documents.append(json.load(f))
    
    print(f"📂 โหลดจากไฟล์: {len(documents)} เอกสาร")
    return documents

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """แบ่งข้อความเป็น chunks แบบง่าย"""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        # ถ้าไม่ใช่ chunk สุดท้าย ให้ตัดที่ตำแหน่งเว้นวรรคใกล้ที่สุด
        if end < text_length:
            last_space = chunk.rfind(' ')
            if last_space != -1:
                chunk = chunk[:last_space]
                end = start + last_space
        
        chunks.append(chunk.strip())
        start = end - overlap  # overlap เพื่อรักษา context
    
    return [c for c in chunks if c]  # กรองช่องว่าง

def ingest_documents():
    """Main ingestion function with Integrated Embedding"""
    print("=" * 80)
    print("📦 Data Ingestion Process (Integrated Embedding)")
    print("=" * 80)
    
    # Initialize Pinecone client
    print("\n⚙️  กำลัง initialize Pinecone client...")
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(INDEX_NAME)
    
    # Load documents
    print("\n📂 กำลังโหลดข้อมูล...")
    documents = load_sample_data()
    print(f"✅ โหลดข้อมูล {len(documents)} เอกสาร")
    
    # Check if we have documents
    if not documents:
        print("\n❌ ไม่พบข้อมูลที่จะ ingest!")
        print("💡 กรุณาตรวจสอบว่ามีไฟล์ JSON ใน sample_data/ หรือไม่")
        return
    
    # Process and upsert
    print("\n🔄 กำลัง process และ upsert ข้อมูล...")
    print("💡 Pinecone จะสร้าง embedding ให้อัตโนมัติ!\n")
    
    all_records = []
    
    for doc_idx, doc in enumerate(documents):
        print(f"📄 Processing: {doc['title']}")
        
        # Chunk the content
        chunks = chunk_text(doc['content'])
        print(f"   - Chunks: {len(chunks)}")
        
        # เตรียม records สำหรับ upsert_records
        # ไม่ต้องสร้าง embedding เอง!
        for chunk_idx, chunk in enumerate(chunks):
            record_id = f"doc_{doc_idx}_chunk_{chunk_idx}"
            
            # Record format สำหรับ integrated embedding
            # ต้องมี field "content" ตาม field_map ที่กำหนดไว้
            record = {
                "_id": record_id,
                "content": chunk,  # field นี้จะถูก embed อัตโนมัติ
                "title": doc["title"],
                "category": doc["category"],
                "chunk_index": chunk_idx,
                "total_chunks": len(chunks)
            }
            
            all_records.append(record)
        
        print(f"   ✅ เตรียม {len(chunks)} records")
    
    # Check if we have records to upsert
    if not all_records:
        print("\n❌ ไม่มี records ที่จะ upsert!")
        print("💡 ตรวจสอบว่าข้อมูลมี content หรือไม่")
        return
    
    # Upsert to Pinecone using upsert_records (for integrated embedding)
    print(f"\n⬆️  กำลัง upsert {len(all_records)} records เข้า Pinecone...")
    print("⚡ Pinecone กำลังสร้าง embeddings อัตโนมัติ...\n")
    
    # Upsert in batches
    # Note: namespace เป็น parameter แรก (positional), records เป็น parameter ที่สอง
    # Best Practice: สำหรับ integrated embedding ใช้ batch_size = 96 (ตาม Pinecone docs)
    batch_size = 96
    for i in range(0, len(all_records), batch_size):
        batch = all_records[i:i+batch_size]
        try:
            index.upsert_records(NAMESPACE, batch)
            print(f"   - Upserted batch {i//batch_size + 1} ({len(batch)} records)")
        except Exception as e:
            print(f"   ❌ Error upserting batch {i//batch_size + 1}: {str(e)}")
            raise
    
    print("\n✅ Upsert สำเร็จ!")
    print("🎉 ข้อมูลถูก embed และ index โดย Pinecone แล้ว!")
    
    # Show index stats
    print("\n📊 สถิติ Index:")
    stats = index.describe_index_stats()
    print(f"   - Total vectors: {stats.total_vector_count:,}")
    print(f"   - Dimension: {stats.dimension}")
    if stats.namespaces:
        for ns, info in stats.namespaces.items():
            ns_name = ns if ns else "(default)"
            print(f"   - Namespace '{ns_name}': {info.vector_count:,} vectors")

def main():
    """Main function"""
    try:
        ingest_documents()
        
        print("\n" + "=" * 80)
        print("✅ Data ingestion completed successfully!")
        print("=" * 80)
        print("\n📖 Next step:")
        print("   รัน: python agent.py เพื่อทดสอบ RAG chat")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
