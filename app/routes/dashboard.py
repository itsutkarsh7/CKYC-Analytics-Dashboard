from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request

from app.pipeline import (
    PipelineStore,
    BUCKETS,
    compute_kpis,
    compute_overall_stats,
    compute_product_pivot,
    compute_wip_breakup,
    compute_partner_chart,
    drilldown,
)

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/")
def dashboard():
    master_df = PipelineStore.get()

    if master_df is None or master_df.empty:
        return render_template(
            "dashboard.html",
            has_data=False,
            buckets=BUCKETS,
        )

    kpis = compute_kpis(master_df)
    overall = compute_overall_stats(master_df)
    pivot = compute_product_pivot(master_df)
    wip = compute_wip_breakup(master_df)
    chart = compute_partner_chart(master_df)

    products = ["All"] + sorted([p for p in master_df["PRODUCT"].dropna().unique().tolist()])
    statuses = ["All"] + BUCKETS

    return render_template(
        "dashboard.html",
        has_data=True,
        buckets=BUCKETS,
        kpis=kpis,
        overall=overall,
        pivot=pivot,
        wip=wip,
        chart=chart,
        products=products,
        statuses=statuses,
        total_records=len(master_df),
    )


@dashboard_bp.route("/api/drilldown")
def api_drilldown():
    master_df = PipelineStore.get()
    if master_df is None or master_df.empty:
        return jsonify({"rows": []})

    product = request.args.get("product", "All")
    bucket = request.args.get("bucket", "All")
    partner = request.args.get("partner", "All")

    filtered = drilldown(master_df, product=product, bucket=bucket, partner=partner)
    return jsonify({"rows": filtered.to_dict(orient="records"), "count": len(filtered)})


@dashboard_bp.route("/api/kpis")
def api_kpis():
    master_df = PipelineStore.get()
    if master_df is None or master_df.empty:
        return jsonify({})
    return jsonify(compute_kpis(master_df))
