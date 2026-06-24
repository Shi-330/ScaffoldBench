"""The three core ScaffoldBench metrics."""

from dataclasses import dataclass, field


@dataclass
class ScaffoldBenchResult:
    """Single run result for one scaffold on one task."""

    task_id: str
    passed: bool
    total_tokens: int
    total_time_ms: int
    fault_injected: bool = False
    fault_recovered: bool = False
    error: str | None = None


@dataclass
class ScaffoldBenchScore:
    """Aggregated scores for a scaffold across all tasks."""

    scaffold_name: str
    model_used: str

    # Strategy Score: % of tasks passed with a weak model
    strategy_score: float  # 0-100
    tasks_passed: int
    tasks_total: int

    # Token Efficiency: tasks passed / total tokens (higher = better)
    token_efficiency: float
    total_tokens: int

    # Fault Recovery: % of injected faults successfully recovered
    fault_recovery_rate: float  # 0-100
    faults_injected: int
    faults_recovered: int

    # Metadata
    total_time_ms: int
    errors: list[str] = field(default_factory=list)

    results: list[ScaffoldBenchResult] = field(default_factory=list)


def compute_scores(
    scaffold_name: str,
    model_used: str,
    results: list[ScaffoldBenchResult],
) -> ScaffoldBenchScore:
    """Compute all three metrics from raw results."""
    tasks_total = len(results)
    tasks_passed = sum(1 for r in results if r.passed)
    total_tokens = sum(r.total_tokens for r in results)
    total_time = sum(r.total_time_ms for r in results)

    # Strategy Score
    strategy_score = (tasks_passed / tasks_total * 100) if tasks_total > 0 else 0.0

    # Token Efficiency: tasks passed per 1000 tokens (higher = better)
    token_efficiency = (tasks_passed / (total_tokens / 1000)) if total_tokens > 0 else 0.0

    # Fault Recovery
    fault_results = [r for r in results if r.fault_injected]
    faults_injected = len(fault_results)
    faults_recovered = sum(1 for r in fault_results if r.fault_recovered)
    fault_recovery_rate = (
        (faults_recovered / faults_injected * 100) if faults_injected > 0 else 0.0
    )

    errors = [r.error for r in results if r.error]

    return ScaffoldBenchScore(
        scaffold_name=scaffold_name,
        model_used=model_used,
        strategy_score=strategy_score,
        tasks_passed=tasks_passed,
        tasks_total=tasks_total,
        token_efficiency=token_efficiency,
        total_tokens=total_tokens,
        fault_recovery_rate=fault_recovery_rate,
        faults_injected=faults_injected,
        faults_recovered=faults_recovered,
        total_time_ms=total_time,
        errors=errors,
        results=results,
    )
