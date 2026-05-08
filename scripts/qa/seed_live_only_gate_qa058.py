from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SEED_MODULES = (
    "scripts.qa.seed_governance_qa051",
    "scripts.qa.seed_skill_lifecycle_qa052",
    "scripts.qa.seed_test_bench_qa053",
    "scripts.qa.seed_membership_qa054",
    "scripts.qa.seed_channels_briefing_qa055",
    "scripts.qa.seed_usage_qa056",
    "scripts.qa.seed_operations_qa057",
)


def main() -> int:
    completed: list[str] = []
    for module_name in SEED_MODULES:
        module = import_module(module_name)
        entrypoint = getattr(module, "main", None) or getattr(module, "seed", None)
        if entrypoint is None:
            raise RuntimeError(f"{module_name} does not expose main() or seed()")
        result = entrypoint()
        result_code = 0 if result is None else int(result)
        if result_code != 0:
            return result_code
        completed.append(module_name.rsplit(".", 1)[-1])

    print("Seeded QA058 live-only gate records")
    print(f"seed_modules={','.join(completed)}")
    print("external_calls=0")
    print(
        "seeded_surfaces=governance,skill_lifecycle,test_bench,membership,channels,usage,operations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
