# 🐱 Neko Restaurant Agent with LiteLLM + OpenAI

**Neko Restaurant Agent** คือ AI Agent ที่สร้างขึ้นด้วย [Google Agent Development Kit (ADK)](https://github.com/google-deepmind/agent-development-kit) ร่วมกับ [LiteLLM](https://docs.litellm.ai/) เพื่อใช้งาน **OpenAI GPT models** แทน Gemini

Agent นี้ช่วยจัดการบริการร้านอาหาร เช่น แนะนำเมนูอาหาร, เช็กเวลาที่สามารถจองโต๊ะได้, และเพิ่มรายการอาหารลงในตะกร้า  
Agent ถูกออกแบบให้พูดจาน่ารัก สุภาพ และลงท้ายด้วยคำว่า **"เมี๊ยว~"**

---

## ✨ Features

### Core Features
- **ค้นหาเมนูอาหาร**: แนะนำเมนูจากคำอธิบาย เช่น "อาหารญี่ปุ่น", "ไม่ใส่เนื้อ", "ซูชิ"
- **เช็กเวลาจองโต๊ะ**: แสดงเวลาที่สามารถจองโต๊ะได้ในวันที่เลือก
- **เพิ่มอาหารลงตะกร้า**: จัดการตะกร้าสั่งอาหารของลูกค้า
- **ภาษาตอบกลับ**: พูดจาน่ารัก ใช้คำลงท้าย "เมี๊ยว~"

### LiteLLM + OpenAI Features
- **ADK Agent (Completion API)**: ใช้ `google.adk.models.lite_llm.LiteLlm` เพื่อเชื่อมต่อกับ OpenAI models ผ่าน Completion API
- **Responses API (Direct)**: ใช้ `litellm.responses()` โดยตรงสำหรับ features พิเศษ:
  - **Verbosity Parameter**: ควบคุมความยาวของ response ด้วย `low`, `medium`, `high`
  - **Reusable Prompts**: รองรับ stored prompt templates จาก OpenAI

> **Note**: Google ADK's `LiteLlm` wrapper ใช้ Completion API ภายใน ไม่ใช่ Responses API  
> สำหรับ Verbosity และ Reusable Prompts ต้องเรียก `litellm.responses()` โดยตรง

---

## 📦 Requirements
- Python 3.10+
- ติดตั้ง Google ADK และ LiteLLM
```bash
pip install google-adk litellm python-dotenv
```

---

## 🔧 Environment Variables

ตั้งค่าใน `.env` file:
```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL_ID=gpt-4.1-2025-04-14  # or gpt-5.1-2025-11-13
```

---

## 🚀 Usage

### Run with ADK Web UI (Completion API)
```bash
adk web 6_basic_agent_litellm
```

### Run Responses API Demo (Verbosity + Reusable Prompts)
```bash
python 6_basic_agent_litellm/agent.py
```

---

## 📖 Code Examples

### 1. ADK Agent with LiteLLM (Completion API)
```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# Create agent with OpenAI model via LiteLLM (uses Completion API internally)
model = LiteLlm(model="openai/gpt-4.1-2025-04-14")

agent = Agent(
    name="my_agent",
    model=model,
    description="My agent powered by OpenAI",
    instruction="You are a helpful assistant.",
    tools=[my_tool],
)
```

### 2. Direct Responses API with Verbosity Parameter
```python
from litellm import responses as litellm_responses

# Control response length with verbosity
response = litellm_responses(
    model="openai/gpt-4.1-2025-04-14",
    input="What is AI?",
    text={"verbosity": "low"}  # Options: "low", "medium", "high"
)

# Extract text from response
for item in response.output:
    if hasattr(item, "content"):
        for content in item.content:
            if hasattr(content, "text"):
                print(content.text)
```

### 3. Reusable Prompts (Stored Templates via Responses API)
```python
from litellm import responses as litellm_responses

# Use a stored prompt template from OpenAI
response = litellm_responses(
    model="openai/gpt-4.1-2025-04-14",
    prompt={
        "id": "pmpt_abc123",  # Your stored prompt ID
        "variables": {
            "customer_name": "John",
            "product": "Ramen"
        }
    },
    text={"verbosity": "medium"}
)
```

---

## 📊 API Comparison

| Feature                | ADK LiteLlm (Completion) | litellm.responses() |
|------------------------|--------------------------|---------------------|
| Tool calling           | Yes (via ADK)            | Yes                 |
| Verbosity parameter    | No                       | Yes                 |
| Reusable prompts       | No                       | Yes                 |
| Streaming              | Yes                      | Yes                 |
| ADK Web UI compatible  | Yes                      | No (direct call)    |

---

## 📚 References
- [LiteLLM + Google ADK Tutorial](https://docs.litellm.ai/docs/tutorials/google_adk)
- [OpenAI Responses API](https://docs.litellm.ai/docs/providers/openai/responses_api)
- [Google ADK Documentation](https://github.com/google-deepmind/agent-development-kit)