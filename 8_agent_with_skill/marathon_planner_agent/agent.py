# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent

from .prompts import PLANNER_INSTRUCTION
from .tools import get_tools

# Keep configuration centralized in the repository root.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

description = "Running route planner for park runs, training loops, and optional race events."
tools = get_tools()

root_agent = Agent(
    model=os.getenv("MODEL_ID", "gemini-2.5-flash"),
    name="planner_agent",
    description=description,
    instruction=PLANNER_INSTRUCTION,
    tools=tools,
)
