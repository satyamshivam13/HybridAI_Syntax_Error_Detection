# Adversarial Validation Report

## New Metrics (Unseen Dataset)
- Mutation Accuracy: **87.5%**
- Real-world Accuracy: **94.59%**
- Real-world Robustness: **91.89%**
- Confidence Reliability Score: **9.47/10**

## Overfitting Indicators
- Baseline benchmark accuracy: **100.0%**
- Mutated unseen accuracy: **87.5%**
- Accuracy drop: **12.5%**
- Performance drop outside benchmark: **YES**

## Failure Clusters
- By language: `{'Python': 19, 'Java': 8, 'C++': 2, 'JavaScript': 3}`
- By root cause: `{'noise_only': 21, 'identifier_rename': 3, 'importerror_nonplaceholder_name': 1, 'tuple_unpack_scalar': 2, 'array_scalar_assignment_expr': 2, 'line_long_with_comment_noise': 1, 'post_jump_statement': 1, 'asi_ambiguity': 1}`

## Multi-error Handling
- Primary correctness rate: **1.0**
- Full multi-error match rate: **1.0**
- Avg multi-error recall: **1.0**
- Single-only failures: **0**

## Confidence Integrity
- ECE: **0.0756**
- Confidence=1.0 rate: **0.0**
- Mean confidence (correct vs incorrect): **0.9569 / 0.9541**

## Cross-language Edge Consistency
- Overall family consistency: **1.0**
- Family breakdown: `{'division_expr_zero': 1.0, 'infinite_condition_expr': 1.0, 'unreachable_after_jump': 1.0}`

## Final Verdict
- **⚠️ Conditionally ready (limited scope)**
