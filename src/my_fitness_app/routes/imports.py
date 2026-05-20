from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for

from my_fitness_app.services import (
    garmin_csv_import_service,
    garmin_gpx_import_service,
    garmin_tcx_import_service,
    import_file_service,
)
from my_fitness_app.services.import_file_service import ImportFileValidationError

imports_bp = Blueprint("imports", __name__, url_prefix="/imports")


@imports_bp.get("/")
def list_imports():
    imported_files = import_file_service.list_imported_files(current_app.config["DATABASE_PATH"])
    return render_template("imports/list.html", imported_files=imported_files)


@imports_bp.get("/new")
def new_import():
    return render_template("imports/new.html", errors={})


@imports_bp.post("/")
def create_import():
    uploaded_file = request.files.get("file")
    if uploaded_file is None:
        return (
            render_template(
                "imports/new.html",
                errors={"file": "חובה לבחור קובץ לייבוא."},
            ),
            400,
        )

    try:
        result = import_file_service.upload_import_file(
            current_app.config["DATABASE_PATH"],
            current_app.config["UPLOAD_DIRECTORY"],
            uploaded_file.filename,
            uploaded_file.stream,
        )
    except ImportFileValidationError as error:
        return render_template("imports/new.html", errors=error.errors), 400

    return redirect(
        url_for(
            "imports.get_import",
            imported_file_id=result.imported_file.id,
            duplicate="1" if result.is_duplicate else None,
        )
    )


@imports_bp.get("/<int:imported_file_id>")
def get_import(imported_file_id: int):
    imported_file = import_file_service.get_imported_file(
        current_app.config["DATABASE_PATH"],
        imported_file_id,
    )
    if imported_file is None:
        abort(404)

    return render_template(
        "imports/detail.html",
        imported_file=imported_file,
        is_duplicate=request.args.get("duplicate") == "1",
        import_result=None,
    )


@imports_bp.post("/<int:imported_file_id>/garmin-csv-import")
def import_garmin_csv(imported_file_id: int):
    import_result = garmin_csv_import_service.import_garmin_csv(
        current_app.config["DATABASE_PATH"],
        imported_file_id,
    )
    if import_result is None:
        abort(404)

    return render_template(
        "imports/detail.html",
        imported_file=import_result.imported_file,
        is_duplicate=False,
        import_result=import_result,
    )


@imports_bp.post("/<int:imported_file_id>/garmin-tcx-import")
def import_garmin_tcx(imported_file_id: int):
    import_result = garmin_tcx_import_service.import_garmin_tcx(
        current_app.config["DATABASE_PATH"],
        imported_file_id,
    )
    if import_result is None:
        abort(404)

    return render_template(
        "imports/detail.html",
        imported_file=import_result.imported_file,
        is_duplicate=False,
        import_result=import_result,
    )


@imports_bp.post("/<int:imported_file_id>/garmin-gpx-import")
def import_garmin_gpx(imported_file_id: int):
    import_result = garmin_gpx_import_service.import_garmin_gpx(
        current_app.config["DATABASE_PATH"],
        imported_file_id,
    )
    if import_result is None:
        abort(404)

    return render_template(
        "imports/detail.html",
        imported_file=import_result.imported_file,
        is_duplicate=False,
        import_result=import_result,
    )
