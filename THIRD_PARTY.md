# Third-party material

The code of this repository is under Apache-2.0 ([LICENSE](LICENSE)), **except `core/validate/SysMLv2/`**, described
below, which keeps the licence of the work it derives from.

## Included in this repository

### SysML v2 grammar and generated parser: `core/validate/SysMLv2/`

| Files | Origin |
|---|---|
| `SysMLv2.g4` | ANTLR 4 translation of `InternalSysML.g`, release 2024-04.1 of the [SysML v2 Pilot Implementation](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation), published by the Sireum project in [hamr-sysml-parser](https://github.com/sireum/hamr-sysml-parser), commit `b5978ee`. Byte-identical to `src/org/sireum/hamr/sysml/parser/SysMLv2.g4` in that commit. |
| `SysMLv2Lexer.py`, `SysMLv2Parser.py`, `SysMLv2Listener.py`, `SysMLv2Visitor.py`, `*.interp`, `*.tokens` | Generated from `SysMLv2.g4` with ANTLR 4.13.2. |

**Licence: GNU LGPL 3.0.** Tag 2024-04.1 of the Pilot Implementation is licensed under the LGPL 3.0, and the
hamr-sysml-parser README declares the same licence through a badge pointing to the Pilot Implementation's licence.
The texts are in this folder: [LICENSE-LGPL-3.0.txt](core/validate/SysMLv2/LICENSE-LGPL-3.0.txt) and
[LICENSE-GPL-3.0.txt](core/validate/SysMLv2/LICENSE-GPL-3.0.txt) (copied from that tag). Later releases of the Pilot
Implementation moved to EPL-2.0, which does not change the licence of this earlier version.

The rest of the code uses this folder as a Python library, by importing it. You can replace these files with another
version of the grammar and regenerate them with ANTLR.

### Grammar excerpts in the knowledge bases: `core/agents/agent2/knowledge/`

The knowledge bases are ours, but they quote some rules of the grammar above to explain them to the repair agent.
Those excerpts come from the grammar under the licence stated above.

## Used but not included

| Component | Used for | Licence | How you get it |
|---|---|---|---|
| SysML v2 Pilot Implementation, 2024-04.1 | Reference validation (`tools/pilot/*.java` compile against it) | LGPL-3.0 | Download, see [README.md](README.md) |
| SysML v2 Pilot Implementation, 2026-08 | Reference validation | EPL-2.0 (tag LICENSE) | Download, see [README.md](README.md) |
| ANTLR 4 Python runtime | Grammar validator | BSD-3-Clause | `requirements.txt` |
| [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) | Embeddings | Apache-2.0 | Downloaded on first use |
| Other Python dependencies | See `requirements.txt` | Permissive, each under its own licence (Apache-2.0, BSD, MIT, PSF-based) | `requirements.txt` |

The LLMs are reached through OpenRouter; their outputs and use are subject to the terms of OpenRouter and of each
provider. The source documents of the study are not included.
