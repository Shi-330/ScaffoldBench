"""Example: a minimal scaffold that demonstrates the ScaffoldBench interface.

This is intentionally naive — it just passes the task to the model directly
with no scaffolding strategy. It exists as a baseline to compare against.
"""


class Scaffold:
    """A minimal scaffold: no tool use, no retry, no planning. Just ask.

    To use this as a baseline:
        scaffoldbench run --scaffold examples/basic_scaffold.py

    To write your own scaffold, copy this file and implement the .run() method.
    Your Scaffold class must have:
        def run(self, task_description: str, tools: list[str]) -> str
    """

    def run(self, task_description: str, tools: list[str]) -> str:
        """Run a task. This is where your scaffold logic goes.

        Args:
            task_description: The full task prompt from ScaffoldBench.
            tools: List of tool names the scaffold should make available
                   to the model (e.g. ["calculator", "search"]).

        Returns:
            The model's final output as a string.
        """
        # In a real scaffold, you would:
        # 1. Parse the task
        # 2. Set up the model with available tools
        # 3. Run an agent loop (ReAct, Plan-and-Solve, etc.)
        # 4. Handle tool errors gracefully
        # 5. Return the final answer

        # This baseline just returns a placeholder.
        # Replace with your actual LLM call:
        # return your_llm_invoke(task_description, tools=tools)

        return "[baseline scaffold: not connected to a model yet]"
