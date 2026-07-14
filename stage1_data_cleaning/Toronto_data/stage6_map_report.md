# Toronto数据任务阶段6专题地图说明

## 最终处理与检查范围

2026-07-14使用QGIS LTR 3.44.12和`qgis_process`实际读取工程、修正图层过滤与布局文字，并顺序导出正式地图。检查对象包括：

- `processed/city_tract_indicators.gpkg`；
- `processed/stage5_6_build_summary.json`；
- `../qgis/toronto_stage5_6.qgz`内部XML；
- `../qgis/styles/`中的5个QML样式；
- `../maps/`中的两张正式PNG和两张正式PDF。

QGZ为有效ZIP，内部包含`Map_1_Population_Density`和`Map_2_Low_Income`两个布局。工程中的Windows绝对路径已改为相对路径；人口密度正式图层过滤为`population_density_km2 IS NOT NULL`，No data过滤为`population_density_km2 IS NULL`。两张PNG均为3507×2480（300 DPI）且文件签名有效，两张PDF可由QGIS正常导出和读取。

两张PNG已逐张按原始分辨率检查：CT填色、标题、副标题、图例、单位、比例尺、北箭头、来源、年份、CRS和底部说明均完整可见。并行导出曾导致低收入PNG透明背景异常，最终文件采用顺序导出版本，未保留异常图。

## 地图1：Toronto人口密度

### 正式地图设置

| 项目 | 当前结构检查结果 |
|---|---|
| 地图主题 | Toronto人口密度 |
| 当前指标字段 | `population_density_km2` |
| 是否派生指标 | 否，Statistics Canada直接发布；`pop_density_calc`另作派生指标证据 |
| 指标年份 | 2021 |
| 单位 | 人/km²（people per km²） |
| 派生公式 | 工程另保留`population_2021 / area_km2_calc` |
| 面积公式 | 工程另保留EPSG:3347几何面积 / 1,000,000 |
| 分级方法 | Natural Breaks（Jenks） |
| 分级数量 | 5级 |
| 缺失数量 | 0 |
| 缺失显示 | 工程中有独立`No data`图层，过滤`population_density_km2 IS NULL`并使用灰色单一符号 |
| CRS | NAD83 / Statistics Canada Lambert，EPSG:3347 |
| 边界年份 | 2021 |
| 数据来源 | Statistics Canada, 2021 Census of Population；2021 Census Tract Cartographic Boundary File |
| 图例单位 | people per km² / 人/km² |

正式布局使用`population_density_km2`的5级`graduatedSymbol`。

### 正式人口密度分级与数量

| 等级 | 范围（人/km²） | 要素数 |
|---:|---:|---:|
| 1 | 87.8–5,964.4 | 307 |
| 2 | 5,964.4–12,665.7 | 193 |
| 3 | 12,665.7–23,631.1 | 48 |
| 4 | 23,631.1–41,599.2 | 26 |
| 5 | 41,599.2–77,545.3 | 11 |
| 缺失 | 灰色 | 0 |

共585个CT，分级计数合计585。

### 基于实际数值和位置的观察初稿

以下位置仅按CT要素包围盒中心相对于全市中位X/Y坐标分成四个象限，不等同于正式社区、行政区或人工地图判读。

1. East-South象限的派生密度平均值约14,065.98人/km²，高于East-North的5,655.31、West-North的8,064.49和West-South的6,962.97；最高密度等级12个CT中有7个位于East-South。
2. 最高派生密度为73,931.4062人/km²，对应`DGUID 2021S05075350065.02`，其包围盒中心位于East-South象限。
3. 前两个较低密度等级共有500个CT，占585个CT的85.47%；最高两个等级共有37个CT，说明极高密度CT数量相对较少。

这些观察需要队友在QGIS中结合实际地图位置、道路和城市地理进行**人工检查**，不能仅凭象限粗分命名具体社区或解释城市机制。

### 正式地图字段与派生字段说明

人口密度比较报告显示，`population_density_km2`使用官方`LANDAREA`，而当前派生字段使用较大的制图几何面积，导致585个CT的派生密度系统性低于官方密度。正式专题地图建议改用：

```text
population_density_km2
```

同时保留`pop_density_calc`作为课程要求的派生指标证据。2026-07-14已将正式图切换并保存为官方字段，副标题改为`Statistics Canada reported population density, 2021 | 5-class Natural Breaks (Jenks)`，随后重新导出PNG/PDF。QGIS实际5级分级为：87.8–5,964.4（307）、5,964.4–12,665.7（193）、12,665.7–23,631.1（48）、23,631.1–41,599.2（26）、41,599.2–77,545.3（11）。

