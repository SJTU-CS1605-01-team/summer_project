# 阶段5—6 PPT第7—10页材料

## 第7页：实际指标表与ID连接逻辑

建议证据：

- `evidence/stage5_csv_table.png`（建议加宽DGUID后重截）；
- `evidence/stage5_join_fields.png`。

页面短文：

> Toronto指标子表包含585条2021 Census Tract记录和10项指标。边界与指标表通过完整文本型DGUID一对一连接，两侧DGUID均无空值和重复，不需要拼接省、市或CMA编码，也不存在数值转换导致的前导零丢失。

页面数字：`585 records | 10 indicators | DGUID ↔ DGUID | one-to-one`。

## 第8页：连接结果与质量

建议证据：

- 重截后的连接属性表；
- 重截后的匹配汇总；
- `evidence/stage5_join_status.png`可作为补充。

页面短文：

> Toronto边界585个CT与指标表585条记录全部匹配，成功585、未匹配边界0、未匹配指标0，匹配率为100.00%。7项社会经济指标各有2个NULL，这些记录的DGUID均已连接，属于指标值缺失，不是ID连接失败。

页面数字：`585 / 585 matched | 100.00% | unmatched 0 + 0`。

## 第9页：人口密度专题地图

最终证据应使用重新导出的`maps/toronto_population_density_2021.png`，不能使用当前副标题错误的版本。

页面短文：

> 正式地图使用Statistics Canada 2021官方人口密度字段`population_density_km2`，单位为people per km²，并采用5级Natural Breaks（Jenks）。项目同时在EPSG:3347下计算`area_km2_calc`和`pop_density_calc = population_2021 / area_km2_calc`，作为派生指标证据。官方字段与派生字段的差异主要来自LANDAREA和制图几何面积口径不同。

QGIS实际断点及数量：

- 87.8–5,964.4：307；
- 5,964.4–12,665.7：193；
- 12,665.7–23,631.1：48；
- 23,631.1–41,599.2：26；
- 41,599.2–77,545.3：11。

汇报时需补充1—2条经地图人工确认的空间分布观察，不把粗略象限统计直接说成具体社区结论。

## 第10页：低收入比例专题地图

建议证据：

- `maps/toronto_low_income_2020.png`；
- `evidence/stage6_lowincome_symbology.png`；
- `evidence/stage6_lowincome_layout.png`作为备用界面证据。

页面短文：

> 地图展示2020年LIM-AT低收入人口比例，数据由2021 Census Profile按2021 CT发布。583个CT有有效值，2个CT缺失并以灰色显示。地图采用5级Natural Breaks（Jenks），范围为3.6%—45.0%。

页面数字：`reference year 2020 | valid 583 | missing 2 | unit %`。

## 现场问答

**通过什么字段连接？** 完整文本型DGUID直接连接，两侧均无空值和重复，不需拼接编码。

**匹配率是多少？** 585个Toronto CT全部匹配，匹配率100.00%，未匹配边界和指标均为0。

**计算了什么派生指标？** EPSG:3347几何面积`area_km2_calc`和人口密度`pop_density_calc`。

**为什么正式图用官方密度？** 官方字段使用Statistics Canada的LANDAREA口径，适合正式统计展示；派生密度仍保留，证明完成了字段计算并用于口径比较。

**低收入为什么写2020？** 该收入指标由2021 Census Profile发布，但收入参考年份是2020。
