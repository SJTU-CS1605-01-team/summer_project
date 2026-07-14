# Toronto阶段5—6当前状态

> 2026-07-14最终更新：阶段6 QGIS工程和两张正式专题地图已修正并通过文件与视觉验收；阶段5数据成果通过，现有展示截图仍有小幅优化建议。详细证据矩阵见`stage5_6_evidence_audit.md`。

## 2026-07-14最新结论

- 阶段5数据主体仍通过：585个边界与585条指标一对一匹配，成功585、未匹配0、匹配率100.00%。
- 阶段5临时连接、连接状态和公式截图已经补充；连接后属性表未同时显示DGUID与LANDAREA，派生结果截图未显示两个派生字段，匹配汇总把数字0显示为“假”，仍需重截。
- 低收入正式PNG/PDF已顺序重导出，字段、2020参考年份、5级Jenks和2个灰色No data均与数据一致。
- 人口密度正式图已使用官方`population_density_km2`，QGIS实际5级数量为307、193、48、26、11；副标题已改为官方统计口径。
- `qgis/toronto_stage5_6.qgz`已保存相对数据路径、正式人口密度过滤条件和正确副标题，可由QGIS LTR 3.44.12重新导出。
- 两张正式PNG均为3507×2480（300 DPI），标题、图例、比例尺、北箭头、来源、年份和CRS说明完整。

当前状态应表述为：**阶段5数据成果通过，但展示截图仍有小幅优化建议；阶段6工程和两张正式专题地图通过。**

## 检查边界

本轮实际使用QGIS LTR 3.44.12和`qgis_process`读取工程并导出布局。通过`qgis/fix_stage6_project.py`将旧Windows绝对路径改为相对路径，修正人口密度主图和No data过滤条件及副标题；未重建或改写阶段4、5 GeoPackage和原始数据。

指定的`stage1_data_cleaning/docs/数据下载汇报要求(5).docx`在工作区中不存在。本轮使用最初上传的`C:\Users\awaiting\Desktop\数据下载汇报要求.docx`核对阶段5、6、PPT第7—10页和现场证据要求。若缺失文件是不同版本，需要人工补核。

## 1. 已完成并经过文件检查

### 阶段5数据成果

- `processed/toronto_indicators_2021.csv`：585条记录，DGUID无空值、无重复；
- `processed/city_tract_indicators.gpkg`：只读SQLite检查可用；
- `city_tract_indicators`：585个CT、585个唯一DGUID、EPSG:3347；
- `toronto_city_boundary_2021`：1个Toronto市界；
- DGUID ↔ DGUID为文本型一对一连接；
- 成功匹配585、未匹配边界0、未匹配指标0、匹配率100.00%；
- `join_status='matched'`且`join_matched=1`共585条；
- 10条确定性随机抽查、100个指标值均与CSV一致；
- 十项指标覆盖率已重新计算并记录；
- 指标字段NULL已与ID连接失败明确区分。

正式报告：

- `stage5_join_quality_report.md`。

### 派生密度核验

- `area_km2_calc`由EPSG:3347几何面积换算；
- Python重新解析几何后，与字段最大差约0.000000506 km²；
- `pop_density_calc = population_2021 / area_km2_calc`公式成立；
- 官方密度使用`population_2021 / LANDAREA`，舍入误差不超过0.0499人/km²；
- 平均密度差、相对差、面积关系及20个离群点已生成；
- 正式人口密度地图建议使用官方`population_density_km2`，派生字段保留为课程证据。

正式文件：

- `population_density_comparison.md`；
- `population_density_outliers.csv`。

### 阶段6结构、数据和正式地图

- QGZ ZIP结构完整；
- 工程中存在两个布局；
- QML中存在人口密度5级分级、低收入5级分级和灰色No data样式；
- 正式PNG为3507×2480（300 DPI）且签名有效；
- 正式PDF由QGIS成功导出；
- 分级阈值、每级数量、缺失数量和年份已重新核对；
- 低收入指标年份已确认为2020，边界/Census产品年份为2021。

正式说明：

- `stage6_map_report.md`；
- `stage5_6_qgis_manual_checklist.md`。

## 2. 阶段6最终视觉核验

以下文件已完成逐张视觉验收：

- `qgis/toronto_stage5_6.qgz`；
- `qgis/styles/*.qml`；
- `maps/toronto_population_density_2021.png/.pdf`；
- `maps/toronto_low_income_2020.png/.pdf`。

检查结果：

- 字体、标题和来源完整，无截断；
- 图例顺序、单位和颜色正确；
- 低收入图保留灰色No data类别；
- 比例尺、北箭头和地图范围清晰；
- 布局为A4横向、300 DPI，适合PPT和打印；
- 正式人口密度图已从派生字段切换为官方字段。

历史`_preview`人口密度图仍使用`pop_density_calc`，仅作为派生指标过程证据；最终正式图使用官方`population_density_km2`，两者不会混用。

## 3. 仍建议优化的阶段5展示证据

阶段6最小返工项1—4已经完成。剩余建议只涉及阶段5/派生过程截图：

1. 重截连接后属性表，使DGUID、LANDAREA及连接指标同时可见；
2. 重截派生结果，使DGUID、人口、两种面积/密度字段同时可见；
3. 重新展示匹配汇总，使未匹配边界和未匹配指标明确显示数字0；
4. 建议加宽指标表中的DGUID列后重截。

正式地图文件必须为：

```text
maps/toronto_population_density_2021.png
maps/toronto_population_density_2021.pdf
maps/toronto_low_income_2020.png
maps/toronto_low_income_2020.pdf
```

## 4. 阶段6验收记录

本轮已经完成：

1. 只读检查最终QGZ、PNG和PDF是否存在且可读取；
2. 核对正式人口密度图使用`population_density_km2`；
3. 核对人口密度5级Jenks阈值和数量；
4. 核对低收入图仍使用`low_income_lim_at_pct`且年份为2020；
5. 核对2个低收入缺失CT是否以灰色处理；
6. 检查两张正式地图的标题、图例、比例尺、北箭头、来源、CRS和版面；
7. 保留阶段5截图改进项，不将其误报为阶段6地图缺陷；
8. 更新本状态报告、阶段6报告和证据矩阵。

## 当前结论

阶段5的数据连接主体通过，界面证据仍建议小幅优化；阶段6低收入图、人口密度图和QGIS工程均通过。两张正式地图可直接用于提交和答辩，历史`_preview`文件不应替代正式版本。
