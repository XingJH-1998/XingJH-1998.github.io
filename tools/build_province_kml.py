#!/usr/bin/env python3
"""Build province-level KML tiers and a single WKT CSV from eBird + DataV boundaries.

Usage:
    python3 build_province_kml.py "/path/to/MyEBirdData.csv" china-provinces.json

Outputs one KML per richness tier, plus a combined KML. Import each tier KML
into Google My Maps as its own layer and give the layer a matching colour.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from collections import defaultdict
from xml.sax.saxutils import escape

try:  # Optional: used to clean self-intersecting WKT polygons for My Maps.
    import shapely
    from shapely import wkt as shapely_wkt
    from shapely.geometry import shape as shapely_shape
    from shapely.ops import unary_union
    from shapely.validation import make_valid
    HAS_SHAPELY = True
except ImportError:  # pragma: no cover
    HAS_SHAPELY = False

PROVINCE_NAMES = {
    110000: ("Beijing", "北京"), 120000: ("Tianjin", "天津"), 130000: ("Hebei", "河北"),
    140000: ("Shanxi", "山西"), 150000: ("Inner Mongolia", "内蒙古"),
    210000: ("Liaoning", "辽宁"), 220000: ("Jilin", "吉林"), 230000: ("Heilongjiang", "黑龙江"),
    310000: ("Shanghai", "上海"), 320000: ("Jiangsu", "江苏"), 330000: ("Zhejiang", "浙江"),
    340000: ("Anhui", "安徽"), 350000: ("Fujian", "福建"), 360000: ("Jiangxi", "江西"),
    370000: ("Shandong", "山东"), 410000: ("Henan", "河南"), 420000: ("Hubei", "湖北"),
    430000: ("Hunan", "湖南"), 440000: ("Guangdong", "广东"), 450000: ("Guangxi", "广西"),
    460000: ("Hainan", "海南"), 500000: ("Chongqing", "重庆"), 510000: ("Sichuan", "四川"),
    520000: ("Guizhou", "贵州"), 530000: ("Yunnan", "云南"), 540000: ("Tibet", "西藏"),
    610000: ("Shaanxi", "陕西"), 620000: ("Gansu", "甘肃"), 630000: ("Qinghai", "青海"),
    640000: ("Ningxia", "宁夏"), 650000: ("Xinjiang", "新疆"),
    710000: ("Taiwan", "台湾"), 810000: ("Hong Kong", "香港"), 820000: ("Macau", "澳门"),
}

TIERS = [
    ("400plus", "400+ species", "1f4d36", "b3"),
    ("250-399", "250-399 species", "5b7f5f", "b3"),
    ("100-249", "100-249 species", "a3b58a", "b3"),
    ("under-100", "Under 100 species", "d8c9a3", "b3"),
    ("no-data", "No eBird records", "e7e2d8", "8c"),
]


def kml_color(hex_color: str, alpha: str = "b3") -> str:
    r, g, b = (hex_color[i:i + 2] for i in (0, 2, 4))
    return f"{alpha}{b}{g}{r}".lower()


def tier_for(species: int) -> str:
    if species >= 400:
        return "400plus"
    if species >= 250:
        return "250-399"
    if species >= 100:
        return "100-249"
    if species > 0:
        return "under-100"
    return "no-data"


def province_stats(source: Path):
    stats = defaultdict(lambda: {"species": set(), "checklists": set(), "sites": set()})
    with source.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            code = row["State/Province"]
            if not code.startswith("CN-"):
                continue
            stats[code]["species"].add(row["Scientific Name"])
            stats[code]["checklists"].add(row["Submission ID"])
            stats[code]["sites"].add(row["Location ID"])
    return stats


def ring_coordinates(ring) -> str:
    return " ".join(f"{lon:.6f},{lat:.6f},0" for lon, lat in ring)


def polygon_xml(polygon) -> str:
    if not polygon:
        return ""
    parts = ["<Polygon><outerBoundaryIs><LinearRing><coordinates>",
             ring_coordinates(polygon[0]),
             "</coordinates></LinearRing></outerBoundaryIs>"]
    for hole in polygon[1:]:
        parts += ["<innerBoundaryIs><LinearRing><coordinates>",
                  ring_coordinates(hole),
                  "</coordinates></LinearRing></innerBoundaryIs>"]
    parts.append("</Polygon>")
    return "".join(parts)


def geometry_xml(geometry) -> str:
    if geometry["type"] == "Polygon":
        return polygon_xml(geometry["coordinates"])
    if geometry["type"] == "MultiPolygon":
        return "<MultiGeometry>" + "".join(polygon_xml(p) for p in geometry["coordinates"]) + "</MultiGeometry>"
    return ""


def wkt_ring(ring) -> str:
    points = list(ring)
    if points[0] != points[-1]:
        points.append(points[0])
    return "(" + ", ".join(f"{lon:.5f} {lat:.5f}" for lon, lat in points) + ")"


def wkt_polygon(rings) -> str:
    return "(" + ", ".join(wkt_ring(ring) for ring in rings) + ")"


def wkt_geometry(geometry) -> str:
    if geometry["type"] == "Polygon":
        return "POLYGON " + wkt_polygon(geometry["coordinates"])
    if geometry["type"] == "MultiPolygon":
        return "MULTIPOLYGON (" + ", ".join(wkt_polygon(poly) for poly in geometry["coordinates"]) + ")"
    return ""


def wkt_for(geometry) -> str:
    """Return a valid WKT polygon, repairing shared-border self-intersections when possible."""
    if HAS_SHAPELY:
        geom = shapely_shape(geometry)
        geom = make_valid(geom)
        if geom.geom_type not in ("Polygon", "MultiPolygon"):
            polygons = [part for part in getattr(geom, "geoms", []) if part.geom_type in ("Polygon", "MultiPolygon")]
            if polygons:
                geom = unary_union(polygons)
        if not geom.is_empty and geom.geom_type in ("Polygon", "MultiPolygon"):
            return shapely_wkt.dumps(geom, rounding_precision=5, trim=True)
    return wkt_geometry(geometry)


def species_bucket(species: int) -> str:
    if species >= 400:
        return "400+"
    if species >= 250:
        return "250-399"
    if species >= 100:
        return "100-249"
    if species > 0:
        return "Under 100"
    return "No data"


def style_xml(style_id: str, color: str, alpha: str) -> str:
    fill = kml_color(color, alpha)
    return (
        f'<Style id="{style_id}">'
        f'<LineStyle><color>ff7d8778</color><width>1</width></LineStyle>'
        f'<PolyStyle><color>{fill}</color><fill>1</fill><outline>1</outline></PolyStyle>'
        f'</Style>'
    )


def placemark(feature, stats, style_id: str) -> str:
    props = feature["properties"]
    adcode = props["adcode"]
    code = f"CN-{adcode // 10000:02d}"
    en, zh = PROVINCE_NAMES[adcode]
    data = stats.get(code)
    if data and data["species"]:
        species = len(data["species"])
        sites = len(data["sites"])
        checklists = len(data["checklists"])
        description = f"{species} species · {sites} sites · {checklists} checklists"
    else:
        species = sites = checklists = 0
        description = "No eBird records in this export"
    name = f"{en} {zh}"
    return (
        "<Placemark>"
        f"<name>{escape(name)}</name>"
        f"<description><![CDATA[{description}]]></description>"
        f"<styleUrl>#{style_id}</styleUrl>"
        "<ExtendedData>"
        f'<Data name="Species"><value>{species}</value></Data>'
        f'<Data name="Sites"><value>{sites}</value></Data>'
        f'<Data name="Checklists"><value>{checklists}</value></Data>'
        "</ExtendedData>"
        f"{geometry_xml(feature['geometry'])}"
        "</Placemark>"
    )


def document(name: str, body: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
        f"<name>{escape(name)}</name>"
        f"{body}"
        "</Document></kml>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="eBird MyEBirdData.csv export")
    parser.add_argument("boundaries", type=Path, help="China province GeoJSON (DataV 100000_full.json)")
    parser.add_argument("--out", type=Path, default=Path("map-data"), help="output directory (default: map-data)")
    args = parser.parse_args()

    source = args.source
    boundary_file = args.boundaries
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    stats = province_stats(source)
    geo = json.loads(boundary_file.read_text(encoding="utf-8"))
    features = [f for f in geo["features"] if isinstance(f["properties"].get("adcode"), int)]

    # Per-tier KML files: import each one as a separate My Maps layer.
    by_tier = defaultdict(list)
    for feature in features:
        adcode = feature["properties"]["adcode"]
        data = stats.get(f"CN-{adcode // 10000:02d}")
        species = len(data["species"]) if data else 0
        by_tier[tier_for(species)].append(feature)

    for tier_id, label, color, alpha in TIERS:
        style = style_xml("province", color, alpha)
        marks = "".join(placemark(f, stats, "province") for f in by_tier[tier_id])
        body = style + marks
        path = out / f"china-provinces-{tier_id}.kml"
        path.write_text(document(f"China provinces · {label}", body), encoding="utf-8")
        print(f"  {path.name}: {len(by_tier[tier_id])} provinces")

    # Combined KML: keeps per-province colours in Google Earth; My Maps may reset styles.
    styles = "".join(style_xml(f"tier-{tier_id}", color, alpha) for tier_id, _, color, alpha in TIERS)
    marks = []
    for feature in features:
        adcode = feature["properties"]["adcode"]
        data = stats.get(f"CN-{adcode // 10000:02d}")
        species = len(data["species"]) if data else 0
        marks.append(placemark(feature, stats, f"tier-{tier_for(species)}"))
    (out / "china-provinces-all.kml").write_text(
        document("China provinces · birding richness", styles + "".join(marks)), encoding="utf-8"
    )
    print(f"  china-provinces-all.kml: {len(features)} provinces")

    # One-row-per-province CSV with WKT geometry: a single My Maps layer,
    # styled by the "Species Bucket" column. More reliable than KML colours.
    wkt_rows = []
    for feature in features:
        adcode = feature["properties"]["adcode"]
        en, zh = PROVINCE_NAMES[adcode]
        data = stats.get(f"CN-{adcode // 10000:02d}")
        species = len(data["species"]) if data else 0
        sites = len(data["sites"]) if data else 0
        checklists = len(data["checklists"]) if data else 0
        description = (f"{species} species · {sites} sites · {checklists} checklists"
                       if species else "No eBird records in this export")
        wkt_rows.append({
            "Name": f"{en} {zh}",
            "Description": description,
            "WKT": wkt_for(feature["geometry"]),
            "Level": "Province",
            "Species": species,
            "Sites": sites,
            "Checklists": checklists,
            "Species Bucket": species_bucket(species),
        })
    wkt_rows.sort(key=lambda row: (-row["Species"], row["Name"]))
    wkt_path = out / "mymaps-china-provinces-wkt.csv"
    with wkt_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "Name", "Description", "WKT", "Level", "Species", "Sites",
            "Checklists", "Species Bucket",
        ])
        writer.writeheader()
        writer.writerows(wkt_rows)
    print(f"  {wkt_path.name}: {len(wkt_rows)} provinces ({wkt_path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
