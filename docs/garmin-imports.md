# Garmin CSV Imports

CP07 adds a small Garmin CSV import path on top of CP06 raw file storage.

## Supported file type

Only uploaded raw import files with `file_type` set to `csv` can be processed by the
Garmin CSV importer.

CP07 does not parse FIT, TCX, or GPX files and does not integrate with Garmin Connect.

## Supported CSV columns

The first supported fixture format is:

```text
activity_date,start_time,activity_type,duration_minutes,notes
```

Required columns:

- `activity_date`: workout date in `YYYY-MM-DD` format.
- `start_time`: activity start time in `HH:MM` or `HH:MM:SS` format.
- `activity_type`: workout type text.
- `duration_minutes`: positive integer duration in minutes.

Optional columns:

- `notes`: free text copied into the created workout notes.

The parser also accepts these simple header aliases:

- `Activity Date` or `Date` for `activity_date`
- `Start Time` or `Time` for `start_time`
- `Activity Type` or `Type` for `activity_type`
- `Duration Minutes` or `Duration` for `duration_minutes`

## Created workouts

Each valid CSV row creates one `workout` record using existing workout fields:

- `workout_date` from `activity_date`
- `workout_type` from `activity_type`
- `duration_minutes` from `duration_minutes`
- `source` set to `garmin_csv`
- `notes` containing the Garmin CSV start time, CSV row number, and optional CSV notes

CP07 does not add strength training details, dashboard metrics, analytics, or medical
interpretation.

## Duplicate detection

The importer skips likely duplicate Garmin CSV workouts when an existing `garmin_csv`
workout has the same:

- workout date
- start time
- workout type
- duration in minutes

The workout table does not have a separate start-time column in CP07. The importer
stores the CSV start time in a deterministic notes prefix so duplicates can be checked
without changing the workout schema.

## Import status

CP07 adds two `imported_file` fields:

- `import_status`
- `import_error_message`

Status values:

- `not_imported`: raw file has been uploaded but not processed by the Garmin CSV
  importer.
- `imported`: CSV processing completed without malformed rows. This can include rows
  skipped as duplicates.
- `partial_failure`: at least one valid row was created or skipped as a duplicate, and
  at least one malformed row was found.
- `failed`: no valid rows were processed, or the file could not be processed as a
  Garmin CSV import.

Malformed rows are not silently ignored. Row-level errors are shown in the import result
summary and stored in `import_error_message`.
