# 🚀 Pinecone RAG with MCP Tools (TRUE Integrated Embedding)

POC สำหรับการสร้างระบบ RAG (Retrieval-Augmented Generation) โดยใช้ Pinecone Integrated Embedding และ MCP Tools

## 📋 Overview

Project นี้แสดงวิธีการสร้างและใช้งาน RAG system แบบ **Best Practice** ด้วย:
- **Pinecone Integrated Embedding**: ไม่ต้องสร้าง embeddings เอง!
- **Pinecone Hosted Model**: multilingual-e5-large (รองรับภาษาไทย)
- **Google ADK**: Agent framework
- **MCP Tools**: Model Context Protocol สำหรับเชื่อมต่อ Pinecone

## 🎉 ข้อดีของ Integrated Embedding

✅ **ไม่ต้องเรียก OpenAI API** - ประหยัดค่าใช้จ่าย  
✅ **ค้นหาด้วย text โดยตรง** - ไม่ต้องสร้าง embedding ก่อน search  
✅ **ใช้ MCP search-records ได้เต็มรูปแบบ** - ตามที่ MCP ออกแบบไว้  
✅ **Consistent Embeddings** - ใช้ model เดียวกันตลอด  
✅ **ลด Latency** - embed + search ในที่เดียว  
✅ **Maintainable** - ไม่ต้องจัดการ embedding pipeline

## 🏗️ Architecture

```
User Query
    ↓
Google ADK Agent
    ↓
MCP Pinecone Tools
    ↓
Pinecone Index (test-rag-integrated)
    ↓
Retrieved Context
    ↓
Gemini LLM (สังเคราะห์คำตอบ)
    ↓
Response to User
```

## 📦 Index Configuration

- **Name**: `test-rag-integrated`
- **Embedding Model**: multilingual-e5-large (Pinecone hosted)
- **Dimension**: 1024
- **Metric**: cosine
- **Cloud**: AWS
- **Region**: us-west-2
- **Type**: Serverless with Integrated Inference
- **Field Map**: `{"text": "content"}`
- **Namespace**: `__default__`

## ⚡ Quick Start

```bash
# 1. สร้างและ activate virtual environment
cd 5_pinecone_rag_with_mcp_tools
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 2. ติดตั้ง dependencies
pip install -r requirements.txt

# 3. ตั้งค่า .env (ใน root folder)
# PINECONE_API_KEY="your_key"
# GEMINI_API_KEY="your_key"

# 4. สร้าง index และ ingest data
python3 create_index.py
python3 ingest_data.py

# 5. กลับไปที่ root แล้วทดสอบ RAG agent
cd ..

# CLI version:
adk run 5_pinecone_rag_with_mcp_tools/pinecone_rag_agent

# หรือ Web UI (แนะนำ):
adk web 5_pinecone_rag_with_mcp_tools
```

## 🔧 Setup (รายละเอียด)

### 1. สร้าง Virtual Environment

```bash
# สร้าง virtual environment
python3 -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate

# Windows:
# .venv\Scripts\activate
```

### 2. ติดตั้ง Dependencies

```bash
# ติดตั้ง dependencies ทั้งหมด (ใช้ไฟล์ใน folder นี้)
pip install -r requirements.txt
```

**หมายเหตุ**: 
- ✅ POC นี้มี `requirements.txt` ของตัวเอง (self-contained)
- ✅ ใช้ virtual environment ของ PoC นี้แยกจาก root เพราะ MCP Web UI ต้องใช้ `google-adk` 2.x
- ✅ รวม `google-adk`, `pinecone-client`, และ `python-dotenv` แล้ว
- ✅ ไม่ต้องติดตั้ง `openai` เพราะใช้ Pinecone integrated embedding!

### 3. ตั้งค่า Environment Variables

แก้ไขไฟล์ `.env` ในโฟลเดอร์ root:

```bash
# Pinecone Configuration (จำเป็น)
PINECONE_API_KEY="your_pinecone_api_key_here"

# Google Gemini Configuration (จำเป็น)
GEMINI_API_KEY="your_gemini_api_key_here"

# ไม่ต้องมี OPENAI_API_KEY แล้ว!
```

### 4. สร้าง Pinecone Index

```bash
# ตรวจสอบว่า activate .venv แล้ว
python3 create_index.py
```

สคริปต์นี้จะ:
- ✅ ตรวจสอบว่า index มีอยู่หรือไม่
- ✅ สร้าง serverless index พร้อม **integrated embedding**
- ✅ ใช้ Pinecone hosted model: multilingual-e5-large
- ✅ แสดงข้อมูล index configuration

### 5. Ingest ข้อมูล

```bash
# ตรวจสอบว่า activate .venv แล้ว
python3 ingest_data.py
```

