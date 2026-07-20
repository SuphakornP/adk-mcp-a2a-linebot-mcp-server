# ADK Agents with Skills

Blog-writing agent ที่ใช้ [ADK SkillToolset](https://adk.dev/skills/) ตามบทความ [Developer’s Guide to Building ADK Agents with Skills](https://developers.googleblog.com/developers-guide-to-building-adk-agents-with-skills/)

สาธิต 4 skill patterns และ progressive disclosure (L1 / L2 / L3)

## Patterns

| Pattern | Skill | วิธีโหลด |
|---------|-------|----------|
| 1. Inline | `seo-checklist` | `models.Skill` ในโค้ด |
| 2. File-based | `blog-writer` | `load_skill_from_dir` + `SKILL.md` |
| 3. External | `content-research-writer` | โหลดจาก directory (รูปแบบ community skill) |
| 4. Meta / factory | `skill-creator` | skill ที่สร้าง `SKILL.md` ใหม่ได้ |

`SkillToolset` สร้าง tools อัตโนมัติ: `list_skills` (L1), `load_skill` (L2), `load_skill_resource` (L3)

## Prerequisites

- Python 3.11+
- [Google API key](https://aistudio.google.com/apikey)

## Quick Start

รันจาก root ของ repository นี้:

```bash
source .venv/bin/activate
pip install -r requirements.txt
adk web 8_agent_with_skill
```

Agent โหลด `GEMINI_API_KEY` และ `MODEL_ID` จาก `.env` ที่ root โดยตรง
จากนั้นเลือก `blog_skills_agent` ใน ADK Web

ตัวอย่าง prompt ภาษาไทยอยู่ที่ [README หลัก](../README.md#example-prompts)

## โครงสร้างโปรเจกต์

```
8_agent_with_skill/
├── blog_skills_agent/
│   ├── agent.py              # Root agent + SkillToolset
│   └── skills/
│       ├── blog-writer/
│       │   ├── SKILL.md
│       │   └── references/style-guide.md
│       └── content-research-writer/
│           ├── SKILL.md
│           └── references/seo-guidelines.md
└── README.md
```
