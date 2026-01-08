# Apply ADK client streaming patch BEFORE any ADK imports
import adk_client_streaming_patch  # noqa: F401

import asyncio
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from a2a.client.client import ClientConfig as A2AClientConfig
from a2a.client.client_factory import ClientFactory as A2AClientFactory

# Create A2A client factory with streaming enabled
a2a_client_config = A2AClientConfig(streaming=True)
a2a_client_factory = A2AClientFactory(config=a2a_client_config)

# Remote Travel Agent (A2A agent) with streaming enabled
remote_travel_agent = RemoteA2aAgent(
    name="travel_agent",
    description=(
        "ผู้ช่วยการท่องเที่ยวที่เชี่ยวชาญด้านการวางแผนการเดินทางและค้นหาที่พัก Airbnb "
        "สามารถค้นหาที่พัก ดูรายละเอียด และแนะนำตัวเลือกที่เหมาะสมได้"
    ),
    agent_card=f"http://localhost:8001/{AGENT_CARD_WELL_KNOWN_PATH}",
    a2a_client_factory=a2a_client_factory,
)

# Create a session service for the travel agent tool
_travel_session_service = InMemorySessionService()
_travel_runner = Runner(
    agent=remote_travel_agent,
    app_name="travel_agent_tool",
    session_service=_travel_session_service,
)

async def get_travel_info(query: str) -> str:
    """
    ค้นหาข้อมูลการท่องเที่ยวและที่พัก Airbnb จากผู้ช่วยการท่องเที่ยว
    
    Args:
        query: คำถามหรือความต้องการเกี่ยวกับการท่องเที่ยว เช่น "หาที่พักเชียงใหม่ 2 คืน งบ 2000 บาท"
    
    Returns:
        ข้อมูลการท่องเที่ยวและคำแนะนำที่พักจากผู้ช่วยการท่องเที่ยว
    """
    import uuid
    
    user_id = "tool_user"
    session_id = str(uuid.uuid4())
    
    # Create session
    await _travel_session_service.create_session(
        app_name="travel_agent_tool",
        user_id=user_id,
        session_id=session_id,
    )
    
    # Create user message
    user_content = genai_types.Content(
        role="user",
        parts=[genai_types.Part.from_text(text=query)],
    )
    
    # Collect all responses (without SSE streaming to avoid issues with function tools)
    full_response = ""
    async for event in _travel_runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    if not getattr(event, 'partial', False):
                        full_response = part.text
    
    return full_response if full_response else "ไม่สามารถรับข้อมูลจากผู้ช่วยการท่องเที่ยวได้ กรุณาลองใหม่อีกครั้ง"


# Create the function tool
travel_tool = FunctionTool(func=get_travel_info)

# Main Assistant Agent that uses travel agent as a tool
root_agent = LlmAgent(
    model="gemini-3-flash-preview",
    name="assistant_agent",
    description="ผู้ช่วยอัจฉริยะที่สามารถช่วยเหลือในหลากหลายเรื่อง",
    instruction="""
    คุณคือผู้ช่วยอัจฉริยะที่พร้อมช่วยเหลือผู้ใช้ในหลากหลายเรื่อง
    
    ความสามารถของคุณ:
    1. **การท่องเที่ยวและที่พัก**: เมื่อผู้ใช้ถามเกี่ยวกับการท่องเที่ยว ที่พัก Airbnb หรือการวางแผนการเดินทาง
       ให้ใช้ function "get_travel_info" เพื่อค้นหาข้อมูลจากผู้ช่วยการท่องเที่ยว
    
    วิธีการทำงาน:
    - รับฟังความต้องการของผู้ใช้อย่างตั้งใจ
    - เมื่อต้องการข้อมูลการท่องเที่ยว ให้เรียกใช้ get_travel_info(query="คำถามเกี่ยวกับการท่องเที่ยว")
    - **สำคัญ**: เมื่อได้รับผลลัพธ์จาก function ให้ทบทวนและปรับปรุงคำตอบก่อนตอบผู้ใช้
    - สรุปข้อมูลให้กระชับ เข้าใจง่าย และเพิ่มคำแนะนำของคุณเอง
    - ตอบกลับเป็นภาษาเดียวกับที่ผู้ใช้ใช้ในการสนทนา
    
    ตัวอย่างการทำงาน:
    1. ผู้ใช้ถาม: "อยากไปเที่ยวเชียงใหม่"
    2. คุณเรียก get_travel_info(query="อยากไปเที่ยวเชียงใหม่ ช่วยแนะนำที่พักและสถานที่ท่องเที่ยว") เพื่อค้นหาข้อมูล
    3. รับผลลัพธ์จาก function
    4. ทบทวนและปรับปรุงคำตอบ เพิ่มความเป็นกันเอง และคำแนะนำเพิ่มเติม
    5. ตอบผู้ใช้ด้วยคำตอบที่ปรับปรุงแล้ว
    """,
    tools=[travel_tool],
)