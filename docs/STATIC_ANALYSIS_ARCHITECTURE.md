# OmniSyntax Semantic Static Analysis Architecture

## Phase 1: Reject Current Architecture

Deleted from the active path:
- Single-primary detection as the engine's internal model.
- Constant `confidence = 1.0` rule exits.
- Static import-only classification as the source of truth.

Rewritten:
- `src.error_engine.detect_errors()` now routes to `src.static_pipeline.detect_errors_static()`.
- `src.multi_error_detector.detect_all_errors()` now routes to `src.static_pipeline.detect_all_errors_static()` except for legacy monkeypatch compatibility tests.
- The active engine now uses typed IR statements, a symbol table, expression value states, CFG-lite checks, semantic analyzers, aggregation, ranking, and calibration.

Preserved:
- API/CLI/Streamlit dictionary contracts.
- Tutor explanation integration.
- Existing ML health/degraded-mode warning contract.
- Legacy helper functions only as compatibility surface, not as the active architecture.

## Phase 2: Pipeline

1. Parsing
   - Data structures: `IRProgram`, `IRStatement`.
   - Algorithms: Python AST parse; C/Java/C++/JavaScript lightweight statement parser with balanced string/comment handling.
   - Shared: normalized statement kinds such as `assignment`, `definition`, `loop`, `jump`, `import`, `include`.
   - Language-specific: Python AST extraction; C-like delimiter/bracket/string handling.
   - Resolves: benchmark overfitting to surface regexes and brittle single-language control flow.

2. Symbol Table
   - Data structures: `SymbolTable`, `Symbol`.
   - Algorithms: declaration/import/include/function/parameter collection and value propagation.
   - Shared: `symbols`, `imports`, `includes`.
   - Language-specific: Python builtins, JS globals, C/C++ includes, Java imports.
   - Resolves: MissingImport versus NameError confusion and undeclared identifier cascades.

3. Expression Evaluation
   - Data structures: `ValueFact`, `ValueState` with `Zero`, `NonZero`, `Unknown`, `MaybeZero`.
   - Algorithms: constant folding, boolean/comparison evaluation, variable value propagation, denominator state extraction.
   - Shared: Python AST expression evaluation after C-like expression normalization.
   - Resolves: non-literal zero failures such as `(2-2)` and aliases like `d = 0; x / d`.

4. Control Flow
   - Data structures: block IDs attached to `IRStatement`.
   - Algorithms: CFG-lite post-jump reachability and loop truth evaluation.
   - Shared: `jump` and `loop` IR nodes.
   - Language-specific: finite C-like `for` updates are not treated as infinite.
   - Resolves: heuristic loop detection and post-return unreachable code failures.

5. Semantic Analysis
   - Data structures: `AnalysisIssue`, `Evidence`.
   - Algorithms: type compatibility, import/include resolution, dangling pointer lifetime, invalid assignment shape, line expansion.
   - Shared: common issue model and evidence scoring.
   - Language-specific: Python annotations/defaults, Java standard imports, C/C++ headers, JS ASI tolerance.
   - Resolves: rule-only semantic blind spots.

6. Multi-Error Aggregation
   - Data structures: issue lists plus grouped `errors[]`.
   - Algorithms: key-based deduplication and provable causal suppression.
   - Shared: all detections return `errors[]`; `primary_error` is only a ranked view.
   - Resolves: single-error API dominance.

7. Ranking
   - Data structures: ordered priority table plus confidence and location tie-breaks.
   - Algorithms: stable primary selection over aggregated findings.
   - Resolves: unstable mixed-error precedence.

8. Confidence Calibration
   - Data structures: calibration bins and evidence strengths.
   - Algorithms: evidence combination with ambiguity/overlap penalties and bounded calibrated outputs.
   - Shared: every issue receives calibrated confidence; NoError receives calibrated confidence.
   - Resolves: fake constant `1.0` confidence.

