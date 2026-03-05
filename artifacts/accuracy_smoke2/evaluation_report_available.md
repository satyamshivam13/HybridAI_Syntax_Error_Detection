# Exhaustive Accuracy Evaluation

- Mode: `available`
- Seed: `20260305`
- Command: `python scripts/evaluate_exhaustive_accuracy.py --seed 20260305 --grammar-per-language 20 --mutation-per-language 10 --quality-sample-size 20 --fix-sample-size 20 --compare-sample-size 20`
- Samples: `4520`
- Overall accuracy: `0.681195`
- NoError false-positive rate: `0.027778`
- API/core mismatch count: `0`
- Release recommendation: `NO-GO`

## Quality Gates
- NoError FPR <= 1%: `False`
- Critical label recall >= 95%: `False`
- API/core agreement: `True`

## API Routes
- /health: `{"status": "healthy", "version": "1.1.0", "supported_languages": ["Python", "Java", "C", "C++", "JavaScript"], "ml_model_loaded": true, "degraded_reason": null, "max_code_size": 200000, "rate_limit_per_minute": 0}`
- /check status counts: `{"200": 4520}`
- /fix status counts: `{"NaN": 4500, "200.0": 20}`
- /quality status counts: `{"NaN": 4500, "200.0": 20}`

## Model Availability Comparison
- Comparison summary: `{"actual_available_model_loaded": true, "forced_unavailable_model_loaded": false, "subset_size": 20, "accuracy_available_subset": 0.75, "accuracy_forced_unavailable_subset": 0.35}`

## Per-language Metrics
  language  samples  accuracy
         C      712  0.542135
       C++      598  0.566890
      Java      731  0.529412
JavaScript     1065  0.975587
    Python     1414  0.656294

## Per-label Metrics
               label  precision   recall       f1  support
      DivisionByZero   1.000000 0.761708 0.864738      726
 DuplicateDefinition   1.000000 0.755760 0.860892      217
         ImportError   0.966292 0.646617 0.774775      133
    IndentationError   0.986111 1.000000 0.993007       71
        InfiniteLoop   1.000000 0.780142 0.876494      141
   InvalidAssignment   1.000000 0.351695 0.520376      236
         LineTooLong   0.829268 0.790698 0.809524      129
    MissingDelimiter   0.989276 0.946154 0.967235      390
      MissingInclude   0.000000 0.000000 0.000000       85
      MutableDefault   1.000000 0.986842 0.993377       76
             NoError   0.333016 0.972222 0.496102      720
         SyntaxError   0.000000 0.000000 0.000000        0
        TypeMismatch   0.944444 0.044041 0.084158      386
      UnclosedString   1.000000 0.948718 0.973684      156
UndeclaredIdentifier   0.957746 0.260536 0.409639      261
    UnmatchedBracket   0.981273 0.996198 0.988679      263
     UnreachableCode   1.000000 0.952096 0.975460      167
      UnusedVariable   1.000000 0.238532 0.385185      327
      WildcardImport   0.971429 0.944444 0.957746       36

## Confusion Highlights
          true_label      predicted_label  count  rate_within_true_label  true_total
        TypeMismatch              NoError    369                0.955959         386
      UnusedVariable              NoError    249                0.761468         327
UndeclaredIdentifier              NoError    192                0.735632         261
      DivisionByZero              NoError    173                0.238292         726
   InvalidAssignment              NoError    149                0.631356         236
      MissingInclude              NoError     85                1.000000          85
 DuplicateDefinition              NoError     53                0.244240         217
         ImportError              NoError     42                0.315789         133
        InfiniteLoop              NoError     31                0.219858         141
         LineTooLong              NoError     26                0.201550         129
    MissingDelimiter              NoError     21                0.053846         390
             NoError          LineTooLong     20                0.027778         720
     UnreachableCode              NoError      8                0.047904         167
      UnclosedString     UnmatchedBracket      5                0.032051         156
         ImportError     MissingDelimiter      4                0.030075         133
      UnclosedString              NoError      3                0.019231         156
   InvalidAssignment UndeclaredIdentifier      3                0.012712         236
      WildcardImport          ImportError      2                0.055556          36
      MutableDefault              NoError      1                0.013158          76
         LineTooLong     IndentationError      1                0.007752         129
         ImportError       WildcardImport      1                0.007519         133
   InvalidAssignment         TypeMismatch      1                0.004237         236
UndeclaredIdentifier          ImportError      1                0.003831         261
    UnmatchedBracket          LineTooLong      1                0.003802         263

