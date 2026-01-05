import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import litellm
from litellm import responses as litellm_responses

# LangSmith - Observability and Tracing for Google ADK
from langsmith.integrations.otel import configure as configure_langsmith

load_dotenv()

# =============================================================================
# LangSmith Configuration
# Configure tracing before any ADK agent calls
# Requires: LANGSMITH_API_KEY and LANGSMITH_PROJECT in .env
# =============================================================================
#configure_langsmith()

# =============================================================================
# Configuration
# =============================================================================
OPENAI_MODEL_ID = os.getenv("OPENAI_MODEL_ID", "gpt-5-mini-2025-08-07")
CLAUDE_MODEL_ID = os.getenv("CLAUDE_MODEL_ID", "global.anthropic.claude-sonnet-4-20250514-v1:0")

# Set AWS credentials for LiteLLM Bedrock
# LiteLLM expects these specific environment variable names
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("BEDROCK_ACCESS_KEY_ID", "")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("BEDROCK_SECRET_ACCESS_KEY", "")
os.environ["AWS_REGION_NAME"] = os.getenv("AWS_REGION_NAME", "us-west-2")

# =============================================================================
# LiteLLM Model Configuration
# 
# LiteLlm accepts **kwargs which are passed to litellm.acompletion().
# 
# Supported parameters include:
#   - temperature, max_tokens, top_p, presence_penalty, frequency_penalty
#   - stop, seed, logit_bias, user, response_format
#   - reasoning_effort: "none" | "minimal" | "low" | "medium" | "high" | "default"
#   - verbosity: "low" | "medium" | "high" (GPT-5 models only)
#   - extra_headers, api_base, api_key
#
# NOTE: reasoning_effort works with reasoning models (o1, o3, gpt-5 series)
#       verbosity works with GPT-5 models via Chat Completions API
# =============================================================================
gpt_model = LiteLlm(
    model=f"openai/{OPENAI_MODEL_ID}",
    # Standard completion parameters
    # temperature=1.0, # 1.0 is the default value can't be changed when using gpt 5 series
    max_tokens=1000,
    # GPT-5 / Reasoning model parameters (uncomment if using supported model)
    reasoning_effort="low",  # For o1, o3, gpt-5 reasoning models
    verbosity="medium",      # For gpt-5 models
    # OpenAI Web Search Tool - enables real-time web search
    # Requires search-enabled model (e.g., gpt-4o-search-preview) or gpt-4o with tools
    web_search_options={
        "search_context_size": "medium"  # Options: "low", "medium" (default), "high"
    }
)

