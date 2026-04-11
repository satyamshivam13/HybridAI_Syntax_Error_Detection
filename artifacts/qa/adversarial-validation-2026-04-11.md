# Adversarial Validation Report

## New Metrics (Unseen Dataset)
- Mutation Accuracy: **86.25%**
- Real-world Accuracy: **48.65%**
- Real-world Robustness: **22.97%**
- Confidence Reliability Score: **8.24/10**

## Overfitting Indicators
- Baseline benchmark accuracy: **100.0%**
- Mutated unseen accuracy: **86.25%**
- Accuracy drop: **13.75%**
- Performance drop outside benchmark: **YES**

## Failure Clusters
- By language: `{'Python': 23, 'Java': 10, 'C': 6, 'C++': 6, 'JavaScript': 7}`
- By root cause: `{'identifier_rename': 2, 'nonliteral_zero': 11, 'importerror_nonplaceholder_name': 5, 'unknown_import_symbol_set': 3, 'equivalent_loop_condition': 8, 'line_long_via_expression': 3, 'tuple_unpack_scalar': 2, 'array_scalar_assignment_expr': 2, 'static_import_dictionary_gap': 1, 'literal_only_zero_detector': 5, 'rigid_loop_pattern': 4, 'java_import_symbol_gap': 1, 'post_jump_statement': 3, 'lifetime_static_pattern': 1, 'asi_ambiguity': 1}`

## Multi-error Handling
- Primary correctness rate: **1.0**
- Full multi-error match rate: **0.0**
- Avg multi-error recall: **0.433**
- Single-only failures: **3**

## Confidence Integrity
- ECE: **0.1877**
- Confidence=1.0 rate: **1.0**
- Mean confidence (correct vs incorrect): **1.0 / 1.0**

## Cross-language Edge Consistency
- Overall family consistency: **0.083**
- Family breakdown: `{'division_expr_zero': 0.0, 'infinite_condition_expr': 0.0, 'unreachable_after_jump': 0.25}`

## Final Verdict
- **❌ Overfitted / unsafe**
