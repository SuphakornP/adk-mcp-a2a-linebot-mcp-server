#!/usr/bin/env python3
"""
RAG Agent with Pinecone MCP Tools
ใช้ Pinecone index ที่มี integrated embedding สำหรับการค้นหาข้อมูล
"""

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Validate required environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not PINECONE_API_KEY:
    print("⚠️  Warning: PINECONE_API_KEY not set in .env file")
    print("Pinecone MCP toolset will not be available.")
    exit(1)

# ตั้งค่า Pinecone MCP Toolset
# ใช้ Official Pinecone MCP server
pinecone_mcp_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@pinecone-database/mcp",  # ✅ ชื่อ package ที่ถูกต้อง
            ],
            env={
                "PINECONE_API_KEY": PINECONE_API_KEY,
            },
        ),
    ),
)

# Agent instruction
agent_instruction_prompt = """
คุณคือ Sales Knowledge Assistant ที่เชี่ยวชาญด้านความรู้เกี่ยวกับการขาย

หน้าที่ของคุณ:
- ตอบคำถามเกี่ยวกับทักษะการขาย เทคนิคการขาย และการจัดการการคัดค้าน
- ใช้เครื่องมือ Pinecone search เพื่อค้นหาข้อมูลที่เกี่ยวข้อง
- สังเคราะห์ข้อมูลจากหลายแหล่งและตอบคำถามอย่างครบถ้วน
- อ้างอิงแหล่งที่มาของข้อมูล (ถ้ามี metadata)
- ตอบเป็นภาษาไทยที่เข้าใจง่าย

วิธีการทำงาน:
1. เมื่อได้รับคำถามจากผู้ใช้ ให้ใช้ search-records tool เพื่อค้นหาข้อมูลที่เกี่ยวข้อง
   - ใช้ index name: "test-rag-integrated"
   - ใช้ namespace: "" (empty string สำหรับ default namespace)
   - ค้นหา top 5-10 ผลลัพธ์
   - ส่ง query เป็น text โดยตรง (ไม่ต้องสร้าง embedding เอง!)
   - ตัวอย่าง: search_records(name="test-rag-integrated", namespace="", query={"topK": 5, "inputs": {"text": "คำถามของผู้ใช้"}})
   
2. อ่านและวิเคราะห์ข้อมูลที่ได้จากการค้นหา

3. สังเคราะห์คำตอบที่:
   - ตอบคำถามโดยตรง
   - ให้ข้อมูลที่ครบถ้วนและเป็นประโยชน์
   - มีตัวอย่างหรือรายละเอียดเพิ่มเติม (ถ้ามี)
   - อ้างอิงแหล่งที่มา (title หรือ category จาก metadata)

4. ถ้าไม่พบข้อมูลที่เกี่ยวข้อง:
   - บอกผู้ใช้ว่าไม่พบข้อมูลในฐานความรู้
   - เสนอให้ผู้ใช้ถามคำถามในมุมอื่น

ตัวอย่างการตอบ:
"จากข้อมูลที่ค้นพบ ทักษะการขายที่สำคัญมี 3 ประการหลัก:

1. **การฟังอย่างตั้งใจ (Active Listening)** - นักขายต้องรู้จักฟังความต้องการของลูกค้า...

2. **การสร้างความไว้วางใจ (Building Trust)** - ลูกค้าจะซื้อจากคนที่พวกเขาไว้วางใจ...

3. **ความรู้เกี่ยวกับผลิตภัณฑ์ (Product Knowledge)** - นักขายต้องเข้าใจผลิตภัณฑ์อย่างลึกซึ้ง...

(ที่มา: ทักษะการขายที่สำคัญ)"

คำแนะนำสำคัญ:
- ถ้าคำถามไม่ชัดเจน ให้ถามย้อนกลับเพื่อความชัดเจน
- ใช้ข้อมูลจาก knowledge base เป็นหลัก
- ตอบด้วยภาษาที่เข้าใจง่าย ไม่ใช้คำยาก
- จัดรูปแบบการตอบให้อ่านง่าย (ใช้ bullet points, numbering, bold)
"""

# สร้าง RAG Agent
# สามารถใช้กับทั้ง CLI และ ADK Web UI
rag_agent = Agent(
    model='gemini-3.8-flash',
    name='sales_knowledge_assistant',
    description="Sales Knowledge Assistant with RAG - ตอบคำถามเกี่ยวกับทักษะการขายและเทคนิคการขาย",
    instruction=agent_instruction_prompt,
    tools=[pinecone_mcp_toolset],
)

# Alias สำหรับ ADK Web UI (ต้องมี root_agent)
root_agent = rag_agent

def main():
    """Main function สำหรับทดสอบ agent"""
    print("=" * 80)
    print("🤖 Sales Knowledge Assistant (RAG)")
    print("=" * 80)
    print("พิมพ์ 'exit' หรือ 'quit' เพื่อออก\n")
    
    while True:
        try:
            user_input = input("\n💬 คำถาม: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit', 'ออก']:
                print("\n👋 ขอบคุณที่ใช้บริการ!")
                break
            
            print("\n🤔 กำลังค้นหาและวิเคราะห์ข้อมูล...\n")
            
            # ส่งคำถามไปยัง agent
            response = rag_agent.run(user_input)
            
            print("─" * 80)
            print("🤖 คำตอบ:")
            print("─" * 80)
            print(response.text)
            print("─" * 80)
            
        except KeyboardInterrupt:
            print("\n\n👋 ขอบคุณที่ใช้บริการ!")
            break
        except Exception as e:
            print(f"\n❌ เกิดข้อผิดพลาด: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
