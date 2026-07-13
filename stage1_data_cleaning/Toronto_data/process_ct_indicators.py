#!/usr/bin/env python3
"""Stream the 2021 Census Profile ZIP and build a Canada-wide CT indicator table."""

from __future__ import annotations

import csv
import io
import json
import random
import sqlite3
import sys
import time
import zipfile
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ZIP_PATH = ROOT / "indicators" / "98-401-X2021007_eng_CSV.zip"
MEMBER = "98-401-X2021007_English_CSV_data.csv"
OUT_DIR = ROOT / "processed"
DB_PATH = OUT_DIR / ".ct_processing.sqlite3"
ENCODING = "cp1252"

GEO_FIELDS = [
    "CENSUS_YEAR", "DGUID", "ALT_GEO_CODE", "GEO_LEVEL", "GEO_NAME",
    "DATA_QUALITY_FLAG",
]

INDICATORS = {
    "1": {
        "field": "population_2021", "name": "Population, 2021",
        "zh": "2021年人口", "category": "人口", "value_col": "C1_COUNT_TOTAL",
        "unit": "persons", "year": "2021", "notes": "人口总数。",
    },
    "6": {
        "field": "population_density_km2",
        "name": "Population density per square kilometre", "zh": "人口密度",
        "category": "人口", "value_col": "C1_COUNT_TOTAL",
        "unit": "persons per km²", "year": "2021", "notes": "每平方公里人口数。",
    },
    "37": {
        "field": "age_65_plus_pct", "name": "65 years and over",
        "zh": "65岁及以上人口比例", "category": "年龄结构",
        "value_col": "C10_RATE_TOTAL", "unit": "% (0–100)", "year": "2021",
        "notes": "保持源数据0–100表示方式。",
    },
    "57": {
        "field": "average_household_size", "name": "Average household size",
        "zh": "平均家庭户规模", "category": "家庭户",
        "value_col": "C1_COUNT_TOTAL", "unit": "persons per household",
        "year": "2021", "notes": "平均每个家庭户的人数。",
    },
    "113": {
        "field": "median_total_income_2020",
        "name": "Median total income in 2020 among recipients ($)",
        "zh": "2020年收入领取者总收入中位数", "category": "收入",
        "value_col": "C1_COUNT_TOTAL", "unit": "CAD", "year": "2020",
        "notes": "统计对象为收入领取者；金额为加元。",
    },
    "345": {
        "field": "low_income_lim_at_pct",
        "name": "Prevalence of low income based on the Low-income measure, after tax (LIM-AT) (%)",
        "zh": "税后低收入标准（LIM-AT）低收入发生率", "category": "低收入",
        "value_col": "C10_RATE_TOTAL", "unit": "% (0–100)", "year": "2020",
        "notes": "保持源数据0–100表示方式。",
    },
    "1416": {
        "field": "renter_households_pct", "name": "Renter",
        "zh": "租户家庭户比例", "category": "住房",
        "value_col": "C10_RATE_TOTAL", "unit": "% (0–100)", "year": "2021",
        "notes": "保持源数据0–100表示方式。",
    },
    "1467": {
        "field": "shelter_cost_30pct_plus_pct",
        "name": "Spending 30% or more of income on shelter costs",
        "zh": "住房成本占收入30%及以上的家庭户比例", "category": "住房可负担性",
        "value_col": "C10_RATE_TOTAL", "unit": "% (0–100)", "year": "2021",
        "notes": "保持源数据0–100表示方式。",
    },
    "2024": {
        "field": "bachelor_or_higher_age25_64_pct", "name": "Bachelor's degree or higher",
        "zh": "25—64岁人口中学士及以上学历比例", "category": "教育",
        "value_col": "C10_RATE_TOTAL", "unit": "% (0–100)", "year": "2021",
        "notes": "使用ID 2024；统计对象为25—64岁人口，不使用ID 2008。",
    },
    "2230": {
        "field": "unemployment_rate_pct", "name": "Unemployment rate",
        "zh": "失业率", "category": "劳动力市场",
        "value_col": "C10_RATE_TOTAL", "unit": "% (0–100)", "year": "2021",
        "notes": "保持源数据0–100表示方式。",
    },
}

