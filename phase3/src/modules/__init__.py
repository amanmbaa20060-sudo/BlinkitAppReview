"""Discovery question modules Q1–Q8."""

from __future__ import annotations

from typing import Any, Callable

from . import q1, q2, q3, q4, q5, q6, q7, q8

ModuleFn = Callable[[list[dict[str, Any]], dict[str, Any]], list[dict[str, Any]]]

MODULES: dict[str, ModuleFn] = {
    "Q1": q1.run,
    "Q2": q2.run,
    "Q3": q3.run,
    "Q4": q4.run,
    "Q5": q5.run,
    "Q6": q6.run,
    "Q7": q7.run,
    "Q8": q8.run,
}

QUESTIONS = {
    "Q1": "Why do users repeatedly buy from the same categories?",
    "Q2": "What prevents users from exploring new categories?",
    "Q3": "How do users discover products today?",
    "Q4": "What role do habits play in shopping behavior?",
    "Q5": "What information do users need before trying a new category?",
    "Q6": "What frustrations emerge repeatedly?",
    "Q7": "Which user segments are more likely to experiment?",
    "Q8": "What unmet needs emerge consistently across discussions?",
}
