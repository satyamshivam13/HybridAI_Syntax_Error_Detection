# Exhaustive Accuracy Evaluation

- Mode: `unavailable`
- Seed: `20260305`
- Command: `python scripts/evaluate_exhaustive_accuracy.py --seed 20260305 --grammar-per-language 10000 --mutation-per-language 2500 --quality-sample-size 5000 --compare-sample-size 5000`
- Samples: `61580`
- Overall accuracy: `0.890305`
- NoError false-positive rate: `0.000059`
- API/core mismatch count: `0`
- Release recommendation: `NO-GO`

## Quality Gates
- NoError FPR <= 1%: `True`
- Critical label recall >= 95%: `False`
- API/core agreement: `True`

## API Routes
- /health: `{"status": "degraded", "version": "1.1.0", "supported_languages": ["Python", "Java", "C", "C++", "JavaScript"], "ml_model_loaded": false, "degraded_reason": "syntax_error_model.pkl: No module named 'sklearn.ensemble._gb_losses' | error_classifier.pkl: [Errno 2] No such file or directory: 'models\\\\tfidf.pkl'", "max_code_size": 200000, "rate_limit_per_minute": 0}`
- /check status counts: `{"200": 61580}`
- /fix status counts: `{"200": 61580}`
- /quality status counts: `{"NaN": 56580, "200.0": 5000}`

## Model Availability Comparison
- Comparison summary: `{"actual_unavailable_model_loaded": false, "simulated_available_model_loaded": false, "subset_size": 5000, "accuracy_unavailable_subset": 0.8928, "accuracy_simulated_available_subset": 0.9022}`

## Per-language Metrics
  language  samples  accuracy
         C    12144  0.898304
       C++    12034  0.903025
      Java    12091  0.898602
JavaScript    12130  0.850453
    Python    13181  0.900387

## Per-label Metrics
               label  precision   recall       f1  support
      DivisionByZero   0.000000 0.000000 0.000000      726
 DuplicateDefinition   0.000000 0.000000 0.000000      217
         ImportError   0.000000 0.000000 0.000000      856
    IndentationError   0.997743 1.000000 0.998870      442
        InfiniteLoop   0.000000 0.000000 0.000000      141
   InvalidAssignment   0.000000 0.000000 0.000000      236
         LineTooLong   0.000000 0.000000 0.000000      129
    MissingDelimiter   1.000000 0.294971 0.455563     2207
      MissingInclude   0.000000 0.000000 0.000000      805
      MutableDefault   0.000000 0.000000 0.000000       76
             NoError   0.883492 0.999941 0.938116    50620
         SyntaxError   0.000000 0.000000 0.000000        0
        TypeMismatch   0.000000 0.000000 0.000000      386
      UnclosedString   1.000000 0.802735 0.890575     1901
UndeclaredIdentifier   0.000000 0.000000 0.000000      261
    UnmatchedBracket   0.994991 0.776258 0.872119     2047
     UnreachableCode   0.000000 0.000000 0.000000      167
      UnusedVariable   0.000000 0.000000 0.000000      327
      WildcardImport   0.000000 0.000000 0.000000       36

## Confusion Highlights
          true_label  predicted_label  count  rate_within_true_label  true_total
    MissingDelimiter          NoError   1556                0.705029        2207
         ImportError          NoError    856                1.000000         856
      MissingInclude          NoError    805                1.000000         805
      DivisionByZero          NoError    726                1.000000         726
    UnmatchedBracket          NoError    458                0.223742        2047
        TypeMismatch          NoError    386                1.000000         386
      UnclosedString          NoError    370                0.194634        1901
      UnusedVariable          NoError    327                1.000000         327
UndeclaredIdentifier          NoError    261                1.000000         261
 DuplicateDefinition          NoError    217                1.000000         217
     UnreachableCode          NoError    167                1.000000         167
   InvalidAssignment          NoError    165                0.699153         236
        InfiniteLoop          NoError    141                1.000000         141
         LineTooLong          NoError    128                0.992248         129
      MutableDefault          NoError     76                1.000000          76
   InvalidAssignment      SyntaxError     71                0.300847         236
      WildcardImport          NoError     36                1.000000          36
      UnclosedString UnmatchedBracket      5                0.002630        1901
             NoError UnmatchedBracket      3                0.000059       50620
         LineTooLong IndentationError      1                0.007752         129

## Top Failures
           sample_id language expected_label_norm core_predicted  core_confidence                                                                                                                                                                                                                        snippet                                 source_path  source_line      corpus_type                        generator     seed
