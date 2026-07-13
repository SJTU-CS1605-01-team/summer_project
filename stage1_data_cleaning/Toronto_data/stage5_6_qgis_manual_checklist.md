# 阶段5—6队友QGIS人工操作与截图清单

## 使用目的

技术主体已经生成。队友不需要重新调查数据，也不要重做或覆盖主成果；任务是使用准备好的QGIS工程复现关键界面、核对地图、正式导出并保存证据。

必须打开的工程：

```text
C:\Users\awaiting\Desktop\summer_project\stage1_data_cleaning\qgis\toronto_stage5_6.qgz
```

建议使用项目现有QGIS 3.44.12 LTR。操作前确认整个`summer_project`目录结构没有移动。

## 重要安全规则

1. 演示连接必须输出为**临时图层**。
2. 不得覆盖、删除或重命名`city_tract_indicators`主图层。
3. 不得修改`toronto_stage4.gpkg`中的原始阶段4结果。
4. 字段计算器步骤只展示公式并点击“取消”，不要点击“确定”或更新字段。
5. 不要把指标NULL改为0。
6. 所有截图都要保留QGIS标题栏、图层面板，以及属性表或设置窗口。
7. 最终PNG/PDF必须从QGIS布局管理器导出，不能把预览图简单改名。

## A. 打开工程并检查图层

### A1. 打开工程

菜单：

```text
项目 → 打开…
```

选择`stage1_data_cleaning/qgis/toronto_stage5_6.qgz`。

应看到三个图层组：

- `Map 1 - Population Density`；
- `Map 2 - Low Income`；
- `Stage 5 - Join Evidence`。

如果出现数据源缺失，不要随意选择同名文件；停止操作并记录缺失图层名称。

### A2. 检查工程CRS

查看QGIS右下角，应该显示：

```text
EPSG:3347
```

如果不是3347，不要直接更改数据图层CRS，先记录问题。

## B. 第5部分：指标表与连接证据

### B1. 展示真实指标表

在图层面板展开：

```text
Stage 5 - Join Evidence
```

右键`toronto_indicators_2021`：

```text
打开属性表
```

横向滚动，使以下字段同时尽量可见：

```text
DGUID
population_2021
median_total_income_2020
low_income_lim_at_pct
unemployment_rate_pct
```

属性表应有585条记录。截图保存为：

```text
Toronto_data/evidence/stage5_csv_table.png
```

截图必须看到真实数据行、DGUID和至少两个指标，不要只截字段名。

### B2. 添加阶段4原始CT图层用于演示

准备好的阶段5工程没有把阶段4原始CT放在证据组中。菜单：

```text
图层 → 添加图层 → 添加矢量图层…
```

数据源选择：

```text
stage1_data_cleaning/Toronto_data/processed/toronto_stage4.gpkg
```

只选择图层：

```text
toronto_ct_2021_raw
```

添加后不要编辑它。

### B3. 打开临时连接工具

菜单：

```text
处理 → 工具箱
```

搜索：

```text
按字段值连接属性
Join attributes by field value
```

参数填写：

| 参数 | 选择 |
|---|---|
| 输入图层 | `toronto_ct_2021_raw` |
| 输入图层字段 | `DGUID` |
| 输入图层2 | `toronto_indicators_2021` |
| 输入图层2字段 | `DGUID` |
| 连接类型/方法 | 一对一，采用第一个匹配记录 |
| 丢弃无法连接的记录 | 不勾选 |
| 输出 | 创建临时图层 |

在点击运行前截图：

```text
Toronto_data/evidence/stage5_join_fields.png
```

截图必须看到两侧都是`DGUID`，并能看到“临时输出”。绝对不要把输出位置设为`city_tract_indicators.gpkg`。

### B4. 运行临时连接并展示结果

点击“运行”。完成后，右键新出现的临时连接图层：

```text
打开属性表
```

应有585条记录。横向滚动并显示：

```text
CTUID
DGUID
LANDAREA
population_2021
median_total_income_2020
low_income_lim_at_pct
```

截图保存为：

```text
Toronto_data/evidence/stage5_joined_table.png
```

截图后可以从图层面板移除临时图层；只移除临时结果，不删除磁盘文件。

