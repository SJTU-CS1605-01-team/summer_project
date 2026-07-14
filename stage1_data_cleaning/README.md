# Toronto 2021 Census Tract 数据项目

本目录是团队数据阶段的统一入口。阶段1—3负责确定研究单元、整理官方边界和收集CT级指标；阶段4—6负责Toronto City空间筛选、属性连接和专题地图。

> `Toronto_data/processed/canada_ct_10_indicators_2021.csv`是加拿大所有Census Tract的阶段3结果，不是Toronto City子集。Toronto CMA代码前缀`535`不能代替Toronto City市界。阶段4使用Toronto City官方CSD边界完成了空间筛选。

## 当前阶段状态

| 阶段 | 内容 | 当前状态 | 主要证据 |
|---|---|---|---|
| 1 | 确定tract-like单元 | 已完成 | `Toronto_data/CT_definition/tract_like_selection.md` |
| 2 | 获取并核验2021 CT边界 | 已完成 | `Toronto_data/boundary/`、`Toronto_data/quality_report.md` |
| 3 | 收集10项CT级指标 | 已完成 | `Toronto_data/indicator_inventory.xlsx`、`Toronto_data/processed/canada_ct_10_indicators_2021.csv` |
| 4 | Toronto City筛选与几何检查 | 已完成 | `Toronto_data/stage4_qgis_quality_report.md`、`Toronto_data/processed/toronto_stage4.gpkg` |
| 5 | DGUID连接与匹配率 | 数据成果通过；展示截图仍有小幅返工建议 | `Toronto_data/stage5_join_quality_report.md` |
| 6 | 派生指标与专题地图 | 文件已生成，但独立视觉检查未通过；两张正式图均需返工 | `Toronto_data/stage6_map_report.md`、`stage5_6_current_status.md`、`maps/` |

### 对队友阶段4—6成果的独立检查（2026-07-14）

- 阶段4通过数据检查：`toronto_stage4.gpkg`含1个Toronto City边界和585个Toronto CT。
- 阶段5通过数据检查：指标CSV为585条唯一DGUID；连接GeoPackage为585条，`join_status='matched'`和`join_matched=1`均为585，匹配率100.00%。现有报告指出部分QGIS展示截图仍需重截。
- 阶段6的PNG/PDF和QGZ文件可以读取，但**不能作为最终验收地图直接使用**：
  - `toronto_population_density_2021.png`只显示城市轮廓，没有显示585个CT的人口密度分级填色，副标题仍写`Derived indicator`；
  - `toronto_low_income_2020.png`有CT分级填色，但标题、图例标题、单位/分级说明、来源、比例尺和底部文字存在明显截断；
  - `toronto_stage5_6.qgz`内部仍包含`pop_density_calc`配置，尚未完整保存正式人口密度字段修改。

因此当前准确表述是：**阶段4完成；阶段5数据完成、展示证据待小修；阶段6数据与草图已生成，但两张正式地图均未通过最终视觉验收。**

## 阶段1—3答辩问题整理

### 1. 该国最合适的tract-like单元是什么？为什么不用更粗行政区？

Canada最合适的tract-like单元是Statistics Canada的2021 **Census tract（CT）**。CT是小型、相对稳定的统计地理单元，通常人口为2,500—7,500人，推荐平均约5,000人，并直接承载人口、收入、住房、教育和就业指标，适合比较Toronto内部社会经济差异。

不使用更粗单元的原因：

- Census Metropolitan Area范围过大；Toronto CMA包含Toronto City及周边城市。
- Census Subdivision大致对应城市或市镇，只能表达Toronto整体，不能展示市内差异。
- Census Division更粗，不适合作为城市内部分析基本单元。

证据：`Toronto_data/CT_definition/tract_like_selection.md`、`Toronto_data/CT_definition/definition_page.png`。

### 2. 该单元是统计区、普查区还是行政区？是否全国统一覆盖？

CT是Statistics Canada划定的**普查统计区/统计地理单元**，不是行政区。它采用全国统一定义和编码体系，但不连续覆盖加拿大全部国土；CT只设置在Census Metropolitan Areas及符合条件的Census Agglomerations中。Toronto属于有CT覆盖的CMA。

“全国统一定义”不等于“全国所有地区都有CT”。阶段3的Canada-wide CT表包含全国所有已设置的6,247个CT。

证据：`Toronto_data/CT_definition/tract_like_selection.md`、`Toronto_data/processed/processing_report.md`。

### 3. Shapefile的年份、CRS和唯一编码是什么？

