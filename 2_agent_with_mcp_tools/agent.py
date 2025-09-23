from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
import os 

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

line_bot_mcp_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@line/line-bot-mcp-server",
            ],
            env={
                "CHANNEL_ACCESS_TOKEN": os.getenv("CHANNEL_ACCESS_TOKEN"),
                "DESTINATION_USER_ID":  os.getenv("DESTINATION_USER_ID"),
            },
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
- เมื่อผู้ใช้ต้องการรับผลใน LINE ให้สร้าง Flex Message เท่านั้น 
    -  ให้สร้าง Flex Message ตาม สเปค LINE Flex Message อย่างเคร่งครัด (มี type, altText, contents, และโครงสร้าง bubble/carousel ถูกต้อง) 
    - และใช้เครื่องมือ line_bot_mcp_toolset ในการส่ง Flex Message

ข้อจำกัด Flex:
- altText ต้องมี (สูงสุด ~400 ตัวอักษร)
- carousel.contents สูงสุด 12 bubbles
- รูปใน hero ไม่มีไม่เป็นไร
- ใช้ wrap: true กับข้อความยาว
- หลีกเลี่ยงข้อความยาวเกินไปใน text เดียว ให้แบ่งเป็นหลายบรรทัด
"""

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='travel_manager',
    description="Travel Agent Manager",
    instruction=agent_instruction_prompt,
    tools=[airbnb_mcp_toolset, line_bot_mcp_toolset],
)