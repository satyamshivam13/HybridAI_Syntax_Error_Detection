# Exhaustive Accuracy Evaluation

- Mode: `available`
- Seed: `20260305`
- Command: `python scripts/evaluate_exhaustive_accuracy.py --seed 20260305 --grammar-per-language 200 --mutation-per-language 50 --quality-sample-size 50 --fix-sample-size 50 --compare-sample-size 100`
- Samples: `5552`
- Overall accuracy: `0.734510`
- NoError false-positive rate: `0.000000`
- API/core mismatch count: `0`
- Release recommendation: `NO-GO`

## Quality Gates
- NoError FPR <= 1%: `True`
- Critical label recall >= 95%: `False`
- API/core agreement: `True`

## API Routes
- /health: `{"status": "healthy", "version": "1.1.0", "supported_languages": ["Python", "Java", "C", "C++", "JavaScript"], "ml_model_loaded": true, "degraded_reason": null, "max_code_size": 200000, "rate_limit_per_minute": 0}`
- /check status counts: `{"200": 5552}`
- /fix status counts: `{"NaN": 5502, "200.0": 50}`
- /quality status counts: `{"NaN": 5502, "200.0": 50}`

## Model Availability Comparison
- Comparison summary: `{"actual_available_model_loaded": true, "forced_unavailable_model_loaded": false, "subset_size": 100, "accuracy_available_subset": 0.77, "accuracy_forced_unavailable_subset": 0.41}`

## Per-language Metrics
  language  samples  accuracy
         C      920  0.641304
       C++      802  0.667082
      Java      932  0.623391
JavaScript     1273  0.973291
    Python     1625  0.697231

## Per-label Metrics
               label  precision   recall       f1  support
      DivisionByZero   1.000000 0.761708 0.864738      726
 DuplicateDefinition   1.000000 0.755760 0.860892      217
         ImportError   0.966292 0.589041 0.731915      146
    IndentationError   0.987654 1.000000 0.993789       80
        InfiniteLoop   1.000000 0.780142 0.876494      141
   InvalidAssignment   1.000000 0.351695 0.520376      236
         LineTooLong   1.000000 0.790698 0.883117      129
    MissingDelimiter   0.972431 0.921615 0.946341      421
      MissingInclude   0.000000 0.000000 0.000000       92
      MutableDefault   1.000000 0.986842 0.993377       76
             NoError   0.528376 1.000000 0.691421     1620
         SyntaxError   0.000000 0.000000 0.000000        0
        TypeMismatch   0.944444 0.044041 0.084158      386
      UnclosedString   1.000000 0.882051 0.937330      195
UndeclaredIdentifier   0.957746 0.260536 0.409639      261
    UnmatchedBracket   0.982993 0.976351 0.979661      296
     UnreachableCode   1.000000 0.952096 0.975460      167
      UnusedVariable   0.962963 0.238532 0.382353      327
      WildcardImport   0.971429 0.944444 0.957746       36

## Confusion Highlights
          true_label      predicted_label  count  rate_within_true_label  true_total
        TypeMismatch              NoError    369                0.955959         386
      UnusedVariable              NoError    249                0.761468         327
UndeclaredIdentifier              NoError    192                0.735632         261
      DivisionByZero              NoError    173                0.238292         726
   InvalidAssignment              NoError    149                0.631356         236
      MissingInclude              NoError     92                1.000000          92
 DuplicateDefinition              NoError     53                0.244240         217
         ImportError              NoError     48                0.328767         146
    MissingDelimiter              NoError     33                0.078385         421
        InfiniteLoop              NoError     31                0.219858         141
         LineTooLong              NoError     26                0.201550         129
      UnclosedString              NoError     15                0.076923         195
         ImportError     MissingDelimiter     11                0.075342         146
     UnreachableCode              NoError      8                0.047904         167
    UnmatchedBracket              NoError      7                0.023649         296
      UnclosedString     UnmatchedBracket      5                0.025641         195
      UnclosedString       UnusedVariable      3                0.015385         195
   InvalidAssignment UndeclaredIdentifier      3                0.012712         236
      WildcardImport          ImportError      2                0.055556          36
      MutableDefault              NoError      1                0.013158          76
         LineTooLong     IndentationError      1                0.007752         129
         ImportError       WildcardImport      1                0.006849         146
   InvalidAssignment         TypeMismatch      1                0.004237         236
