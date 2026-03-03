# -*- coding: utf-8 -*-
"""Script to add JavaScript support, merge error types, and retrain the model."""

import sys, os, io

import pandas as pd
import numpy as np
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from scipy.sparse import hstack
import joblib

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE, "dataset", "merged", "all_errors_v2.csv")

print("=" * 80)
print("  MERGING ERROR TYPES & ADDING JAVASCRIPT")
print("=" * 80)

# 1. Load Data
df = pd.read_csv(DATA_FILE)
print(f"  Loaded dataset: {len(df)} rows, {df['error_type'].nunique()} types")

# 2. Merge Error Types
df.loc[df['error_type'] == 'MissingImport', 'error_type'] = 'ImportError'
df.loc[df['error_type'] == 'NameError', 'error_type'] = 'UndeclaredIdentifier'
print(f"  Merged NameError->UndeclaredIdentifier and MissingImport->ImportError.")
print(f"  New error type count: {df['error_type'].nunique()}")

# 3. Generate JavaScript Data
js_samples = []

vars = ['data', 'result', 'count', 'total', 'item', 'index', 'value', 'user', 'id', 'name']
funcs = ['processData', 'calculateTotal', 'fetchUser', 'updateState', 'renderView', 'init']

def add_js(err_type, code):
    js_samples.append({'language': 'JavaScript', 'error_type': err_type, 'buggy_code': code})

for _ in range(60):
    v1, v2 = random.sample(vars, 2)
    f1 = random.choice(funcs)
    n1 = random.randint(1, 100)
    
    # DivisionByZero
    add_js("DivisionByZero", f"let {v1} = {n1} / 0;\nconsole.log({v1});")
    add_js("DivisionByZero", f"function {f1}() {{\n  return {n1} / (5 - 5);\n}}")
    
    # DuplicateDefinition
    add_js("DuplicateDefinition", f"let {v1} = 10;\nlet {v1} = 20;")
    add_js("DuplicateDefinition", f"const {v2} = 'test';\nconst {v2} = 'test2';")
    
    # ImportError
    add_js("ImportError", f"import {{ {v1} }} from './nonexistent_module.js';")
    add_js("ImportError", f"const {v2} = require('unknown-package');")
    
    # InfiniteLoop
    add_js("InfiniteLoop", f"while(true) {{\n  console.log('loop');\n}}")
    add_js("InfiniteLoop", f"for(let i=0; i>=0; i++) {{\n  {v1} += i;\n}}")
    
    # InvalidAssignment
    add_js("InvalidAssignment", f"const {v1} = 5;\n{v1} = 10;")
    add_js("InvalidAssignment", f"5 = {v2};")
    
    # LineTooLong
    long_str = "x" * 120
    add_js("LineTooLong", f"const {v1} = '{long_str}';")
    
    # MissingDelimiter
    add_js("MissingDelimiter", f"const obj = {{ name: 'test' age: 25 }}")
    add_js("MissingDelimiter", f"let {v1} = 5\nlet {v2} = 10")
    
    # NoError
    add_js("NoError", f"const {v1} = {n1};\nconsole.log({v1});")
    add_js("NoError", f"function {f1}({v2}) {{\n  return {v2} * 2;\n}}")
    add_js("NoError", f"const {v2} = () => {{ return '{v1}'; }};")
    add_js("NoError", f"import {{ {f1} }} from './utils.js';")
    
    # TypeMismatch
    add_js("TypeMismatch", f"let {v1} = 'string';\nlet res = {v1} * 5;")
    add_js("TypeMismatch", f"function {f1}(x) {{ return x; }}\n{f1}({{}} + []);")
    
    # UnclosedString
    add_js("UnclosedString", f"const {v1} = 'unclosed string;\nconsole.log({v1});")
    add_js("UnclosedString", f"let msg = \"Hello World;")
    
    # UndeclaredIdentifier
    add_js("UndeclaredIdentifier", f"console.log(undefined_var);")
    add_js("UndeclaredIdentifier", f"{f1}({v2}); // {v2} is not defined")
    
    # UnmatchedBracket
    add_js("UnmatchedBracket", f"function {f1}() {{\n  console.log('test');\n")
    add_js("UnmatchedBracket", f"if ({v1} > 5) {{\n  {v2} = 10;\n}} else {{\n")
    
    # UnreachableCode
    add_js("UnreachableCode", f"function {f1}() {{\n  return;\n  console.log('unreachable');\n}}")
    add_js("UnreachableCode", f"while(false) {{\n  console.log('never runs');\n}}")
    
    # UnusedVariable
    add_js("UnusedVariable", f"function {f1}() {{\n  let {v1} = 5;\n  return 10;\n}}")
    add_js("UnusedVariable", f"const {v2} = 'unused';\nconsole.log('hello');")

