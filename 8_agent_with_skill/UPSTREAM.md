# Upstream Source

- Repository: https://github.com/punsiriboo/adk-skills
- Revision: `31ea9299f6556c53779144e18a0c617f372fafa1`
- Revision date: 2026-07-19
- Imported directories: `blog_skills_agent`, `marathon_planner_agent`
- Imported asset: upstream `img/title.png` as `upstream-title.png`

Local integration changes:

1. Both agents load `.env` from this repository's root.
2. Both agents use the root `MODEL_ID` setting.
3. Dependencies are managed by the root `requirements.txt`.
4. Upstream `marathon_planner_agent/sample.env` is represented in the root
   `.env.example` instead of creating a nested environment file.
5. The upstream title image is stored at the agents-directory root so ADK Web
   does not mistake an `img` directory for a third agent.