## 地图2：Toronto低收入人口比例

### 正式地图设置

| 项目 | 当前结构检查结果 |
|---|---|
| 地图主题 | Toronto低收入人口比例 |
| 指标字段 | `low_income_lim_at_pct` |
| 是否派生指标 | 否，Statistics Canada Census Profile直接发布 |
| 指标参考年份 | **2020** |
| Census产品/边界年份 | 2021 |
| 单位 | % |
| 分级方法 | Natural Breaks（Jenks） |
| 分级数量 | 5级 |
| 缺失数量 | 2 |
| 缺失DGUID | `2021S05075350006.00`、`2021S05075350205.00` |
| 缺失显示 | 工程中有独立`No data`图层，过滤`low_income_lim_at_pct IS NULL`并使用灰色单一符号 |
| CRS | NAD83 / Statistics Canada Lambert，EPSG:3347 |
| 数据来源 | Statistics Canada, 2021 Census Profile；2021 Census Tract Cartographic Boundary File |
| 图例单位 | % |

低收入指标必须标注为收入参考年份2020，不能仅因为它来自2021 Census Profile就错误写成“2021低收入率”。

### 低收入比例分级与数量

| 等级 | 范围（%） | 要素数 |
|---:|---:|---:|
| 1 | 3.6–8.6 | 145 |
| 2 | 8.6–13.6 | 232 |
| 3 | 13.6–19.5 | 133 |
| 4 | 19.5–27.3 | 60 |
| 5 | 27.3–45.0 | 13 |
| 缺失 | 灰色 | 2 |

有效值583个、缺失2个，合计585个CT。

### 基于实际数值和位置的观察初稿

1. 四象限粗分中，East-South的低收入比例平均值最高，为14.36%；West-South最低，为11.04%。East-North和West-North分别为13.44%和13.62%。
2. 最高等级27.3%–45.0%共有13个CT，其中East-South 6个、East-North 5个、West-North 2个，West-South在该等级中为0个。
3. 全市最大值为45.0%，对应`DGUID 2021S05075350376.06`；其次为39.0%，对应`2021S05075350033.00`。这些高值CT的具体社区名称和城市背景必须在QGIS或可靠底图中**人工核验**。

## 布局和视觉检查结果

QGZ内部布局包含标题、指标/年份副标题、图例、比例尺、北箭头、数据来源、缺失值说明和EPSG:3347说明。最终PNG逐项检查结果：

- 标题、图例和来源文字：完整，无截断；
- 字体：QGIS导出正常；
- 图例符号、顺序和单位：与分级和字段一致；
- 缺失值：低收入图保留灰色No data类别；
- Toronto市界、比例尺和北箭头：清晰且位于版面内；
- 色带：人口密度为蓝色顺序色带，低收入为橙色顺序色带；
- 正式PNG/PDF：300 DPI顺序导出。

正式文件为`toronto_population_density_2021.png/.pdf`和`toronto_low_income_2020.png/.pdf`；`_preview`文件仅为历史预览，不作为最终地图。

## PPT第9页文字初稿

> 地图1展示Toronto 2021 Census Tract人口密度，正式地图建议使用Statistics Canada发布的`population_density_km2`并采用5级Natural Breaks（Jenks）。项目同时在EPSG:3347下计算`population_2021 / area_km2_calc`作为派生指标证据。官方密度使用LANDAREA，派生密度使用制图几何面积，两者口径差异已单独检查。

## PPT第10页文字初稿

> 地图2展示2020年LIM-AT低收入人口比例，数据由2021 Census Profile按2021 CT发布。583个CT有有效值，2个CT缺失并以灰色表示。地图采用5级Natural Breaks（Jenks），指标范围为3.6%–45.0%，年份必须标注为2020。

## 阶段6当前结论

2026-07-14最终复核显示，两张正式PNG/PDF均已由QGIS LTR 3.44.12顺序导出并通过视觉检查。人口密度图使用官方`population_density_km2`，585个CT全部进入5级Jenks；低收入图使用`low_income_lim_at_pct`，583个有效值和2个灰色No data与数据一致。QGZ已保存相对路径、正式字段过滤和正确副标题，ZIP完整性检查通过。**阶段6专题地图与可复现工程通过验收。**