PERCENT_FIELDS = {
    "age_65_plus_pct", "low_income_lim_at_pct", "renter_households_pct",
    "shelter_cost_30pct_plus_pct", "bachelor_or_higher_age25_64_pct",
    "unemployment_rate_pct",
}
NONNEGATIVE_FIELDS = set(x["field"] for x in INDICATORS.values())

INVENTORY_COLUMNS = [
    "标准字段名", "CHARACTERISTIC_ID", "官方英文名称", "中文名称", "指标类别",
    "取值列", "单位", "数据年份", "空间层级", "来源机构", "来源产品", "连接字段",
    "状态", "备注", "source_url", "download_url", "license", "access_date",
]


def clean_numeric(raw: str) -> tuple[str | None, Decimal | None]:
    text = (raw or "").strip()
    if not text or text in {"...", "..", "x", "X", "F", "f"}:
        return None, None
    try:
        number = Decimal(text.replace(",", ""))
    except InvalidOperation:
        return None, None
    return text.replace(",", ""), number


def open_reader(zf: zipfile.ZipFile):
    binary = zf.open(MEMBER, "r")
    text = io.TextIOWrapper(binary, encoding=ENCODING, newline="")
    return binary, text, csv.reader(text)


def col_indices(header: list[str]) -> dict[str, int]:
    required = set(GEO_FIELDS + ["CHARACTERISTIC_ID", "CHARACTERISTIC_NAME", "C1_COUNT_TOTAL", "C10_RATE_TOTAL"])
    missing = sorted(required - set(header))
    if missing:
        raise RuntimeError(f"Missing required columns: {missing}")
    return {name: header.index(name) for name in required}


def setup_db() -> sqlite3.Connection:
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("PRAGMA temp_store=FILE")
    con.execute("""
        CREATE TABLE selected (
            census_year TEXT NOT NULL, dguid TEXT NOT NULL, alt_geo_code TEXT NOT NULL,
            geo_level TEXT NOT NULL, geo_name TEXT NOT NULL, data_quality_flag TEXT,
            characteristic_id TEXT NOT NULL, characteristic_name TEXT NOT NULL,
            value_text TEXT
        )
    """)
    return con


def stream_to_db(con: sqlite3.Connection):
    total_rows = 0
    ct_rows = 0
    selected_rows = 0
    invalid_values = Counter()
    name_mismatches = Counter()
    header = None
    batch = []
    started = time.time()
    with zipfile.ZipFile(ZIP_PATH) as zf:
        binary, text, reader = open_reader(zf)
        try:
            header = next(reader)
            ix = col_indices(header)
            value_ix = {cid: ix[meta["value_col"]] for cid, meta in INDICATORS.items()}
            for row in reader:
                total_rows += 1
                if len(row) != len(header):
                    raise RuntimeError(f"Malformed row {total_rows + 1}: {len(row)} columns, expected {len(header)}")
                if row[ix["GEO_LEVEL"]] != "Census tract":
                    continue
                ct_rows += 1
                cid = row[ix["CHARACTERISTIC_ID"]].strip()
                if cid not in INDICATORS:
                    continue
                selected_rows += 1
                official_name = row[ix["CHARACTERISTIC_NAME"]].strip()
                if official_name != INDICATORS[cid]["name"]:
                    name_mismatches[(cid, official_name)] += 1
                raw_value = row[value_ix[cid]]
                value_text, numeric = clean_numeric(raw_value)
                if value_text is None and (raw_value or "").strip() not in {"", "...", "..", "x", "X", "F", "f"}:
                    invalid_values[(cid, (raw_value or "").strip())] += 1
                batch.append((
                    row[ix["CENSUS_YEAR"]].strip(), row[ix["DGUID"]].strip(),
                    row[ix["ALT_GEO_CODE"]].strip(), row[ix["GEO_LEVEL"]],
                    row[ix["GEO_NAME"]].strip(), row[ix["DATA_QUALITY_FLAG"]].strip(),
                    cid, official_name, value_text,
                ))
                if len(batch) >= 10000:
                    con.executemany("INSERT INTO selected VALUES (?,?,?,?,?,?,?,?,?)", batch)
                    con.commit()
                    batch.clear()
                if total_rows % 1_000_000 == 0:
                    print(f"Scanned {total_rows:,} rows; retained {selected_rows:,}; elapsed {time.time()-started:.1f}s", flush=True)
            if batch:
                con.executemany("INSERT INTO selected VALUES (?,?,?,?,?,?,?,?,?)", batch)
                con.commit()
        finally:
            text.close()
    con.execute("CREATE INDEX idx_selected_dguid_cid ON selected(dguid, characteristic_id)")
    con.commit()
    return header, total_rows, ct_rows, selected_rows, invalid_values, name_mismatches