## Phase 3: Implemented Core

Implemented in `src/static_pipeline.py`:
- Expression evaluator with arithmetic, boolean, comparison folding, alias propagation, and denominator extraction.
- CFG-lite block tracking, loop truth evaluation, and unreachable detection.
- Import/include resolver chain for Python modules, Java standard imports, and C/C++ standard headers with unknown fallback behavior.
- Multi-error aggregation with deduplication and causal suppression for string/bracket and missing-include/undeclared cascades.
- Shared IR spanning Python, Java, C, C++, and JavaScript.
- Evidence-based confidence calibration with no default `1.0`.

## Phase 4: Validation System

Implemented:
- `scripts/production_validation.py`
  - Mutation robustness gate.
  - Real-world messy code gate.
  - Multi-error recall gate.
  - Cross-language consistency gate.
  - Confidence ECE and non-constant confidence gate.
- `tests/test_static_pipeline_validation.py`
  - Regression coverage for confidence ECE and required pipeline stages.

The original 240-case benchmark is replayed with `scripts/replay_mapping_audit.py` and treated as regression coverage only.

## Phase 5: Batch Results

Batch 1: Expression evaluator + loop condition fixes
- Implemented constant folding and symbol propagation.
- Added CFG loop condition truth evaluation.
- Result: production validation mutation suite passes; adversarial mutation improved from the given 86.25% baseline to 87.5%, but remains below 95%.

Batch 2: Multi-error system redesign
- `detect_all_errors()` now always returns grouped `errors[]`.
- `detect_errors()` exposes `primary_error` as ranked view.
- Result: production multi-error recall suite passes at 1.0.

Batch 3: CFG-lite + unreachable detection
- Added block IDs, post-jump checks, and finite `for` handling.
- Result: production cross-language consistency suite passes at 1.0.

Batch 4: Import resolver redesign
- Added resolver paths for Python modules, Java imports, C/C++ headers, and unknown fallback.
- Result: real-world messy suite passes at 1.0; adversarial real-world accuracy is 94.59%.

Batch 5: Confidence calibration
- Replaced constant confidence with evidence and calibration bins.
- Result: production ECE is 0.0385 and confidence is not constant.

Batch 6: Cross-language consistency via IR
- Shared `IRStatement` and semantic stages across all supported languages.
- Result: production cross-language consistency suite is 1.0.

## Validation Results

Latest commands:
- `python -m pytest tests/ -q -p no:cacheprovider`
  - 168 passed, 1 skipped, 1 xfailed.
- `python scripts/replay_mapping_audit.py --dataset artifacts/qa/mapping_audit_2026-04-11.json --output artifacts/qa/replay-static-pipeline.json`
  - 211/240 passed.
  - Accuracy score: 8.79/10.
  - Production-readiness score: 8.31/10.
- `python scripts/adversarial_validation.py`
  - Mutation accuracy: 87.5%.
  - Real-world accuracy: 94.59%.
  - Confidence reliability: 9.47.
  - Verdict: CONDITIONALLY_READY.
- `python scripts/production_validation.py`
  - Mutation robustness: 1.0.
  - Real-world messy accuracy: 1.0.
  - Multi-error recall: 1.0.
  - Cross-language consistency: 1.0.
  - Confidence ECE: 0.0385.
  - Confidence constant: false.

## Remaining Risks

- Broader adversarial mutation accuracy is 87.5%, below the required 95%.
- Legacy replay still has 29 failures; the benchmark is not a production proof, but it shows unsupported edges remain.
- C-like parsing is CFG-lite, not a full compiler front end.
- Import resolution is structural and conservative; package ecosystem ambiguity remains.
- Confidence calibration uses shipped bins, not a trained calibration artifact.

## Final Verdict

NOT READY.

The new architecture eliminates the identified root causes in the active engine path and passes the newly implemented production validation suites, but the broader adversarial mutation result does not meet the required 95% production criterion.
