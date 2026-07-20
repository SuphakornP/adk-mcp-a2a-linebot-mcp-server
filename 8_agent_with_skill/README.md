# ADK Skills PoC

PoC นี้รวมตัวอย่าง ADK Skills ทั้งหมดจาก
[`punsiriboo/adk-skills`](https://github.com/punsiriboo/adk-skills) ไว้ในโฟลเดอร์เดียว
โดยอ้างอิง source revision `31ea9299f6556c53779144e18a0c617f372fafa1`
(2026-07-19)

คู่มือทดสอบแบบละเอียดพร้อม architecture, expected tool flow, observability และ
troubleshooting อยู่ที่ [`TESTING_GUIDE.md`](TESTING_GUIDE.md)

## Agents

| Agent | สิ่งที่สาธิต |
|---|---|
| `blog_skills_agent` | Inline, file-based, external และ meta/factory skills |
| `marathon_planner_agent` | Dynamic skill loading, skill scripts/assets, Maps MCP และ artifact map |

`SkillToolset` ใช้ progressive disclosure 3 ระดับ:

1. `list_skills` แสดง metadata ของ skills ที่มี
2. `load_skill` โหลด instructions เมื่อต้องใช้งาน
3. `load_skill_resource` โหลด references, assets หรือ scripts ที่เกี่ยวข้อง

## Project Structure

```text
8_agent_with_skill/
├── blog_skills_agent/
│   ├── agent.py
│   └── skills/
│       ├── blog-writer/
│       └── content-research-writer/
├── marathon_planner_agent/
│   ├── agent.py
│   ├── prompts.py
│   ├── tools.py
│   └── skills/
│       ├── gis-spatial-engineering/
│       ├── mapping/
│       └── race-director/
├── TESTING_GUIDE.md
└── README.md
```

ทั้งสอง agents โหลด configuration จาก `.env` ที่ root ของ repository โดยตรง
และไม่มี `.env` แยกอยู่ในโฟลเดอร์นี้

## Setup

รันจาก root ของ repository:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Blog Skills Agent ใช้ `GEMINI_API_KEY` และ `MODEL_ID` ที่มีอยู่แล้วใน root `.env`

Marathon Planner Agent ต้องเพิ่มค่าต่อไปนี้ใน root `.env` โดยดูชื่อและตัวอย่างค่าได้จาก
root `.env.example`:

- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
- `GOOGLE_MAPS_API_KEY`

ถ้ายังไม่ตั้งค่า Google Cloud หรือ Maps ตัว Marathon Planner ยัง import ได้ แต่ Maps MCP
จะถูกปิดไว้จนกว่าจะตั้งค่าครบ

## Run

เปิด agents directory ด้วย ADK Web:

```bash
adk web 8_agent_with_skill
```

เปิด `http://127.0.0.1:8000` แล้วเลือก agent ที่ต้องการ

หรือรันแยกใน terminal:

```bash
adk run 8_agent_with_skill/blog_skills_agent
adk run 8_agent_with_skill/marathon_planner_agent
```

## Example Prompts

### Blog Skills Agent

```text
ช่วยรีวิว SEO ให้บทความชื่อ "เริ่มต้นกับ BigQuery AI"
```

```text
ใช้ content research skill ช่วยวางโครงบทความเรื่อง BigQuery AI
```

```text
ช่วยสร้าง SKILL.md สำหรับรีวิวความปลอดภัยของโค้ด Python
```

### Marathon Planner Agent

```text
ช่วยวางแผน Run club 100 คน ระยะ 10 กม. จากสวนลุมพินีไปสะพานเขียว
```

```text
ออกแบบเส้นทางวิ่งรูปหัวใจภายในสวนลุมพินี ระยะ 10 กม.
```

## Upstream Notes

- Blog Skills patterns มาจาก `blog_skills_agent` ใน upstream repository
- Marathon Planner คง source, skill definitions, references, scripts และ GeoJSON assets
  จาก `marathon_planner_agent` ไว้ครบ
- การปรับเฉพาะ repository นี้คือใช้ `MODEL_ID` และโหลด `.env` จาก root
- Source ฝั่ง Marathon Planner ที่มี Apache 2.0 header ยังคง attribution เดิมไว้
