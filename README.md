# LLM_Syntax_Error_Checker (Student Project)

This project is a student-level MVP that detects four common Python syntax error types:
- `MissingColon`
- `UnmatchedBracket`
- `IndentationError`
- `UnclosedQuotes`

It is implemented as a Streamlit web app plus a deterministic checker and an evaluation script using a synthetic dataset of 420 labeled examples.

## Files
- `app.py` — Streamlit UI
- `syntax_checker.py` — core detection logic
- `evaluate.py` — evaluate detector on dataset (produces `results.json`)
- `cli.py` — simple CLI tool
- `dataset/errors_dataset.csv` — synthetic dataset (420 samples)
- `samples/` — a few example `.py` files
- `requirements.txt`

## How to run
1. Create and activate a Python 3.8+ virtual environment.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run Streamlit app:
   ```
   streamlit run app.py
   ```
4. Evaluate on dataset:
   ```
   python evaluate.py --dataset dataset/errors_dataset.csv --out results.json
   ```

## Notes
- The detector is deterministic and fast; it is not an LLM. The code is structured so you can plug in an LLM later for richer diagnostics.
- The dataset is synthetic and focused on the 4 target error types for project evaluation and demo.