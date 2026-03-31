import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

load_dotenv()

OPENAI_MODEL_ID = os.getenv("OPENAI_MODEL_ID", "gpt-5.4-mini")

# =============================================================================
# LiteLLM Model Configuration - OpenAI Responses API
#
# Using "openai/responses/<model>" prefix to route through LiteLLM's
# OpenAI Responses API integration instead of the Chat Completions API.
#
# LiteLlm accepts **kwargs which are ALL passed through to litellm.acompletion().
# Below are all configurable parameters for the Responses API.
# =============================================================================
gpt_model = LiteLlm(
    model=f"openai/responses/{OPENAI_MODEL_ID}",

    # -------------------------------------------------------------------------
    # Output Length Control
    # -------------------------------------------------------------------------
    max_tokens=1000,                    # Max output tokens for the response

    # -------------------------------------------------------------------------
    # Verbosity (GPT-5 series / Responses API)
    # Controls response length: "low" = concise, "medium" = balanced, "high" = detailed
    # Can be passed as top-level kwarg OR nested inside `text` dict
    # -------------------------------------------------------------------------
    # verbosity="medium",               # Top-level shorthand (Chat Completions style)
    text={"verbosity": "medium"},       # Responses API native format

    # -------------------------------------------------------------------------
    # Reasoning Effort (GPT-5 / o1 / o3 reasoning models)
    # Controls how much "thinking" the model does before responding
    # Values: "none" | "low" | "medium" | "high"
    # Can include summary: {"effort": "high", "summary": "auto"|"concise"|"detailed"}
    # Note: summary requires OpenAI organization verification
    # -------------------------------------------------------------------------
    reasoning_effort="low",             # Simple string format
    # reasoning={                        # Responses API native format (dict)
    #     "effort": "high",
    #     "summary": "auto",            # Requires org verification
    # },

    # -------------------------------------------------------------------------
    # Sampling / Creativity Parameters
    # -------------------------------------------------------------------------
    # temperature=1.0,                  # 0-2, randomness (GPT-5 series fixed at 1.0)
    # top_p=1.0,                        # 0-1, nucleus sampling (alternative to temperature)
    # seed=42,                          # Integer, for reproducible outputs

    # -------------------------------------------------------------------------
    # Repetition Penalty
    # -------------------------------------------------------------------------
    # presence_penalty=0.0,             # -2 to 2, penalize new topics already mentioned
    # frequency_penalty=0.0,            # -2 to 2, penalize tokens by existing frequency

    # -------------------------------------------------------------------------
    # Stop Sequences
    # -------------------------------------------------------------------------
    # stop=["END", "DONE"],             # List of strings to stop generation

    # -------------------------------------------------------------------------
    # Web Search (OpenAI built-in tool)
    # Enables real-time web search during generation
    # -------------------------------------------------------------------------
    # web_search_options={
    #     "search_context_size": "medium",  # "low" | "medium" (default) | "high"
    # },

    # -------------------------------------------------------------------------
    # LiteLLM Behavior
    # -------------------------------------------------------------------------
    # drop_params=True,                 # Silently drop unsupported params instead of error
    # api_base="https://...",           # Custom API endpoint
    # api_key="sk-...",                 # Override API key (prefer env var OPENAI_API_KEY)
)

# ทำสร้าง Function เพื่อให้ AI นำไปเรียกใช้งาน
def find_menu_items(description: str):
    """ค้นหารายการอาหารจากคำอธิบาย เช่น ประเภทอาหาร ชื่อเมนู วัตถุดิบ หรือสไตล์

    Args:
        description: คำอธิบายประเภทอาหาร เช่น อาหารญี่ปุ่น เผ็ด ไม่ใส่เนื้อ หรือชื่อเมนู
    """
    return ["ราเมนหมูชาชู", "ข้าวหน้าปลาแซลมอน", "ซูชิปลาทูน่า"]


def get_reservation_slots(date: str):
    """ดูเวลาที่สามารถจองโต๊ะได้ในร้านนั้น

    Args:
        date: วันที่ต้องการจอง (รูปแบบ MM-DD)
    """
    return ["17:00", "18:30", "20:00"]

def add_to_cart(menu: str):
    """เพิ่มเมนูอาหารลงในรายการสั่ง
    Args:
        menu: รายการอาหาร
    """
    return "OK"


root_agent = Agent(
    name="neko_restaurant_agent",
    model=gpt_model,
    description="Neko restaurant agent powered by OpenAI Responses API via LiteLLM",
    instruction="""
    คุณคือผู้ช่วยร้านอาหารชื่อ 'เนโกะ' 🐱
    คุณพูดจาน่ารัก สุภาพ ใช้คำลงท้ายว่า 'เมี๊ยว~'
    หน้าที่ของคุณคือช่วยลูกค้าร้านหาร
    เมื่อลูกค้าถามถึงเมนู ให้ดููข้อมูลจากระบบเพื่อตอบ ถ้าไม่รู้ ให้ตอบอย่างสุภาพว่าไม่รู้
    เมื่อลูกค้าต้องการของคิว เช็กคิวว่างจากระบบเพื่อจองโต๊ะให้ลูกค้า ถ้าไม่รู้ว่ามีคิวว่าเวลาไหนบ้าง ให้ตอบอย่างสุภาพว่าไม่รู้
    """,
    tools=[find_menu_items, get_reservation_slots, add_to_cart],
)
