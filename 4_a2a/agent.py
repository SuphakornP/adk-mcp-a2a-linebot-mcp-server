from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools import AgentTool

# Remote Travel Agent (A2A agent)
remote_travel_agent = RemoteA2aAgent(
    name="travel_agent",
    description=(
        "ผู้ช่วยการท่องเที่ยวที่เชี่ยวชาญด้านการวางแผนการเดินทางและค้นหาที่พัก Airbnb "
        "สามารถค้นหาที่พัก ดูรายละเอียด และแนะนำตัวเลือกที่เหมาะสมได้"
    ),
    agent_card=f"http://localhost:8001/{AGENT_CARD_WELL_KNOWN_PATH}",
)

# Wrap remote_travel_agent as a tool so assistant_agent can call it and stream its own response
travel_agent_tool = AgentTool(agent=remote_travel_agent)

# Main Assistant Agent that uses travel agent as a tool
root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="assistant_agent",
    description="ผู้ช่วยอัจฉริยะที่สามารถช่วยเหลือในหลากหลายเรื่อง",
    instruction="""
    คุณคือผู้ช่วยอัจฉริยะที่พร้อมช่วยเหลือผู้ใช้ในหลากหลายเรื่อง
    
    ความสามารถของคุณ:
    1. **การท่องเที่ยวและที่พัก**: เมื่อผู้ใช้ถามเกี่ยวกับการท่องเที่ยว ที่พัก Airbnb หรือการวางแผนการเดินทาง
       ให้ใช้ travel_agent tool เพื่อค้นหาข้อมูลจากผู้ช่วยการท่องเที่ยว
    
    วิธีการทำงาน:
    - รับฟังความต้องการของผู้ใช้อย่างตั้งใจ
    - เมื่อต้องการข้อมูลการท่องเที่ยว ให้เรียกใช้ travel_agent tool
    - **สำคัญ**: เมื่อได้รับผลลัพธ์จาก tool ให้ทบทวนและปรับปรุงคำตอบก่อนตอบผู้ใช้
    - สรุปข้อมูลให้กระชับ เข้าใจง่าย และเพิ่มคำแนะนำของคุณเอง
    - ตอบกลับเป็นภาษาเดียวกับที่ผู้ใช้ใช้ในการสนทนา
    """,
    tools=[travel_agent_tool],
)