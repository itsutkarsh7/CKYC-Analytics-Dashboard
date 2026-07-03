"""
CKYC Analytics & Reconciliation Pipeline
=========================================
See task docstring in repo history; consolidated pandas pipeline replacing
the two dead/unwired architecture stacks.
"""

import os
import uuid
import pandas as pd
import numpy as np

BUCKETS = [
    "CKYC Completed",
    "Pending with CERSAI",
    "Under Resolution with Ops",
    "CKYC Upload Pending",
    "Auto Resolution",
    "Issue with CKYC",
    "Manually Reported by Ops",
]

MASTER_COLUMNS = [
    "CKYC_NO", "CUSTOMER_ID", "PRODUCT", "PARTNER", "SOURCE_REPORT",
    "BUCKET", "REMARKS",
]

PRODUCT_GROUPS = {
    "Co-Lending": ["Fintech Partnership", "Embedded Finance"],
    "BranchLed": [],
    "Partner Reporting": [],
    "WSL": [],
}

COLUMN_ALIASES = {
    "ckyc_no": "CKYC_NO", "ckycno": "CKYC_NO", "ckyc number": "CKYC_NO",
    "ckyc_number": "CKYC_NO",
    "customer_id": "CUSTOMER_ID", "customer id": "CUSTOMER_ID", "cust_id": "CUSTOMER_ID",
    "product": "PRODUCT", "product_name": "PRODUCT",
    "partner": "PARTNER", "partner_name": "PARTNER", "sub_product": "PARTNER",
    "status": "STATUS", "cersai_status": "STATUS", "upload_status": "STATUS",
    "remarks": "REMARKS", "remark": "REMARKS", "comments": "REMARKS",
    "date": "DATE", "upload_date": "DATE", "record_date": "DATE",
    "match_flag": "MATCH_FLAG", "data_match": "MATCH_FLAG",
}


def load_report(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext in (".xlsx", ".xls"):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath)
    return df


def validate_report(df, name):
    if df is None or df.empty:
        raise ValueError(f"{name} is empty or could not be read.")
    if df.shape[1] == 0:
        raise ValueError(f"{name} has no columns.")
    return True


