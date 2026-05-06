import argparse
import csv
import os
import re
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv


AMAP_PLACE_TEXT_URL = "https://restapi.amap.com/v3/place/text"
AMAP_GEOCODE_URL = "https://restapi.amap.com/v3/geocode/geo"


def normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", "", str(value).strip())


def split_aliases(alias_text: str) -> List[str]:
    if not alias_text:
        return []

    parts = re.split(r"[|,，/、;；]", alias_text)
    return [p.strip() for p in parts if p.strip()]


def safe_float_pair(location: str) -> Tuple[str, str]:
    """
    高德 location 格式通常是 "longitude,latitude"
    """
    if not location or "," not in location:
        return "", ""

    lon, lat = location.split(",", 1)
    return lon.strip(), lat.strip()


def request_json(url: str, params: Dict[str, str], timeout: int = 10) -> Dict:
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        return {
            "status": "0",
            "info": f"REQUEST_ERROR: {exc}",
            "pois": [],
            "geocodes": [],
        }


def search_amap_poi(
    keyword: str,
    city: str,
    amap_key: str,
    offset: int = 10,
) -> List[Dict]:
    params = {
        "key": amap_key,
        "keywords": keyword,
        "city": city,
        "citylimit": "true",
        "offset": str(offset),
        "page": "1",
        "extensions": "all",
        "output": "JSON",
    }

    data = request_json(AMAP_PLACE_TEXT_URL, params)

    if data.get("status") != "1":
        print(f"[WARN] POI search failed: keyword={keyword}, info={data.get('info')}")
        return []

    pois = data.get("pois", [])
    if isinstance(pois, list):
        return pois
    return []


def geocode_fallback(
    address: str,
    city: str,
    amap_key: str,
) -> Optional[Dict]:
    params = {
        "key": amap_key,
        "address": address,
        "city": city,
        "output": "JSON",
    }

    data = request_json(AMAP_GEOCODE_URL, params)

    if data.get("status") != "1":
        print(f"[WARN] Geocode failed: address={address}, info={data.get('info')}")
        return None

    geocodes = data.get("geocodes", [])
    if not geocodes:
        return None

    return geocodes[0]


def score_poi_match(row: Dict[str, str], poi: Dict) -> int:
    """
    简单可解释匹配分。
    这个分数不是推荐分，只用于判断高德返回结果是否像目标 POI。
    """
    target_name = normalize_text(row.get("poi_name"))
    aliases = [normalize_text(x) for x in split_aliases(row.get("poi_alias", ""))]
    target_city = normalize_text(row.get("city"))
    target_district = normalize_text(row.get("district"))

    amap_name = normalize_text(poi.get("name"))
    amap_city = normalize_text(poi.get("cityname"))
    amap_district = normalize_text(poi.get("adname"))
    amap_address = normalize_text(poi.get("address"))
    amap_type = normalize_text(poi.get("type"))

    score = 0

    # 名称匹配最重要
    if amap_name == target_name:
        score += 60
    elif target_name and target_name in amap_name:
        score += 45
    elif amap_name and amap_name in target_name:
        score += 35

    # 别名匹配
    for alias in aliases:
        if not alias:
            continue
        if amap_name == alias:
            score += 40
            break
        if alias in amap_name or amap_name in alias:
            score += 25
            break

    # 城市匹配
    if target_city and target_city in amap_city:
        score += 20

    # 区县匹配
    if target_district and target_district in amap_district:
        score += 15

    # 地址包含目标区县或地点名
    if target_district and target_district in amap_address:
        score += 5
    if target_name and target_name in amap_address:
        score += 5

    # 类型弱匹配
    poi_type = normalize_text(row.get("poi_type"))
    if poi_type and poi_type in amap_type:
        score += 5

    # 明显不在重庆，强惩罚
    if target_city and target_city not in amap_city:
        score -= 50

    return max(score, 0)


def choose_best_poi(row: Dict[str, str], pois: List[Dict]) -> Tuple[Optional[Dict], int]:
    if not pois:
        return None, 0

    scored = [(poi, score_poi_match(row, poi)) for poi in pois]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[0]


def build_search_keywords(row: Dict[str, str]) -> List[str]:
    keywords = []

    name = row.get("poi_name", "").strip()
    if name:
        keywords.append(name)

    aliases = split_aliases(row.get("poi_alias", ""))
    for alias in aliases:
        if alias not in keywords:
            keywords.append(alias)

    # 最后尝试“城市 + 名称”
    city = row.get("city", "").strip()
    if city and name:
        city_name = f"{city}{name}"
        if city_name not in keywords:
            keywords.append(city_name)

    return keywords


