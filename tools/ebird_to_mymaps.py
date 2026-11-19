#!/usr/bin/env python3
"""Build Google My Maps-ready layers from an eBird "MyEBirdData.csv" export.

Usage:
    python3 tools/ebird_to_mymaps.py "/path/to/MyEBirdData.csv" --out map-data

Each row is one eBird location, aggregated over every checklist. Coordinates
are WGS84. The output includes precise birding locations, so keep it out of
public repositories and review it before publishing a public map.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

COUNTRY_NAMES = {
    "CN": "China (中国)",
    "MY": "Malaysia",
    "US": "United States",
    "ID": "Indonesia",
    "GB": "United Kingdom",
    "KH": "Cambodia",
    "BD": "Bangladesh",
    "LK": "Sri Lanka",
    "JP": "Japan",
}

# code: (English, Chinese, macro region)
PROVINCES = {
    "CN-11": ("Beijing", "北京", "North"),
    "CN-12": ("Tianjin", "天津", "North"),
    "CN-13": ("Hebei", "河北", "North"),
    "CN-14": ("Shanxi", "山西", "North"),
    "CN-15": ("Inner Mongolia", "内蒙古", "North"),
    "CN-21": ("Liaoning", "辽宁", "Northeast"),
    "CN-22": ("Jilin", "吉林", "Northeast"),
    "CN-23": ("Heilongjiang", "黑龙江", "Northeast"),
    "CN-31": ("Shanghai", "上海", "East"),
    "CN-32": ("Jiangsu", "江苏", "East"),
    "CN-33": ("Zhejiang", "浙江", "East"),
    "CN-34": ("Anhui", "安徽", "East"),
    "CN-35": ("Fujian", "福建", "East"),
    "CN-36": ("Jiangxi", "江西", "East"),
    "CN-37": ("Shandong", "山东", "East"),
    "CN-41": ("Henan", "河南", "Central"),
    "CN-42": ("Hubei", "湖北", "Central"),
    "CN-43": ("Hunan", "湖南", "Central"),
    "CN-44": ("Guangdong", "广东", "South"),
    "CN-45": ("Guangxi", "广西", "South"),
    "CN-46": ("Hainan", "海南", "South"),
    "CN-50": ("Chongqing", "重庆", "Southwest"),
    "CN-51": ("Sichuan", "四川", "Southwest"),
    "CN-52": ("Guizhou", "贵州", "Southwest"),
    "CN-53": ("Yunnan", "云南", "Southwest"),
    "CN-54": ("Tibet", "西藏", "Southwest"),
    "CN-61": ("Shaanxi", "陕西", "Northwest"),
    "CN-62": ("Gansu", "甘肃", "Northwest"),
    "CN-63": ("Qinghai", "青海", "Northwest"),
    "CN-64": ("Ningxia", "宁夏", "Northwest"),
    "CN-65": ("Xinjiang", "新疆", "Northwest"),
}

COLUMNS = [
    "Name", "Description", "Latitude", "Longitude",
    "Country", "Province", "Region", "Checklists", "Species",
    "First Visit", "Last Visit", "Species Bucket", "Visit Bucket",
]


def bucket_species(n: int) -> str:
    for limit, label in ((300, "300+"), (200, "200-299"), (150, "150-199"),
                         (100, "100-149"), (50, "50-99")):
        if n >= limit:
            return label
    return "Under 50"


def bucket_visits(n: int) -> str:
    for limit, label in ((20, "20+"), (10, "10-19"), (5, "5-9"), (2, "2-4")):
        if n >= limit:
            return label
    return "1"


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {path.name}: {len(rows)} rows")


def aggregate(source: Path) -> tuple[dict, int]:
    sites: dict[str, dict] = {}
    checklists: set[str] = set()
    with source.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            key = row["Location ID"].strip() or row["Location"].strip()
            site = sites.setdefault(key, {
                "name": row["Location"].strip(),
                "lid": row["Location ID"].strip(),
                "checklists": set(),
                "species": set(),
                "dates": [],
                "coords": [],
                "country": row["State/Province"].split("-")[0],
                "province": row["State/Province"],
            })
            site["checklists"].add(row["Submission ID"])
            site["species"].add(row["Scientific Name"])
            site["dates"].append(row["Date"])
            site["coords"].append((float(row["Latitude"]), float(row["Longitude"])))
            checklists.add(row["Submission ID"])
    return sites, len(checklists)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="eBird MyEBirdData.csv export")
    parser.add_argument("--out", type=Path, default=Path("map-data"), help="output directory (default: map-data)")
    args = parser.parse_args()

    sites, n_checklists = aggregate(args.source)
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    name_counts = Counter(site["name"] for site in sites.values())
    rows = []
    for site in sites.values():
        coords = site["coords"]
        lat = sum(c[0] for c in coords) / len(coords)
        lon = sum(c[1] for c in coords) / len(coords)
        country = site["country"]
        code = site["province"]

        if country == "CN" and code in PROVINCES:
            prov_en, prov_zh, region = PROVINCES[code]
            province = f"{prov_en} ({prov_zh})"
            region_label = f"China · {region}"
        else:
            province = code
            region_label = COUNTRY_NAMES.get(country, country)
            region = "International"

        name = site["name"]
        if name_counts[name] > 1:
            name = f"{name} [{province}]"

        first, last = min(site["dates"]), max(site["dates"])
        visits = len(site["checklists"])
        species = len(site["species"])
        description = " · ".join([
            f"{province}, {COUNTRY_NAMES.get(country, country)}",
            f"{visits} checklists",
            f"{species} species",
            f"first {first}, latest {last}",
            f"eBird ID {site['lid']}" if site["lid"] else "",
        ]).strip(" ·")

        rows.append({
            "Name": name,
            "Description": description,
            "Latitude": f"{lat:.6f}",
            "Longitude": f"{lon:.6f}",
            "Country": COUNTRY_NAMES.get(country, country),
            "Province": province,
            "Region": region_label,
            "Checklists": visits,
            "Species": species,
            "First Visit": first,
            "Last Visit": last,
            "Species Bucket": bucket_species(species),
            "Visit Bucket": bucket_visits(visits),
            "_country": country,
            "_macro": region,
            "_species": site["species"],
        })

    rows.sort(key=lambda r: (-r["Checklists"], r["Name"]))

    print("Site layers:")
    write_csv(out / "sites-all.csv", rows)
    write_csv(out / "sites-china.csv", [r for r in rows if r["_country"] == "CN"])
    write_csv(out / "sites-international.csv", [r for r in rows if r["_country"] != "CN"])

    china_groups = {
        "sites-china-east-north.csv": {"North", "Northeast", "East"},
        "sites-china-south-central.csv": {"Central", "South"},
        "sites-china-west.csv": {"Southwest", "Northwest"},
    }
    for filename, macros in china_groups.items():
        write_csv(out / filename, [r for r in rows if r["_country"] == "CN" and r["_macro"] in macros])

    # Small enough to use on a public page after a manual privacy review.
    write_csv(out / "sites-curated.csv", [r for r in rows if r["Checklists"] >= 3])

    print("Summary layers:")
    provinces = defaultdict(lambda: {"coords": [], "checklists": 0, "species": set()})
    for r in rows:
        if r["_country"] != "CN":
            continue
        p = provinces[r["Province"]]
        p["coords"].append((float(r["Latitude"]), float(r["Longitude"])))
        p["checklists"] += r["Checklists"]
        p["species"] |= r["_species"]

    province_rows = []
    for name, p in provinces.items():
        region = next((v[2] for v in PROVINCES.values() if f"{v[0]} ({v[1]})" == name), "")
        species = len(p["species"])
        province_rows.append({
            "Name": name,
            "Description": f"China · {region} · {species} species · {len(p['coords'])} sites · {p['checklists']} checklists",
            "Latitude": f"{sum(c[0] for c in p['coords']) / len(p['coords']):.6f}",
            "Longitude": f"{sum(c[1] for c in p['coords']) / len(p['coords']):.6f}",
            "Country": "China (中国)",
            "Province": name,
            "Region": f"China · {region}",
            "Checklists": p["checklists"],
            "Species": species,
            "Species Bucket": bucket_species(species),
            "Visit Bucket": bucket_visits(p["checklists"]),
        })
    province_rows.sort(key=lambda r: -r["Species"])
    write_csv(out / "provinces-china.csv", province_rows)

    countries = defaultdict(lambda: {"coords": [], "checklists": 0, "species": set(), "sites": 0})
    for r in rows:
        c = countries[r["Country"]]
        c["coords"].append((float(r["Latitude"]), float(r["Longitude"])))
        c["checklists"] += r["Checklists"]
        c["species"] |= r["_species"]
        c["sites"] += 1

    country_rows = []
    for name, c in countries.items():
        species = len(c["species"])
        country_rows.append({
            "Name": name,
            "Description": f"{species} species · {c['sites']} sites · {c['checklists']} checklists",
            "Latitude": f"{sum(p[0] for p in c['coords']) / len(c['coords']):.6f}",
            "Longitude": f"{sum(p[1] for p in c['coords']) / len(c['coords']):.6f}",
            "Country": name,
            "Region": name,
            "Checklists": c["checklists"],
            "Species": species,
            "Species Bucket": bucket_species(species),
            "Visit Bucket": bucket_visits(c["checklists"]),
        })
    country_rows.sort(key=lambda r: -r["Species"])
    write_csv(out / "countries.csv", country_rows)

    print("\nTotals:")
    print(f"  checklists: {n_checklists}")
    print(f"  sites: {len(rows)}")
    print(f"  species: {len({sp for r in rows for sp in r['_species']})}")
    print(f"  China sites: {sum(1 for r in rows if r['_country'] == 'CN')}")
    print(f"  sites with 3+ checklists: {sum(1 for r in rows if r['Checklists'] >= 3)}")


if __name__ == "__main__":
    main()
