"""Print the model registry; with --check, verify it against the live OpenRouter catalog.

    python -m evaluation.list_models [--check]
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request

from core.config import OPENROUTER_BASE_URL
from core.models import SUPPORTED_MODELS


PRICE_TOLERANCE = 1e-6


def print_registry() -> None:
    header = f"{'alias':<24}{'openrouter_id':<32}{'in $/M':>8}{'out $/M':>9}  {'effort':<8}{'temp':<6}{'json':<6}{'role':<11}provider"
    print(header)
    print("-" * len(header))
    for spec in SUPPORTED_MODELS.values():
        print(f"{spec.alias:<24}{spec.openrouter_id:<32}{spec.input_usd_per_m:>8.2f}{spec.output_usd_per_m:>9.2f}  "
              f"{spec.reasoning_effort or '-':<8}{'yes' if spec.supports_temperature else 'no':<6}"
              f"{'yes' if spec.supports_json_mode else 'no':<6}{spec.role:<11}{spec.provider or '-'}")


def fetch_catalog() -> dict[str, dict]:
    with urllib.request.urlopen(f"{OPENROUTER_BASE_URL}/models", timeout=30) as response:
        data = json.load(response)["data"]
    return {model["id"]: model for model in data}


def fetch_endpoint(model_id: str, provider: str) -> dict | None:
    """The pinned provider's endpoint (its own price and parameters), or None if it does not serve the model."""
    with urllib.request.urlopen(f"{OPENROUTER_BASE_URL}/models/{model_id}/endpoints", timeout=30) as response:
        endpoints = json.load(response)["data"]["endpoints"]
    return next((e for e in endpoints if e.get("tag") == provider), None)


def check(catalog: dict[str, dict]) -> list[str]:
    problems = []
    for spec in SUPPORTED_MODELS.values():
        entry = catalog.get(spec.openrouter_id)
        if entry is None:
            problems.append(f"{spec.alias}: '{spec.openrouter_id}' does not exist on OpenRouter")
            continue
        if spec.provider:
            entry = fetch_endpoint(spec.openrouter_id, spec.provider)
            if entry is None:
                problems.append(f"{spec.alias}: pinned provider '{spec.provider}' does not serve {spec.openrouter_id}")
                continue
        pricing = entry.get("pricing", {})
        live_in = float(pricing.get("prompt", 0)) * 1e6
        live_out = float(pricing.get("completion", 0)) * 1e6
        if abs(live_in - spec.input_usd_per_m) > PRICE_TOLERANCE or abs(live_out - spec.output_usd_per_m) > PRICE_TOLERANCE:
            problems.append(
                f"{spec.alias}: price changed (registry {spec.input_usd_per_m:.4f}/{spec.output_usd_per_m:.4f}, "
                f"OpenRouter {live_in:.4f}/{live_out:.4f} USD per M in/out)"
            )
        params = set(entry.get("supported_parameters") or [])
        if spec.supports_temperature and "temperature" not in params:
            problems.append(f"{spec.alias}: registry sends temperature but OpenRouter does not list it")
        if spec.supports_json_mode and "response_format" not in params:
            problems.append(f"{spec.alias}: registry uses JSON mode but OpenRouter does not list response_format")
        if spec.reasoning_effort and "reasoning" not in params:
            problems.append(f"{spec.alias}: registry sets reasoning effort but the model has no 'reasoning' parameter")
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="Compare ids and prices with the OpenRouter catalog.")
    args = parser.parse_args()

    print_registry()
    if not args.check:
        return
    problems = check(fetch_catalog())
    if problems:
        print("\nWARNINGS:")
        for problem in problems:
            print(f"  - {problem}")
        sys.exit(1)
    print(f"\nOK: all {len(SUPPORTED_MODELS)} models exist on OpenRouter with the registered prices.")


if __name__ == "__main__":
    main()
