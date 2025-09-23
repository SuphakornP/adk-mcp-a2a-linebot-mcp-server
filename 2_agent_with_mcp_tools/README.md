# Travel Agent Manager with Google ADK + Airbnb MCP Server

โครงการนี้เป็นตัวอย่างการสร้าง **Travel Agent Manager** โดยใช้  
[Google Agent Development Kit (ADK)](https://github.com/google-deepmind/agent-development-kit)  
ร่วมกับ **Airbnb MCP Server** เพื่อให้ AI Agent สามารถค้นหาและแนะนำที่พักได้อัตโนมัติ

---

## 🔎 Overview
- ใช้โมเดล **Gemini 2.0 Flash** เป็น LLM หลัก
- เชื่อมต่อกับ **Airbnb MCP Server** ผ่าน STDIO
- ผู้ใช้สามารถถามเกี่ยวกับการหาที่พัก และ Agent จะช่วย:
  - ค้นหาที่พัก Airbnb
  - ถามรายละเอียดเพิ่มเติม (สถานที่, งบประมาณ, วันที่เข้าพัก, จำนวนผู้เข้าพัก)
  - แนะนำที่พักอย่างสุภาพและชัดเจน
  - ตอบกลับในภาษาที่ผู้ใช้ใช้ (ไทย/อังกฤษ)

---

## 📦 Requirements
- Python 3.10+
- ติดตั้ง [Google ADK](https://github.com/google-deepmind/agent-development-kit)
- ติดตั้ง [Node.js](https://nodejs.org/) + `npx`
- ติดตั้ง [Airbnb MCP Server](https://github.com/openbnb-org/mcp-server-airbnb): @openbnb/mcp-server-airbnb
```
{
  "mcpServers": {
    "airbnb": {
      "command": "npx",
      "args": [
        "-y",
        "@openbnb/mcp-server-airbnb"
      ]
    }
  }
}
```
