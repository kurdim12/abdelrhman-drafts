"""Simple workflow automation utilities for FinanceGuard AI."""

from typing import Callable, List

WorkStep = Callable[[], None]


def run_workflow(steps: List[WorkStep]) -> None:
    """Run a sequence of steps with basic error handling."""
    for step in steps:
        try:
            step()
        except Exception as exc:
            print(f"Step {step.__name__} failed: {exc}")
            break
    else:
        print("Workflow completed successfully.")
