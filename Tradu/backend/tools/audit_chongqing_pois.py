import csv
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple


INPUT_PATH = Path("data/processed/chongqing_pois_enriched.csv")
REPORT_PATH = Path("docs/data_quality/chongqing_poi_audit_report.md")
AREA_SUMMARY_PATH = Path("data/processed/chongqing_pois_area_summary.csv")


# 重庆主城区及周边粗略经纬度范围，用于发现明显错误点
# 不是严格行政边界，只做异常检查
CHONGQING_LON_MIN = 105.0
CHONGQING_LON_MAX = 107.5
CHONGQING_LAT_MIN = 28.5
CHONGQING_LAT_MAX = 30.5


REQUIRED_COLUMNS = [
    "poi_name",
    "city",
    "district",
    "poi_type",
    "tags",
    "recommended_duration_minutes",
    "best_time",
    "price_level",
    "indoor_outdoor",
    "nearby_area",
    "amap_poi_id",
    "longitude",
    "latitude",
    "match_status",
    "match_score",
]


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_float(value: str):
    try:
        return float(value)
    except Exception:
        return None


def check_missing_required(rows: List[Dict[str, str]]) -> List[Tuple[int, str, str]]:
    problems = []

    for idx, row in enumerate(rows, start=2):  # CSV 第1行是表头
        for col in REQUIRED_COLUMNS:
            if not str(row.get(col, "")).strip():
                problems.append((idx, row.get("poi_name", ""), col))

    return problems