สคริปต์นี้จะ:
- ✅ โหลดข้อมูล sample จาก `sample_data/` (หรือสร้างใหม่ถ้าไม่มี)
- ✅ แบ่งข้อความเป็น chunks (500 characters, overlap 50)
- ✅ Upsert เข้า Pinecone (Pinecone จะสร้าง embeddings ให้อัตโนมัติ!)
- ✅ **ไม่ต้องเรียก OpenAI API!**

### 6. ใช้งาน RAG Agent

#### วิธีที่ 1: รันแบบ CLI (Command Line)

```bash
# รันจาก repository root
adk run 5_pinecone_rag_with_mcp_tools/pinecone_rag_agent
```

#### วิธีที่ 2: รันแบบ Web UI (แนะนำ!) 🌐

```bash
# รันจาก repository root โดยให้ PoC 5 เป็น agents directory
adk web 5_pinecone_rag_with_mcp_tools
```

จากนั้นเปิดเบราว์เซอร์ที่ `http://localhost:8000` และเลือก
`pinecone_rag_agent`

**ข้อดีของ Web UI:**
- ✅ UI สวยงาม ใช้งานง่าย
- ✅ เห็นประวัติการสนทนา
- ✅ ทดสอบได้สะดวกกว่า CLI
- ✅ เหมือนกับ agent ตัวอื่นๆ ในโปรเจกต์

Agent จะ:
- ✅ รับคำถามจาก user
- ✅ ค้นหาข้อมูลด้วย MCP search-records (ส่ง text โดยตรง!)
- ✅ สังเคราะห์คำตอบด้วย Gemini
- ✅ แสดงคำตอบพร้อมอ้างอิงแหล่งที่มา

## 📁 Project Structure

```
5_pinecone_rag_with_mcp_tools/
├── .venv/                   # Virtual environment (git ignored)
├── .gitignore               # Git ignore rules
├── requirements.txt         # ✨ Dependencies (self-contained)
├── __init__.py              # Package initialization
├── pinecone_rag_agent/      # ชื่อ app ที่ผ่าน ADK validation
│   ├── __init__.py          # ADK package entry point
│   └── agent.py             # ✨ RAG agent สำหรับ CLI และ Web UI
├── create_index.py          # สร้าง Pinecone index (integrated embedding)
├── ingest_data.py           # Chunk และ upsert data (ไม่ต้องสร้าง embedding!)
├── README.md                # เอกสารนี้
└── sample_data/             # Sample documents
    ├── sample_1.json        # ทักษะการขายที่สำคัญ
    ├── sample_2.json        # เทคนิคการปิดการขาย
    └── sample_3.json        # การจัดการการคัดค้าน
```

## 💡 Usage Examples

### ตัวอย่างคำถาม

```
💬 ทักษะการขายที่สำคัญมีอะไรบ้าง?

💬 มีเทคนิคการปิดการขายอะไรบ้าง?

💬 จะจัดการกับการคัดค้านของลูกค้าอย่างไร?

💬 การสร้างความไว้วางใจกับลูกค้าทำอย่างไร?
```

### ตัวอย่างการตอบ

Agent จะ:
1. 🔍 ค้นหาข้อมูลที่เกี่ยวข้องใน Pinecone (top 5-10 results)
2. 📖 อ่านและวิเคราะห์ข้อมูล
3. 🤖 สังเคราะห์คำตอบที่ครบถ้วน
4. 📝 จัดรูปแบบให้อ่านง่าย (bullet points, numbering)
5. 🔗 อ้างอิงแหล่งที่มา

## 🔍 MCP Tools ที่ใช้

Agent ใช้ MCP Pinecone tools ดังนี้:

- **search-records**: ค้นหาข้อมูลที่คล้ายกับ query
- **describe-index**: ดูข้อมูล index configuration
- **describe-index-stats**: ดูสถิติของ index

## 📊 Data Flow

```
1. User Question
   ↓
2. Agent receives question
   ↓
3. Agent calls search-records (via MCP)
   ↓
4. Pinecone returns relevant chunks
   ↓
5. Agent synthesizes answer with Gemini
   ↓
6. User receives comprehensive answer
```

## 🎯 Key Features

- ✅ **Serverless Pinecone**: Auto-scaling, pay-per-use
- ✅ **MCP Integration**: Standardized tool protocol
- ✅ **Semantic Search**: ค้นหาตามความหมาย ไม่ใช่แค่ keyword
- ✅ **Context-aware**: รักษา context ด้วย chunk overlap
- ✅ **Source Attribution**: อ้างอิงแหล่งที่มาของข้อมูล
- ✅ **Thai Language Support**: รองรับภาษาไทยเต็มรูปแบบ

## 🔧 Customization

### เพิ่มข้อมูลของคุณเอง

1. สร้างไฟล์ JSON ใน `sample_data/`:
   ```json
   {
     "title": "หัวข้อของคุณ",
     "content": "เนื้อหาของคุณ...",
     "category": "category_name"
   }
   ```

