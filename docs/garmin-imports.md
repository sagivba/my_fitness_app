# Garmin Imports

Garmin imports build on CP06 raw file storage. Files are uploaded first, then imported
from the imported file detail page.

## Supported File Types

Supported import processors:

- CSV: small documented activity export format.
- TCX: basic activity XML.
- GPX: basic track XML.

Unsupported:

- FIT parsing is not implemented.
- Garmin Connect API integration is not implemented.
- Maps, charts, dashboard metrics, analytics, and strength training details are not
  part of the Garmin import foundation.

## CSV

The supported CSV fixture format is:

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

Accepted header aliases:

- `Activity Date` or `Date` for `activity_date`
- `Start Time` or `Time` for `start_time`
- `Activity Type` or `Type` for `activity_type`
- `Duration Minutes` or `Duration` for `duration_minutes`

CSV imports create one workout per valid row with `source` set to `garmin_csv`.

## TCX

TCX imports use Python standard-library XML parsing and support XML namespaces.

Supported fields when present:

- Activity sport type.
- Activity start time from the first lap `StartTime`, falling back to activity `Id`.
- Duration from lap `TotalTimeSeconds`.
- Distance from lap `DistanceMeters`.
- Calories from lap `Calories`.
- Average heart rate from lap `AverageHeartRateBpm/Value`.
- Max heart rate from lap `MaximumHeartRateBpm/Value`.
- Source metadata in workout notes.

TCX imports create one workout per supported TCX file with `source` set to
`garmin_tcx`. Optional missing fields do not fail the import. Missing optional fields
are recorded in deterministic workout notes.

Unsupported or incomplete TCX structures fail predictably. For example, a TCX file
without an `Activity`, without a `Lap`, or without a usable start time is marked
`failed` with a clear `import_error_message`.

## GPX

GPX imports use Python standard-library XML parsing and support XML namespaces.

Supported fields when present:

- First track point time as start time.
- Last track point time as end time.
- Duration from first and last point time.
- Track type from `type`, falling back to `name`, then `GPX activity`.
- Track point count.
- Track segment count.
- Distance calculated with the Haversine formula between consecutive track points in
  each segment.
- Elevation min, max, and gain from track point `ele` values.

GPX imports create one workout per supported GPX file with `source` set to
`garmin_gpx`. Start/end time, distance, point count, segment count, elevation metadata,
and missing optional fields are recorded in deterministic workout notes.

GPX files must include at least one track, at least one segment, at least two track
points, numeric coordinates, and enough timestamps to compute a positive duration. If
that data is missing, the import is marked `failed` with a clear
`import_error_message`.

## Duplicate Detection

CSV duplicate detection compares existing `garmin_csv` workouts by:

- workout date
- start time stored in deterministic notes
- workout type
- duration in minutes

TCX and GPX duplicate detection compares existing Garmin file imports by:

- workout date
- start time stored in deterministic notes
- workout type
- source (`garmin_tcx` or `garmin_gpx`)
- duration in minutes when available
- distance stored in deterministic notes when available

Re-importing the same supported fixture does not create duplicate workouts. Duplicate
rows or files are reported in the import summary as skipped duplicates.

## Import Status

Garmin import processors reuse the `imported_file` fields:

- `import_status`
- `import_error_message`

Status values:

- `not_imported`: raw file has been uploaded but not processed.
- `imported`: processing completed without malformed rows or fatal parser errors. This
  can include rows or files skipped as duplicates.
- `partial_failure`: CSV processing created or skipped at least one valid row and found
  at least one malformed row.
- `failed`: no valid workout could be processed, the file type is not supported by the
  chosen importer, or the file is malformed/incomplete.

Errors are shown in the import result summary and stored in `import_error_message`.
Malformed data is not silently ignored.

## Known Limitations

- No FIT support.
- No Garmin Connect API.
- No route maps or charts.
- No dashboard metrics or analytics.
- No schema fields for start time, end time, distance, calories, or heart rate yet.
  These values are stored in deterministic workout notes for CP08.
