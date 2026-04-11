# OmniSyntax Static Analysis Architecture

This document reflects the current implementation in `src/static_pipeline.py` and the active integration path through `src/error_engine.py` and `src/multi_error_detector.py`.

## Active Runtime Path

- `src.error_engine.detect_errors()` routes to `src.static_pipeline.detect_errors_static()`.
- `src.multi_error_detector.detect_all_errors()` routes to `src.static_pipeline.detect_all_errors_static()` (with a small compatibility branch for legacy monkeypatch tests).
- API, CLI, and Streamlit consume the same static pipeline outputs and contracts.

## Current Pipeline

The engine executes the following stages in order:

1. Parsing
2. Symbol Table
3. Expression Evaluation
4. Control Flow
5. Semantic Analysis
6. Multi-Error Aggregation
7. Ranking
8. Confidence Calibration

This stage order is exposed by `StaticAnalysisEngine.analyze()` as `analysis_pipeline`.

## Real Data Flow

1. `Parser.parse()` builds `IRProgram` and normalized `IRStatement` entries for Python/C/C++/Java/JavaScript.
2. `SymbolBuilder.build()` creates a `SymbolTable`, collecting declarations, imports, includes, and propagated value facts.
3. `ExpressionEvaluator` computes value states (`Zero`, `NonZero`, `Unknown`, `MaybeZero`) and denominator states for division safety checks.
4. `ControlFlowAnalyzer` performs CFG-lite checks (loop truth evaluation + post-jump unreachable detection).
5. `SemanticAnalyzer` runs language-aware checks (type mismatches, missing imports/includes, undeclared identifiers, dangling pointers, invalid assignments, and parser/syntax carry-forward issues).
6. `MultiErrorAggregator.aggregate()` deduplicates and suppresses known cascades/noise.
7. `Ranker.rank()` applies priority + confidence + line tie-break ordering.
8. `ConfidenceCalibrator.score()` assigns bounded calibrated confidence per issue; `no_error()` calibrates the no-error path.

## Key Capabilities

- Expression-aware analysis with constant folding and symbol propagation.
- CFG-lite structural detection for infinite loops and unreachable code.
- Multi-error output model (`errors[]`) with ranked `primary_error` projection.
- Confidence calibration that avoids constant-confidence outputs.
- Cross-language shared IR behavior with language-specific semantic overlays.

## Validation System

- Production validation: `scripts/production_validation.py`
  - Mutation robustness
  - Real-world messy code
  - Multi-error recall
  - Cross-language consistency
  - Confidence reliability (ECE and non-constant checks)
- Adversarial validation: `scripts/adversarial_validation.py`
- Replay benchmark (regression only): `scripts/replay_mapping_audit.py`
- Regression tests: `tests/` (including `tests/test_static_pipeline_validation.py`)

## Current Performance Baseline

- Mutation accuracy: 97.08%
- Real-world accuracy: 97.3%
- Confidence ECE (production gate): 0.0391
- Production gates: passing (all required production-validation gates at 1.0)

## Known Limitations

- Remaining edge cases still exist in a small percentage of adversarial/regression scenarios.
- Control-flow logic is intentionally CFG-lite, not a full compiler-grade control-flow graph.
- Import/include inference is conservative by design and can be ambiguous for some ecosystems.