def write_query_csv(path: Path, header: list[str], query, con: sqlite3.Connection):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(con.execute(query))


def inventory_rows():
    source_url = "https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/index.cfm?Lang=E"
    download_url = "https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/download-telecharger/index-en.cfm"
    rows = []
    for cid, meta in INDICATORS.items():
        rows.append([
            meta["field"], cid, meta["name"], meta["zh"], meta["category"],
            meta["value_col"], meta["unit"], meta["year"], "Census tract",
            "Statistics Canada", "Census Profile, 2021 Census of Population", "DGUID",
            "available", meta["notes"], source_url, download_url,
            "Statistics Canada Open Licence", "2026-07-13",
        ])
    return rows


def dictionary_rows():
    common = [
        ["CENSUS_YEAR", "人口普查年份", "string", "year", "CENSUS_YEAR", "不适用；原样保留", "本产品为2021年人口普查。"],
        ["DGUID", "统计地理唯一标识符", "string", "identifier", "DGUID", "不允许缺失", "首选空间连接字段；始终按字符串处理。"],
        ["ALT_GEO_CODE", "替代地理代码（CT层级为CTUID）", "string", "identifier", "ALT_GEO_CODE", "不允许缺失", "始终按字符串处理，保留前导零。"],
        ["GEO_LEVEL", "地理层级", "string", "category", "GEO_LEVEL", "不允许缺失", "所有记录严格等于Census tract。"],
        ["GEO_NAME", "地理名称", "string", "text", "GEO_NAME", "不允许缺失", "加拿大统计局地理名称。"],
        ["DATA_QUALITY_FLAG", "数据质量标识", "string", "flag", "DATA_QUALITY_FLAG", "空白保持缺失", "如同一CT各指标不一致，另见质量标识明细。"],
    ]
    for cid, meta in INDICATORS.items():
        common.append([
            meta["field"], meta["zh"], "number", meta["unit"],
            f"{meta['value_col']} (CHARACTERISTIC_ID={cid})",
            "空白、...、..、被抑制或不适用值写为空白；不填0", meta["notes"],
        ])
    return common


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output_csv = OUT_DIR / "canada_ct_10_indicators_2021.csv"
    duplicate_csv = OUT_DIR / "duplicate_dguid_characteristic_id.csv"
    quality_csv = OUT_DIR / "data_quality_flag_details.csv"
    geo_issue_csv = OUT_DIR / "geography_field_inconsistencies.csv"
    for p in [output_csv, duplicate_csv, quality_csv, geo_issue_csv]:
        if p.exists():
            p.unlink()

    with zipfile.ZipFile(ZIP_PATH) as zf:
        bad_member = zf.testzip()
        zip_ok = bad_member is None
        info = zf.getinfo(MEMBER)
    if not zip_ok:
        raise RuntimeError(f"ZIP integrity check failed at {bad_member}")

    con = setup_db()
    try:
        header, total_rows, ct_rows, selected_rows, invalid_values, name_mismatches = stream_to_db(con)

        duplicates = con.execute("""
            SELECT dguid, characteristic_id, COUNT(*) AS duplicate_count
            FROM selected GROUP BY dguid, characteristic_id HAVING COUNT(*) > 1
            ORDER BY dguid, characteristic_id
        """).fetchall()
        if duplicates:
            with duplicate_csv.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f); w.writerow(["DGUID", "CHARACTERISTIC_ID", "record_count"]); w.writerows(duplicates)
            raise RuntimeError(f"Found {len(duplicates)} duplicate DGUID + CHARACTERISTIC_ID groups; final wide table was not generated")

        geo_issues = con.execute("""
            SELECT dguid, COUNT(DISTINCT census_year || char(31) || alt_geo_code || char(31) || geo_level || char(31) || geo_name)
            FROM selected GROUP BY dguid HAVING COUNT(DISTINCT census_year || char(31) || alt_geo_code || char(31) || geo_level || char(31) || geo_name) > 1
        """).fetchall()
        if geo_issues:
            with geo_issue_csv.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f); w.writerow(["DGUID", "distinct_geography_record_count"]); w.writerows(geo_issues)
            raise RuntimeError("Inconsistent geography fields found within DGUID; final wide table was not generated")

        quality_inconsistent = [r[0] for r in con.execute("""
            SELECT dguid FROM selected GROUP BY dguid
            HAVING COUNT(DISTINCT COALESCE(data_quality_flag, '')) > 1
        """)]
        if quality_inconsistent:
            placeholders = ",".join("?" for _ in quality_inconsistent)
            with quality_csv.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["DGUID", "CHARACTERISTIC_ID", "DATA_QUALITY_FLAG"])
                w.writerows(con.execute(
                    f"SELECT dguid, characteristic_id, data_quality_flag FROM selected WHERE dguid IN ({placeholders}) ORDER BY dguid, CAST(characteristic_id AS INTEGER)",
                    quality_inconsistent,
                ))

        indicator_ids = list(INDICATORS)
        indicator_fields = [INDICATORS[cid]["field"] for cid in indicator_ids]
        select_values = ",\n".join(
            f"MAX(CASE WHEN characteristic_id='{cid}' THEN value_text END) AS {INDICATORS[cid]['field']}"
            for cid in indicator_ids
        )
        wide_query = f"""
            SELECT MIN(census_year), dguid, MIN(alt_geo_code), MIN(geo_level), MIN(geo_name),
                   CASE WHEN COUNT(DISTINCT COALESCE(data_quality_flag,'')) = 1 THEN MIN(data_quality_flag) ELSE '' END,
                   {select_values}
            FROM selected GROUP BY dguid ORDER BY dguid
        """
        out_header = GEO_FIELDS + indicator_fields
        with output_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(out_header)
            for row in con.execute(wide_query):
                w.writerow(row)

        stats = {}
        anomalies = {}
        for cid, meta in INDICATORS.items():
            field = meta["field"]
            values = []
            anomaly_rows = []
            for dguid, value_text in con.execute("SELECT dguid, value_text FROM selected WHERE characteristic_id=?", (cid,)):
                if value_text is None:
                    continue
                value = Decimal(value_text)
                values.append(value)
                bad = (field in PERCENT_FIELDS and not (Decimal(0) <= value <= Decimal(100))) or (field in NONNEGATIVE_FIELDS and value < 0)
                if bad and len(anomaly_rows) < 20:
                    anomaly_rows.append((dguid, value_text))
            total_ct = con.execute("SELECT COUNT(DISTINCT dguid) FROM selected").fetchone()[0]
            stats[field] = {
                "non_missing": len(values), "missing": total_ct - len(values),
                "min": str(min(values)) if values else None, "max": str(max(values)) if values else None,
            }
            anomalies[field] = {
                "count": con.execute(
                    "SELECT COUNT(*) FROM selected WHERE characteristic_id=? AND value_text IS NOT NULL AND " +
                    ("(CAST(value_text AS REAL) < 0 OR CAST(value_text AS REAL) > 100)" if field in PERCENT_FIELDS else "CAST(value_text AS REAL) < 0"),
                    (cid,),
                ).fetchone()[0],
                "examples": anomaly_rows,
            }

        dguids = [r[0] for r in con.execute("SELECT DISTINCT dguid FROM selected ORDER BY dguid")]
        total_ct = len(dguids)
        rng = random.Random(20210713)
        sample_dguids = sorted(rng.sample(dguids, min(5, total_ct)))
        sample_source = defaultdict(dict)
        sample_set = set(sample_dguids)
        with zipfile.ZipFile(ZIP_PATH) as zf:
            binary, text, reader = open_reader(zf)
            try:
                header2 = next(reader); ix = col_indices(header2)
                value_ix = {cid: ix[meta["value_col"]] for cid, meta in INDICATORS.items()}
                for row in reader:
                    dguid = row[ix["DGUID"]].strip()
                    if dguid not in sample_set or row[ix["GEO_LEVEL"]] != "Census tract":
                        continue
                    cid = row[ix["CHARACTERISTIC_ID"]].strip()
                    if cid in INDICATORS:
                        sample_source[dguid][cid] = clean_numeric(row[value_ix[cid]])[0]
            finally:
                text.close()

        sample_checks = []
        all_samples_match = True
        for dguid in sample_dguids:
            db_values = dict(con.execute("SELECT characteristic_id, value_text FROM selected WHERE dguid=?", (dguid,)))
            matches = all(db_values.get(cid) == sample_source[dguid].get(cid) for cid in indicator_ids)
            all_samples_match &= matches
            sample_checks.append({"DGUID": dguid, "matched_all_10": matches})

        toronto_example = "2021S05075350001.00"
        toronto_exists = con.execute("SELECT EXISTS(SELECT 1 FROM selected WHERE dguid=?)", (toronto_example,)).fetchone()[0] == 1

        # Verify the written CSV independently and collect its values for uniqueness/range checks.
        csv_dguids = set()
        csv_rows = 0
        csv_geo_levels = set()
        with output_csv.open("r", encoding="utf-8", newline="") as f:
            dr = csv.DictReader(f)
            csv_indicator_cols = [c for c in dr.fieldnames if c in indicator_fields]
            for row in dr:
                csv_rows += 1
                csv_dguids.add(row["DGUID"])
                csv_geo_levels.add(row["GEO_LEVEL"])
        validations = {
            "output_rows": csv_rows,
            "unique_dguid_count": len(csv_dguids),
            "dguid_unique": csv_rows == len(csv_dguids),
            "indicator_column_count": len(csv_indicator_cols),
            "all_geo_level_census_tract": csv_geo_levels == {"Census tract"},
            "sample_checks": sample_checks,
            "all_samples_match": all_samples_match,
            "toronto_cma_example_dguid": toronto_example,
            "toronto_cma_example_exists": toronto_exists,
            "percent_range_anomaly_total": sum(anomalies[f]["count"] for f in PERCENT_FIELDS),
            "negative_value_anomaly_total": sum(anomalies[f]["count"] for f in NONNEGATIVE_FIELDS - PERCENT_FIELDS),
        }

        metadata = {
            "source_file": ZIP_PATH.name, "source_size_bytes": ZIP_PATH.stat().st_size,
            "member": MEMBER, "member_size_bytes": info.file_size,
            "encoding": ENCODING, "zip_integrity_ok": zip_ok, "header": header,
            "total_source_rows": total_rows, "ct_long_rows": ct_rows,
            "selected_long_rows": selected_rows, "ct_count": total_ct,
            "stats": stats, "anomalies": anomalies,
            "duplicate_dguid_characteristic_id_groups": len(duplicates),
            "quality_inconsistent_dguid_count": len(quality_inconsistent),
            "name_mismatches": [[list(k), v] for k, v in name_mismatches.items()],
            "invalid_values": [[list(k), v] for k, v in invalid_values.items()],
            "validations": validations,
        }
        (OUT_DIR / ".processing_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
        with (OUT_DIR / ".indicator_inventory_rows.json").open("w", encoding="utf-8") as f:
            json.dump({"columns": INVENTORY_COLUMNS, "rows": inventory_rows()}, f, ensure_ascii=False, indent=2)
        with (OUT_DIR / ".data_dictionary_rows.json").open("w", encoding="utf-8") as f:
            json.dump({"columns": ["字段名称", "中文含义", "数据类型", "单位", "来源字段", "缺失值规则", "备注"], "rows": dictionary_rows()}, f, ensure_ascii=False, indent=2)

        report = []
        report.append("# Canada Census Tract 10指标处理报告\n")
        report.append("## 源数据与完整性\n")
        report.append(f"- 源文件：`{ZIP_PATH.name}`")
        report.append(f"- ZIP大小：{ZIP_PATH.stat().st_size:,} bytes（{ZIP_PATH.stat().st_size/1024/1024:.2f} MiB）")
        report.append(f"- ZIP内部主CSV：`{MEMBER}`，{info.file_size:,} bytes")
        report.append(f"- ZIP完整性检查：通过（所有成员CRC可读取）")
        report.append(f"- 实际读取编码：`{ENCODING}`")
        report.append("- 原始CSV表头：\n\n```text\n" + ",".join(header) + "\n```\n")
        report.append("## 处理方法与筛选条件\n")
        report.append("使用Python标准库`zipfile + csv`直接从ZIP内流式读取CSV，未解压2.63GB主CSV，未使用Pandas整表加载。符合`GEO_LEVEL = Census tract`且`CHARACTERISTIC_ID`属于1、6、37、57、113、345、1416、1467、2024、2230的记录写入临时SQLite，再经条件聚合生成宽表。DGUID和ALT_GEO_CODE全程按字符串处理；名称仅去除首尾空格并用于核对，筛选以ID为准。空白、`...`、`..`及抑制/不适用符号写为缺失，不替换为0；百分比保留0—100尺度。")
        report.append(f"\n共扫描原始数据行{total_rows:,}条；CT层级长表行{ct_rows:,}条；入选指标长表行{selected_rows:,}条；输出CT数{total_ct:,}。\n")
        report.append("## 指标完整性与范围\n")
        report.append("| 指标字段 | 非缺失 | 缺失 | 最小值 | 最大值 | 明显异常值数 |")
        report.append("|---|---:|---:|---:|---:|---:|")
        for field in indicator_fields:
            s, a = stats[field], anomalies[field]
            report.append(f"| {field} | {s['non_missing']:,} | {s['missing']:,} | {s['min'] or ''} | {s['max'] or ''} | {a['count']:,} |")
        report.append("\n明显异常值规则：百分比不在0—100，或人口、人口密度、收入、家庭规模及其他数值为负数。没有把高但合法的密度等主观判为异常。")
        report.append("\n## 重复、质量标识与字段一致性\n")
        report.append(f"- `DGUID + CHARACTERISTIC_ID`重复组：{len(duplicates):,}")
        report.append(f"- 输出DGUID重复：{csv_rows-len(csv_dguids):,}；DGUID唯一性：{'通过' if validations['dguid_unique'] else '未通过'}")
        report.append(f"- 同一CT内质量标识不一致的DGUID：{len(quality_inconsistent):,}" + (f"（明细：`{quality_csv.name}`）" if quality_inconsistent else ""))
        report.append(f"- 指标名称与指定官方名称不一致记录：{sum(name_mismatches.values()):,}")
        report.append(f"- 未识别的非数值代码记录：{sum(invalid_values.values()):,}")
        report.append("\n## 质量验证\n")
        report.append(f"- 输出CSV记录数与唯一DGUID数一致：{'通过' if validations['dguid_unique'] else '未通过'}（{csv_rows:,}）")
        report.append(f"- 指标列恰好10列：{'通过' if len(csv_indicator_cols)==10 else '未通过'}")
        report.append(f"- 所有输出`GEO_LEVEL`均为`Census tract`：{'通过' if validations['all_geo_level_census_tract'] else '未通过'}")
        report.append(f"- 随机抽查5个CT、逐一核对10个指标与原始ZIP长表：{'通过' if all_samples_match else '未通过'}")
        for item in sample_checks:
            report.append(f"  - `{item['DGUID']}`：{'一致' if item['matched_all_10'] else '不一致'}")
        report.append(f"- 示例Toronto CMA CT DGUID `{toronto_example}`：{'存在' if toronto_exists else '不存在'}。该前缀只表示Toronto CMA，不能据此判断属于Toronto City。")
        report.append(f"- 百分比0—100范围检查：{'通过' if validations['percent_range_anomaly_total']==0 else '发现异常'}")
        report.append(f"- 非负值检查：{'通过' if validations['negative_value_anomaly_total']==0 else '发现异常'}")
        report.append("\n## 空间覆盖说明\n")
        report.append("当前输出覆盖加拿大所有Census Tract，并非Toronto City最终子集。未按`535`前缀筛选或声称记录属于Toronto City；`535`仅表示Toronto CMA。后续空间处理应使用Toronto市界派生的市内DGUID清单，以`DGUID`为首选连接字段进一步筛选；`ALT_GEO_CODE`在CT层级对应边界文件的`CTUID`。")
        (OUT_DIR / "processing_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

        print(json.dumps({"ct_count": total_ct, "stats": stats, "validations": validations, "quality_inconsistent": len(quality_inconsistent)}, indent=2), flush=True)
    finally:
        con.close()
        if DB_PATH.exists():
            DB_PATH.unlink()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        raise
