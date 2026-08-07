"""The detangle run itself — ADR-002 (approved 2026-08-05).

The reorder plan is data: authored as an 8g stage-A artifact (AI-drafted,
human-approved, landed by PR), executed by the tool, never authored by it.
``plan.py`` holds the schema, loader and validation; execution and the
generated self-report arrive with the ``detangle restructure`` command.
``position.py`` (ADR-004 Decision 8) reports blocks a human moved by hand,
which a run puts back, and offers the plan line that would ratify the move.
"""

from .plan import CHECKS, Plan, load_plan, validate_plan

__all__ = ["CHECKS", "Plan", "load_plan", "validate_plan"]