def check_coordinate_range(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    abnormal = []

    for row in rows:
        lon = to_float(row.get("longitude", ""))
        lat = to_float(row.get("latitude", ""))

        if lon is None or lat is None:
            abnormal.append({
                "poi_name": row.get("poi_name", ""),
                "reason": "missing_or_invalid_coordinate",
                "longitude": row.get("longitude", ""),
                "latitude": row.get("latitude", ""),
                "amap_name": row.get("amap_name", ""),
                "match_status": row.get("match_status", ""),
            })
            continue

        if not (CHONGQING_LON_MIN <= lon <= CHONGQING_LON_MAX and CHONGQING_LAT_MIN <= lat <= CHONGQING_LAT_MAX):
            abnormal.append({
                "poi_name": row.get("poi_name", ""),
                "reason": "out_of_chongqing_range",
                "longitude": row.get("longitude", ""),
                "latitude": row.get("latitude", ""),
                "amap_name": row.get("amap_name", ""),
                "match_status": row.get("match_status", ""),
            })

    return abnormal


def check_duplicates(rows: List[Dict[str, str]]) -> Dict[str, List[str]]:
    name_counter = Counter(row.get("poi_name", "").strip() for row in rows)
    amap_id_counter = Counter(row.get("amap_poi_id", "").strip() for row in rows if row.get("amap_poi_id", "").strip())

    duplicate_names = [name for name, count in name_counter.items() if name and count > 1]
    duplicate_amap_ids = [pid for pid, count in amap_id_counter.items() if pid and count > 1]

    return {
        "duplicate_names": duplicate_names,
        "duplicate_amap_ids": duplicate_amap_ids,
    }


def area_summary(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    area_map = defaultdict(list)

    for row in rows:
        area = row.get("nearby_area", "").strip() or "未分组"
        area_map[area].append(row)

    summary_rows = []
    for area, items in sorted(area_map.items(), key=lambda x: len(x[1]), reverse=True):
        types = Counter(item.get("poi_type", "") for item in items)
        districts = Counter(item.get("district", "") for item in items)

        summary_rows.append({
            "nearby_area": area,
            "poi_count": str(len(items)),
            "districts": "|".join([f"{k}:{v}" for k, v in districts.items() if k]),
            "poi_types": "|".join([f"{k}:{v}" for k, v in types.items() if k]),
            "poi_names": "|".join([item.get("poi_name", "") for item in items]),
        })

    return summary_rows


def status_summary(rows: List[Dict[str, str]]) -> Counter:
    return Counter(row.get("match_status", "unknown") for row in rows)


def type_summary(rows: List[Dict[str, str]]) -> Counter:
    return Counter(row.get("poi_type", "unknown") for row in rows)


def district_summary(rows: List[Dict[str, str]]) -> Counter:
    return Counter(row.get("district", "unknown") for row in rows)


def low_confidence_rows(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [
        row for row in rows
        if row.get("match_status") != "matched"
    ]


def generate_report(rows: List[Dict[str, str]]) -> str:
    missing = check_missing_required(rows)
    coord_abnormal = check_coordinate_range(rows)
    duplicates = check_duplicates(rows)
    area_rows = area_summary(rows)
    low_rows = low_confidence_rows(rows)

    status = status_summary(rows)
    types = type_summary(rows)
    districts = district_summary(rows)

    lines = []
    lines.append("# 重庆 POI 种子数据质量审核报告\n")
    lines.append("## 1. 基础统计\n")
    lines.append(f"- POI 总数：{len(rows)}")
    lines.append(f"- 匹配状态统计：{dict(status)}")
    lines.append(f"- 类型统计：{dict(types)}")
    lines.append(f"- 行政区统计：{dict(districts)}\n")

    lines.append("## 2. 必填字段缺失检查\n")
    if not missing:
        lines.append("- 未发现必填字段缺失。\n")
    else:
        lines.append(f"- 发现 {len(missing)} 个字段缺失：")
        for row_idx, poi_name, col in missing:
            lines.append(f"  - 第 {row_idx} 行：{poi_name} 缺失字段 `{col}`")
        lines.append("")

    lines.append("## 3. 经纬度异常检查\n")
    if not coord_abnormal:
        lines.append("- 未发现明显经纬度异常。\n")
    else:
        lines.append(f"- 发现 {len(coord_abnormal)} 个经纬度异常或缺失：")
        for item in coord_abnormal:
            lines.append(
                f"  - {item['poi_name']}：{item['reason']}，"
                f"lon={item['longitude']}，lat={item['latitude']}，"
                f"amap_name={item['amap_name']}，status={item['match_status']}"
            )
        lines.append("")

    lines.append("## 4. 重复数据检查\n")
    if not duplicates["duplicate_names"] and not duplicates["duplicate_amap_ids"]:
        lines.append("- 未发现重复 POI 名称或重复高德 POI ID。\n")
    else:
        if duplicates["duplicate_names"]:
            lines.append(f"- 重复 POI 名称：{duplicates['duplicate_names']}")
        if duplicates["duplicate_amap_ids"]:
            lines.append(f"- 重复高德 POI ID：{duplicates['duplicate_amap_ids']}")
        lines.append("")

    lines.append("## 5. 低置信度匹配检查\n")
    if not low_rows:
        lines.append("- 没有低置信度匹配。\n")
    else:
        lines.append(f"- 发现 {len(low_rows)} 条非 matched 数据，需要人工确认：")
        for row in low_rows:
            lines.append(
                f"  - {row.get('poi_name')}：status={row.get('match_status')}，"
                f"score={row.get('match_score')}，keyword={row.get('match_keyword')}，"
                f"amap_name={row.get('amap_name')}，address={row.get('amap_address')}，"
                f"district={row.get('amap_adname')}"
            )
        lines.append("")

    lines.append("## 6. 片区分组检查\n")
    lines.append("| 片区 | POI数量 | POI列表 |")
    lines.append("|---|---:|---|")
    for item in area_rows:
        lines.append(f"| {item['nearby_area']} | {item['poi_count']} | {item['poi_names']} |")
    lines.append("")

    lines.append("## 7. 审核结论\n")
    if len(low_rows) <= 2 and not coord_abnormal and not duplicates["duplicate_amap_ids"]:
        lines.append("- 当前 POI 数据质量可以进入数据库设计与导入准备阶段。")
        lines.append("- 仍建议人工检查低置信度条目，确认其是否为正确地点。")
    else:
        lines.append("- 当前 POI 数据仍需要修正后再进入下一阶段。")
        lines.append("- 优先修正经纬度异常、重复高德 POI ID 和低置信度条目。")

    return "\n".join(lines)


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"File not found: {INPUT_PATH}")

    rows = read_csv(INPUT_PATH)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = generate_report(rows)
    REPORT_PATH.write_text(report, encoding="utf-8")

    area_rows = area_summary(rows)
    write_csv(
        AREA_SUMMARY_PATH,
        area_rows,
        ["nearby_area", "poi_count", "districts", "poi_types", "poi_names"]
    )

    print(f"[INFO] Audit report written: {REPORT_PATH}")
    print(f"[INFO] Area summary written: {AREA_SUMMARY_PATH}")

    print("\n[SUMMARY]")
    print(f"total: {len(rows)}")
    print(f"match_status: {dict(status_summary(rows))}")
    print(f"low_confidence_or_unmatched: {len(low_confidence_rows(rows))}")
    print(f"coordinate_abnormal: {len(check_coordinate_range(rows))}")
    print(f"duplicate_names: {len(check_duplicates(rows)['duplicate_names'])}")
    print(f"duplicate_amap_ids: {len(check_duplicates(rows)['duplicate_amap_ids'])}")


if __name__ == "__main__":
    main()