def enrich_row(row: Dict[str, str], amap_key: str, sleep_seconds: float) -> Dict[str, str]:
    city = row.get("city", "重庆").strip() or "重庆"

    existing_id = row.get("amap_poi_id", "").strip()
    existing_lon = row.get("longitude", "").strip()
    existing_lat = row.get("latitude", "").strip()

    # 已经完整补全的，保留
    if existing_id and existing_lon and existing_lat:
        row["match_status"] = row.get("match_status", "already_enriched") or "already_enriched"
        return row

    best_poi = None
    best_score = 0
    best_keyword = ""

    for keyword in build_search_keywords(row):
        pois = search_amap_poi(keyword=keyword, city=city, amap_key=amap_key)
        candidate, score = choose_best_poi(row, pois)

        if score > best_score:
            best_poi = candidate
            best_score = score
            best_keyword = keyword

        time.sleep(sleep_seconds)

        # 分数足够高就不继续试别名
        if best_score >= 85:
            break

    if best_poi:
        lon, lat = safe_float_pair(best_poi.get("location", ""))

        row["amap_poi_id"] = best_poi.get("id", "") or row.get("amap_poi_id", "")
        row["longitude"] = lon or row.get("longitude", "")
        row["latitude"] = lat or row.get("latitude", "")
        row["amap_name"] = best_poi.get("name", "")
        row["amap_address"] = best_poi.get("address", "")
        row["amap_type"] = best_poi.get("type", "")
        row["amap_cityname"] = best_poi.get("cityname", "")
        row["amap_adname"] = best_poi.get("adname", "")
        row["match_score"] = str(best_score)
        row["match_keyword"] = best_keyword

        if best_score >= 75:
            row["match_status"] = "matched"
        elif best_score >= 45:
            row["match_status"] = "need_review"
        else:
            row["match_status"] = "low_confidence"

        return row

    # POI 搜索失败后，尝试地理编码兜底
    address = f"{city}{row.get('district', '')}{row.get('poi_name', '')}"
    geocode = geocode_fallback(address=address, city=city, amap_key=amap_key)
    time.sleep(sleep_seconds)

    if geocode:
        lon, lat = safe_float_pair(geocode.get("location", ""))

        row["longitude"] = lon or row.get("longitude", "")
        row["latitude"] = lat or row.get("latitude", "")
        row["amap_poi_id"] = row.get("amap_poi_id", "")
        row["amap_name"] = geocode.get("formatted_address", "")
        row["amap_address"] = geocode.get("formatted_address", "")
        row["amap_type"] = "geocode"
        row["amap_cityname"] = geocode.get("city", "")
        row["amap_adname"] = geocode.get("district", "")
        row["match_score"] = "30"
        row["match_keyword"] = address
        row["match_status"] = "geocode_only"
        return row

    row["match_score"] = "0"
    row["match_keyword"] = ""
    row["match_status"] = "not_found"
    return row


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    if not rows:
        raise ValueError("No rows to write.")

    path.parent.mkdir(parents=True, exist_ok=True)

    # 收集所有字段，兼容新增列
    fieldnames = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich Chongqing POI CSV with AMap POI ID and coordinates.")
    parser.add_argument("--input", default="data/seed/chongqing_pois.csv")
    parser.add_argument("--output", default="data/processed/chongqing_pois_enriched.csv")
    parser.add_argument("--low-confidence", default="data/processed/chongqing_pois_low_confidence.csv")
    parser.add_argument("--sleep", type=float, default=0.2, help="Sleep seconds between API calls.")
    args = parser.parse_args()

    load_dotenv()

    amap_key = os.getenv("AMAP_WEB_SERVICE_KEY")
    if not amap_key:
        raise RuntimeError("Missing AMAP_WEB_SERVICE_KEY in .env")

    input_path = Path(args.input)
    output_path = Path(args.output)
    low_confidence_path = Path(args.low_confidence)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    backup_path = input_path.with_suffix(".backup.csv")
    if not backup_path.exists():
        shutil.copyfile(input_path, backup_path)
        print(f"[INFO] Backup created: {backup_path}")

    rows = read_csv(input_path)
    print(f"[INFO] Loaded rows: {len(rows)}")

    enriched_rows = []
    for idx, row in enumerate(rows, start=1):
        name = row.get("poi_name", "")
        print(f"[{idx}/{len(rows)}] Enriching: {name}")
        enriched = enrich_row(row=row, amap_key=amap_key, sleep_seconds=args.sleep)
        enriched_rows.append(enriched)

    write_csv(output_path, enriched_rows)
    print(f"[INFO] Enriched CSV written: {output_path}")

    low_rows = [
        row for row in enriched_rows
        if row.get("match_status") in {"need_review", "low_confidence", "geocode_only", "not_found"}
    ]

    if low_rows:
        write_csv(low_confidence_path, low_rows)
        print(f"[WARN] Low-confidence rows written: {low_confidence_path}")
    else:
        print("[INFO] No low-confidence rows.")

    status_count = {}
    for row in enriched_rows:
        status = row.get("match_status", "unknown")
        status_count[status] = status_count.get(status, 0) + 1

    print("\n[SUMMARY]")
    for status, count in status_count.items():
        print(f"{status}: {count}")


if __name__ == "__main__":
    main()