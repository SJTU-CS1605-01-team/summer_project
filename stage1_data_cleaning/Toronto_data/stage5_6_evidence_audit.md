# 阶段5—6证据复核报告（2026-07-14）

## 1. 复核依据与边界

本报告重新依据桌面文件`C:\Users\awaiting\Desktop\数据下载汇报要求.docx`核对阶段5、阶段6、PPT第7—10页和现场展示要求。复核采用现有CSV、GeoPackage的SQLite只读查询、QGZ的ZIP/XML只读检查、PNG/PDF结构检查和截图人工查看；没有启动QGIS、PyQGIS或处理算法，也没有修改GPKG、QGZ、QML、PNG、PDF及原始数据。

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
| 人口密度使用官方字段 | `evidence/stage6_density_symbology.png` | 会话中通过 | 符号化窗口显示`population_density_km2`和5级Jenks，但磁盘QGZ未保存该修改。 |
| 人口密度布局说明正确 | 布局截图、正式PNG | 未通过 | 布局截图显示尝试修改为官方说明，但正式PNG仍写“Derived indicator”。 |
| 低收入字段与年份正确 | 低收入符号化、布局和正式地图 | 通过 | `low_income_lim_at_pct`，收入参考年2020，单位%，5级Jenks。 |
| 缺失值处理 | 数据、QGZ和正式低收入地图 | 通过 | 低收入有效583、NULL 2，No data过滤正确并使用灰色；人口密度缺失0。 |
| 两张正式PNG/PDF | `maps/`四个非preview文件 | 部分通过 | 文件均存在，PNG为3507×2480、约300 DPI，PDF头尾完整；人口密度图需修正后重导出。 |
| 保存可复现QGIS工程 | `qgis/toronto_stage5_6.qgz` | 未通过 | 文件时间仍为2026-07-13；内部仍使用`pop_density_calc`及旧副标题，截图窗口标题有`*`。 |

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

## 5. 必须完成的最小返工

1. 在QGIS中将人口密度正式图层设为`population_density_km2`，No data过滤设为`population_density_km2 IS NULL`。
2. 将人口密度副标题改为`Statistics Canada reported population density, 2021 | 5-class Natural Breaks (Jenks)`。
3. 保存`qgis/toronto_stage5_6.qgz`，确认工程与布局标题不再显示`*`。
4. 从布局管理器重新导出人口密度PNG和PDF。
5. 重截连接后属性表，使DGUID、LANDAREA及连接指标同时可见。
6. 重截派生字段，使DGUID、population_2021、LANDAREA、area_km2_calc、pop_density_calc、population_density_km2同时可见。
7. 重新展示匹配汇总，使两个未匹配数量明确显示数字0而不是“假”。
8. 建议加宽实际指标表DGUID列后重截，以显示至少一条完整DGUID。

这些步骤必须在真实QGIS界面完成；不能通过修改PNG或手工编辑QGZ XML代替。完成后再进行最终验收。

## 6. 当前验收结论

- 阶段5数据成果：通过。
- 阶段5最终展示证据：部分通过，需重截/优化2—3张。
- 阶段6低收入地图：通过现有文件级和视觉检查。
- 阶段6人口密度地图：未通过，字段修改未保存且正式图副标题错误。
- QGIS工程复现要求：未通过，必须真实保存工程。

因此截至2026-07-14，阶段5、6尚未整体完成到可最终提交状态。
