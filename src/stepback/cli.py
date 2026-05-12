"""``stepback`` CLI."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import click

from stepback import (
    AnthropicCompletion,
    Strategy,
    load_questions,
    run_all,
)


@click.group()
def cli():
    """reproduce-stepback CLI."""


@cli.command(name="list")
def list_questions_cmd():
    """List the 40 benchmark questions with their tested principles."""
    for q in load_questions():
        click.echo(f"{q.id}  [{q.principle}] {q.question[:70]}")


@cli.command()
@click.option("--out", default="bench/anthropic_results.json")
@click.option("--model", default=None)
def run(out, model):
    """Run all three strategies against Anthropic Haiku 4.5."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        click.echo("ANTHROPIC_API_KEY not set", err=True)
        sys.exit(2)
    backend = AnthropicCompletion(model=model)
    questions = load_questions()
    click.echo(f"running 3 strategies x {len(questions)} questions on {backend.model}...")
    results = run_all(backend, questions)

    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {
                "model": backend.model,
                "n_questions": len(questions),
                "strategies": [
                    {
                        "strategy": r.strategy.value,
                        "accuracy": r.accuracy,
                        "correct": r.correct,
                        "unparseable": r.unparseable,
                        "wrong_ids": [p.question_id for p in r.per_question if not p.correct],
                    }
                    for r in results
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    click.echo(f"\nwrote {out_path}\n")
    for r in results:
        click.echo(
            f"  {r.strategy.value:12s} acc={r.accuracy*100:.1f}% "
            f"(correct={r.correct}/{r.n}, unparseable={r.unparseable})"
        )
