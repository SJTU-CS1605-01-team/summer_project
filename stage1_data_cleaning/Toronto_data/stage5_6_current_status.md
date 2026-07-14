# Toronto阶段5—6当前状态

> 2026-07-14复核更新：队友已新增阶段5、6截图和四个非`preview`地图文件，但最终验收尚未通过。详细证据矩阵见`stage5_6_evidence_audit.md`。

## 2026-07-14最新结论

- 阶段5数据主体仍通过：585个边界与585条指标一对一匹配，成功585、未匹配0、匹配率100.00%。
- 阶段5临时连接、连接状态和公式截图已经补充；连接后属性表未同时显示DGUID与LANDAREA，派生结果截图未显示两个派生字段，匹配汇总把数字0显示为“假”，仍需重截。
- 低收入正式PNG/PDF已经生成，字段、2020参考年份、5级Jenks和2个灰色No data均与数据一致。
- 人口密度符号化截图已经切换到官方`population_density_km2`，QGIS实际5级数量为307、193、48、26、11。
- 人口密度正式PNG仍保留“Derived indicator”副标题，与官方字段图例矛盾，必须修正后重新从布局管理器导出。
- `qgis/toronto_stage5_6.qgz`没有保存队友修改；QGZ内部仍使用`pop_density_calc`及旧副标题，未达到工程复现要求。

当前状态应表述为：**阶段5数据成果通过，但展示证据需小幅返工；阶段6低收入图通过，人口密度图和QGIS工程未通过。**

## 检查边界

本轮没有运行PyQGIS、`python-qgis-ltr`、`qgis_process`、`build_stage5_6.py`，也没有启动QGIS。现有GPKG、QGZ、QML、PNG和PDF均未修改。本轮只使用普通Python的CSV、JSON、SQLite和ZIP读取能力进行只读核验，并新增Markdown/CSV报告。

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

### 阶段6结构和数据

- QGZ ZIP结构完整；
- 工程中存在两个布局；
- QML中存在人口密度5级分级、低收入5级分级和灰色No data样式；
- 预览PNG为3507×2480且签名有效；
- 预览PDF具有有效文件头和EOF；
- 分级阈值、每级数量、缺失数量和年份已重新核对；
- 低收入指标年份已确认为2020，边界/Census产品年份为2021。

正式说明：

- `stage6_map_report.md`；
- `stage5_6_qgis_manual_checklist.md`。

## 2. 已生成但仍需QGIS人工视觉核验

以下文件结构完整，但不能视为已经完成视觉验收：

- `qgis/toronto_stage5_6.qgz`；
- `qgis/styles/*.qml`；
- `maps/toronto_population_density_2021_preview.png/.pdf`；
- `maps/toronto_low_income_2020_preview.png/.pdf`。

需要人工确认：

- 字体、标题和来源是否截断；
- 图例顺序、单位和颜色是否正确；
- 灰色缺失值是否可见；
- 比例尺、北箭头和地图范围是否合适；
- 布局是否适合PPT和打印；
- 正式人口密度图是否已从派生字段切换为官方字段。

当前人口密度预览使用`pop_density_calc`。它是有效派生指标，但基于完整几何面积，系统性低于以LANDAREA计算的官方密度。预览文件不能直接冒充最终正式人口密度地图。

## 3. 队友仍需完成

队友已完成大部分原清单，目前只需针对验收缺口返工：

1. 在QGIS中确认人口密度正式图层使用`population_density_km2`，No data过滤同步使用该字段；
2. 将人口密度副标题改为官方密度说明；
3. 保存`qgis/toronto_stage5_6.qgz`，确认窗口标题不再显示`*`；
4. 从布局管理器重新导出人口密度PNG和PDF；
5. 重截连接后属性表，使DGUID、LANDAREA及连接指标同时可见；
6. 重截派生结果，使DGUID、人口、两种面积/密度字段同时可见；
7. 重新展示匹配汇总，使未匹配边界和未匹配指标明确显示数字0；
8. 建议加宽指标表中的DGUID列后重截。

正式地图文件必须为：

```text
maps/toronto_population_density_2021.png
maps/toronto_population_density_2021.pdf
maps/toronto_low_income_2020.png
maps/toronto_low_income_2020.pdf
```

## 4. 队友完成后Codex最终需要验收

队友通知完成后，Codex需要：

1. 只读检查最终QGZ、PNG和PDF是否存在且可读取；
2. 核对正式人口密度图使用`population_density_km2`；
3. 核对人口密度5级Jenks阈值和数量；
4. 核对低收入图仍使用`low_income_lim_at_pct`且年份为2020；
5. 核对2个低收入缺失CT是否以灰色处理；
6. 检查两张正式地图的标题、图例、比例尺、北箭头、来源、CRS和版面；
7. 检查阶段5、6截图是否覆盖老师要求；
8. 检查PPT第7—10页使用的数字与报告一致；
9. 如发现问题，只针对具体问题修正，不重新运行完整阶段5、6流程；
10. 完成最终验收结论和PPT用文字。

## 当前结论

阶段5的数据连接主体通过，界面证据需小幅返工；低收入正式地图通过；人口密度正式图与QGIS工程未通过。当前不能宣布阶段5、6整体最终完成，最小返工清单见`stage5_6_evidence_audit.md`。
