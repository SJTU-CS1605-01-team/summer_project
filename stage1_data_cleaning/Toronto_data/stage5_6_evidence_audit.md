# 阶段5—6证据复核报告（2026-07-14）

## 1. 复核依据与边界

本报告依据桌面文件`C:\Users\awaiting\Desktop\数据下载汇报要求.docx`核对阶段5、阶段6、PPT第7—10页和现场展示要求。数据复核采用CSV、GeoPackage的SQLite只读查询；阶段6最终修正使用QGIS LTR 3.44.12和`qgis_process`实际读取工程并顺序导出布局，随后检查QGZ ZIP/XML、PNG/PDF和视觉版面。未修改阶段4、5 GeoPackage、CSV或原始数据。

老师要求的核心证据为：真实指标表、两侧连接字段、连接后属性表、成功/未匹配数量与匹配率、至少一个派生指标、分级与缺失值处理，以及至少两张由QGIS布局管理器导出的正式专题地图。

## 2. 阶段5要求—证据矩阵

| 要求 | 当前证据 | 复核结果 | 说明 |
|---|---|---|---|
| 展示实际指标表、ID、年份和真实数据行 | `evidence/stage5_csv_table.png` | 部分通过 | 585条、年份、DGUID字段和多项指标可见，但DGUID值被截断；建议加宽DGUID列重截。 |
| 展示两侧连接字段 | `evidence/stage5_join_fields.png` | 通过 | 两侧均为`DGUID`，一对一，未勾选丢弃未匹配，输出为临时图层。 |
| 连接使用临时输出，不覆盖主成果 | `evidence/stage5_join_fields.png` | 通过 | 输出栏显示“创建临时图层”。 |
| 展示连接后属性表 | `evidence/stage5_joined_table.png` | 部分通过 | 585条和连接后的指标可见，但截图未同时显示DGUID与LANDAREA。 |
| 展示永久连接状态 | `evidence/stage5_join_status.png` | 通过 | `join_status=matched`、`join_matched=1`及585条可见。 |
| 展示成功、未匹配与匹配率 | `evidence/stage5_match_summary.png` | 部分通过 | 585、585、585、100和一对一可见；两个未匹配数量被QGIS识别为布尔值“假”，不适合作为最终PPT证据。真实CSV和GPKG复核值均为0。 |
| 说明字段类型、前导零和拼接规则 | `stage5_join_quality_report.md` | 通过 | 两侧DGUID均按文本处理，无空值、无重复、无需拼接。 |
| 永久输出`city_tract_indicators.gpkg` | `processed/city_tract_indicators.gpkg` | 通过 | 585个CT，一对一连接，主成果只读检查通过。 |

阶段5数据结论仍为：边界585、指标585、成功585、未匹配边界0、未匹配指标0、匹配率100.00%。阶段5数据成果合格，但最终PPT截图尚需优化两张，建议同时优化实际指标表的DGUID显示。

## 3. 阶段6要求—证据矩阵

| 要求 | 当前证据 | 复核结果 | 说明 |
|---|---|---|---|
| 展示面积派生公式 | `evidence/stage6_area_calculator.png` | 通过 | 已选择`area_km2_calc`并显示`$area / 1000000`。 |
| 展示派生人口密度公式 | `evidence/stage6_density_calculator.png` | 通过 | CASE公式完整可见。 |
| 展示派生结果字段 | `evidence/stage6_derived_fields.png` | 未通过 | 截图没有显示`area_km2_calc`、`pop_density_calc`，也未同时显示DGUID、LANDAREA和官方密度。 |
| 人口密度使用官方字段 | QGZ、正式PNG/PDF、`evidence/stage6_density_symbology.png` | 通过 | 正式图使用`population_density_km2`和5级Jenks；主图与No data过滤已保存。 |
| 人口密度布局说明正确 | QGZ、正式PNG/PDF | 通过 | 副标题已改为Statistics Canada reported population density，不再写“Derived indicator”。 |
| 低收入字段与年份正确 | 低收入符号化、布局和正式地图 | 通过 | `low_income_lim_at_pct`，收入参考年2020，单位%，5级Jenks。 |
| 缺失值处理 | 数据、QGZ和正式低收入地图 | 通过 | 低收入有效583、NULL 2，No data过滤正确并使用灰色；人口密度缺失0。 |
| 两张正式PNG/PDF | `maps/`四个非preview文件 | 通过 | 文件均存在；PNG为3507×2480、300 DPI，PDF由QGIS成功导出，两张图均通过视觉检查。 |
| 保存可复现QGIS工程 | `qgis/toronto_stage5_6.qgz` | 通过 | 相对数据路径、正式人口密度字段过滤和正确副标题均已保存；QGZ完整性检查通过。 |

## 4. 当前QGIS实际分级

队友符号化截图中，官方人口密度字段`population_density_km2`的QGIS 5级Jenks断点为：

| 范围（people per km²） | CT数 |
|---:|---:|
| 87.8–5,964.4 | 307 |
| 5,964.4–12,665.7 | 193 |
| 12,665.7–23,631.1 | 48 |
| 23,631.1–41,599.2 | 26 |
| 41,599.2–77,545.3 | 11 |
| 合计 | 585 |

以上数量由GeoPackage只读重新计算。它与先前普通Python估算的Jenks断点不同；最终汇报应使用保存后的QGIS界面结果，并保证地图、报告和PPT完全一致。

低收入比例的实际分级保持为：3.6–8.6（145）、8.6–13.6（232）、13.6–19.5（133）、19.5–27.3（60）、27.3–45.0（13），另有2个灰色No data。

## 5. 返工完成情况

1. 已将人口密度正式图层设为`population_density_km2 IS NOT NULL`，No data图层设为`population_density_km2 IS NULL`。
2. 已将人口密度副标题改为`Statistics Canada reported population density, 2021 | 5-class Natural Breaks (Jenks)`。
3. 已保存`qgis/toronto_stage5_6.qgz`并将旧Windows绝对路径改为相对路径。
4. 已由QGIS LTR 3.44.12重新导出人口密度和低收入正式PNG/PDF，并逐图检查。
5. 阶段5连接表、派生字段、数字0显示和DGUID列宽截图仍属于展示优化建议，不影响阶段6地图验收结论。

工程修复记录在`qgis/fix_stage6_project.py`；最终布局由QGIS实际加载工程后导出，未手工修改PNG。

## 6. 当前验收结论

- 阶段5数据成果：通过。
- 阶段5最终展示证据：部分通过，需重截/优化2—3张。
- 阶段6低收入地图：通过文件级和视觉检查。
- 阶段6人口密度地图：通过，使用官方字段和正确副标题。
- QGIS工程复现要求：通过，工程可由QGIS LTR 3.44.12读取并重新导出。

因此截至2026-07-14，阶段6已完成到可最终提交状态；阶段5数据成果通过，但若老师要求现场截图展示，仍建议优化2—3张截图。