# Claude Model
claude_model = LiteLlm(
    model=f"bedrock/{CLAUDE_MODEL_ID}",
    max_tokens=1000
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


# =============================================================================
# Reusable Prompt Template
# This prompt can be stored and reused across multiple requests
# =============================================================================
NEKO_RESTAURANT_PROMPT = """
คุณคือผู้ช่วยร้านอาหารชื่อ 'เนโกะ' 🐱
คุณพูดจาน่ารัก สุภาพ ใช้คำลงท้ายว่า 'เมี๊ยว~'
หน้าที่ของคุณคือช่วยลูกค้าร้านหาร
เมื่อลูกค้าถามถึงเมนู ให้ดููข้อมูลจากระบบเพื่อตอบ ถ้าไม่รู้ ให้ตอบอย่างสุภาพว่าไม่รู้
เมื่อลูกค้าต้องการของคิว เช็กคิวว่างจากระบบเพื่อจองโต๊ะให้ลูกค้า ถ้าไม่รู้ว่ามีคิวว่าเวลาไหนบ้าง ให้ตอบอย่างสุภาพว่าไม่รู้
"""

# =============================================================================
# Google ADK Agent with LiteLLM + OpenAI
# 
# The LiteLlm wrapper passes **kwargs to the underlying LiteLLM completion call.
# Verbosity and reasoning parameters are included via the model configuration above.
# =============================================================================
root_agent = Agent(
    name="neko_restaurant_agent",
    model=gpt_model, #gpt_model, claude_model
    description="Neko restaurant agent powered by OpenAI via LiteLLM",
    instruction=NEKO_RESTAURANT_PROMPT,
    tools=[find_menu_items, get_reservation_slots, add_to_cart],
)


# =============================================================================
# Alternative: Create agents with different verbosity levels
# =============================================================================
def create_agent_with_verbosity(verbosity: str = "medium", reasoning_effort: str = None):
    """
    Factory function to create an agent with specific verbosity and reasoning settings.
    
    Args:
        verbosity: "low" | "medium" | "high" - controls response length
        reasoning_effort: "minimal" | "low" | "medium" | "high" - for o-series models
    
    Returns:
        Agent configured with the specified settings
    """
    kwargs = {
        "text": {"verbosity": verbosity},
    }
    if reasoning_effort:
        kwargs["reasoning"] = {"effort": reasoning_effort}
    
    llm = LiteLlm(
        model=f"openai/{OPENAI_MODEL_ID}",
        **kwargs
    )
    
    return Agent(
        name=f"neko_agent_{verbosity}",
        model=llm,
        description=f"Neko restaurant agent (verbosity={verbosity})",
        instruction=NEKO_RESTAURANT_PROMPT,
        tools=[find_menu_items, get_reservation_slots, add_to_cart],
    )


# Pre-configured agents with different verbosity levels
agent_low_verbosity = create_agent_with_verbosity("low")
agent_medium_verbosity = create_agent_with_verbosity("medium")
agent_high_verbosity = create_agent_with_verbosity("high")


# =============================================================================
# OpenAI Responses API - Direct Usage
# These functions use litellm.responses() directly for Responses API features
# that are NOT available through ADK's LiteLlm wrapper
# =============================================================================

def call_responses_api(
    input_text: str,
    system_prompt: str = None,
    verbosity: str = "medium",
):
    """
    Call OpenAI Responses API with verbosity parameter.
    
    This is a direct call to the Responses API, bypassing ADK's completion-based flow.
    Use this when you need Responses API specific features like verbosity control.
    
    Args:
        input_text: The user's input/question
        system_prompt: Optional system prompt (uses NEKO_RESTAURANT_PROMPT if None)
        verbosity: Response verbosity level - "low", "medium", or "high"
                   - low: concise, brief responses
                   - medium: balanced responses (default)
                   - high: detailed, comprehensive responses
    
    Returns:
        The response from the model
    """
    if verbosity not in ["low", "medium", "high"]:
        raise ValueError("verbosity must be 'low', 'medium', or 'high'")
    
    # Build input with system prompt if provided
    full_input = input_text
    if system_prompt:
        full_input = f"{system_prompt}\n\nUser: {input_text}"
    
    response = litellm_responses(
        model=f"openai/{OPENAI_MODEL_ID}",
        input=full_input,
        text={"verbosity": verbosity}
    )
    return response


def call_responses_api_with_reusable_prompt(
    prompt_id: str,
    variables: dict,
    verbosity: str = "medium",
):
    """
    Call OpenAI Responses API with reusable prompts (stored templates).
    
    Reusable prompts allow you to store prompt templates in OpenAI and reference
    them by ID. This is useful for:
    - Version control of prompts
    - Centralized prompt management
    - A/B testing different prompt versions
    
    Note: You need to create the prompt template first via OpenAI API.
    
    Args:
        prompt_id: The ID of the stored prompt template (e.g., "pmpt_abc123")
        variables: Dictionary of variables to substitute in the prompt
        verbosity: Response verbosity level - "low", "medium", or "high"
    
    Returns:
        The response from the model
    """
    if verbosity not in ["low", "medium", "high"]:
        raise ValueError("verbosity must be 'low', 'medium', or 'high'")
    
    response = litellm_responses(
        model=f"openai/{OPENAI_MODEL_ID}",
        prompt={
            "id": prompt_id,
            "variables": variables,
        },
        text={"verbosity": verbosity}
    )
    return response


def extract_response_text(response) -> str:
    """
    Extract text content from OpenAI Responses API response.
    
    Args:
        response: The response object from litellm.responses()
    
    Returns:
        The extracted text content
    """
    output_text = ""
    for item in response.output:
        if hasattr(item, "content"):
            for content in item.content:
                if hasattr(content, "text"):
                    output_text += content.text
    return output_text


# =============================================================================
# Example usage when running directly
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("LiteLLM + Google ADK with OpenAI Responses API Demo")
    print("=" * 70)
    print(f"\nModel: openai/{OPENAI_MODEL_ID}")
    print(f"Agent: {root_agent.name}")
    print(f"Description: {root_agent.description}")
    
    # ==========================================================================
    # Demo 1: Verbosity Parameter with Responses API
    # ==========================================================================
    print("\n" + "=" * 70)
    print("DEMO 1: Verbosity Parameter (OpenAI Responses API)")
    print("=" * 70)
    print("\nThe verbosity parameter controls response length:")
    print("  - low: concise, brief responses")
    print("  - medium: balanced responses")
    print("  - high: detailed, comprehensive responses")
    
    test_question = "What is a restaurant?"
    
    for verbosity_level in ["low", "medium", "high"]:
        print(f"\n--- Verbosity: {verbosity_level.upper()} ---")
        try:
            response = call_responses_api(
                input_text=test_question,
                verbosity=verbosity_level
            )
            output_text = extract_response_text(response)
            # Show truncated response
            display_text = output_text[:300] + "..." if len(output_text) > 300 else output_text
            print(f"Response: {display_text}")
            if hasattr(response, "usage"):
                print(f"Output tokens: {response.usage.output_tokens}")
        except Exception as e:
            print(f"Error: {e}")
    
    # ==========================================================================
    # Demo 2: Responses API with System Prompt (Reusable Prompt Pattern)
    # ==========================================================================
    print("\n" + "=" * 70)
    print("DEMO 2: Responses API with Reusable System Prompt")
    print("=" * 70)
    print("\nUsing NEKO_RESTAURANT_PROMPT as a reusable system prompt:")
    
    try:
        response = call_responses_api(
            input_text="มีเมนูอะไรแนะนำบ้างคะ?",
            system_prompt=NEKO_RESTAURANT_PROMPT,
            verbosity="medium"
        )
        output_text = extract_response_text(response)
        print(f"\nResponse:\n{output_text}")
        if hasattr(response, "usage"):
            print(f"\nOutput tokens: {response.usage.output_tokens}")
    except Exception as e:
        print(f"Error: {e}")
    
    # ==========================================================================
    # Demo 3: Stored Reusable Prompts (OpenAI Feature)
    # ==========================================================================
    print("\n" + "=" * 70)
    print("DEMO 3: Stored Reusable Prompts (OpenAI Feature)")
    print("=" * 70)
    print("""
OpenAI's Reusable Prompts feature allows you to store prompt templates
and reference them by ID. This is useful for:
  - Version control of prompts
  - Centralized prompt management  
  - A/B testing different prompt versions

To use stored prompts:
1. Create a prompt template via OpenAI API
2. Get the prompt ID (e.g., 'pmpt_abc123')
3. Call with variables:

    response = call_responses_api_with_reusable_prompt(
        prompt_id="pmpt_abc123",
        variables={
            "customer_name": "John",
            "menu_item": "Ramen"
        },
        verbosity="medium"
    )
""")
    
    print("=" * 70)
    print("Summary: API Comparison")
    print("=" * 70)
    print("""
| Feature                | ADK LiteLlm (Completion) | litellm.responses() |
|------------------------|--------------------------|---------------------|
| Tool calling           | Yes (via ADK)            | Yes                 |
| Verbosity parameter    | No                       | Yes                 |
| Reusable prompts       | No                       | Yes                 |
| Streaming              | Yes                      | Yes                 |
| ADK Web UI compatible  | Yes                      | No (direct call)    |
""")