js_df = pd.DataFrame(js_samples).drop_duplicates()
print(f"  Generated {len(js_df)} JavaScript samples.")

# 4. Combine and Save
df = pd.concat([df, js_df], ignore_index=True)
df = df.drop_duplicates(subset=['buggy_code', 'error_type', 'language'], keep='first')
print(f"  Total samples after merge: {len(df)}")
df.to_csv(DATA_FILE, index=False)
print("  Saved updated dataset to all_errors_v2.csv")

# 5. Extract Features
print("\n" + "=" * 80)
print("  RETRAINING ML MODEL (5 LANGUAGES, 18 ERROR TYPES)")
print("=" * 80)

df['code_length'] = df['buggy_code'].str.len()
df['num_lines'] = df['buggy_code'].str.count('\n') + 1
df['has_division'] = (df['buggy_code'].str.contains('/') & df['buggy_code'].str.contains('0')).astype(int)
df['has_type_conv'] = df['buggy_code'].str.contains(r'int\(|float\(|str\(|bool\(|Number\(|String\(', regex=True).astype(int)

# Missing colon pattern (Python/JS objects)
mc = (~df['buggy_code'].str.contains(':')) & df['buggy_code'].str.contains(r'def |if |for |while |class |\{', regex=True)
df['missing_colon'] = mc.astype(int)

# Missing semicolon pattern (C/Java/C++/JS APIs)
ms = (~df['buggy_code'].str.contains(';')) & df['buggy_code'].str.contains(r'printf|cout|System\.out|fprintf|console\.log', regex=True)
df['missing_semicolon'] = ms.astype(int)

df['compares_zero'] = df['buggy_code'].str.contains(r'== 0|!= 0|=== 0|!== 0|/0|/ 0', regex=True).astype(int)
df['has_string_ops'] = df['buggy_code'].str.contains(r'\.upper\(\)|\.lower\(\)|\.split\(\)|\.join\(|\.strip\(\)|\.toUpperCase\(\)', regex=True).astype(int)
df['has_type_decl'] = df['buggy_code'].str.contains(r'\b(int|float|double|String|char|bool|let|const|var)\b', regex=True).astype(int)
df['bracket_diff'] = df['buggy_code'].str.count(r'\(') - df['buggy_code'].str.count(r'\)')

num_cols = ['code_length', 'num_lines', 'has_division', 'has_type_conv',
            'missing_colon', 'missing_semicolon', 'compares_zero',
            'has_string_ops', 'has_type_decl', 'bracket_diff']

le = LabelEncoder()
y = le.fit_transform(df['error_type'])

X_t_tr, X_t_te, X_n_tr, X_n_te, y_tr, y_te = train_test_split(
    df['buggy_code'], df[num_cols], y, test_size=0.2, random_state=42, stratify=y
)

vec = TfidfVectorizer(max_features=8000, ngram_range=(1,3), min_df=2, max_df=0.95,
                      sublinear_tf=True, analyzer='char', strip_accents='unicode')
X_tr = hstack([vec.fit_transform(X_t_tr), X_n_tr.values])
X_te = hstack([vec.transform(X_t_te), X_n_te.values])

print("  Training Gradient Boosting Classifier...")
model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
model.fit(X_tr, y_tr)

y_pred = model.predict(X_te)
acc = accuracy_score(y_te, y_pred)
print(f"  Accuracy on test set: {acc*100:.2f}%")

# Save Models
MODELS_DIR = os.path.join(BASE, "models")
joblib.dump(model, os.path.join(MODELS_DIR, 'syntax_error_model.pkl'))
joblib.dump(vec, os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl'))
joblib.dump(le, os.path.join(MODELS_DIR, 'label_encoder.pkl'))
joblib.dump(num_cols, os.path.join(MODELS_DIR, 'numerical_features.pkl'))
print("  Models saved successfully.")
