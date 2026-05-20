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
- Maps, charts, advanced analytics, and strength training details are not part of the
  Garmin import foundation.

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

- `end_time`: activity end time in `HH:MM` or `HH:MM:SS` format.
- `distance_meters`: positive numeric distance in meters.
- `calories`: positive integer calories.
- `average_heart_rate`: positive integer average heart rate.
- `max_heart_rate`: positive integer max heart rate.
- `external_activity_id`: optional external activity identifier.
- `notes`: free text copied into the created workout notes.

Accepted header aliases:

- `Activity Date` or `Date` for `activity_date`
- `Start Time` or `Time` for `start_time`
- `Activity Type` or `Type` for `activity_type`
- `Duration Minutes` or `Duration` for `duration_minutes`
- `Distance Meters` or `Distance (m)` for `distance_meters`
- `Average Heart Rate`, `Avg Heart Rate`, or `Avg HR` for `average_heart_rate`
- `Max Heart Rate` or `Max HR` for `max_heart_rate`
- `External Activity ID` or `Activity ID` for `external_activity_id`

CSV imports create one workout per valid row with `source` set to `garmin_csv`.
Supported optional metrics are stored in structured workout fields.

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
- External activity ID from activity `Id` when available.
- Source metadata in workout notes.

TCX imports create one workout per supported TCX file with `source` set to
`garmin_tcx`. Parsed metrics are stored in structured workout fields. Optional
missing fields do not fail the import. Missing optional fields are recorded in
deterministic workout notes.

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
- Elevation min, max, gain, and loss from track point `ele` values.
- External activity ID derived from the first track point timestamp when available.

GPX imports create one workout per supported GPX file with `source` set to
`garmin_gpx`. Parsed start/end time, duration, distance, and elevation gain/loss are
stored in structured workout fields. Start/end time, distance, point count, segment
count, elevation metadata, and missing optional fields are also recorded in
deterministic workout notes.

GPX files must include at least one track, at least one segment, at least two track
points, numeric coordinates, and enough timestamps to compute a positive duration. If
that data is missing, the import is marked `failed` with a clear
`import_error_message`.

## Duplicate Detection

CSV duplicate detection compares existing `garmin_csv` workouts by:

- workout date
- structured start time
- workout type
- duration in minutes

TCX and GPX duplicate detection compares existing Garmin file imports by:

- workout date
- structured start time
- workout type
- source (`garmin_tcx` or `garmin_gpx`)
- duration in minutes when available
- structured distance when available

For workouts imported before structured metric columns existed, duplicate detection
keeps a legacy fallback against deterministic notes. New dashboard metrics do not use
that fallback and do not parse notes.

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

## Structured Workout Metrics

Garmin imports now persist supported metadata into nullable workout columns:

- `start_time`
- `end_time`
- `duration_seconds`
- `distance_meters`
- `calories`
- `average_heart_rate`
- `max_heart_rate`
- `elevation_gain_meters`
- `elevation_loss_meters`
- `external_activity_id`

Workout notes remain a human-readable import summary. They are not an analytics source
and the mini dashboard does not parse them.

Existing SQLite databases are updated by a small idempotent compatibility check during
application startup. It adds missing nullable workout metric columns and preserves
existing rows.

## Mini Dashboard

The mini dashboard summarizes workouts from structured persisted fields only. It
shows totals for workouts, duration, distance, calories, heart-rate values when
available, recent workouts, and simple breakdowns by source and workout type. It is
not a full analytics system and does not include charts, maps, trend analysis, or
causal claims.

## Known Limitations

- No FIT support.
- No Garmin Connect API.
- No route maps or charts.
- No advanced analytics.
- Notes are kept for readable summaries and legacy duplicate fallback only.
