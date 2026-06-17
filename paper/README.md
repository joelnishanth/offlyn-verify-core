# Paper

**Policy at the Actuation Boundary: Hardware-Enforced Safety for AI-Controlled Robots**

Draft v0.1 — June 2026

## Files

- `policy_at_actuation_boundary_offlyn_verify_core_draft_v0_1.pdf` — compiled draft
- `policy_at_actuation_boundary_offlyn_verify_core_draft_v0_1.tex` — LaTeX source

## Building

To rebuild the PDF from source:

```bash
pdflatex policy_at_actuation_boundary_offlyn_verify_core_draft_v0_1.tex
bibtex policy_at_actuation_boundary_offlyn_verify_core_draft_v0_1
pdflatex policy_at_actuation_boundary_offlyn_verify_core_draft_v0_1.tex
pdflatex policy_at_actuation_boundary_offlyn_verify_core_draft_v0_1.tex
```

Build artifacts (`.aux`, `.log`, `.out`, etc.) are gitignored.
