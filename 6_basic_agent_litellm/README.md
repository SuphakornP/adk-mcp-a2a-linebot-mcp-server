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
- **ADK Agent (Completion API)**: ใช้ `google.adk.models.lite_llm.LiteLlm` เพื่อเชื่อมต่อกับ OpenAI models
- **GPT-5 Parameters**: รองรับ `reasoning_effort` และ `verbosity` สำหรับ GPT-5 models
- **Responses API (Direct)**: ใช้ `litellm.responses()` โดยตรงสำหรับ Reusable Prompts

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
OPENAI_MODEL_ID=gpt-5-mini-2025-08-07  # or gpt-5.1-2025-11-13, gpt-4.1-2025-04-14
```

---

## ⚙️ LiteLlm Configuration Parameters

`LiteLlm` accepts `**kwargs` which are passed to `litellm.acompletion()`.

### Standard Parameters (All Models)

| Parameter | Type | Description |
|-----------|------|-------------|
| `temperature` | float | Sampling temperature (0-2). **Note**: GPT-5 series uses fixed 1.0 |
| `max_tokens` | int | Maximum tokens in response |
| `max_completion_tokens` | int | Upper bound for completion tokens |
| `top_p` | float | Nucleus sampling parameter |
| `presence_penalty` | float | Penalize based on token presence (-2.0 to 2.0) |
| `frequency_penalty` | float | Penalize based on token frequency (-2.0 to 2.0) |
| `stop` | str/list | Stop sequences |
| `seed` | int | Random seed for reproducibility |
| `logit_bias` | dict | Modify token probabilities |
| `user` | str | User identifier for tracking |
| `response_format` | dict | Response format specification |
| `logprobs` | bool | Return log probabilities |
| `top_logprobs` | int | Number of top logprobs to return |
| `extra_headers` | dict | Additional HTTP headers |
| `api_base` | str | Custom API base URL |
| `api_key` | str | API key override |

### GPT-5 / Reasoning Model Parameters

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `reasoning_effort` | str | `"none"`, `"minimal"`, `"low"`, `"medium"`, `"high"`, `"default"` | Controls reasoning depth for o1, o3, gpt-5 series |
| `verbosity` | str | `"low"`, `"medium"`, `"high"` | Controls response length for GPT-5 models |

### Example Configuration

```python
from google.adk.models.lite_llm import LiteLlm

# Basic configuration
model = LiteLlm(
    model="openai/gpt-4o",
    temperature=0.7,
    max_tokens=1000,
)

# GPT-5 with reasoning and verbosity
model = LiteLlm(
    model="openai/gpt-5-mini-2025-08-07",
    max_tokens=1000,
    reasoning_effort="low",   # Controls reasoning depth
    verbosity="medium",       # Controls response length
)
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

### 1. ADK Agent with LiteLLM + GPT-5
```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# Create model with GPT-5 parameters
model = LiteLlm(
    model="openai/gpt-5-mini-2025-08-07",
    max_tokens=1000,
    reasoning_effort="low",
    verbosity="medium",
)

agent = Agent(
    name="my_agent",
    model=model,
    description="My agent powered by GPT-5",
    instruction="You are a helpful assistant.",
    tools=[my_tool],
)
```

### 2. Reusable Prompts (via Responses API)
```python
from litellm import responses as litellm_responses

# Use a stored prompt template from OpenAI
response = litellm_responses(
    model="openai/gpt-5-mini-2025-08-07",
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

## 📊 Feature Support

| Feature | GPT-4 Series | GPT-5 Series |
|---------|--------------|--------------|
| `temperature` | ✅ Configurable | ❌ Fixed at 1.0 |
| `max_tokens` | ✅ | ✅ |
| `reasoning_effort` | ❌ | ✅ |
| `verbosity` | ❌ | ✅ |
| Tool calling | ✅ | ✅ |
| Streaming | ✅ | ✅ |

---

## 📚 References
- [LiteLLM + Google ADK Tutorial](https://docs.litellm.ai/docs/tutorials/google_adk)
- [OpenAI Responses API](https://docs.litellm.ai/docs/providers/openai/responses_api)
- [Google ADK Documentation](https://github.com/google-deepmind/agent-development-kit)