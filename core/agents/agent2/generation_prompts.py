"""Generation system prompts, by name.

"guided" is the frozen prompt of E1, E2 and E5 (prompts.GENERATE_SYSTEM_PROMPT, hash in tests/golden/frozen_files.json).
"c0_minimal" is the C0 control (E4): it only asks for a textual SysML v2 model per category and for
code only, with no grammar constraints, templates or modelling policy.
"v1" is the earlier generation prompt, the one that produced the E3 error bank, stored byte for
byte (read without stripping). R9 uses it to build an out-of-sample error bank on JWST in the same way.
The user message and the post-processing (clean_sysml) are the same for every prompt.
"""

from pathlib import Path

from .prompts import GENERATE_SYSTEM_PROMPT

_C0_MINIMAL = (Path(__file__).resolve().parent / "c0_minimal_prompt.md").read_text(encoding="utf-8").strip()

_V1 = (Path(__file__).resolve().parent / "v1_generation_prompt.md").read_text(encoding="utf-8")

GENERATION_PROMPTS: dict[str, str] = {
    "guided": GENERATE_SYSTEM_PROMPT,
    "c0_minimal": _C0_MINIMAL,
    "v1": _V1,
}
