"""CLI entry point for ScaffoldBench."""

import argparse
import json
import sys

from .metrics import ScaffoldBenchScore
from .tasks import TASKS


def format_score(score: ScaffoldBenchScore) -> str:
    """Pretty-print a benchmark score."""
    lines = [
        f"",
        f"╔══════════════════════════════════════╗",
        f"║        ScaffoldBench Results         ║",
        f"╠══════════════════════════════════════╣",
        f"║ Scaffold: {score.scaffold_name:<28} ║",
        f"║ Model:    {score.model_used:<28} ║",
        f"╠══════════════════════════════════════╣",
        f"║ Strategy Score:     {score.strategy_score:>5.1f}%          ║",
        f"║   ({score.tasks_passed}/{score.tasks_total} tasks passed)              ║",
        f"║                                      ║",
        f"║ Token Efficiency:   {score.token_efficiency:>5.2f}           ║",
        f"║   (passes per 1K tokens)             ║",
        f"║                                      ║",
        f"║ Fault Recovery:     {score.fault_recovery_rate:>5.1f}%          ║",
        f"║   ({score.faults_recovered}/{score.faults_injected} faults recovered)              ║",
        f"╠══════════════════════════════════════╣",
        f"║ Total Time: {score.total_time_ms/1000:>6.1f}s                    ║",
        f"║ Total Tokens: {score.total_tokens:>7,d}                 ║",
        f"╚══════════════════════════════════════╝",
    ]
    if score.errors:
        lines.append(f"\n  Errors ({len(score.errors)}):")
        for e in score.errors[:5]:
            lines.append(f"    - {e[:100]}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        prog="scaffoldbench",
        description="ScaffoldBench — Benchmark AI agent scaffolds, not models.",
    )
    parser.add_argument(
        "command",
        choices=["run", "list-tasks", "version"],
        default="version",
        nargs="?",
        help="Command to run",
    )
    parser.add_argument(
        "--scaffold",
        type=str,
        help="Path to a scaffold Python module (for 'run')",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="qwen-2.5-7b",
        help="Model to use (default: qwen-2.5-7b)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    args = parser.parse_args()

    if args.command == "version":
        from . import __version__
        print(f"ScaffoldBench v{__version__}")
        sys.exit(0)

    if args.command == "list-tasks":
        print(f"\n  Available tasks ({len(TASKS)}):\n")
        for t in TASKS:
            fault = " [fault injected]" if t.inject_fault else ""
            print(f"  [{t.task_id}] {t.name} ({t.category}){fault}")
            print(f"    {t.description}\n")
        sys.exit(0)

    if args.command == "run":
        if not args.scaffold:
            print("Error: --scaffold is required for 'run' command.")
            print("Usage: scaffoldbench run --scaffold ./my_scaffold.py")
            sys.exit(1)

        # Load the scaffold module
        import importlib.util
        import os

        scaffold_path = os.path.abspath(args.scaffold)
        spec = importlib.util.spec_from_file_location("user_scaffold", scaffold_path)
        if spec is None or spec.loader is None:
            print(f"Error: Could not load scaffold from {scaffold_path}")
            sys.exit(1)

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "Scaffold"):
            print(
                "Error: Scaffold module must export a 'Scaffold' class "
                "with a .run(task_description, tools) method."
            )
            sys.exit(1)

        scaffold = module.Scaffold()
        from .runner import run_benchmark

        if args.scaffold.endswith(".py"):
            scaffold_name = os.path.splitext(os.path.basename(args.scaffold))[0]
        else:
            scaffold_name = args.scaffold

        score = run_benchmark(scaffold, scaffold_name, args.model, TASKS)

        if args.json:
            print(json.dumps({
                "scaffold_name": score.scaffold_name,
                "model_used": score.model_used,
                "strategy_score": score.strategy_score,
                "tasks_passed": score.tasks_passed,
                "tasks_total": score.tasks_total,
                "token_efficiency": score.token_efficiency,
                "total_tokens": score.total_tokens,
                "fault_recovery_rate": score.fault_recovery_rate,
                "faults_injected": score.faults_injected,
                "faults_recovered": score.faults_recovered,
                "total_time_ms": score.total_time_ms,
                "errors": score.errors,
            }, indent=2))
        else:
            print(format_score(score))


if __name__ == "__main__":
    main()
