# Exhaustive Accuracy Evaluation

- Mode: `available`
- Seed: `20260305`
- Command: `python scripts/evaluate_exhaustive_accuracy.py --seed 20260305 --grammar-per-language 10000 --mutation-per-language 2500 --quality-sample-size 5000 --fix-sample-size 5000 --compare-sample-size 5000`
- Samples: `61580`
- Overall accuracy: `0.941832`
- NoError false-positive rate: `0.000000`
- API/core mismatch count: `0`
- Release recommendation: `NO-GO`

## Quality Gates
- NoError FPR <= 1%: `True`
- Critical label recall >= 95%: `False`
- API/core agreement: `True`

## API Routes
- /health: `{"status": "healthy", "version": "1.1.0", "supported_languages": ["Python", "Java", "C", "C++", "JavaScript"], "ml_model_loaded": true, "degraded_reason": null, "max_code_size": 200000, "rate_limit_per_minute": 0}`
- /check status counts: `{"200": 61580}`
- /fix status counts: `{"NaN": 56580, "200.0": 5000}`
- /quality status counts: `{"NaN": 56580, "200.0": 5000}`

## Model Availability Comparison
- Comparison summary: `{"actual_available_model_loaded": true, "forced_unavailable_model_loaded": false, "subset_size": 5000, "accuracy_available_subset": 0.9436, "accuracy_forced_unavailable_subset": 0.9256}`

## Per-language Metrics
  language  samples  accuracy
         C    12144  0.944335
       C++    12034  0.916819
      Java    12091  0.941692
JavaScript    12130  0.970569
    Python    13181  0.936044

## Per-label Metrics
               label  precision   recall       f1  support
      DivisionByZero   1.000000 0.552342 0.711624      726
 DuplicateDefinition   1.000000 0.668203 0.801105      217
         ImportError   0.962025 0.088785 0.162567      856
    IndentationError   0.997743 1.000000 0.998870      442
        InfiniteLoop   1.000000 0.709220 0.829876      141
   InvalidAssignment   1.000000 0.266949 0.421405      236
         LineTooLong   1.000000 0.790698 0.883117      129
    MissingDelimiter   0.830973 0.824196 0.827571     2207
      MissingInclude   0.000000 0.000000 0.000000      805
      MutableDefault   1.000000 0.986842 0.993377       76
             NoError   0.940578 1.000000 0.969379    50620
         SyntaxError   0.000000 0.000000 0.000000        0
        TypeMismatch   0.500000 0.002591 0.005155      386
      UnclosedString   1.000000 0.996844 0.998419     1901
UndeclaredIdentifier   0.750000 0.034483 0.065934      261
    UnmatchedBracket   0.997563 1.000000 0.998780     2047
     UnreachableCode   1.000000 0.946108 0.972308      167
      UnusedVariable   1.000000 0.033639 0.065089      327
      WildcardImport   0.971429 0.944444 0.957746       36

## Confusion Highlights
          true_label      predicted_label  count  rate_within_true_label  true_total
      MissingInclude              NoError    805                1.000000         805
         ImportError              NoError    409                0.477804         856
    MissingDelimiter              NoError    388                0.175804        2207
        TypeMismatch              NoError    385                0.997409         386
         ImportError     MissingDelimiter    370                0.432243         856
      DivisionByZero              NoError    325                0.447658         726
      UnusedVariable              NoError    316                0.966361         327
UndeclaredIdentifier              NoError    251                0.961686         261
   InvalidAssignment              NoError    169                0.716102         236
 DuplicateDefinition              NoError     72                0.331797         217
        InfiniteLoop              NoError     41                0.290780         141
         LineTooLong              NoError     26                0.201550         129
     UnreachableCode              NoError      9                0.053892         167
      UnclosedString     UnmatchedBracket      5                0.002630        1901
   InvalidAssignment UndeclaredIdentifier      3                0.012712         236
      WildcardImport          ImportError      2                0.055556          36
      MutableDefault              NoError      1                0.013158          76
         LineTooLong     IndentationError      1                0.007752         129
   InvalidAssignment         TypeMismatch      1                0.004237         236
UndeclaredIdentifier          ImportError      1                0.003831         261
         ImportError       WildcardImport      1                0.001168         856
      UnclosedString              NoError      1                0.000526        1901

## Top Failures
           sample_id language expected_label_norm   core_predicted  core_confidence                                                                                          snippet                              source_path  source_line      corpus_type                        generator     seed
c2d20f4664ae5d1b25d7        C      MissingInclude          NoError              1.0                                                               int main() { sqrt(16); return 0; }         dataset\merged\all_errors_v2.csv            4          dataset dataset/merged/all_errors_v2.csv 20260305
b5ffb4bebf20a1c35eba     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         2030 mutation_invalid          mutation:import_variant 20260406
b11b03fa539e58922766     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         1977 mutation_invalid          mutation:import_variant 20260406
c01ff713dcf6168b3981     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         1978 mutation_invalid          mutation:import_variant 20260406
42acb77fbff93d4c19f2     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         1981 mutation_invalid          mutation:import_variant 20260406
bebab727bbaa4a3fd263     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         1982 mutation_invalid          mutation:import_variant 20260406
d84945656a7439fe80cc     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         1993 mutation_invalid          mutation:import_variant 20260406
877921b6fd7fd394833a     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         1994 mutation_invalid          mutation:import_variant 20260406
096ca075da0c7ce90ae4     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         2013 mutation_invalid          mutation:import_variant 20260406
882b3db3a5c232dd59e8     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         2022 mutation_invalid          mutation:import_variant 20260406
931a30394e28b6f769ab     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         2023 mutation_invalid          mutation:import_variant 20260406
c9a486c1beddc490bb40     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         2024 mutation_invalid          mutation:import_variant 20260406
846cf88d76d31ed3c23a     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         2029 mutation_invalid          mutation:import_variant 20260406
e908d2e76e2f7a78819a     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         2031 mutation_invalid          mutation:import_variant 20260406
88fda0a65afa821b925e     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         1952 mutation_invalid          mutation:import_variant 20260406
16d1f936aa7bb94ad6f2     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         2040 mutation_invalid          mutation:import_variant 20260406
7f393f829e38c3ff3830     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         2048 mutation_invalid          mutation:import_variant 20260406
8c2c16311b3a110a7786     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         2051 mutation_invalid          mutation:import_variant 20260406
ffa94b211066fd80c876     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         2062 mutation_invalid          mutation:import_variant 20260406
6731edd3863975cdc27b     Java         ImportError MissingDelimiter              1.0 public class Main { public static void main(String[] args){ ArrayList x = new ArrayList(); } }\n generated://mutation/Java/import_variant         2070 mutation_invalid          mutation:import_variant 20260406
