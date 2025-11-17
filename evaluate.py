# evaluate.py - Evaluate the deterministic checker on the dataset
import csv, argparse, json
from syntax_checker import detect_all

def load_dataset(path):
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def evaluate(rows):
    totals = {}
    tp = {}
    fp = {}
    for r in rows:
        expected = r['error_type']
        code = r['buggy_code']
        detected = [d['type'] for d in detect_all(code)]
        totals.setdefault(expected, 0)
        totals[expected] += 1
        if expected in detected:
            tp.setdefault(expected, 0)
            tp[expected] += 1
        for d in detected:
            if d != expected:
                fp.setdefault(d, 0)
                fp[d] = fp.get(d,0) + 1
    results = {}
    for t in totals:
        t_tp = tp.get(t, 0)
        t_total = totals[t]
        recall = t_tp / t_total if t_total else 0.0
        fp_for_t = fp.get(t, 0)
        precision = t_tp / (t_tp + fp_for_t) if (t_tp + fp_for_t) else 0.0
        results[t] = {
            "total": t_total,
            "true_positive": t_tp,
            "false_positive": fp_for_t,
            "recall": round(recall, 4),
            "precision": round(precision, 4)
        }
    overall_tp = sum(tp.values()) if tp else 0
    overall_total = len(rows)
    overall_recall = overall_tp / overall_total if overall_total else 0.0
    return results, round(overall_recall,4)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="dataset/errors_dataset.csv")
    parser.add_argument("--out", default="results.json")
    args = parser.parse_args()
    rows = load_dataset(args.dataset)
    results, overall_recall = evaluate(rows)
    out = {"per_type": results, "overall_recall": overall_recall}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("Evaluation complete. Results saved to", args.out)

if __name__ == "__main__":
    main()