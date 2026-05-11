// Add each block as a separate blank query in Power BI Desktop.
// Requires parameter: GitHubRawBaseUrl
// Requires function query: fxGithubCsv

let
    Source = fxGithubCsv("re_installed_capacity_technology.csv"),
    ChangedTypes = Table.TransformColumnTypes(
        Source,
        {
            {"technology", type text},
            {"cumulative_mw", type number},
            {"cumulative_gw", type number},
            {"retrieved_at_utc", type datetimezone},
            {"source_url", type text}
        }
    )
in
    ChangedTypes

// Query name: Annual RE Capacity Addition
let
    Source = fxGithubCsv("annual_re_capacity_addition.csv"),
    ChangedTypes = Table.TransformColumnTypes(
        Source,
        {
            {"fiscal_year", type text},
            {"technology", type text},
            {"capacity_addition_mw", type number},
            {"capacity_addition_gw", type number},
            {"retrieved_at_utc", type datetimezone},
            {"source_url", type text}
        }
    )
in
    ChangedTypes

// Query name: MNRE Physical Progress Raw
let
    Source = fxGithubCsv("mnre_physical_progress_raw.csv"),
    ChangedTypes = Table.TransformColumnTypes(Source, {{"retrieved_at_utc", type datetimezone}})
in
    ChangedTypes

// Query name: MNRE Annual RE Additions Raw
let
    Source = fxGithubCsv("mnre_annual_re_additions_raw.csv"),
    ChangedTypes = Table.TransformColumnTypes(Source, {{"retrieved_at_utc", type datetimezone}})
in
    ChangedTypes

// Query name: RE CAGR Summary
let
    Source = fxGithubCsv("re_cagr_summary.csv"),
    ChangedTypes = Table.TransformColumnTypes(
        Source,
        {
            {"period_start", type text},
            {"period_end", type text},
            {"periods", Int64.Type},
            {"annual_addition_total_mw", type number},
            {"annual_addition_total_gw", type number},
            {"retrieved_at_utc", type datetimezone}
        }
    )
in
    ChangedTypes

// Query name: CEA Report Links
let
    Source = fxGithubCsv("cea_report_links.csv"),
    ChangedTypes = Table.TransformColumnTypes(Source, {{"retrieved_at_utc", type datetimezone}})
in
    ChangedTypes

// Query name: PM Surya Ghar Tables
let
    Source = fxGithubCsv("pm_surya_ghar_rendered_tables.csv"),
    ChangedTypes = Table.TransformColumnTypes(Source, {{"retrieved_at_utc", type datetimezone}})
in
    ChangedTypes

// Query name: PM Surya Ghar Visible Text
let
    Source = fxGithubCsv("pm_surya_ghar_visible_text.csv"),
    ChangedTypes = Table.TransformColumnTypes(Source, {{"line_number", Int64.Type}, {"retrieved_at_utc", type datetimezone}})
in
    ChangedTypes

// Query name: PM KUSUM Tables
let
    Source = fxGithubCsv("pm_kusum_rendered_tables.csv"),
    ChangedTypes = Table.TransformColumnTypes(Source, {{"retrieved_at_utc", type datetimezone}})
in
    ChangedTypes

// Query name: PM KUSUM Visible Text
let
    Source = fxGithubCsv("pm_kusum_visible_text.csv"),
    ChangedTypes = Table.TransformColumnTypes(Source, {{"line_number", Int64.Type}, {"retrieved_at_utc", type datetimezone}})
in
    ChangedTypes

// Query name: NGHM Green Hydrogen Projects
let
    Source = fxGithubCsv("nghm_green_hydrogen_projects.csv"),
    ChangedTypes = Table.TransformColumnTypes(Source, {{"retrieved_at_utc", type datetimezone}})
in
    ChangedTypes

// Query name: NSGM Smart Meter Tables
let
    Source = fxGithubCsv("nsgm_smart_meters_rendered_tables.csv"),
    ChangedTypes = Table.TransformColumnTypes(Source, {{"retrieved_at_utc", type datetimezone}})
in
    ChangedTypes

// Query name: NSGM Smart Meter Visible Text
let
    Source = fxGithubCsv("nsgm_smart_meters_visible_text.csv"),
    ChangedTypes = Table.TransformColumnTypes(Source, {{"line_number", Int64.Type}, {"retrieved_at_utc", type datetimezone}})
in
    ChangedTypes

// Query name: Refresh Manifest
let
    Source = fxGithubCsv("refresh_manifest.csv"),
    ChangedTypes = Table.TransformColumnTypes(
        Source,
        {
            {"dataset", type text},
            {"file_name", type text},
            {"row_count", Int64.Type},
            {"refreshed_at_utc", type datetimezone}
        }
    )
in
    ChangedTypes

// Query name: Refresh Errors
let
    Source = fxGithubCsv("refresh_errors.csv"),
    ChangedTypes = Table.TransformColumnTypes(Source, {{"retrieved_at_utc", type datetimezone}})
in
    ChangedTypes
