# Apply ADK client streaming patch BEFORE any ADK imports
import adk_client_streaming_patch  # noqa: F401

from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from a2a.client.client import ClientConfig as A2AClientConfig
from a2a.client.client_factory import ClientFactory as A2AClientFactory

# Create A2A client factory with streaming enabled
a2a_client_config = A2AClientConfig(streaming=True)
a2a_client_factory = A2AClientFactory(config=a2a_client_config)

# Remote Travel Agent (A2A sub-agent) with streaming enabled
remote_travel_agent = RemoteA2aAgent(
    name="travel_agent",
    description=(
        "ผู้ช่วยการท่องเที่ยวที่เชี่ยวชาญด้านการวางแผนการเดินทางและค้นหาที่พัก Airbnb "
        "สามารถค้นหาที่พัก ดูรายละเอียด และแนะนำตัวเลือกที่เหมาะสมได้"
    ),
    agent_card=f"http://localhost:8001/{AGENT_CARD_WELL_KNOWN_PATH}",
    a2a_client_factory=a2a_client_factory,
)

# Main Assistant Agent that orchestrates sub-agents
root_agent = LlmAgent(
    model="gemini-3-flash-preview",
    name="assistant_agent",
    description="ผู้ช่วยอัจฉริยะที่สามารถช่วยเหลือในหลากหลายเรื่อง",
    instruction="""
    คุณคือผู้ช่วยอัจฉริยะที่พร้อมช่วยเหลือผู้ใช้ในหลากหลายเรื่อง
    
    ความสามารถของคุณ:
    1. **การท่องเที่ยวและที่พัก**: เมื่อผู้ใช้ถามเกี่ยวกับการท่องเที่ยว ที่พัก Airbnb หรือการวางแผนการเดินทาง
       ให้ใช้ travel_agent sub-agent เพื่อค้นหาและแนะนำที่พักที่เหมาะสม
    
    วิธีการทำงาน:
    - รับฟังความต้องการของผู้ใช้อย่างตั้งใจ
    - ส่งต่อคำขอไปยัง sub-agent ที่เหมาะสม
    - สรุปและนำเสนอข้อมูลให้ผู้ใช้อย่างเข้าใจง่าย
    - ตอบกลับเป็นภาษาเดียวกับที่ผู้ใช้ใช้ในการสนทนา
    
    
    หมายเหตุ: ในอนาคตจะมี sub-agent เพิ่มเติมสำหรับความสามารถอื่นๆ
    """,
    sub_agents=[remote_travel_agent],
)