def clean_report(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": np.nan, "": np.nan, "None": np.nan})
    df = df.drop_duplicates()
    return df


def standardize_report(df, source_report):
    df = df.copy()
    rename_map = {}
    for col in df.columns:
        key = col.strip().lower().replace("-", "_")
        if key in COLUMN_ALIASES:
            rename_map[col] = COLUMN_ALIASES[key]
    df = df.rename(columns=rename_map)

    for required in ["CKYC_NO", "CUSTOMER_ID"]:
        if required not in df.columns:
            df[required] = np.nan

    df["CKYC_NO"] = df["CKYC_NO"].astype(str).str.strip().str.upper()
    df["CUSTOMER_ID"] = df["CUSTOMER_ID"].astype(str).str.strip().str.upper()
    df["CKYC_NO"] = df["CKYC_NO"].replace({"NAN": np.nan})
    df["CUSTOMER_ID"] = df["CUSTOMER_ID"].replace({"NAN": np.nan})

    for opt in ["PRODUCT", "PARTNER", "STATUS", "REMARKS", "MATCH_FLAG"]:
        if opt not in df.columns:
            df[opt] = np.nan

    df["SOURCE_REPORT"] = source_report
    return df


def merge_reports(df_a, df_b, df_c):
    def key_frame(df, tag):
        d = df.copy()
        d["_KEY"] = d["CKYC_NO"].fillna("") + "|" + d["CUSTOMER_ID"].fillna("")
        d = d[d["_KEY"] != "|"]
        d[f"_IN_{tag}"] = True
        d[f"_STATUS_{tag}"] = d["STATUS"]
        d[f"_MATCH_{tag}"] = d["MATCH_FLAG"]
        d[f"_REMARKS_{tag}"] = d["REMARKS"]
        return d

    a = key_frame(df_a, "A")
    b = key_frame(df_b, "B")
    c = key_frame(df_c, "C")

    base = pd.concat([
        c[["_KEY", "CKYC_NO", "CUSTOMER_ID", "PRODUCT", "PARTNER"]],
        a[["_KEY", "CKYC_NO", "CUSTOMER_ID", "PRODUCT", "PARTNER"]],
        b[["_KEY", "CKYC_NO", "CUSTOMER_ID", "PRODUCT", "PARTNER"]],
    ])
    base = (
        base.sort_values("_KEY")
        .groupby("_KEY", as_index=False)
        .agg({
            "CKYC_NO": "first",
            "CUSTOMER_ID": "first",
            "PRODUCT": lambda s: next((x for x in s if pd.notna(x)), np.nan),
            "PARTNER": lambda s: next((x for x in s if pd.notna(x)), np.nan),
        })
    )

    merged = base
    for tag, d in (("A", a), ("B", b), ("C", c)):
        merged = merged.merge(
            d[["_KEY", f"_IN_{tag}", f"_STATUS_{tag}", f"_MATCH_{tag}", f"_REMARKS_{tag}"]],
            on="_KEY", how="left",
        )

    for tag in ("A", "B", "C"):
        merged[f"_IN_{tag}"] = merged[f"_IN_{tag}"].infer_objects(copy=False).fillna(False).astype(bool)

    return merged


def _status_says_completed(s):
    return isinstance(s, str) and s.strip().lower() in (
        "completed", "success", "matched", "verified", "done", "ok"
    )


def _status_says_pending(s):
    return isinstance(s, str) and s.strip().lower() in (
        "pending", "in progress", "processing", "awaiting", "queued"
    )


def _status_says_issue(s):
    return isinstance(s, str) and s.strip().lower() in (
        "mismatch", "issue", "error", "rejected", "conflict", "failed"
    )


def _match_flag_bad(v):
    if isinstance(v, str):
        return v.strip().lower() in ("n", "no", "false", "mismatch", "0")
    return False


def assign_bucket(row):
    """
    Rule Engine - classify one merged record into exactly one of the 7
    operational buckets. Priority order (first match wins):

    1. Issue with CKYC: in Master(C) + at least one of A/B, but status/match
       flag signals a mismatch/conflict.
    2. CKYC Completed: in Master(C) AND both A and B, no issue signalled.
    3. Auto Resolution: in Master(C) AND exactly one of A/B, with a clean
       "completed" status signal (resolved automatically, single source).
    4. Pending with CERSAI: in A/B but not yet in Master(C), status
       suggests it's simply awaiting CERSAI reflection.
    5. CKYC Upload Pending: in A/B, not in Master(C), and no status at all
       recorded (never actually uploaded to CKYC).
    6. Manually Reported by Ops: explicit manual/ops signal or remarks
       present, and no bucket above matched.
    7. Under Resolution with Ops: fallback catch-all for open/ambiguous
       cases still being worked by Operations.
    """
    in_a, in_b, in_c = row["_IN_A"], row["_IN_B"], row["_IN_C"]

    statuses = [row.get("_STATUS_A"), row.get("_STATUS_B"), row.get("_STATUS_C")]
    matches = [row.get("_MATCH_A"), row.get("_MATCH_B"), row.get("_MATCH_C")]
    remarks = [row.get("_REMARKS_A"), row.get("_REMARKS_B"), row.get("_REMARKS_C")]

    has_issue_signal = any(_status_says_issue(s) for s in statuses) or any(_match_flag_bad(m) for m in matches)
    has_completed_signal = any(_status_says_completed(s) for s in statuses)
    has_pending_signal = any(_status_says_pending(s) for s in statuses)
    has_manual_signal = any(
        isinstance(s, str) and ("manual" in s.lower() or "ops" in s.lower()) for s in statuses
    ) or any(isinstance(r, str) and len(r) > 0 for r in remarks)

    if in_c and (in_a or in_b) and has_issue_signal:
        return "Issue with CKYC", "Mismatch/conflict detected between operational report and CKYC master."

    if in_c and in_a and in_b and not has_issue_signal:
        return "CKYC Completed", "Record fully reconciled across Report A, Report B and CKYC Master."

    if in_c and (in_a != in_b) and has_completed_signal and not has_issue_signal:
        return "Auto Resolution", "Record auto-resolved on single-report match with clean completed status."

    if (in_a or in_b) and not in_c and (has_pending_signal or not has_issue_signal) and not has_manual_signal and any(pd.notna(s) for s in statuses):
        return "Pending with CERSAI", "Uploaded to operational report but not yet reflected in CKYC/CERSAI master."

    if (in_a or in_b) and not in_c and all(pd.isna(s) for s in statuses) and not has_manual_signal:
        return "CKYC Upload Pending", "Record not yet uploaded to CKYC master; no status recorded."

    if has_manual_signal and not has_issue_signal:
        return "Manually Reported by Ops", "Case flagged/reported manually by Operations team."

    return "Under Resolution with Ops", "Ambiguous or open case; currently under active resolution by Operations."


def run_rule_engine(merged):
    results = merged.apply(assign_bucket, axis=1, result_type="expand")
    merged["BUCKET"] = results[0]
    merged["REMARKS"] = results[1]

    def source_summary(row):
        srcs = []
        if row["_IN_A"]:
            srcs.append("A")
        if row["_IN_B"]:
            srcs.append("B")
        if row["_IN_C"]:
            srcs.append("C")
        return "+".join(srcs) if srcs else "NONE"

    merged["SOURCE_REPORT"] = merged.apply(source_summary, axis=1)

    master_df = merged[["CKYC_NO", "CUSTOMER_ID", "PRODUCT", "PARTNER", "SOURCE_REPORT", "BUCKET", "REMARKS"]].copy()
    master_df["PRODUCT"] = master_df["PRODUCT"].fillna("Unclassified")
    master_df["PARTNER"] = master_df["PARTNER"].fillna("Unclassified")
    master_df = master_df.reset_index(drop=True)
    return master_df


def run_pipeline(path_a, path_b, path_c):
    raw_a = load_report(path_a)
    raw_b = load_report(path_b)
    raw_c = load_report(path_c)

    validate_report(raw_a, "Report A")
    validate_report(raw_b, "Report B")
    validate_report(raw_c, "Master Report C")

    clean_a = clean_report(raw_a)
    clean_b = clean_report(raw_b)
    clean_c = clean_report(raw_c)

    std_a = standardize_report(clean_a, "A")
    std_b = standardize_report(clean_b, "B")
    std_c = standardize_report(clean_c, "C")

    merged = merge_reports(std_a, std_b, std_c)
    master_df = run_rule_engine(merged)
    return master_df


def compute_kpis(master_df):
    total = len(master_df)
    kpis = {}
    for bucket in BUCKETS:
        count = int((master_df["BUCKET"] == bucket).sum())
        pct = round((count / total) * 100, 2) if total else 0.0
        kpis[bucket] = {"count": count, "pct": pct}
    kpis["_TOTAL"] = total
    return kpis


def compute_overall_stats(master_df):
    total = len(master_df)
    if total == 0:
        return {"uploaded_pct": 0, "completed_pct": 0, "deemed_completed_pct": 0}

    uploaded_pct = round((master_df["SOURCE_REPORT"] != "NONE").mean() * 100, 2)
    completed_pct = round((master_df["BUCKET"] == "CKYC Completed").mean() * 100, 2)
    deemed_completed_buckets = ["CKYC Completed", "Auto Resolution", "Pending with CERSAI"]
    deemed_completed_pct = round(master_df["BUCKET"].isin(deemed_completed_buckets).mean() * 100, 2)

    return {
        "uploaded_pct": uploaded_pct,
        "completed_pct": completed_pct,
        "deemed_completed_pct": deemed_completed_pct,
    }


def _grouped_product_label(product):
    for parent, children in PRODUCT_GROUPS.items():
        if product == parent or product in children:
            return parent, (product if product in children else None)
    return product, None


def compute_product_pivot(master_df):
    """
    Build a PRODUCT/PARTNER x BUCKET pivot with Co-Lending as a parent
    group containing Fintech Partnership and Embedded Finance as sub-rows,
    plus a bolded Grand Total row.
    """
    df = master_df.copy()
    labels = df["PRODUCT"].map(_grouped_product_label)
    df["_PARENT"] = [t[0] for t in labels]
    df["_CHILD"] = [t[1] for t in labels]

    def bucket_counts(sub_df):
        vals = {b: int((sub_df["BUCKET"] == b).sum()) for b in BUCKETS}
        vals["Grand Total"] = len(sub_df)
        return vals

    rows = []
    parent_order = list(PRODUCT_GROUPS.keys())
    extra_parents = [p for p in df["_PARENT"].dropna().unique() if p not in parent_order]
    parent_order += sorted(extra_parents)

    for parent in parent_order:
        parent_df = df[df["_PARENT"] == parent]
        if parent_df.empty:
            continue
        rows.append({"label": parent, "level": "parent", "values": bucket_counts(parent_df)})
        children = sorted(parent_df["_CHILD"].dropna().unique().tolist())
        for child in children:
            child_df = parent_df[parent_df["_CHILD"] == child]
            rows.append({"label": child, "level": "child", "values": bucket_counts(child_df)})

    rows.append({"label": "Total", "level": "total", "values": bucket_counts(df)})

    return {"columns": BUCKETS + ["Grand Total"], "rows": rows}


WIP_BUCKETS = ["Pending with CERSAI", "Under Resolution with Ops", "CKYC Upload Pending",
               "Issue with CKYC", "Manually Reported by Ops"]


def compute_wip_breakup(master_df):
    total = len(master_df)
    wip_total = int(master_df["BUCKET"].isin(WIP_BUCKETS).sum())
    rows = []
    for bucket in WIP_BUCKETS:
        count = int((master_df["BUCKET"] == bucket).sum())
        pct_of_total = round((count / total) * 100, 2) if total else 0
        pct_of_wip = round((count / wip_total) * 100, 2) if wip_total else 0
        rows.append({"bucket": bucket, "count": count, "pct_of_total": pct_of_total, "pct_of_wip": pct_of_wip})
    return {"rows": rows, "wip_total": wip_total, "total": total}


def compute_partner_chart(master_df):
    counts = master_df.groupby("PARTNER").size().sort_values(ascending=False)
    return {"labels": counts.index.tolist(), "values": [int(v) for v in counts.values.tolist()]}


def drilldown(master_df, product=None, bucket=None, partner=None):
    df = master_df.copy()
    if product and product != "All":
        df = df[df["PRODUCT"] == product]
    if bucket and bucket != "All":
        df = df[df["BUCKET"] == bucket]
    if partner and partner != "All":
        df = df[df["PARTNER"] == partner]
    return df


class PipelineStore:
    """Holds the last computed MASTER_DF in memory for the running process."""
    master_df = None
    run_id = None

    @classmethod
    def set(cls, df):
        cls.master_df = df
        cls.run_id = str(uuid.uuid4())

    @classmethod
    def get(cls):
        return cls.master_df
