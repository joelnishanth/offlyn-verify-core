# Patent and Publication Sequence

This document outlines the recommended sequence for patent filings and publications related to VerifyCore and SilicaFold.

## Publication Sequence

### Step 1: Finalize SilicaFold PRs and Tests

- Complete all pending pull requests in the SilicaFold repository
- Ensure all RTL tests pass and are documented
- Verify TinyTapeout submission requirements are met
- Review all public claims for accuracy and patent safety

### Step 2: Publish SilicaFold as Narrow Hardware-Backed Data Paper

- Target: Hardware data paper with narrow scope
- Focus: TinyTapeout RTL primitive for policy-gated actuation
- Include: Test results, RTL verification, silicon submission evidence
- Exclude: Broader VerifyCore architecture claims, production security claims
- Venue: Hardware/embedded systems workshop, arXiv preprint, or TinyTapeout documentation

### Step 3: Use SilicaFold as Supporting Evidence for VerifyCore

- Reference SilicaFold in VerifyCore paper as hardware evidence artifact
- Cite SilicaFold paper or preprint in bibliography
- Clearly distinguish between SilicaFold evidence and VerifyCore architecture
- Do not claim SilicaFold implements the full VerifyCore stack

### Step 4: File or Coordinate VerifyCore Patent Materials

**Critical**: Complete this step before broad public disclosure of claims that go beyond implemented evidence.

- Identify patentable claims in VerifyCore architecture
- Distinguish between claims supported by evidence and future architecture claims
- File provisional patent application covering broader system claims
- Coordinate with patent counsel on claim language and scope

### Step 5: Publish VerifyCore Paper with Clear Boundaries

- Clearly separate implemented evidence from future architecture
- Reference SilicaFold as narrow hardware evidence
- Include detailed limitations section
- Do not overclaim beyond implemented prototype and SilicaFold evidence
- Target: Systems security, robotics, or AI safety venue

### Step 6: Keep Proprietary Details Out of Public Repos

- Do not include proprietary implementation details in public repositories
- Keep production architecture details in internal documentation
- Public repos should contain only what is safe to disclose
- Review all commits for inadvertent disclosure before pushing

## Caution: Coordinate with Patent Counsel

**Important**: Coordinate with patent counsel before publishing claim language that goes beyond the implemented public evidence.

Patent protection requires filing before public disclosure. Once claims are published, they enter the prior art and may not be patentable. The sequence above is designed to:

1. Establish public evidence of feasibility (SilicaFold)
2. Protect broader system claims through patent filings (before VerifyCore paper)
3. Publish the full architecture paper with appropriate limitations

## Timeline Considerations

| Milestone | Dependency | Notes |
|-----------|------------|-------|
| SilicaFold tests complete | — | Required before any publication |
| SilicaFold preprint/paper | Tests complete | Establishes narrow public evidence |
| Patent provisional filed | SilicaFold evidence ready | Must precede broad VerifyCore claims |
| VerifyCore paper submitted | Patent filed | Reference SilicaFold; clear boundaries |
| TinyTapeout silicon received | Tape-out deadline | Additional post-silicon evidence |
| VerifyCore v2 paper | Silicon evidence | Update with measured hardware results |

## What Not to Do

1. **Do not publish broad VerifyCore claims before patent filing** — This could prevent patent protection
2. **Do not claim SilicaFold is "full VerifyCore"** — SilicaFold is narrow evidence
3. **Do not claim production security** — Current artifacts are research prototypes
4. **Do not publish proprietary implementation details** — Keep internal architecture private
5. **Do not skip patent counsel review** — Unreviewed public claims may be harmful

## Checklist Before Each Publication

- [ ] All claims are supported by implemented and tested evidence
- [ ] SilicaFold is referenced as narrow evidence, not full implementation
- [ ] Limitations are clearly stated
- [ ] Patent counsel has reviewed claim language (for broader claims)
- [ ] No proprietary implementation details are disclosed
- [ ] Authorship and attribution are correct
- [ ] Repository URLs and citations are accurate
