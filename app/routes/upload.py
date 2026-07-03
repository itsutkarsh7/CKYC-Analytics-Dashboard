import os
import datetime

from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.utils import secure_filename

from app import db
from app.pipeline import run_pipeline, PipelineStore
from app.models.database import UploadHistory

upload_bp = Blueprint(
    "upload",
    __name__
)


@upload_bp.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        report_a = request.files.get("report_a")
        report_b = request.files.get("report_b")
        report_c = request.files.get("report_c")

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        saved_paths = {}
        uploaded_files = []

        for key, report in (("report_a", report_a), ("report_b", report_b), ("report_c", report_c)):
            if report and report.filename:
                filename = secure_filename(report.filename)
                filepath = os.path.join(upload_folder, filename)
                report.save(filepath)
                saved_paths[key] = filepath
                uploaded_files.append(filename)

        error = None
        if len(saved_paths) < 3:
            error = "Please upload all three files: Report A, Report B and Master Report C."
        else:
            try:
                master_df = run_pipeline(
                    saved_paths["report_a"],
                    saved_paths["report_b"],
                    saved_paths["report_c"],
                )
                PipelineStore.set(master_df)

                for key, filename in zip(["report_a", "report_b", "report_c"], uploaded_files):
                    history = UploadHistory(
                        report_name=filename,
                        uploaded_on=datetime.datetime.utcnow(),
                        total_rows=len(master_df),
                        status="PROCESSED",
                    )
                    db.session.add(history)
                db.session.commit()
            except Exception as exc:
                error = f"Pipeline processing failed: {exc}"

        if error:
            return render_template("upload.html", success=False, error=error, uploaded_files=uploaded_files)

        return redirect(url_for("dashboard.dashboard"))

    return render_template(
        "upload.html",
        success=False
    )
