# Exhaustive Accuracy Evaluation

- Mode: `unavailable`
- Seed: `20260305`
- Command: `python scripts/evaluate_exhaustive_accuracy.py --seed 20260305 --grammar-per-language 20 --mutation-per-language 10 --quality-sample-size 20 --compare-sample-size 20`
- Samples: `4520`
- Overall accuracy: `0.307301`
- NoError false-positive rate: `0.004167`
- API/core mismatch count: `0`
- Release recommendation: `NO-GO`

## Quality Gates
- NoError FPR <= 1%: `True`
- Critical label recall >= 95%: `False`
- API/core agreement: `True`

## API Routes
- /health: `{"status": "degraded", "version": "1.1.0", "supported_languages": ["Python", "Java", "C", "C++", "JavaScript"], "ml_model_loaded": false, "degraded_reason": "syntax_error_model.pkl: No module named 'sklearn.ensemble._gb_losses' | error_classifier.pkl: [Errno 2] No such file or directory: 'models\\\\tfidf.pkl'", "max_code_size": 200000, "rate_limit_per_minute": 0}`
- /check status counts: `{"200": 4520}`
- /fix status counts: `{"200": 4520}`
- /quality status counts: `{"NaN": 4500, "200.0": 20}`

## Model Availability Comparison
- Comparison summary: `{"actual_unavailable_model_loaded": false, "simulated_available_model_loaded": false, "subset_size": 20, "accuracy_unavailable_subset": 0.35, "accuracy_simulated_available_subset": 0.6}`

## Per-language Metrics
  language  samples  accuracy
         C      712  0.282303
       C++      598  0.294314
      Java      731  0.298222
JavaScript     1065  0.315493
    Python     1414  0.323904

## Per-label Metrics
               label  precision   recall       f1  support
      DivisionByZero   0.000000 0.000000 0.000000      726
 DuplicateDefinition   0.000000 0.000000 0.000000      217
         ImportError   0.000000 0.000000 0.000000      133
    IndentationError   0.986111 1.000000 0.993007       71
        InfiniteLoop   0.000000 0.000000 0.000000      141
   InvalidAssignment   0.000000 0.000000 0.000000      236
         LineTooLong   0.000000 0.000000 0.000000      129
    MissingDelimiter   1.000000 0.738462 0.849558      390
      MissingInclude   0.000000 0.000000 0.000000       85
      MutableDefault   0.000000 0.000000 0.000000       76
             NoError   0.190287 0.995833 0.319519      720
         SyntaxError   0.000000 0.000000 0.000000        0
        TypeMismatch   0.000000 0.000000 0.000000      386
      UnclosedString   1.000000 0.878205 0.935154      156
UndeclaredIdentifier   0.000000 0.000000 0.000000      261
    UnmatchedBracket   0.956522 0.669202 0.787472      263
     UnreachableCode   0.000000 0.000000 0.000000      167
      UnusedVariable   0.000000 0.000000 0.000000      327
      WildcardImport   0.000000 0.000000 0.000000       36

## Confusion Highlights
          true_label  predicted_label  count  rate_within_true_label  true_total
      DivisionByZero          NoError    726                1.000000         726
        TypeMismatch          NoError    386                1.000000         386
      UnusedVariable          NoError    327                1.000000         327
UndeclaredIdentifier          NoError    261                1.000000         261
 DuplicateDefinition          NoError    217                1.000000         217
     UnreachableCode          NoError    167                1.000000         167
   InvalidAssignment          NoError    165                0.699153         236
        InfiniteLoop          NoError    141                1.000000         141
         ImportError          NoError    133                1.000000         133
         LineTooLong          NoError    128                0.992248         129
    MissingDelimiter          NoError    102                0.261538         390
    UnmatchedBracket          NoError     87                0.330798         263
      MissingInclude          NoError     85                1.000000          85
      MutableDefault          NoError     76                1.000000          76
   InvalidAssignment      SyntaxError     71                0.300847         236
      WildcardImport          NoError     36                1.000000          36
      UnclosedString          NoError     14                0.089744         156
      UnclosedString UnmatchedBracket      5                0.032051         156
             NoError UnmatchedBracket      3                0.004167         720
         LineTooLong IndentationError      1                0.007752         129

## Top Failures
           sample_id language expected_label_norm core_predicted  core_confidence                                        snippet                      source_path  source_line corpus_type                        generator     seed
