# OmniSyntax v1.1 Requirements

## Milestone Goal

Close the remaining reliability gaps in Python and Java without regressing the shared API, CLI, and Streamlit contracts established in v1.0.

## Requirements

### Detection Reliability
- [ ] **DET-01**: Users can get Python semantic findings in `--all-errors` mode when ML inference is available and confident enough to contribute useful results.
- [ ] **DET-02**: Users do not see the misleading Java `UndeclaredIdentifier` false positive when `TypeMismatch` is the actual primary issue in mixed-error cases.

### Autofix Precision
- [ ] **FIX-01**: Users receive a more precise `IndentationError` fix suggestion that targets the correct indentation location.
- [ ] **FIX-02**: Users receive a more precise `UnclosedString` fix suggestion that closes the string in the most helpful location.

### Regression Coverage
- [ ] **QA-01**: Users can rely on automated regression coverage for the repaired Python and Java scenarios across the supported entry points.

## Future Requirements

- New language support beyond Python, Java, C, C++, and JavaScript.
- Full compiler replacement or parser rewrite for every supported language.
- Hosted SaaS, user accounts, or classroom-management features.

## Out of Scope

- Reworking the existing API, CLI, or Streamlit interfaces beyond what is needed to preserve parity with the fixed scenarios.
- Replacing the hybrid detector architecture.
- Broad model retraining or new ML architecture work unrelated to the listed reliability gaps.

## Traceability

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| DET-01 | Phase 6 | Planned |
| DET-02 | Phase 6 | Planned |
| FIX-01 | Phase 6 | Planned |
| FIX-02 | Phase 6 | Planned |
| QA-01 | Phase 6 | Planned |
