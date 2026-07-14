# Toronto官方与派生人口密度比较

## 1. 比较对象与定义

本报告只读比较`city_tract_indicators.gpkg`中的以下真实字段：

- `population_2021`：2021总人口；
- `LANDAREA`：Statistics Canada发布的陆地面积，km²；
- `area_km2_calc`：EPSG:3347下CT几何面积换算值，km²；
- `pop_density_calc`：项目派生人口密度；
- `population_density_km2`：Statistics Canada发布的人口密度。

本报告统一定义：

```text
差值 = pop_density_calc - population_density_km2
相对差异(%) = 差值 ÷ population_density_km2 × 100%
```

负值表示派生密度低于官方密度。

## 2. 公式和CRS核验

派生公式应为：

```text
pop_density_calc = population_2021 ÷ area_km2_calc
```

只读核验结果：

| 检查项 | 结果 |
|---|---:|
| CT数量 | 585 |
| GeoPackage空间参考 | EPSG:3347，NAD83 / Statistics Canada Lambert |
| 几何重新计算面积与`area_km2_calc`最大差 | 0.000000506 km² |
| `pop_density_calc`与`population_2021 / area_km2_calc`最大差 | 0.2186 人/km² |
| 官方密度与`population_2021 / LANDAREA`最大差 | 0.0499 人/km² |

通过普通Python直接解析GeoPackage几何WKB并使用平面多边形面积公式重新计算，所得面积与`area_km2_calc`一致到约`5.1×10^-7 km²`。GeoPackage元数据明确记录空间图层SRS为EPSG:3347，单位为metre，因此`area_km2_calc`确实基于投影几何面积并除以1,000,000换算为km²。

人口密度公式残差主要来自`area_km2_calc`保留6位小数、`pop_density_calc`保留4位小数；不影响公式成立。官方密度与`population_2021 / LANDAREA`最多相差0.0499人/km²，符合官方密度保留1位小数的舍入结果。

## 3. 差异统计

| 统计项 | 结果 |
|---|---:|
| 平均差（派生－官方） | -414.8642 人/km² |
| 中位差 | -282.4688 人/km² |
| 平均绝对差 | 414.8642 人/km² |
| 最大绝对差 | 3,613.8938 人/km² |
| 平均相对差 | -5.0688% |
| 中位相对差 | -4.6526% |
| 平均绝对相对差 | 5.0688% |
| 中位绝对相对差 | 4.6526% |
| 最大绝对相对差 | 16.0805% |

585个CT的派生密度都低于官方密度。对应地，585个CT的几何面积都大于`LANDAREA`。

## 4. 面积口径关系

| 面积检查 | 结果 |
|---|---:|
| 几何面积大于LANDAREA | 585个 |
| 几何面积等于LANDAREA | 0个 |
| 几何面积小于LANDAREA | 0个 |
| 几何面积/LANDAREA平均比值 | 1.05357 |
| 几何面积/LANDAREA中位比值 | 1.04880 |
| 最小比值 | 1.04714 |
| 最大比值 | 1.19163 |
| 平均面积差 | 0.05957 km² |
| 中位面积差 | 0.039535 km² |

绝对相对密度差与绝对相对面积差的Pearson相关系数为`0.99916`。结合以下两项直接校验：

1. `pop_density_calc ≈ population_2021 / area_km2_calc`；
2. `population_density_km2 ≈ population_2021 / LANDAREA`；

可以确认本数据中的密度差异主要由分母面积口径不同造成，而不是人口字段不一致或连接错误。`area_km2_calc`使用制图边界的完整几何面积，`LANDAREA`是官方陆地面积字段。

## 5. 小面积CT与差异

绝对密度差与`LANDAREA`的Pearson相关系数为`-0.33338`，说明面积较小的高密度CT往往出现更大的“人数/km²”绝对差，但关系不是决定性的。

按LANDAREA分组：

| 分组 | 平均绝对相对密度差 | 中位绝对相对密度差 |
|---|---:|---:|
| 最小面积四分位（146个） | 4.7758% | 4.6510% |
| 最大面积四分位（146个） | 5.3966% | 4.9151% |

因此不能声称“小面积CT具有更大的相对差异”。数据仅支持：若CT本身密度很高，即使面积比例差异约5%，换算为人数/km²后也会产生较大的绝对数值差。

## 6. 水域、湖岸和空间位置

差异最大的20个CT中，按要素包围盒中心相对全市中位坐标粗分：East-South 9个、West-South 4个、West-North 5个、East-North 2个；其中7个位于全市包围盒中心Y坐标的最南四分位。

这些结果不足以确认20个CT是否属于湖岸、水域或河谷边界。当前文件中没有水体图层、湖岸距离字段或官方“水域CT”标记，因此“差异由湖岸边界造成”必须标记为**待人工核验**。队友可在QGIS中叠加Toronto市界和底图，逐个查看`population_density_outliers.csv`中的DGUID。

## 7. 差异最大的20个CT

完整结果保存于：

```text
Toronto_data/population_density_outliers.csv
```

绝对差最大的记录为：

| DGUID | 官方密度 | 派生密度 | 绝对差 | 相对差 | 几何面积/LANDAREA |
|---|---:|---:|---:|---:|---:|
| `2021S05075350065.02` | 77,545.3 | 73,931.4062 | 3,613.8938 | -4.6604% | 1.04888 |

该记录的人口相同，但派生面积比官方LANDAREA大4.8884%，因此派生密度较低。

## 8. 正式专题地图字段建议

**建议正式人口密度地图使用`population_density_km2`。**

理由：

1. 它是Statistics Canada正式发布的CT人口密度；
2. 它使用官方`LANDAREA`陆地面积，与人口居住密度的统计口径更一致；
3. `area_km2_calc`包含制图几何的完整面积，所有CT均比LANDAREA大，导致派生密度系统性低约5.07%；
4. 官方字段便于复现、引用和与其他Statistics Canada产品比较。

同时必须保留`area_km2_calc`和`pop_density_calc`，并在PPT或属性表中展示公式，作为课程要求“至少计算一个派生指标”的证据。派生字段不是错误；它反映的是另一种面积口径，适合用作质量检查和口径比较。

## 9. 对当前预览地图的影响

当前`toronto_stage5_6.qgz`和`population_density.qml`结构检查显示，已生成的人口密度预览使用`pop_density_calc`，不是官方密度。因此当前PNG/PDF只能视为结构预览。

若采纳本报告建议，人口密度图层的分级字段应改为`population_density_km2`，仍采用5级Natural Breaks（Jenks）。2026-07-14队友已在QGIS符号化窗口完成该设置；截图中的QGIS实际分级及按这些断点只读复算的数量为：

| 官方密度范围（人/km²） | 要素数 |
|---|---:|
| 87.8–5,964.4 | 307 |
| 5,964.4–12,665.7 | 193 |
| 12,665.7–23,631.1 | 48 |
| 23,631.1–41,599.2 | 26 |
| 41,599.2–77,545.3 | 11 |

先前普通Python Jenks估算与QGIS实际断点存在小幅差异，最终汇报应采用保存工程中的QGIS实际分级。当前QGZ尚未保存该修改，且正式人口密度PNG仍保留派生指标副标题，因此仍需在QGIS中保存工程、修正副标题并重新导出。
