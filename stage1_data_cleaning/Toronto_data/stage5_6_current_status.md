# Toronto阶段5—6当前状态

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

队友按照`stage5_6_qgis_manual_checklist.md`操作：

1. 打开`qgis/toronto_stage5_6.qgz`；
2. 展示真实Toronto指标表；
3. 添加阶段4原始CT图层，以临时输出复现DGUID连接；
4. 截取两侧DGUID和连接后的属性表；
5. 展示585条匹配和100.00%匹配率；
6. 展示`area_km2_calc`公式，点击取消；
7. 展示`pop_density_calc`公式，点击取消；
8. 展示派生结果和官方密度字段；
9. 将正式人口密度图字段改为`population_density_km2`，重新做5级Jenks；
10. 检查人口密度和低收入两个分级设置；
11. 检查两个布局，确保低收入年份为2020；
12. 从布局管理器以建议300 DPI正式导出四个非预览文件；
13. 保存`toronto_stage5_6.qgz`；
14. 将所有截图保存到`Toronto_data/evidence/`。

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

阶段5的数据连接主体已经通过文件级核验；阶段6的字段、样式、布局和预览结构已经生成，但正式地图尚未由队友在QGIS布局管理器中人工检查和导出。当前可以交给队友继续人工证据与正式制图步骤，尚不能宣布阶段6最终完成。