### B5. 展示永久连接主图层

右键`city_tract_indicators`：

```text
打开属性表
```

确认：

- 总记录数585；
- 能看到`DGUID`和10项指标；
- `join_status`为`matched`；
- `join_matched`为1。

如需截图，可保存为：

```text
Toronto_data/evidence/stage5_join_status.png
```

### B6. 展示匹配率

右键`stage5_join_summary`：

```text
打开属性表
```

应只看到一条汇总记录：

```text
boundary_count = 585
indicator_count = 585
matched_count = 585
unmatched_boundary_count = 0
unmatched_indicator_count = 0
match_rate_pct = 100.00
join_field_boundary = DGUID
join_field_indicators = DGUID
join_relationship = one_to_one
```

截图保存为：

```text
Toronto_data/evidence/stage5_match_summary.png
```

这张图是PPT第8页和现场回答匹配率的核心证据。

## C. 第6部分：派生指标证据

### C1. 展示面积公式，只看不更新

打开`city_tract_indicators`属性表，点击字段计算器图标。

选择：

```text
更新已有字段
```

字段选择：

```text
area_km2_calc
```

表达式输入：

```qgis
$area / 1000000
```

截图保存为：

```text
Toronto_data/evidence/stage6_area_calculator.png
```

截图后必须点击“取消”，不要点击“确定”。字段已经计算完成，不需要再次写入。

### C2. 展示派生人口密度公式，只看不更新

再次打开字段计算器，选择“更新已有字段”：

```text
pop_density_calc
```

表达式输入：

```qgis
CASE
WHEN "population_2021" IS NULL
  OR "area_km2_calc" IS NULL
  OR "area_km2_calc" <= 0
THEN NULL
ELSE "population_2021" / "area_km2_calc"
END
```

截图保存为：

```text
Toronto_data/evidence/stage6_density_calculator.png
```

截图后点击“取消”，不得更新字段。

### C3. 展示派生结果字段

在`city_tract_indicators`属性表中同时显示：

```text
DGUID
population_2021
LANDAREA
area_km2_calc
pop_density_calc
population_density_km2
```

截图保存为：

```text
Toronto_data/evidence/stage6_derived_fields.png
```

这张图说明项目实际保留了派生面积和派生密度，并可与官方密度核对。

## D. 正式人口密度地图

### D1. 了解当前状态

工程中当前人口密度预览使用`pop_density_calc`。数据核验建议最终正式地图改用Statistics Canada官方字段：

```text
population_density_km2
```

派生字段仍保留用于C1—C3证据。

### D2. 修改人口密度分级字段

展开：

```text
Map 1 - Population Density
```

右键`Population density (people per km²)`：

```text
属性 → 符号化
```

设置：

| 设置 | 值 |
|---|---|
| 渲染方式 | 分级（Graduated） |
| 值/字段 | `population_density_km2` |
| 模式 | 自然断点（Jenks） |
| 类别数 | 5 |
| 单位 | people per km² |

点击“分类”。预期范围和数量约为：

| 范围 | 数量 |
|---:|---:|
| 87.8–5,964.4 | 307 |
| 5,964.4–13,133.8 | 195 |
| 13,133.8–24,707.7 | 49 |
| 24,707.7–41,599.2 | 23 |
| 41,599.2–77,545.3 | 11 |

QGIS若因显示精度产生最后一位小数差异，以QGIS实际分类为准，但5类数量合计应为585。

截图保存为：

```text
Toronto_data/evidence/stage6_density_symbology.png
```

点击“应用/确定”。这是队友需要真正修改的地图样式步骤，不是只看后取消。

### D3. 检查人口密度缺失值图层

在`Map 1 - Population Density`组中选择对应的`No data`图层，右键：

```text
筛选…
```

建议改为：

```qgis
"population_density_km2" IS NULL
```

官方密度缺失数应为0；仍保留灰色No data图例以说明处理规则。

### D4. 检查并更新人口密度布局

菜单：

```text
项目 → 布局管理器…
```

打开：

```text
Map_1_Population_Density
```

必须人工检查：

