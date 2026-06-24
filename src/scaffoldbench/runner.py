"""Benchmark runner: executes tasks against a scaffold with a fixed weak model."""

import time
from typing import Protocol

from .metrics import ScaffoldBenchResult, ScaffoldBenchScore, compute_scores
from .tasks import Task


class ScaffoldProtocol(Protocol):
    """A scaffold is anything that takes a task description + tools and returns an output."""

    def run(self, task_description: str, tools: list[str]) -> str: ...


def run_benchmark(
    scaffold: "ScaffoldProtocol",
    scaffold_name: str,
    model_name: str,
    tasks: list[Task],
) -> ScaffoldBenchScore:
    """Run a scaffold against all tasks and compute scores."""
    results: list[ScaffoldBenchResult] = []

    for task in tasks:
        task_desc = task.input_context
        if task.inject_fault:
            task_desc += (
                f"\n\n[Note: {task.fault_description}]"
            )

        start = time.time()
        error: str | None = None
        try:
            output = scaffold.run(task_desc, task.expected_tools)
        except Exception as e:
            output = ""
            error = str(e)

        elapsed_ms = int((time.time() - start) * 1000)

        # Check pass/fail
        try:
            passed = task.evaluate(output) if not error else False
        except Exception:
            passed = False

        # Token count: scaffold should report if possible, otherwise estimate
        total_tokens = _estimate_tokens(task_desc, output)

        results.append(
            ScaffoldBenchResult(
                task_id=task.task_id,
                passed=passed,
                total_tokens=total_tokens,
                total_time_ms=elapsed_ms,
                fault_injected=task.inject_fault,
                fault_recovered=passed and task.inject_fault,
                error=error,
            )
        )

    return compute_scores(scaffold_name, model_name, results)


def _estimate_tokens(prompt: str, output: str) -> int:
    """Rough token estimate (4 chars ~= 1 token)."""
    return (len(prompt) + len(output)) // 4
