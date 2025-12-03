<!--
  SYNC IMPACT REPORT
  ==================
  Version change: N/A → 1.0.0 (Initial constitution)
  Modified principles: N/A (Initial creation)
  Added sections:
    - Core Principles (5 principles)
    - Technology Stack
    - Development Workflow
    - Governance
  Removed sections: N/A
  Templates requiring updates:
    - ✅ plan-template.md (Constitution Check section compatible)
    - ✅ spec-template.md (User stories and requirements aligned)
    - ✅ tasks-template.md (Phase structure compatible)
  Follow-up TODOs: None
-->

# ADK-MCP-A2A-LineBot Constitution

## Core Principles

### I. Agent-First Architecture

Every feature MUST be designed as an autonomous Agent with clear boundaries:
- Agents MUST have a defined **model**, **goal**, **instruction**, and **tools**
- Instruction prompts are the core control mechanism - they define agent behavior, tool selection, and scope
- Each agent folder MUST be self-contained and independently runnable via `adk web`
- Agent configurations MUST be externalized via environment variables (`.env`)

**Rationale**: ADK agents are the fundamental building blocks. Clear separation enables independent testing, deployment, and composition into multi-agent systems.

### II. MCP Tools Integration

Agents MUST integrate external capabilities through the Model Context Protocol (MCP):
- All external tool integrations MUST use MCP-compliant interfaces
- Tool configurations (API keys, secrets) MUST be stored in environment variables, never hardcoded
- Each MCP tool integration MUST be documented with required credentials and usage examples
- Prefer existing MCP tools (Pinecone, LINE Bot, Airbnb) over custom implementations

**Rationale**: MCP provides a standardized way to extend agent capabilities while maintaining security and reusability across different agent implementations.

### III. Modular Examples Structure

The project MUST maintain a progressive learning structure:
- Each numbered folder (`1_basic_agent`, `2_agent_with_mcp_tools`, etc.) represents an incremental complexity level
- Examples MUST build upon previous concepts without breaking backward compatibility
- Each example folder MUST include its own `README.md` explaining the concept demonstrated
- New examples MUST follow the naming convention: `N_descriptive_name/`

**Rationale**: This project serves as educational material. Progressive complexity helps developers learn ADK concepts step-by-step.

### IV. Multi-Language Support

The project MUST support Thai and English documentation:
- Code comments and variable names MUST be in English
- README files and user-facing documentation MAY include Thai explanations
- Error messages and logs MUST be in English for debugging consistency
- Instruction prompts for agents MAY be in Thai when targeting Thai users

**Rationale**: The project targets Thai developers while maintaining international code standards.

### V. Simplicity & YAGNI

Start simple, add complexity only when justified:
- Prefer built-in ADK features over custom implementations
- Each agent SHOULD have a single, well-defined purpose
- Avoid premature abstraction - duplicate code is acceptable for clarity in examples
- Configuration MUST use simple `.env` files, not complex configuration management

**Rationale**: As an educational project, clarity and simplicity take precedence over DRY principles.

## Technology Stack

**Core Framework**: Google Agent Development Kit (ADK)
**Language**: Python 3.11+
**LLM Providers**: OpenAI, Anthropic Claude (via Bedrock), Google Gemini
**Vector Database**: Pinecone (with integrated embeddings)
**Messaging**: LINE Bot API (via MCP)
**Testing**: `adk web` Agent Simulator for interactive testing
**Dependencies**: Managed via `requirements.txt`

**Constraints**:
- All LLM API keys MUST be configured via environment variables
- Pinecone MUST use serverless indexes with integrated embedding models
- LINE Bot integration requires Channel Secret and Access Token

## Development Workflow

### Adding New Examples

1. Create a new numbered folder following the convention
2. Include `__init__.py`, `agent.py`, and `README.md`
3. Update root `README.md` with the new example description
4. Ensure the example runs independently with `adk web`

### Environment Configuration

1. Copy `.env.example` to `.env`
2. Fill in required API keys and credentials
3. Never commit `.env` files to version control

### Testing Agents

1. Use `adk web <module>:agent` for interactive testing
2. Verify agent responds correctly to expected inputs
3. Test edge cases and error handling
4. Document any required setup in the example's README

## Governance

This constitution supersedes all other development practices for this project:
- All new features MUST comply with these principles
- Amendments require updating this document with version increment
- Complexity beyond these guidelines MUST be justified in the implementation plan
- Use `.specify/` templates for structured feature development

**Version**: 1.0.0 | **Ratified**: 2025-12-03 | **Last Amended**: 2025-12-03
