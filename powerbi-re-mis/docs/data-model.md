# Data Model

## Primary tables

| Table | File | Grain |
| --- | --- | --- |
| RE Installed Capacity Technology | `re_installed_capacity_technology.csv` | Technology |
| Annual RE Capacity Addition | `annual_re_capacity_addition.csv` | Fiscal year |
| MNRE Physical Progress Raw | `mnre_physical_progress_raw.csv` | Source row |
| MNRE Annual RE Additions Raw | `mnre_annual_re_additions_raw.csv` | Fiscal year and source row |
| RE CAGR Summary | `re_cagr_summary.csv` | Refresh run |
| CEA Report Links | `cea_report_links.csv` | Report link |
| PM Surya Ghar Tables | `pm_surya_ghar_rendered_tables.csv` | Rendered portal table row |
| PM Surya Ghar Visible Text | `pm_surya_ghar_visible_text.csv` | Rendered portal text line |
| PM KUSUM Tables | `pm_kusum_rendered_tables.csv` | Rendered portal table row |
| PM KUSUM Visible Text | `pm_kusum_visible_text.csv` | Rendered portal text line |
| NGHM Green Hydrogen Projects | `nghm_green_hydrogen_projects.csv` | Project portal row |
| NSGM Smart Meter Tables | `nsgm_smart_meters_rendered_tables.csv` | Rendered portal table row |
| NSGM Smart Meter Visible Text | `nsgm_smart_meters_visible_text.csv` | Rendered portal text line |
| Refresh Manifest | `refresh_manifest.csv` | Generated dataset |
| Refresh Errors | `refresh_errors.csv` | Refresh error |

## Relationships

Start with a lightweight model:

- `Annual RE Capacity Addition[technology]` to `RE Installed Capacity Technology[technology]`
- A separate date/fiscal-year table connected to annual capacity additions
- State/UT dimension after the PM Surya Ghar, KUSUM, and NSGM portal fields are validated against the generated CSVs

## Refresh configuration

Use two scheduled refresh layers:

1. GitHub Actions:
   - Runs once every 3 days.
   - Updates CSV files under `powerbi-re-mis/data/`.
2. Power BI Service:
   - Scheduled refresh aligned with the 3-day GitHub data refresh cadence.
   - Reads CSV files from raw GitHub URLs.

## CEA mapping note

CEA pages usually publish monthly PDF/XLS/XLSX reports. The first version stores the latest report links in `cea_report_links.csv`. After the exact current report file format is confirmed, add a parser for total installed capacity, transmission, power supply, and renewable generation tables.
