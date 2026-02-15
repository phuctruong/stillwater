"""Benchmark 7: Context Compression.

LLM summarizes text, then answers questions from the summary alone.
CPU compares answers against ground truth to measure information retention.
"""

from __future__ import annotations

import re
import time

from stillwater.bench import BenchResult
from stillwater.llm import LLMClient

# Inline fixtures: passages with Q&A ground truth
FIXTURES = [
    {
        "passage": (
            "The Great Wall of China stretches over 13,000 miles. Construction began "
            "in the 7th century BC and continued for over 2,000 years. The wall was "
            "built primarily to protect against invasions from the north. It is made "
            "of stone, brick, tamped earth, and wood. The wall is wide enough for "
            "five horses to ride abreast."
        ),
        "question": "How long is the Great Wall of China?",
        "answer_keywords": ["13,000", "13000", "thirteen thousand"],
    },
    {
        "passage": (
            "Marie Curie was born in Warsaw, Poland in 1867. She was the first woman "
            "to win a Nobel Prize and the only person to win Nobel Prizes in two "
            "different sciences: Physics in 1903 and Chemistry in 1911. She discovered "
            "polonium and radium."
        ),
        "question": "In what two fields did Marie Curie win Nobel Prizes?",
        "answer_keywords": ["physics", "chemistry"],
    },
    {
        "passage": (
            "The Amazon River is approximately 4,000 miles long, making it the second "
            "longest river in the world after the Nile. It carries more water than any "
            "other river, accounting for about 20% of all freshwater that flows into "
            "the world's oceans. The Amazon basin covers 2.7 million square miles."
        ),
        "question": "What percentage of freshwater flowing into oceans comes from the Amazon?",
        "answer_keywords": ["20%", "20 percent", "twenty"],
    },
    {
        "passage": (
            "The human body has 206 bones. The smallest bone is the stapes in the ear, "
            "measuring just 3mm. The largest bone is the femur in the thigh. Bones are "
            "made of collagen and calcium phosphate. New bone cells replace old ones in "
            "a process that takes about 10 years for a complete skeleton renewal."
        ),
        "question": "What is the smallest bone in the human body?",
        "answer_keywords": ["stapes"],
    },
    {
        "passage": (
            "The speed of light in a vacuum is exactly 299,792,458 meters per second. "
            "Light takes about 8 minutes and 20 seconds to travel from the Sun to "
            "Earth. The distance light travels in one year is called a light-year, "
            "which equals about 5.88 trillion miles."
        ),
        "question": "How long does light take to travel from the Sun to Earth?",
        "answer_keywords": ["8 minutes", "8 min"],
    },
    {
        "passage": (
            "Python was created by Guido van Rossum and first released in 1991. "
            "It emphasizes code readability and uses significant whitespace. Python "
            "supports multiple programming paradigms including procedural, object-oriented, "
            "and functional programming. The name comes from Monty Python, not the snake."
        ),
        "question": "Who created Python?",
        "answer_keywords": ["guido", "van rossum"],
    },
    {
        "passage": (
            "Mount Everest stands at 8,849 meters (29,032 feet) above sea level. "
            "It is located in the Mahalangur Himal sub-range of the Himalayas, on the "
            "border between Nepal and Tibet. The first confirmed summit was by Edmund "
            "Hillary and Tenzing Norgay on May 29, 1953."
        ),
        "question": "Who first summited Mount Everest?",
        "answer_keywords": ["hillary", "norgay", "tenzing"],
    },
    {
        "passage": (
            "Honey never spoils. Archaeologists have found 3,000-year-old honey in "
            "Egyptian tombs that was still perfectly edible. Honey's longevity is due "
            "to its low moisture content, acidic pH, and the presence of hydrogen "
            "peroxide. Bees produce honey by collecting nectar and reducing its "
            "water content to below 20%."
        ),
        "question": "Why does honey last so long?",
        "answer_keywords": ["moisture", "acidic", "hydrogen peroxide"],
    },
    {
        "passage": (
            "The International Space Station orbits Earth at an altitude of about "
            "250 miles. It travels at approximately 17,500 miles per hour, completing "
            "one orbit every 90 minutes. The ISS has been continuously occupied since "
            "November 2000 and has hosted astronauts from 19 countries."
        ),
        "question": "How fast does the ISS travel?",
        "answer_keywords": ["17,500", "17500"],
    },
    {
        "passage": (
            "Octopuses have three hearts: two pump blood to the gills and one pumps "
            "it to the rest of the body. They have blue blood because they use copper-based "
            "hemocyanin instead of iron-based hemoglobin. Octopuses are considered the "
            "most intelligent invertebrates and can solve puzzles and open jars."
        ),
        "question": "How many hearts does an octopus have?",
        "answer_keywords": ["three", "3"],
    },
]


def run(client: LLMClient) -> BenchResult:
    """Run context compression benchmark."""
    details: list[dict] = []
    passed = 0
    t0 = time.perf_counter()

    for fixture in FIXTURES:
        try:
            # Step 1: LLM compresses the passage
            summary_prompt = (
                "Summarize the following passage in 1-2 sentences, preserving all "
                "key facts and numbers.\n\n"
                f"Passage: {fixture['passage']}\n\n"
                "Summary:"
            )
            summary = client.generate(summary_prompt, temperature=0)

            # Step 2: LLM answers from summary alone
            qa_prompt = (
                f"Based on this summary, answer the question concisely.\n\n"
                f"Summary: {summary}\n\n"
                f"Question: {fixture['question']}\n"
                f"Answer:"
            )
            answer = client.generate(qa_prompt, temperature=0)

            # CPU compares against ground truth keywords
            answer_lower = answer.lower()
            keyword_found = any(
                kw.lower() in answer_lower for kw in fixture["answer_keywords"]
            )

            if keyword_found:
                passed += 1

            details.append({
                "question": fixture["question"],
                "summary": summary[:200],
                "answer": answer[:200],
                "keywords": fixture["answer_keywords"],
                "keyword_found": keyword_found,
                "passed": keyword_found,
            })
        except Exception as e:
            details.append({
                "question": fixture["question"],
                "error": str(e),
                "passed": False,
            })

    elapsed = (time.perf_counter() - t0) * 1000
    return BenchResult(
        name="Context Compression",
        passed=passed,
        total=len(FIXTURES),
        elapsed_ms=elapsed,
        details=details,
    )
