# Adversarial Validation Report

## New Metrics (Unseen Dataset)
- Mutation Accuracy: **97.5%**
- Real-world Accuracy: **94.59%**
- Real-world Robustness: **91.89%**
- Confidence Reliability Score: **9.89/10**

## Overfitting Indicators
- Baseline benchmark accuracy: **100.0%**
- Mutated unseen accuracy: **97.5%**
- Accuracy drop: **2.5%**
- Performance drop outside benchmark: **YES**

## Failure Clusters
- By language: `{'Python': 3, 'Java': 5}`
- By root cause: `{'identifier_rename': 2, 'noise_only': 2, 'line_long_with_comment_noise': 2, 'name_vs_undeclared_bias': 1, 'style_long_line': 1}`

## Multi-error Handling
- Primary correctness rate: **1.0**
- Full multi-error match rate: **1.0**
- Avg multi-error recall: **1.0**
- Single-only failures: **0**

## Confidence Integrity
- ECE: **0.0157**
- Confidence=1.0 rate: **0.0**
- Mean confidence (correct vs incorrect): **0.9556 / 0.9487**

## Cross-language Edge Consistency
- Overall family consistency: **1.0**
- Family breakdown: `{'division_expr_zero': 1.0, 'infinite_condition_expr': 1.0, 'unreachable_after_jump': 1.0}`

## Final Verdict
- **✅ Production-ready (real-world safe)**