2. รัน `python3 ingest_data.py` ใหม่

### ปรับแต่ง Chunking Strategy

แก้ไขใน `ingest_data.py`:
```python
CHUNK_SIZE = 500      # ขนาด chunk (characters)
CHUNK_OVERLAP = 50    # overlap ระหว่าง chunk
```

### ปรับแต่ง Search Parameters

แก้ไขใน `pinecone_rag_agent/agent.py` (instruction prompt):
```python
# เปลี่ยนจำนวนผลลัพธ์ที่ค้นหา
"ค้นหา top 5-10 ผลลัพธ์"  # → เปลี่ยนเป็น top 3, 15, etc.
```

## 🐛 Troubleshooting

### ❌ Virtual Environment ไม่ทำงาน
```bash
# ตรวจสอบว่า activate แล้ว (ต้องเห็น (.venv) ข้างหน้า prompt)
which python3  # ต้องชี้ไปที่ .venv/bin/python3

# ถ้ายัง activate ไม่ได้
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### ❌ "PINECONE_API_KEY not found"
- ตรวจสอบว่ามีไฟล์ `.env` ในโฟลเดอร์ root (ไม่ใช่ใน 5_pinecone_rag_with_mcp_tools)
- ตรวจสอบว่าใส่ API key ถูกต้อง
- ตรวจสอบว่า activate .venv แล้ว

### ❌ "API key not valid" จาก Generative Language API
- ตรวจสอบ `GEMINI_API_KEY` ใน root `.env`; error นี้หมายถึง Gemini ปฏิเสธ key ก่อนเรียก RAG tool
- ถ้า key ถูกจำกัดการใช้งาน ให้ตรวจว่าอนุญาต Generative Language API และยังไม่ถูก revoke
- หลังแก้ `.env` ให้หยุด ADK Web แล้วเปิดใหม่ เพื่อให้ process โหลดค่าใหม่

### ❌ "Module not found"
```bash
# ตรวจสอบว่าติดตั้ง dependencies แล้ว
pip list | grep pinecone
pip list | grep google-adk

# ถ้ายังไม่มี ให้ติดตั้งใหม่
pip install -r requirements.txt
```

### ❌ "Index not found"
- รัน `python3 create_index.py` ก่อน
- ตรวจสอบว่า index name ถูกต้อง
- ตรวจสอบว่า activate .venv แล้ว

### ❌ "No results found"
- รัน `python3 ingest_data.py` เพื่อ upsert ข้อมูล
- ตรวจสอบว่ามีข้อมูลใน index: ดูที่ Pinecone console

### ❌ MCP connection errors
- ตรวจสอบว่า Node.js และ `npx` พร้อมใช้งาน
- ลอง: `npx -y @pinecone-database/mcp --help`

### ❌ "Invalid app name '5_pinecone_rag_with_mcp_tools'"
- เกิดจากการเปิด root ด้วย `adk web .` แล้วเลือกโฟลเดอร์ที่ขึ้นต้นด้วยตัวเลข
- หยุด server เดิม แล้วรัน `adk web 5_pinecone_rag_with_mcp_tools`
- เลือก `pinecone_rag_agent` และสร้าง session ใหม่

## 📚 Additional Resources

- [Pinecone Documentation](https://docs.pinecone.io/)
- [Pinecone Integrated Inference](https://docs.pinecone.io/guides/inference/understanding-inference)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Google ADK Documentation](https://github.com/google/adk)

## 🎓 Learning Points

จาก POC นี้คุณจะได้เรียนรู้:

1. **RAG Architecture**: วิธีการสร้าง RAG system
2. **Vector Embeddings**: การทำงานของ semantic search
3. **MCP Protocol**: การใช้ MCP tools กับ AI agents
4. **Chunking Strategy**: วิธีแบ่งเอกสารให้มีประสิทธิภาพ
5. **Agent Development**: การสร้าง AI agent ด้วย Google ADK

## 🚀 Next Steps

- [ ] เพิ่มข้อมูลจริงของคุณ
- [ ] ทดลอง chunking strategies ต่างๆ
- [ ] เพิ่ม reranking สำหรับความแม่นยำสูงขึ้น
- [ ] เพิ่ม metadata filtering
- [ ] สร้าง web UI หรือ chatbot interface
- [ ] ทดสอบกับ embedding models อื่นๆ

## 📝 Notes

- ✅ **Index นี้ใช้ TRUE Integrated Embedding** - ตามแนวทาง Best Practice!
- ✅ ใช้ Pinecone hosted model: multilingual-e5-large
- ✅ ไม่ต้องจัดการ embedding pipeline เอง
- ✅ ประหยัดค่าใช้จ่าย (ไม่ต้องเรียก OpenAI API)
- ✅ พร้อมใช้งาน production ทันที!

---

**สร้างโดย**: POC Project  
**วันที่**: 2025  
**Version**: 1.0
