import os 
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.a2a.utils.agent_to_a2a import to_a2a

airbnb_mcp_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@openbnb/mcp-server-airbnb",
                "--ignore-robots-txt"
            ],
        ),
    ),
)

agent_instruction_prompt = """
คุณคือผู้ช่วยการท่องเที่ยวที่เชี่ยวชาญด้านการวางแผนการเดินทางและที่พัก Airbnb
หน้าที่ของคุณ:
- ช่วยผู้ใช้ค้นหาที่พัก Airbnb  
- ควรถามคำถามเพื่อความชัดเจนเพิ่มเติมเสมอ (เช่น สถานที่ งบประมาณ วันที่เข้าพัก จำนวนผู้เข้าพัก)  
- เมื่อได้ข้อมูลครบให้ Search ที่พักจาก Airbnb ด้วย airbnb_mcp_toolset
- และหากลูกต้าขอข้อมูลที่พักใดเป็นพิเศษให้ดึงจาก Airbnb ได้ ด้วย airbnb_mcp_toolset
- แนะนำตัวเลือกที่เหมาะสมอย่างสุภาพและเข้าใจง่าย  
- ตอบกลับเป็นภาษาเดียวกับที่ผู้ใช้ใช้ในการสนทนา 
"""

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='travel_manager',
    description="Travel Agent Manager",
    instruction=agent_instruction_prompt,
    tools=[airbnb_mcp_toolset],
)

a2a_app = to_a2a(root_agent, port=8001)

# To Start A2A Contribuiting
# uvicorn agent:a2a_app --port 8001 --reload --env-file .env