deb6f5f885684c82116f   Python      DivisionByZero        NoError              1.0                                                                                                                                                                                                                     x = 10 / 0            dataset\merged\all_errors_v2.csv            2          dataset dataset/merged/all_errors_v2.csv 20260305
798ab36a4eaf438170f8     Java         ImportError        NoError              1.0                                                                                                                               public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n    generated://mutation/Java/import_variant         2114 mutation_invalid          mutation:import_variant 20260406
13e3da19d2e367165f8f     Java    MissingDelimiter        NoError              1.0 public class Main {\n  static int f_26(int x) { int total = x + 1082; for(int j=0;j<5;j++){ total += j; } return total; }\n  public static void main(String[] args) { int v94 = f_26(549) System.out.println(v94 + 1382); }\n} generated://mutation/Java/semicolon_removal         1732 mutation_invalid       mutation:semicolon_removal 20260406
b5aa86310a6d063e7e2a     Java         ImportError        NoError              1.0                                                                                                                               public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n    generated://mutation/Java/import_variant         1729 mutation_invalid          mutation:import_variant 20260406
8d100ae8280e31c10feb     Java         ImportError        NoError              1.0                                                                                                                               public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n    generated://mutation/Java/import_variant         1727 mutation_invalid          mutation:import_variant 20260406
49d349c9b350b96dc765     Java         ImportError        NoError              1.0                                                                                                                               public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n    generated://mutation/Java/import_variant         1722 mutation_invalid          mutation:import_variant 20260406
a57ac75a142d6cc1cb82     Java    MissingDelimiter        NoError              1.0     public class Main {\n  static int f_7(int x) { int total = x + 351; for(int j=0;j<2;j++){ total += j; } return total; }\n  public static void main(String[] args) { int v30 = f_7(150) System.out.println(v30 + 600); }\n} generated://mutation/Java/semicolon_removal         1721 mutation_invalid       mutation:semicolon_removal 20260406
161469a0208b8e71eefe     Java    MissingDelimiter        NoError              1.0    public class Main {\n  static int f_6(int x) { int total = x + 503; for(int j=0;j<3;j++){ total += j; } return total; }\n  public static void main(String[] args) { int v87 = f_6(1444) System.out.println(v87 + 977); }\n} generated://mutation/Java/semicolon_removal         1715 mutation_invalid       mutation:semicolon_removal 20260406
62359da5f32570fb3fe5     Java    MissingDelimiter        NoError              1.0 public class Main {\n  static int f_11(int x) { int total = x + 754; for(int j=0;j<4;j++){ total += j; } return total; }\n  public static void main(String[] args) { int v38 = f_11(1602) System.out.println(v38 + 1521); }\n} generated://mutation/Java/semicolon_removal         1713 mutation_invalid       mutation:semicolon_removal 20260406
ef00d662cbc57551beaf     Java         ImportError        NoError              1.0                                                                                                                               public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n    generated://mutation/Java/import_variant         1705 mutation_invalid          mutation:import_variant 20260406
e69b7a16162adad0a1d2     Java         ImportError        NoError              1.0                                                                                                                               public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n    generated://mutation/Java/import_variant         1703 mutation_invalid          mutation:import_variant 20260406
d5cac3c211e32a20d74f     Java         ImportError        NoError              1.0                                                                                                                               public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n    generated://mutation/Java/import_variant         1697 mutation_invalid          mutation:import_variant 20260406
1c149959c2597add3789     Java         ImportError        NoError              1.0                                                                                                                               public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n    generated://mutation/Java/import_variant         1696 mutation_invalid          mutation:import_variant 20260406
26d3adc5c286c7693e15     Java         ImportError        NoError              1.0                                                                                                                               public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n    generated://mutation/Java/import_variant         1693 mutation_invalid          mutation:import_variant 20260406
f4e2b08ce20574345485     Java         ImportError        NoError              1.0                                                                                                                               public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n    generated://mutation/Java/import_variant         1691 mutation_invalid          mutation:import_variant 20260406
5bdf11fe66db4787b8fa     Java         ImportError        NoError              1.0                                                                                                                               public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n    generated://mutation/Java/import_variant         1689 mutation_invalid          mutation:import_variant 20260406
fc72e845af1ae5d5d9cd     Java    MissingDelimiter        NoError              1.0  public class Main {\n  static int f_30(int x) { int total = x + 557; for(int j=0;j<3;j++){ total += j; } return total; }\n  public static void main(String[] args) { int v67 = f_30(320) System.out.println(v67 + 1405); }\n} generated://mutation/Java/semicolon_removal         1687 mutation_invalid       mutation:semicolon_removal 20260406
fcd93e16f9091c2a4d9e     Java    MissingDelimiter        NoError              1.0  public class Main {\n  static int f_16(int x) { int total = x + 1370; for(int j=0;j<1;j++){ total += j; } return total; }\n  public static void main(String[] args) { int v61 = f_16(506) System.out.println(v61 + 233); }\n} generated://mutation/Java/semicolon_removal         1685 mutation_invalid       mutation:semicolon_removal 20260406
a84aead776abf54de3e2     Java    MissingDelimiter        NoError              1.0   public class Main {\n  static int f_27(int x) { int total = x + 451; for(int j=0;j<5;j++){ total += j; } return total; }\n  public static void main(String[] args) { int v47 = f_27(830) System.out.println(v47 + 553); }\n} generated://mutation/Java/semicolon_removal         1682 mutation_invalid       mutation:semicolon_removal 20260406
49afcb521f489f050f9e     Java    MissingDelimiter        NoError              1.0 public class Main {\n  static int f_33(int x) { int total = x + 1409; for(int j=0;j<5;j++){ total += j; } return total; }\n  public static void main(String[] args) { int v74 = f_33(454) System.out.println(v74 + 1416); }\n} generated://mutation/Java/semicolon_removal         1733 mutation_invalid       mutation:semicolon_removal 20260406
