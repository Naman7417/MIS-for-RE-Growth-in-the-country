# India RE Growth MIS - Power BI Source Kit

This folder contains the Git-friendly source files for a dynamic Power BI MIS dashboard on renewable energy growth in India.

## Architecture

1. A GitHub Actions workflow runs once every 3 days.
2. `scripts/fetch_re_mis_data.py` pulls data from MNRE, CEA, PM Surya Ghar, PM-KUSUM, NGHM, and NSGM sources.
3. Normalized CSV outputs are committed under `powerbi-re-mis/data/`.
4. Power BI reads those CSVs from the repository raw URLs.
5. Power BI Service scheduled refresh is configured to match the 3-day data cadence.

This avoids depending on Power BI Service to scrape JavaScript dashboards directly.

## Source URLs

- MNRE physical progress: https://mnre.gov.in/en/physical-progress/
- MNRE year-wise achievement: https://mnre.gov.in/en/year-wise-achievement/
- CEA executive summary: https://cea.nic.in/executive-summary-report/?lang=en
- CEA installed capacity: https://cea.nic.in/installed-capacity-report/?lang=en
- CEA transmission reports: https://cea.nic.in/transmission-reports/?lang=en
- CEA power supply: https://cea.nic.in/power-supply/?lang=en
- CEA renewable generation: https://cea.nic.in/renewable-generation-report/?lang=en
- PM Surya Ghar progress: https://pmsuryaghar.gov.in/#/state-ut-wise-progress
- PM-KUSUM achievements: https://pmkusum.mnre.gov.in/#/landing#achievement
- NGHM projects: https://nghm.mnre.gov.in/project?language=en
- NSGM smart meter stats: https://www.nsgm.gov.in/en/sm-stats-all

## Files

- `scripts/fetch_re_mis_data.py`: scraper and normalizer.
- `requirements.txt`: Python dependencies for local and GitHub Actions execution.
- `data/`: generated CSV layer consumed by Power BI.
- `power-query/`: Power Query M snippets to paste into Power BI Desktop.
- `dax/measures.dax`: DAX measures for KPIs, growth, and dashboard cards.
- `docs/dashboard-design.md`: page layout and visuals.
- `docs/data-model.md`: tables, relationships, and refresh setup.

## Local refresh

Use Python 3.14 for local refresh.

```powershell
cd "C:\Users\NAMAN741\OneDrive\Documents\New project"
py -3.14 -m venv .venv-re-mis
.\.venv-re-mis\Scripts\Activate.ps1
pip install -r powerbi-re-mis\requirements.txt
playwright install chromium
python powerbi-re-mis\scripts\fetch_re_mis_data.py
```

## Power BI setup

1. Run the local refresh once, or let GitHub Actions create the CSVs.
2. Push this folder to GitHub.
3. In Power BI Desktop, create a parameter named `GitHubRawBaseUrl`.
   Example:
   `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/powerbi-re-mis/data/`
4. Add the Power Query snippets from `power-query/` as blank queries.
5. Load the model and paste measures from `dax/measures.dax`.
6. Publish to Power BI Service.
7. Configure scheduled refresh to align with the 3-day GitHub data refresh cadence.

## Refresh note

The GitHub source refresh is scheduled once every 3 days. If Power BI Service does not offer an exact 3-day interval in your workspace, schedule Power BI less frequently than the GitHub job or trigger report refresh manually after the GitHub workflow completes.

## Avoiding GitHub raw 400 errors

The raw base URL is a prefix used by Power Query and is not a browsable folder. Opening only the base URL may return:

```text
400: invalid request
```

Test a real CSV file URL instead:

```text
https://raw.githubusercontent.com/<owner>/<repo>/<branch>/powerbi-re-mis/data/refresh_manifest.csv
```
