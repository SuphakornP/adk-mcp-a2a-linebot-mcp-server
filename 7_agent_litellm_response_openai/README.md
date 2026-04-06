# 🐱 Neko Restaurant Agent — OpenAI Responses API

**Neko Restaurant Agent** คือ AI Agent ที่สร้างขึ้นด้วย [Google Agent Development Kit (ADK)](https://github.com/google-deepmind/agent-development-kit)  
ใช้ **OpenAI Responses API** ผ่าน LiteLLM โดยใช้โมเดล **gpt-5.4-mini** (latest)

---

## ✨ Features
- **ค้นหาเมนูอาหาร**: แนะนำเมนูจากคำอธิบาย เช่น "อาหารญี่ปุ่น", "ไม่ใส่เนื้อ", "ซูชิ"
- **เช็กเวลาจองโต๊ะ**: แสดงเวลาที่สามารถจองโต๊ะได้ในวันที่เลือก
- **เพิ่มอาหารลงตะกร้า**: จัดการตะกร้าสั่งอาหารของลูกค้า
- **ภาษาตอบกลับ**: พูดจาน่ารัก ใช้คำลงท้าย "เมี๊ยว~"
- **Safety guardrails**: บล็อกคำขอนอกขอบเขต คำสั่ง jailbreak การขอข้อมูลลับ คำสั่งระบบ และธุรกรรมการเงินก่อนถึงโมเดล
- **OpenAI Responses API**: ใช้ `openai/responses/gpt-5.4-mini` ผ่าน LiteLLM

---

## 📦 Requirements
- Python 3.10+
- ติดตั้ง Google ADK + LiteLLM
```bash
pip install google-adk litellm python-dotenv
```

## 🔑 Environment Variables
สร้างไฟล์ `.env` ที่ root ของโปรเจกต์:
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL_ID=gpt-5.4-mini   # optional, defaults to gpt-5.4-mini
```

## 🚀 Run
```bash
adk web 7_agent_litellm_response_openai
```

## ⚙️ Available Configuration Parameters

| Parameter | Values | Description |
|---|---|---|
| `max_tokens` | integer | จำกัดจำนวน output tokens |
| `text` | `{"verbosity": "low"\|"medium"\|"high"}` | ควบคุมความยาวคำตอบ (Responses API native) |
| `verbosity` | `"low"` \| `"medium"` \| `"high"` | ควบคุมความยาวคำตอบ (Chat Completions shorthand) |
| `reasoning_effort` | `"none"` \| `"low"` \| `"medium"` \| `"high"` | ควบคุมความลึกของการคิด (GPT-5/o-series) |
| `reasoning` | `{"effort": "high", "summary": "auto"}` | Reasoning config แบบ dict (Responses API native) |
| `temperature` | 0-2 | ความสุ่ม (GPT-5 series อาจล็อกที่ 1.0) |
| `top_p` | 0-1 | Nucleus sampling |
| `seed` | integer | สำหรับผลลัพธ์ที่ทำซ้ำได้ |
| `presence_penalty` | -2 ถึง 2 | ลดการพูดซ้ำหัวข้อเดิม |
| `frequency_penalty` | -2 ถึง 2 | ลดการใช้คำซ้ำ |
| `stop` | list of strings | หยุดสร้างข้อความเมื่อเจอคำที่กำหนด |
| `web_search_options` | `{"search_context_size": "medium"}` | เปิด web search ขณะสร้างคำตอบ |
| `drop_params` | `True` / `False` | ให้ LiteLLM ข้ามพารามิเตอร์ที่ไม่รองรับแทนที่จะ error |

> **Note:** `reasoning.summary` ต้องการ OpenAI organization verification

## 📝 Notes
- ใช้ LiteLLM model prefix `openai/responses/<model>` เพื่อเรียก OpenAI Responses API แทน Chat Completions API
- Responses API รองรับ features เพิ่มเติม เช่น verbosity, reusable prompts, web search
- `LiteLlm(**kwargs)` ส่ง kwargs ทั้งหมดตรงไปยัง `litellm.acompletion()` — สามารถใช้พารามิเตอร์ใดก็ได้ที่ LiteLLM รองรับ
- ใช้ Google ADK `before_agent_callback` เพื่อปฏิเสธคำขอนอกขอบเขตหรือไม่ปลอดภัยตั้งแต่ต้นทาง
- ใช้ Google ADK `before_tool_callback` เป็น defense in depth เพื่อ allowlist เฉพาะ tools ของร้านอาหารและบล็อก input ที่น่าสงสัย

## 🛡️ Guardrail Scope
- อนุญาตเฉพาะคำขอเกี่ยวกับเมนูอาหาร การแนะนำอาหาร การจองโต๊ะ และการสั่งอาหารของร้านเนโกะ
- ปฏิเสธคำขอที่พยายามให้ละเลยคำสั่ง เปิดเผย prompt หรือข้อมูลลับ รันคำสั่งระบบ หรือดึงข้อมูลส่วนตัว
- ปฏิเสธคำขอซื้อของ จ่ายเงิน โอนเงิน หรือธุรกรรมการเงินอื่นที่ agent นี้ไม่มีสิทธิ์ทำ
- หากคำขอไม่อยู่ในขอบเขต Agent จะปฏิเสธอย่างสุภาพแทนการส่งต่อให้โมเดลตอบเอง
