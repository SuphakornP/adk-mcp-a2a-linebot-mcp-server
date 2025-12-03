# 🌱 Spec-Kit Guide for Windsurf IDE

A guide to using [GitHub Spec-Kit](https://github.com/github/spec-kit) with Windsurf IDE for Spec-Driven Development.

## 📋 Table of Contents

- [What is Spec-Driven Development?](#what-is-spec-driven-development)
- [Installation](#installation)
- [Initialize Project](#initialize-project)
- [Available Slash Commands](#available-slash-commands)
- [Workflow](#workflow)
- [Examples](#examples)
- [Tips](#tips)

---

## What is Spec-Driven Development?

Spec-Driven Development is a methodology where you:

1. **Define what you want** before how to build it
2. **Create specifications** that guide AI-assisted development
3. **Generate implementation plans** based on specs
4. **Break down into tasks** for systematic execution
5. **Implement with AI assistance** following the plan

---

## Installation

### Prerequisites

- [uv](https://docs.astral.sh/uv/) - Python package installer
- [Windsurf IDE](https://windsurf.com/)

### Install Specify CLI

**Option 1: Persistent Installation (Recommended)**

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

**Option 2: One-time Usage**

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init <PROJECT_NAME>
```

### Upgrade Specify CLI

```bash
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git
```

### Verify Installation

```bash
specify check
```

---

## Initialize Project

### New Project

```bash
specify init my-project --ai windsurf
```

### Existing Project (Current Directory)

```bash
specify init --here --ai windsurf
```

### Force Initialization (Non-empty Directory)

```bash
specify init --here --force --ai windsurf
```

### Additional Options

| Option | Description |
|--------|-------------|
| `--no-git` | Skip git initialization |
| `--debug` | Enable debug output |
| `--github-token <token>` | Use GitHub token for API requests |

---

## Available Slash Commands

After running `specify init`, these slash commands become available in Windsurf chat:

### Core Commands

| Command | Description |
|---------|-------------|
| `/speckit.constitution` | Create project principles and development guidelines |
| `/speckit.specify` | Define what you want to build (focus on "what" and "why") |
| `/speckit.plan` | Create technical implementation plan with tech stack |
| `/speckit.tasks` | Break down plan into actionable tasks |
| `/speckit.implement` | Execute all tasks and build the feature |

### Optional Commands

| Command | Description |
|---------|-------------|
| `/speckit.clarify` | Clarify requirements before planning |
| `/speckit.analyze` | Analyze existing code or specifications |
| `/speckit.checklist` | Generate validation checklist |
| `/quizme` | Test understanding of the specification |

---

## Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Spec-Driven Development                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. /speckit.constitution  ──►  Define project principles        │
│           │                                                      │
│           ▼                                                      │
│  2. /speckit.specify       ──►  Describe what to build           │
│           │                                                      │
│           ▼                                                      │
│  3. /speckit.clarify       ──►  (Optional) Clarify requirements  │
│           │                                                      │
│           ▼                                                      │
│  4. /speckit.plan          ──►  Create implementation plan       │
│           │                                                      │
│           ▼                                                      │
│  5. /speckit.tasks         ──►  Break down into tasks            │
│           │                                                      │
│           ▼                                                      │
│  6. /speckit.implement     ──►  Execute and build                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Examples

### Example 1: Building an API

**Step 1: Establish Principles**
```
/speckit.constitution Create principles focused on:
- RESTful API design standards
- Comprehensive error handling
- Input validation
- Security best practices
- Test coverage requirements
```

**Step 2: Define Specification**
```
/speckit.specify Build a user authentication API that supports:
- User registration with email verification
- Login with JWT tokens
- Password reset functionality
- Rate limiting for security
```

**Step 3: Create Plan**
```
/speckit.plan Use the following tech stack:
- FastAPI for the web framework
- PostgreSQL for database
- Redis for rate limiting and caching
- JWT for authentication tokens
- Pytest for testing
```

**Step 4: Generate Tasks**
```
/speckit.tasks
```

**Step 5: Implement**
```
/speckit.implement
```

---

### Example 2: Building a Frontend Feature

**Step 1: Establish Principles**
```
/speckit.constitution Create principles for:
- Responsive design (mobile-first)
- Accessibility (WCAG 2.1 AA)
- Performance optimization
- Component reusability
```

**Step 2: Define Specification**
```
/speckit.specify Build a photo album organizer that:
- Displays photos in a tile-like grid
- Groups albums by date
- Supports drag-and-drop reorganization
- Shows photo previews on hover
```

**Step 3: Create Plan**
```
/speckit.plan Use:
- React with TypeScript
- TailwindCSS for styling
- React DnD for drag-and-drop
- Local storage for persistence
```

**Step 4-5: Generate Tasks and Implement**
```
/speckit.tasks
/speckit.implement
```

---

## Tips

### Best Practices

1. **Be specific in specifications** - The more detail you provide, the better the implementation
2. **Focus on "what" not "how"** - Let the AI determine implementation details
3. **Review generated plans** - Validate before proceeding to tasks
4. **Iterate on clarifications** - Use `/speckit.clarify` when requirements are unclear

### Common Issues

| Issue | Solution |
|-------|----------|
| Commands not recognized | Run `specify init --here --ai windsurf` again |
| Outdated CLI | Run `uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git` |
| Permission errors | Check file permissions in `.windsurf/rules/` |

### Project Structure After Init

```
your-project/
├── .windsurf/
│   └── rules/
│       └── speckit.md          # Slash command definitions
├── .speckit/
│   ├── constitution.md         # Project principles
│   ├── spec.md                 # Feature specifications
│   ├── plan.md                 # Implementation plan
│   └── tasks.md                # Task breakdown
└── ... (your project files)
```

---

## Resources

- [Spec-Kit GitHub Repository](https://github.com/github/spec-kit)
- [Video Overview](https://www.youtube.com/watch?v=a9eR1xsfvHg)
- [Comprehensive Guide](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- [Upgrade Guide](https://github.com/github/spec-kit/blob/main/docs/upgrade.md)

---

## License

Spec-Kit is maintained by GitHub. See the [original repository](https://github.com/github/spec-kit) for license information.