UndeclaredIdentifier          ImportError      1                0.003831         261

## Top Failures
           sample_id language expected_label_norm core_predicted  core_confidence                                        snippet                      source_path  source_line corpus_type                        generator     seed
e748067d30a6d49688a5        C    MissingDelimiter        NoError              1.0                                       continue dataset\merged\all_errors_v2.csv            3     dataset dataset/merged/all_errors_v2.csv 20260305
c3321304c61fe4f78dbf     Java   InvalidAssignment        NoError              1.0                                  57 = sum_val; dataset\merged\all_errors_v2.csv         2077     dataset dataset/merged/all_errors_v2.csv 20260305
f6ddd574f9bd9d6d9b61     Java      UnusedVariable        NoError              1.0     int idx = 55;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2211     dataset dataset/merged/all_errors_v2.csv 20260305
a8b1fcf81c8b6b283230     Java      UnusedVariable        NoError              1.0    int data = 80;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2210     dataset dataset/merged/all_errors_v2.csv 20260305
21f143948e95989a952e     Java      UnusedVariable        NoError              1.0     int num = 77;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2209     dataset dataset/merged/all_errors_v2.csv 20260305
4f9a7390c1f673c8ae2f     Java      UnusedVariable        NoError              1.0       int z = 20;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2208     dataset dataset/merged/all_errors_v2.csv 20260305
5ee0dd98cc92f3392fde     Java      UnusedVariable        NoError              1.0   int width = 52;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2207     dataset dataset/merged/all_errors_v2.csv 20260305
ea984a37255f9bbd875e     Java      UnusedVariable        NoError              1.0  int height = 30;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2206     dataset dataset/merged/all_errors_v2.csv 20260305
0d8f72bc4aed4b5e9d99     Java      UnusedVariable        NoError              1.0  int amount = 23;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2205     dataset dataset/merged/all_errors_v2.csv 20260305
8b44748150909339475b     Java      UnusedVariable        NoError              1.0       int x = 31;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2204     dataset dataset/merged/all_errors_v2.csv 20260305
8aef5e5585de2fe1cc4f     Java      UnusedVariable        NoError              1.0       int m = 38;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2203     dataset dataset/merged/all_errors_v2.csv 20260305
34f1dd297c4a25f427d6     Java      UnusedVariable        NoError              1.0  int height = 27;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2202     dataset dataset/merged/all_errors_v2.csv 20260305
c366ee386e3d906bb9a1     Java      UnusedVariable        NoError              1.0        int x = 6;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2201     dataset dataset/merged/all_errors_v2.csv 20260305
9fb7b4414adc67157446     Java      UnusedVariable        NoError              1.0 int sum_val = 74;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2200     dataset dataset/merged/all_errors_v2.csv 20260305
c5ce9ba19145d27316e9     Java      UnusedVariable        NoError              1.0 int sum_val = 64;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2199     dataset dataset/merged/all_errors_v2.csv 20260305
6d031e907ca4a0f92acf     Java   InvalidAssignment        NoError              1.0                                      67 = num; dataset\merged\all_errors_v2.csv         2084     dataset dataset/merged/all_errors_v2.csv 20260305
1b990515bf80693add91     Java   InvalidAssignment        NoError              1.0                            int height = "phi"; dataset\merged\all_errors_v2.csv         2083     dataset dataset/merged/all_errors_v2.csv 20260305
03da599a46c8e071c72b     Java   InvalidAssignment        NoError              1.0                           int length = "info"; dataset\merged\all_errors_v2.csv         2082     dataset dataset/merged/all_errors_v2.csv 20260305
fb4519fc1d0318c1dbd8     Java   InvalidAssignment        NoError              1.0                         int distance = "data"; dataset\merged\all_errors_v2.csv         2081     dataset dataset/merged/all_errors_v2.csv 20260305
3254e96ea1b4cfbf3786     Java   InvalidAssignment        NoError              1.0                                 12 = distance; dataset\merged\all_errors_v2.csv         2080     dataset dataset/merged/all_errors_v2.csv 20260305
