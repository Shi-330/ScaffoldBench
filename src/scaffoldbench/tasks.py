"""Standard task definitions for ScaffoldBench.

Each task defines a clear input, expected behavior, and pass/fail criteria.
Tasks are designed to be:
- Solvable by a competent scaffold even with a weak model
- Sensitive to scaffold quality (tool use, memory, error handling)
- Quick to run (sub-30s each with a small local model)
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class Task:
    """A single benchmark task."""

    task_id: str
    name: str
    description: str
    category: str  # "reasoning", "tool_use", "memory", "error_handling"
    input_context: str
    expected_tools: list[str]  # tools the scaffold should make available
    evaluate: Any  # callable that takes (output: str) -> bool
    inject_fault: bool = False  # whether to inject a tool error during this task
    fault_description: str = ""


# --- Sample Tasks ---

TASKS: list[Task] = [
    Task(
        task_id="basic-001",
        name="Simple Reasoning",
        description="Answer a straightforward factual question using provided context.",
        category="reasoning",
        input_context=(
            "Read the following context and answer the question.\n\n"
            "Context: The company Acme Corp was founded in 2019 by Sarah Chen "
            "and raised $12M Series A in 2021. Its main product is a "
            "cloud-based payroll system for small businesses.\n\n"
            "Question: Who founded Acme Corp and in what year?"
        ),
        expected_tools=[],
        evaluate=lambda output: "sarah chen" in output.lower() and "2019" in output,
    ),
    Task(
        task_id="basic-002",
        name="Number Extraction",
        description="Extract specific numbers from a financial paragraph and compute a simple ratio.",
        category="reasoning",
        input_context=(
            "Extract the two numbers from the following text and compute their ratio.\n\n"
            "Text: 'In Q3 2025, total revenue reached $4.5 million while operating "
            "costs were $1.8 million.'\n\n"
            "Compute: revenue / costs. Return the result rounded to 2 decimal places."
        ),
        expected_tools=[],
        evaluate=lambda output: "2.5" in output.replace(" ", ""),
    ),
    Task(
        task_id="tool-001",
        name="Calculator Invocation",
        description="Use a calculator tool to compute a multi-step math problem.",
        category="tool_use",
        input_context=(
            "Use the calculator tool to solve: ((127 * 43) + 891) / 17.\n"
            "Return the final result rounded to the nearest integer."
        ),
        expected_tools=["calculator"],
        # ((127*43) + 891) / 17 = (5461 + 891) / 17 = 6352 / 17 = 373.647... → 374
        evaluate=lambda output: "374" in output.replace(" ", "").replace(".", "").replace("0", "") or "374" in output,
    ),
    Task(
        task_id="tool-002",
        name="Web Search Simulation",
        description="Given a 'search' tool that returns results, answer a question.",
        category="tool_use",
        input_context=(
            "Use the search tool to find the capital of Bhutan, then answer: "
            "'What is the capital of Bhutan?'"
        ),
        expected_tools=["search"],
        evaluate=lambda output: "thimphu" in output.lower(),
    ),
    Task(
        task_id="mem-001",
        name="Multi-turn Context",
        description="Answer a question that requires remembering information from earlier in the conversation.",
        category="memory",
        input_context=(
            "First, remember this: the user's name is Alex, Alex works as a "
            "backend engineer, and Alex's project codename is 'Phoenix'.\n\n"
            "Now answer: What is the user's name, job title, and project codename?"
        ),
        expected_tools=[],
        evaluate=lambda output: "alex" in output.lower() and "backend" in output.lower() and "phoenix" in output.lower(),
    ),
    Task(
        task_id="err-001",
        name="Graceful Tool Failure",
        description="Handle a tool that returns an error and retry or fallback.",
        category="error_handling",
        input_context=(
            "Use the 'database_query' tool to find the total number of users "
            "in the system. If the tool fails, try again once. If it still fails, "
            "respond with 'Unable to query database after retry.'"
        ),
        expected_tools=["database_query"],
        inject_fault=True,
        fault_description="database_query returns 'ConnectionError: timeout' on first call",
        evaluate=lambda output: (
            "unable to query" in output.lower()
            or "retry" in output.lower()
            or "failed" in output.lower()
        ),
    ),
]