deb6f5f885684c82116f   Python      DivisionByZero        NoError              1.0                                     x = 10 / 0 dataset\merged\all_errors_v2.csv            2     dataset dataset/merged/all_errors_v2.csv 20260305
e901626dbf65c74ea47b     Java     UnreachableCode        NoError              1.0            return 54;\nSystem.out.println(86); dataset\merged\all_errors_v2.csv         2129     dataset dataset/merged/all_errors_v2.csv 20260305
0b091af0ee1431be773c     Java     UnreachableCode        NoError              1.0                break;\nSystem.out.println(63); dataset\merged\all_errors_v2.csv         2131     dataset dataset/merged/all_errors_v2.csv 20260305
ab272f0db53b3f7c85ef     Java     UnreachableCode        NoError              1.0            return 78;\nSystem.out.println(67); dataset\merged\all_errors_v2.csv         2132     dataset dataset/merged/all_errors_v2.csv 20260305
d7a57dfff78ba3b82d03     Java     UnreachableCode        NoError              1.0            return 76;\nSystem.out.println(83); dataset\merged\all_errors_v2.csv         2133     dataset dataset/merged/all_errors_v2.csv 20260305
5774e41f0fd4364980f4     Java     UnreachableCode        NoError              1.0                break;\nSystem.out.println(78); dataset\merged\all_errors_v2.csv         2134     dataset dataset/merged/all_errors_v2.csv 20260305
d7f6ce667b6ae885dc4b     Java     UnreachableCode        NoError              1.0                break;\nSystem.out.println(83); dataset\merged\all_errors_v2.csv         2135     dataset dataset/merged/all_errors_v2.csv 20260305
1af34d15a082d9697938     Java     UnreachableCode        NoError              1.0                break;\nSystem.out.println(81); dataset\merged\all_errors_v2.csv         2136     dataset dataset/merged/all_errors_v2.csv 20260305
e49936cb73db0f6b0e42     Java     UnreachableCode        NoError              1.0                break;\nSystem.out.println(24); dataset\merged\all_errors_v2.csv         2137     dataset dataset/merged/all_errors_v2.csv 20260305
c5ce9ba19145d27316e9     Java      UnusedVariable        NoError              1.0 int sum_val = 64;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2199     dataset dataset/merged/all_errors_v2.csv 20260305
9fb7b4414adc67157446     Java      UnusedVariable        NoError              1.0 int sum_val = 74;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2200     dataset dataset/merged/all_errors_v2.csv 20260305
c366ee386e3d906bb9a1     Java      UnusedVariable        NoError              1.0        int x = 6;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2201     dataset dataset/merged/all_errors_v2.csv 20260305
34f1dd297c4a25f427d6     Java      UnusedVariable        NoError              1.0  int height = 27;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2202     dataset dataset/merged/all_errors_v2.csv 20260305
8aef5e5585de2fe1cc4f     Java      UnusedVariable        NoError              1.0       int m = 38;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2203     dataset dataset/merged/all_errors_v2.csv 20260305
8b44748150909339475b     Java      UnusedVariable        NoError              1.0       int x = 31;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2204     dataset dataset/merged/all_errors_v2.csv 20260305
0d8f72bc4aed4b5e9d99     Java      UnusedVariable        NoError              1.0  int amount = 23;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2205     dataset dataset/merged/all_errors_v2.csv 20260305
ea984a37255f9bbd875e     Java      UnusedVariable        NoError              1.0  int height = 30;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2206     dataset dataset/merged/all_errors_v2.csv 20260305
f1369463d5904aafb979     Java     UnreachableCode        NoError              1.0                break;\nSystem.out.println(64); dataset\merged\all_errors_v2.csv         2130     dataset dataset/merged/all_errors_v2.csv 20260305
dd4afcc531ad029f3344     Java     UnreachableCode        NoError              1.0                break;\nSystem.out.println(82); dataset\merged\all_errors_v2.csv         2128     dataset dataset/merged/all_errors_v2.csv 20260305
4f9a7390c1f673c8ae2f     Java      UnusedVariable        NoError              1.0       int z = 20;\nSystem.out.println("done"); dataset\merged\all_errors_v2.csv         2208     dataset dataset/merged/all_errors_v2.csv 20260305
