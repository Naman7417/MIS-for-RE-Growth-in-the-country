from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "data"


URLS = {
    "mnre_physical_progress": "https://mnre.gov.in/en/physical-progress/",
    "mnre_year_wise_achievement": "https://mnre.gov.in/en/year-wise-achievement/",
    "cea_executive_summary": "https://cea.nic.in/executive-summary-report/?lang=en",
    "cea_installed_capacity": "https://cea.nic.in/installed-capacity-report/?lang=en",
    "cea_transmission_reports": "https://cea.nic.in/transmission-reports/?lang=en",
    "cea_power_supply": "https://cea.nic.in/power-supply/?lang=en",
    "cea_renewable_generation": "https://cea.nic.in/renewable-generation-report/?lang=en",
    "pm_surya_ghar": "https://pmsuryaghar.gov.in/#/state-ut-wise-progress",
    "pm_kusum": "https://pmkusum.mnre.gov.in/#/landing#achievement",
    "nghm_projects": "https://nghm.mnre.gov.in/project?language=en",
    "nsgm_smart_meters": "https://www.nsgm.gov.in/en/sm-stats-all",
}


TECH_MAP = {
    "solar": "Solar",
    "wind": "Wind",
    "small hydro": "Hydro",
    "large hydro": "Hydro",
    "hydro": "Hydro",
    "biomass": "Bioenergy",
    "bio": "Bioenergy",
    "waste": "Bioenergy",
}