| 项目 | 答案 |
|---|---|
| 产品 | 2021 Census Tract Cartographic Boundary File |
| 发布机构 | Statistics Canada |
| 年份 | 2021 |
| 格式 | Shapefile |
| CRS | NAD83 / Statistics Canada Lambert |
| EPSG | 3347 |
| 坐标单位 | metre |
| 首选唯一编码 | `DGUID` |
| 备用唯一编码 | `CTUID` |
| 名称字段 | `CTNAME` |
| 陆地面积字段 | `LANDAREA`，单位km² |

全国边界包含6,247个要素，Shapefile的`.shp/.shx/.dbf/.prj`齐全，DGUID和CTUID均无重复。阶段4随后从该全国边界筛选出585个Toronto City CT。

证据：`Toronto_data/boundary/url.txt`、`Toronto_data/boundary/boundary_download_page.png`、`Toronto_data/quality_report.md`。

### 4. 经济社会指标是否发布在同一空间层级？

是。所选10项指标的原始`GEO_LEVEL`均严格等于`Census tract`，边界也是2021 Census Tract边界。没有把CMA、市级或省级数据拆分或下推到CT。

阶段3宽表包含6个地理/质量字段和10个指标字段，共6,247行，每个DGUID一行。收入中位数和LIM-AT参考年份为2020，但由2021 Census Profile按2021 CT体系发布，不构成空间年份错配。

证据：`Toronto_data/indicator_inventory.xlsx`、`data_dictionary.xlsx`、`processed/processing_report.md`。

### 5. 哪些指标可直接连接？哪些只能标记为partial、coarser_level或missing？

本项目选择的10项指标全部是Statistics Canada正式发布的CT级指标，均标记为`available`，连接方式均为`direct_join`，不存在`coarser_level`或`disaggregate`指标，也没有把任何指标整体标记为`missing`。

`available`不表示每个CT的每个值都非空。官方抑制、不适用或质量限制造成的空值保留为空，不能替换为0。100% data与25% sample data的抽样基础不同，后者在小人口CT中应更谨慎解释。

证据：`Toronto_data/indicator_inventory.xlsx`中的`indicator_inventory`和`quality_summary`工作表。

### 6. Shapefile与指标表通过什么字段连接？是否需要清洗前导零或拼接编码？

首选连接为完整文本型`DGUID ↔ DGUID`。不需要拼接省、市或CMA代码，也不能把DGUID转换为数值。阶段3的`ALT_GEO_CODE`在CT层级对应边界`CTUID`，可作为辅助核对字段；两者同样应按文本保存。

阶段1—3只准备连接字段、不执行实际连接。阶段5随后验证Toronto边界与指标表的585个DGUID完全一致，实际匹配率为100.00%。

证据：`Toronto_data/data_dictionary.xlsx`、`Toronto_data/stage5_join_quality_report.md`。

## 阶段1—3核心成果

```text
stage1_data_cleaning/
├── README.md
├── docs/
│   ├── indicator_inventory.xlsx
│   └── data_dictionary.xlsx
└── Toronto_data/
    ├── README.md
    ├── quality_report.md
    ├── STAGE1_3_RESPONSIBILITY_ANSWERS.txt
    ├── CT_definition/
    ├── boundary/
    ├── indicators/
    ├── evidence/
    ├── processed/
    │   ├── canada_ct_10_indicators_2021.csv
    │   └── processing_report.md
    ├── indicator_inventory.xlsx
    ├── data_dictionary.xlsx
    └── process_ct_indicators.py
```

全国CT宽表验证结果：6,247行、6,247个唯一DGUID、恰好10个指标列，全部记录为`Census tract`。空白、`...`、抑制和不适用值保留为缺失；百分比保持0—100表示方式。

## 与阶段4—6的衔接

- 阶段4使用Toronto City的2021 CSD ID `3520005`和`are within`规则获得585个市内CT。
- 阶段5以文本型DGUID完成585对585的一对一连接，匹配率100.00%。
- 阶段6计算`area_km2_calc`和`pop_density_calc`；正式人口密度图建议使用官方`population_density_km2`字段。
- 阶段4和阶段5的数据检查结果已与实际GeoPackage/CSV一致。
- 阶段6须重新在QGIS布局管理器中检查图层可见性和文字框尺寸，再导出两张正式PNG/PDF；当前文件不可直接用于最终答辩。

更完整的阶段1—3问题答案及证据路径见`Toronto_data/STAGE1_3_RESPONSIBILITY_ANSWERS.txt`。
