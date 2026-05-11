# MIS for RE Growth in the Country

Power BI source kit for a dynamic renewable energy growth MIS dashboard for India.

The implementation is under `powerbi-re-mis/` and includes:

- Python 3.14 refresh script
- GitHub Actions workflow scheduled once every 3 days
- Power Query snippets for Power BI Desktop
- DAX measures
- Dashboard and data model documentation

After the GitHub workflow creates CSV files under `powerbi-re-mis/data/`, use this Power BI raw base URL:

```text
https://raw.githubusercontent.com/Naman7417/MIS-for-RE-Growth-in-the-country/main/powerbi-re-mis/data/
```

Do not paste the base URL directly into a browser or Power BI Web connector as a standalone web page. GitHub raw URLs do not list folders, so the base URL can show `400: invalid request`.

Use it only as the `GitHubRawBaseUrl` parameter in Power Query. To test that raw file access works, open this file URL instead:

```text
https://raw.githubusercontent.com/Naman7417/MIS-for-RE-Growth-in-the-country/main/powerbi-re-mis/data/refresh_manifest.csv
```