@dataclass
class FetchResult:
    table_name: str
    rows: list[dict[str, Any]]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def clean_header(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    text = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return text or "column"


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def numeric_value(value: Any) -> float | None:
    if value is None:
        return None
    text = clean_text(value)
    if not text or text.lower() in {"nan", "-", "--", "na", "n/a"}:
        return None
    match = re.search(r"-?\d+(?:,\d{2,3})*(?:\.\d+)?|-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    return float(match.group(0).replace(",", ""))


def make_request(url: str) -> requests.Response:
    headers = {
        "User-Agent": "Mozilla/5.0 PowerBI-RE-MIS data refresh",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    response = requests.get(url, headers=headers, timeout=45)
    response.raise_for_status()
    return response


def read_html_tables(url: str) -> list[pd.DataFrame]:
    response = make_request(url)
    return pd.read_html(StringIO(response.text))


def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = [" ".join(clean_text(part) for part in col if clean_text(part)) for col in frame.columns]
    frame.columns = [clean_header(col) for col in frame.columns]
    return frame


def best_table(tables: list[pd.DataFrame]) -> pd.DataFrame:
    if not tables:
        return pd.DataFrame()
    return max(tables, key=lambda frame: frame.shape[0] * max(frame.shape[1], 1))


def technology_from_label(label: str) -> str | None:
    lower = label.lower()
    for key, tech in TECH_MAP.items():
        if key in lower:
            return tech
    return None


def detect_value_column(df: pd.DataFrame, preferred_terms: list[str]) -> str | None:
    columns = list(df.columns)
    for term in preferred_terms:
        for col in columns:
            if term in col:
                return col
    numeric_scores = []
    for col in columns:
        score = df[col].map(numeric_value).notna().sum()
        numeric_scores.append((score, col))
    numeric_scores.sort(reverse=True)
    return numeric_scores[0][1] if numeric_scores and numeric_scores[0][0] else None


def parse_mnre_physical_progress() -> list[FetchResult]:
    tables = read_html_tables(URLS["mnre_physical_progress"])
    df = flatten_columns(best_table(tables))
    if df.empty:
        return []

    label_col = df.columns[0]
    cumulative_col = detect_value_column(df, ["cumulative", "total"])
    current_year_col = detect_value_column(df, ["achievement_during", "during", "fy"])

    raw_rows: list[dict[str, Any]] = []
    tech_rows: dict[str, float] = {}

    for _, row in df.iterrows():
        label = clean_text(row.get(label_col))
        if not label:
            continue
        cumulative_mw = numeric_value(row.get(cumulative_col)) if cumulative_col else None
        current_year_mw = numeric_value(row.get(current_year_col)) if current_year_col else None
        raw_rows.append(
            {
                "source": "MNRE physical progress",
                "source_url": URLS["mnre_physical_progress"],
                "technology_raw": label,
                "cumulative_mw": cumulative_mw,
                "cumulative_gw": None if cumulative_mw is None else round(cumulative_mw / 1000, 4),
                "current_year_addition_mw": current_year_mw,
                "current_year_addition_gw": None if current_year_mw is None else round(current_year_mw / 1000, 4),
                "retrieved_at_utc": utc_now(),
            }
        )
        tech = technology_from_label(label)
        if tech and cumulative_mw is not None:
            tech_rows[tech] = tech_rows.get(tech, 0.0) + cumulative_mw

    normalized = [
        {
            "source": "MNRE physical progress",
            "technology": tech,
            "cumulative_mw": round(value, 3),
            "cumulative_gw": round(value / 1000, 4),
            "retrieved_at_utc": utc_now(),
            "source_url": URLS["mnre_physical_progress"],
        }
        for tech, value in sorted(tech_rows.items())
    ]
    return [
        FetchResult("mnre_physical_progress_raw", raw_rows),
        FetchResult("re_installed_capacity_technology", normalized),
    ]


def parse_mnre_year_wise_achievement() -> list[FetchResult]:
    tables = read_html_tables(URLS["mnre_year_wise_achievement"])
    df = flatten_columns(best_table(tables))
    if df.empty:
        return []

    label_col = df.columns[0]
    year_cols = [col for col in df.columns if re.search(r"20\d{2}", col)]
    rows: list[dict[str, Any]] = []
    aggregate_by_fy: dict[str, float] = {}

    for _, row in df.iterrows():
        label = clean_text(row.get(label_col))
        if not label:
            continue
        tech = technology_from_label(label) or label
        for col in year_cols:
            value_mw = numeric_value(row.get(col))
            if value_mw is None:
                continue
            fy = re.sub(r"^.*?(20\d{2}.*)$", r"\1", col).replace("_", "-")
            rows.append(
                {
                    "source": "MNRE year-wise achievement",
                    "fiscal_year": fy,
                    "technology_raw": label,
                    "technology": tech,
                    "capacity_addition_mw": value_mw,
                    "capacity_addition_gw": round(value_mw / 1000, 4),
                    "retrieved_at_utc": utc_now(),
                    "source_url": URLS["mnre_year_wise_achievement"],
                }
            )
            if tech in {"Solar", "Wind", "Hydro", "Bioenergy"}:
                aggregate_by_fy[fy] = aggregate_by_fy.get(fy, 0.0) + value_mw

    aggregate_rows = [
        {
            "source": "MNRE year-wise achievement",
            "fiscal_year": fy,
            "technology": "Total RE",
            "capacity_addition_mw": round(value, 3),
            "capacity_addition_gw": round(value / 1000, 4),
            "retrieved_at_utc": utc_now(),
            "source_url": URLS["mnre_year_wise_achievement"],
        }
        for fy, value in sorted(aggregate_by_fy.items())
    ]
    annual_total_mw = sum(aggregate_by_fy.values())
    cagr_rows: list[dict[str, Any]] = []
    if aggregate_by_fy and annual_total_mw > 0:
        periods = len(aggregate_by_fy)
        cagr_rows.append(
            {
                "source": "MNRE year-wise achievement and MNRE physical progress",
                "period_start": min(aggregate_by_fy.keys()),
                "period_end": max(aggregate_by_fy.keys()),
                "periods": periods,
                "annual_addition_total_mw": round(annual_total_mw, 3),
                "annual_addition_total_gw": round(annual_total_mw / 1000, 4),
                "note": "Use with latest cumulative RE capacity to calculate CAGR after validating FY labels from source page.",
                "retrieved_at_utc": utc_now(),
                "source_url": URLS["mnre_year_wise_achievement"],
            }
        )
    return [
        FetchResult("mnre_annual_re_additions_raw", rows),
        FetchResult("annual_re_capacity_addition", aggregate_rows),
        FetchResult("re_cagr_summary", cagr_rows),
    ]


def parse_report_links() -> list[FetchResult]:
    rows: list[dict[str, Any]] = []
    for source_name in [
        "cea_executive_summary",
        "cea_installed_capacity",
        "cea_transmission_reports",
        "cea_power_supply",
        "cea_renewable_generation",
    ]:
        url = URLS[source_name]
        response = make_request(url)
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            href = urljoin(url, link["href"])
            if not re.search(r"\.(pdf|xlsx?|csv)(?:\?|$)", href, re.IGNORECASE):
                continue
            rows.append(
                {
                    "source": source_name,
                    "report_title": clean_text(link.get_text(" ")),
                    "report_url": href,
                    "file_type": href.rsplit(".", 1)[-1].split("?", 1)[0].lower(),
                    "retrieved_at_utc": utc_now(),
                    "source_url": url,
                }
            )
    return [FetchResult("cea_report_links", rows)]


def parse_nghm_projects() -> list[FetchResult]:
    tables = read_html_tables(URLS["nghm_projects"])
    rows: list[dict[str, Any]] = []
    for index, table in enumerate(tables, start=1):
        df = flatten_columns(table)
        for _, row in df.iterrows():
            item = {col: clean_text(row.get(col)) for col in df.columns}
            if not any(item.values()):
                continue
            item["source"] = "NGHM project portal"
            item["source_table"] = index
            item["source_url"] = URLS["nghm_projects"]
            item["retrieved_at_utc"] = utc_now()
            rows.append(item)
    return [FetchResult("nghm_green_hydrogen_projects", rows)]


async def render_dynamic_source(name: str, url: str) -> list[FetchResult]:
    try:
        from playwright.async_api import async_playwright
    except Exception:
        return [
            FetchResult(
                f"{name}_render_status",
                [
                    {
                        "source": name,
                        "status": "playwright_not_available",
                        "source_url": url,
                        "retrieved_at_utc": utc_now(),
                    }
                ],
            )
        ]

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 1200})
        await page.goto(url, wait_until="domcontentloaded", timeout=90000)
        try:
            await page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            pass
        await page.wait_for_timeout(5000)
        html = await page.content()
        visible_text = await page.locator("body").inner_text(timeout=15000)
        await browser.close()

    rendered_tables: list[dict[str, Any]] = []
    try:
        tables = pd.read_html(StringIO(html))
    except ValueError:
        tables = []

    for table_index, table in enumerate(tables, start=1):
        df = flatten_columns(table)
        for _, row in df.iterrows():
            item = {col: clean_text(row.get(col)) for col in df.columns}
            if not any(item.values()):
                continue
            item["source"] = name
            item["source_table"] = table_index
            item["source_url"] = url
            item["retrieved_at_utc"] = utc_now()
            rendered_tables.append(item)

    text_lines = [
        {
            "source": name,
            "line_number": i + 1,
            "text": line.strip(),
            "source_url": url,
            "retrieved_at_utc": utc_now(),
        }
        for i, line in enumerate(visible_text.splitlines())
        if line.strip()
    ]

    return [
        FetchResult(f"{name}_rendered_tables", rendered_tables),
        FetchResult(f"{name}_visible_text", text_lines),
    ]


def write_csv(output_dir: Path, result: FetchResult) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{result.table_name}.csv"
    rows = result.rows
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    columns: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in columns:
                columns.append(key)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run_static_sources(output_dir: Path) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    tasks = [
        ("mnre_physical_progress", parse_mnre_physical_progress),
        ("mnre_year_wise_achievement", parse_mnre_year_wise_achievement),
        ("cea_report_links", parse_report_links),
        ("nghm_projects", parse_nghm_projects),
    ]
    for name, parser in tasks:
        try:
            for result in parser():
                write_csv(output_dir, result)
        except Exception as exc:
            errors.append(
                {
                    "source": name,
                    "status": "error",
                    "message": str(exc),
                    "retrieved_at_utc": utc_now(),
                }
            )
    return errors


async def run_dynamic_sources(output_dir: Path) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    for name in ["pm_surya_ghar", "pm_kusum", "nsgm_smart_meters"]:
        try:
            for result in await render_dynamic_source(name, URLS[name]):
                write_csv(output_dir, result)
        except Exception as exc:
            errors.append(
                {
                    "source": name,
                    "status": "error",
                    "message": str(exc),
                    "retrieved_at_utc": utc_now(),
                }
            )
    return errors


def write_refresh_manifest(output_dir: Path, errors: list[dict[str, str]]) -> None:
    manifest_rows = [
        {
            "dataset": path.stem,
            "file_name": path.name,
            "row_count": max(sum(1 for _ in path.open(encoding="utf-8")) - 1, 0) if path.stat().st_size else 0,
            "refreshed_at_utc": utc_now(),
        }
        for path in sorted(output_dir.glob("*.csv"))
        if path.name != "refresh_errors.csv"
    ]
    write_csv(output_dir, FetchResult("refresh_manifest", manifest_rows))
    write_csv(output_dir, FetchResult("refresh_errors", errors))


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh India RE MIS source data.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="CSV output directory")
    parser.add_argument("--skip-dynamic", action="store_true", help="Skip JavaScript-rendered sources")
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    errors = run_static_sources(output_dir)

    if not args.skip_dynamic:
        import asyncio

        errors.extend(asyncio.run(run_dynamic_sources(output_dir)))

    write_refresh_manifest(output_dir, errors)
    if errors:
        for error in errors:
            print(f"{error['source']}: {error['message']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