## Top Failures
           sample_id language expected_label_norm core_predicted  core_confidence                         snippet                      source_path  source_line corpus_type                        generator     seed
e748067d30a6d49688a5        C    MissingDelimiter        NoError              1.0                        continue dataset\merged\all_errors_v2.csv            3     dataset dataset/merged/all_errors_v2.csv 20260305
9609f0cadec6468ae328     Java DuplicateDefinition        NoError              1.0 int width = 3;\nint width = 96; dataset\merged\all_errors_v2.csv         2016     dataset dataset/merged/all_errors_v2.csv 20260305
3254e96ea1b4cfbf3786     Java   InvalidAssignment        NoError              1.0                  12 = distance; dataset\merged\all_errors_v2.csv         2080     dataset dataset/merged/all_errors_v2.csv 20260305
9ea5c9b88749bac4e103     Java   InvalidAssignment        NoError              1.0                   21 = sum_val; dataset\merged\all_errors_v2.csv         2079     dataset dataset/merged/all_errors_v2.csv 20260305
5e49f1a5605baf418a7c     Java   InvalidAssignment        NoError              1.0              int age = "debug"; dataset\merged\all_errors_v2.csv         2078     dataset dataset/merged/all_errors_v2.csv 20260305
c3321304c61fe4f78dbf     Java   InvalidAssignment        NoError              1.0                   57 = sum_val; dataset\merged\all_errors_v2.csv         2077     dataset dataset/merged/all_errors_v2.csv 20260305
9472738852770ef66aa5     Java   InvalidAssignment        NoError              1.0                    28 = length; dataset\merged\all_errors_v2.csv         2076     dataset dataset/merged/all_errors_v2.csv 20260305
b74a5027b4056bda2f9c     Java   InvalidAssignment        NoError              1.0            int price = "omega"; dataset\merged\all_errors_v2.csv         2075     dataset dataset/merged/all_errors_v2.csv 20260305
174790d5405293ddc722     Java   InvalidAssignment        NoError              1.0                int n = "hello"; dataset\merged\all_errors_v2.csv         2074     dataset dataset/merged/all_errors_v2.csv 20260305
48af4379f9b441eb20c4     Java   InvalidAssignment        NoError              1.0             int length = "phi"; dataset\merged\all_errors_v2.csv         2073     dataset dataset/merged/all_errors_v2.csv 20260305
e6d8a6f2f0dcb83df37b     Java   InvalidAssignment        NoError              1.0           int price = "status"; dataset\merged\all_errors_v2.csv         2072     dataset dataset/merged/all_errors_v2.csv 20260305
1cfaae34e5aad07f707c     Java   InvalidAssignment        NoError              1.0                int y = "debug"; dataset\merged\all_errors_v2.csv         2071     dataset dataset/merged/all_errors_v2.csv 20260305
78b59d96e20430690e86     Java   InvalidAssignment        NoError              1.0                    24 = amount; dataset\merged\all_errors_v2.csv         2070     dataset dataset/merged/all_errors_v2.csv 20260305
41e5027dc1dc63ce1233     Java   InvalidAssignment        NoError              1.0                    10 = volume; dataset\merged\all_errors_v2.csv         2069     dataset dataset/merged/all_errors_v2.csv 20260305
cfe318a0ffca58498e8c     Java   InvalidAssignment        NoError              1.0                 int b = "beta"; dataset\merged\all_errors_v2.csv         2068     dataset dataset/merged/all_errors_v2.csv 20260305
c2702a507656c4da8bc2     Java   InvalidAssignment        NoError              1.0                  69 = time_val; dataset\merged\all_errors_v2.csv         2067     dataset dataset/merged/all_errors_v2.csv 20260305
3e7e96a35f84a571ec97     Java   InvalidAssignment        NoError              1.0                     66 = width; dataset\merged\all_errors_v2.csv         2066     dataset dataset/merged/all_errors_v2.csv 20260305
04d3d316bee3c0e58214     Java   InvalidAssignment        NoError              1.0                      16 = area; dataset\merged\all_errors_v2.csv         2065     dataset dataset/merged/all_errors_v2.csv 20260305
421136d885ce8ef3bbe8     Java   InvalidAssignment        NoError              1.0           int sum_val = "name"; dataset\merged\all_errors_v2.csv         2064     dataset dataset/merged/all_errors_v2.csv 20260305
c5142458d3b4a6058030     Java   InvalidAssignment        NoError              1.0                     90 = price; dataset\merged\all_errors_v2.csv         2063     dataset dataset/merged/all_errors_v2.csv 20260305