- 标题完整；
- 图例显示5个等级和`people per km²`；
- 比例尺、北箭头存在；
- 数据年份为2021；
- CRS为EPSG:3347；
- Statistics Canada来源完整；
- 字体、图例和来源文字没有被截断；
- Toronto地图位于页面中央。

当前副标题含“Derived indicator”。若正式地图已经改用官方字段，需要选中副标题，在右侧“项目属性/主要属性”中改为：

```text
Statistics Canada reported population density, 2021 | 5-class Natural Breaks (Jenks)
```

布局完整截图：

```text
Toronto_data/evidence/stage6_density_layout.png
```

## E. 正式低收入比例地图

### E1. 检查低收入分级

展开：

```text
Map 2 - Low Income
```

右键`Low-income prevalence (LIM-AT, %)`：

```text
属性 → 符号化
```

应看到：

```text
字段：low_income_lim_at_pct
方式：自然断点（Jenks）
类别数：5
单位：%
```

预期范围和数量：

| 范围 | 数量 |
|---:|---:|
| 3.6–8.6 | 145 |
| 8.6–13.6 | 232 |
| 13.6–19.5 | 133 |
| 19.5–27.3 | 60 |
| 27.3–45.0 | 13 |
| 缺失 | 2 |

截图保存为：

```text
Toronto_data/evidence/stage6_low_income_symbology.png
```

不要点击“重新分类”，除非当前阈值与上表不一致。

### E2. 检查灰色缺失值

同组`No data`图层应筛选：

```qgis
"low_income_lim_at_pct" IS NULL
```

应有2个要素，并使用灰色符号。不能把缺失值改为0。

### E3. 检查低收入布局

打开布局：

```text
Map_2_Low_Income
```

必须检查：

- 标题完整；
- 指标明确为LIM-AT比例；
- **指标参考年份写2020**；
- Census产品/边界年份可写2021；
- 图例单位为`%`；
- 2个缺失CT以灰色表示；
- 5级Jenks图例完整；
- 比例尺、北箭头、来源和EPSG:3347完整；
- 文字无截断、颜色可辨识。

截图保存为：

```text
Toronto_data/evidence/stage6_low_income_layout.png
```

低收入指标不得错误标注为2021。

## F. 从布局管理器正式导出

### F1. 人口密度地图

在`Map_1_Population_Density`布局中：

```text
布局 → 导出为图像…
```

保存为：

```text
stage1_data_cleaning/maps/toronto_population_density_2021.png
```

PNG建议设置为300 DPI。

然后：

```text
布局 → 导出为PDF…
```

保存为：

```text
stage1_data_cleaning/maps/toronto_population_density_2021.pdf
```

### F2. 低收入地图

在`Map_2_Low_Income`布局中同样导出：

```text
stage1_data_cleaning/maps/toronto_low_income_2020.png
stage1_data_cleaning/maps/toronto_low_income_2020.pdf
```

PNG建议300 DPI。导出文件名中的年份必须保留2020。

## G. 保存工程

完成地图字段、分级和布局修改后：

```text
项目 → 保存
```

保存到当前`toronto_stage5_6.qgz`。不要另存为覆盖`toronto_stage1.qgz`。

## H. 队友最终交付清单

### 截图

- [ ] `stage5_csv_table.png`
- [ ] `stage5_join_fields.png`
- [ ] `stage5_joined_table.png`
- [ ] `stage5_join_status.png`（推荐）
- [ ] `stage5_match_summary.png`
- [ ] `stage6_area_calculator.png`
- [ ] `stage6_density_calculator.png`
- [ ] `stage6_derived_fields.png`
- [ ] `stage6_density_symbology.png`
- [ ] `stage6_density_layout.png`
- [ ] `stage6_low_income_symbology.png`
- [ ] `stage6_low_income_layout.png`

### 正式地图

- [ ] `maps/toronto_population_density_2021.png`
- [ ] `maps/toronto_population_density_2021.pdf`
- [ ] `maps/toronto_low_income_2020.png`
- [ ] `maps/toronto_low_income_2020.pdf`

### 完成后告诉Codex

队友完成后不要自行删除预览文件。通知Codex进行最终验收，重点核对正式人口密度字段、Jenks阈值、低收入年份、缺失值灰色显示、截图完整性和布局导出元数据。
