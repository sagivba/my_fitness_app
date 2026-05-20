# Task 06 - Add raw import file storage

## Branch

```text
codex-cli/add-raw-import-file-storage
```

## Suggested Codex effort

High. File handling and security boundaries need care.

## Goal

Add safe raw file upload and metadata storage for future Garmin imports.

## Scope

1. Add an import/upload page for activity files.
2. Store uploaded files under a configured local upload directory, defaulting to an `instance/uploads` path.
3. Store metadata in `imported_file`: source, original filename, stored path, file type, sha256, import time, status, and error message.
4. Validate allowed extensions: csv, tcx, gpx, fit.
5. Sanitize filenames and avoid path traversal.
6. Compute SHA-256 for duplicate detection.
7. Add tests for allowed extensions, rejected extensions, hashing, duplicate detection, and route behavior.
8. Document upload storage and privacy expectations.

## Out of scope

1. Do not parse Garmin files yet.
2. Do not create workouts from uploaded files yet.
3. Do not integrate with Garmin Connect API.
4. Do not upload files to external services.

## Likely files to touch

- `src/my_fitness_app/routes/import_routes.py`
- `src/my_fitness_app/services/import_file_service.py`
- `src/my_fitness_app/model/imported_file.py`
- `src/my_fitness_app/utils/files.py`
- `src/my_fitness_app/utils/hashing.py`
- `templates/imports/*.html`
- `tests/`
- `.env.example`
- `README.md`

## Validation

```bash
scripts/test.sh full local
scripts/lint.sh
```

## Acceptance criteria

- Allowed file types can be uploaded and stored locally.
- File metadata and hash are saved.
- Dangerous filenames are handled safely.
- Duplicate file upload is detected or clearly represented.
- Tests and lint pass.


## Slash goal

```text
/goal
Add safe raw file upload and metadata storage for future Garmin imports.

Use branch: codex-cli/add-raw-import-file-storage

Scope:
1. Add an import/upload page for activity files.
2. Store uploaded files under a configured local upload directory, defaulting to an `instance/uploads` path.
3. Store metadata in `imported_file`: source, original filename, stored path, file type, sha256, import time, status, and error message.
4. Validate allowed extensions: csv, tcx, gpx, fit.
5. Sanitize filenames and avoid path traversal.
6. Compute SHA-256 for duplicate detection.
7. Add tests for allowed extensions, rejected extensions, hashing, duplicate detection, and route behavior.
8. Document upload storage and privacy expectations.

Out of scope:
1. Do not parse Garmin files yet.
2. Do not create workouts from uploaded files yet.
3. Do not integrate with Garmin Connect API.
4. Do not upload files to external services.

Constraints:
- Read AGENTS.md before making changes.
- Keep changes small and reviewable.
- Preserve routes -> services -> model boundaries.
- Use unittest only. Do not introduce pytest.
- Do not edit unrelated files.
- Do not commit secrets or local .env files.
- Update docs when commands, structure, behavior, or workflow changes.

Validation:
```bash
scripts/test.sh full local
scripts/lint.sh
```

Acceptance criteria:
- Allowed file types can be uploaded and stored locally.
- File metadata and hash are saved.
- Dangerous filenames are handled safely.
- Duplicate file upload is detected or clearly represented.
- Tests and lint pass.
```
