import json
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def analyze_dataframe(df: pd.DataFrame, contamination: float = 0.05) -> dict:
    if df.empty:
        raise ValueError("The uploaded CSV has no data rows.")
    if len(df.columns) == 0:
        raise ValueError("The uploaded CSV has no columns.")

    total_rows, total_cols = df.shape
    missing_by_column = df.isna().sum().astype(int).to_dict()
    duplicate_rows = int(df.duplicated().sum())
    blank_strings = {}
    for col in df.select_dtypes(include=["object", "string"]).columns:
        count = int(df[col].astype("string").str.strip().eq("").fillna(False).sum())
        if count:
            blank_strings[str(col)] = count

    issues = []
    for col, count in missing_by_column.items():
        if count:
            issues.append({"issue": "Missing values", "column": str(col), "count": int(count)})
    if duplicate_rows:
        issues.append({"issue": "Duplicate rows", "column": "(all columns)", "count": duplicate_rows})
    for col, count in blank_strings.items():
        issues.append({"issue": "Blank strings", "column": col, "count": count})

    numeric = df.select_dtypes(include=[np.number]).replace([np.inf, -np.inf], np.nan)
    anomaly_records = pd.DataFrame()
    anomaly_count = 0
    if numeric.shape[1] > 0 and len(df) >= 10:
        # Median imputation supports numeric columns containing missing values.
        model_input = numeric.fillna(numeric.median()).fillna(0)
        if model_input.shape[1] and model_input.nunique(dropna=False).max() > 1:
            model = IsolationForest(contamination=contamination, random_state=42)
            labels = model.fit_predict(model_input)
            scores = -model.decision_function(model_input)
            mask = labels == -1
            anomaly_records = df.loc[mask].copy()
            anomaly_records.insert(0, "source_row", np.flatnonzero(mask) + 2)  # CSV row including header
            anomaly_records["anomaly_score"] = scores[mask].round(5)
            anomaly_records = anomaly_records.sort_values("anomaly_score", ascending=False)
            anomaly_count = int(mask.sum())

    issue_count = sum(int(x["count"]) for x in issues)
    # Transparent heuristic: row-level issue counts are capped to avoid scores below zero.
    affected_rows_estimate = min(total_rows, issue_count)
    quality_score = max(0.0, 100.0 * (1 - affected_rows_estimate / max(total_rows, 1)))
    summary = {
        "total_rows": int(total_rows),
        "total_columns": int(total_cols),
        "issue_count": int(issue_count),
        "duplicate_rows": duplicate_rows,
        "anomaly_count": anomaly_count,
        "quality_score": round(quality_score, 2),
        "numeric_columns_used": list(map(str, numeric.columns)),
    }
    report = {
        "summary": summary,
        "missing_by_column": {str(k): int(v) for k, v in missing_by_column.items()},
        "blank_strings": blank_strings,
        "issues": issues,
        "anomaly_count": anomaly_count,
    }
    return {
        "summary": summary,
        "missing_by_column": {str(k): int(v) for k, v in missing_by_column.items()},
        "issues": issues,
        "anomaly_records": anomaly_records,
        "report_json": json.dumps(report, indent=2, ensure_ascii=False),
    }
