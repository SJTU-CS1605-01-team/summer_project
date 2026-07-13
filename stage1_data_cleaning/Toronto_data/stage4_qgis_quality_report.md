# Toronto数据任务阶段4 QGIS空间质量报告

## 边界数据检查摘要

| 项目 | 检查结果 |
|---|---|
| 研究对象 | Canada，Toronto City |
| tract-like单元 | 2021 Census tract（CT） |
| CT原始边界 | `boundary/lct_000b21a_e/lct_000b21a_e.shp` |
| 城市边界来源 | 2021 Census Subdivision Cartographic Boundary File |
| 城市边界原始文件 | `boundary/lcsd000b21a_e/lcsd000b21a_e.shp` |
| Toronto筛选字段 | `CSDUID = '3520005'` |
| Toronto DGUID | `2021A00053520005` |
| Toronto CSD名称/类型 | `Toronto` / `C` |
| CRS | NAD83 / Statistics Canada Lambert，EPSG:3347，metre |
| 边界年份 | 2021 |
| QGIS版本 | QGIS 3.44.12 LTR（Solothurn） |
| 阶段4永久输出 | `processed/toronto_stage4.gpkg` |
| QGIS工程 | `../qgis/toronto_stage1.qgz` |
| 检查日期 | 2026-07-13 |

边界下载页面：

https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?Year=21

许可证：

https://www.statcan.gc.ca/en/terms-conditions/open-licence

## 1. 文件加载与CRS检查

2021 Census Subdivision（CSD）和2021 Census Tract（CT）两个Shapefile均能在QGIS中正常加载、显示并打开属性表。CSD原始图层包含5,161个要素，CT原始图层包含6,247个要素。

两个图层的原始CRS均为NAD83 / Statistics Canada Lambert（EPSG:3347），坐标单位为metre。该CRS为投影坐标系，可用于后续面积和人口密度计算。本阶段未对原始坐标进行无依据的重新定义，也不存在城市边界与CT边界的CRS混用。

## 2. Toronto City边界提取

Toronto City从全国CSD边界中按属性筛选：

```qgis
"CSDUID" = '3520005'
```

筛选结果为1个要素，属性核对如下：

| 字段 | 值 |
|---|---|
| `CSDUID` | `3520005` |
| `DGUID` | `2021A00053520005` |
| `CSDNAME` | `Toronto` |
| `CSDTYPE` | `C` |
| `PRUID` | `35` |
| `LANDAREA` | 631.0983 km² |
| 几何有效性 | 有效 |

筛选后的城市边界已永久保存到`processed/toronto_stage4.gpkg`中的`toronto_city_boundary_2021`图层。

## 3. Toronto Census Tract空间筛选规则

本阶段比较了两种空间关系：

| 空间规则 | CT数量 | 判断 |
|---|---:|---|
| `intersect`（相交） | 622 | 不采用；包含37个仅接触或跨越市界、但不属于Toronto City内部的边缘CT |
| `are within`（位于内部） | 585 | 采用；与2021 Toronto CSD边界体系相匹配 |

最终使用QGIS“按位置提取（Extract by location）”，输入全国CT边界，以`toronto_city_boundary_2021`为比较图层，空间谓词设为`are within`。该操作只筛选属于Toronto City的完整CT要素，不切割原始CT几何，避免将完整CT人口指标错误分配到被切割后的局部面积。

筛选结果已永久保存到`processed/toronto_stage4.gpkg`中的`toronto_ct_2021_raw`图层。

## 4. QGIS空间质量检查结果

| 检查项目 | 结果 | 处理方式/说明 |
|---|---|---|
| 文件可打开 | 是 | CSD、CT Shapefile及阶段4 GeoPackage均可正常读取 |
| CRS完整 | 是 | 原始和输出均为EPSG:3347，坐标单位metre |
| 全国CT数量 | 6,247 | 原始2021 Census Tract边界记录数 |
| Toronto City CT数量 | 585 | 使用`are within`空间关系获得 |
| `DGUID`唯一 | 是 | 585个非空值、585个唯一值 |
| `CTUID`唯一 | 是 | 585个非空值、585个唯一值 |
| 空几何 | 0 | 无需删除或补建 |
| 无效几何 | 0 | GEOS检查通过，无需对Toronto子集执行修复几何 |
| 重复DGUID | 0 | 无需去重 |
| 重复CTUID | 0 | 无需去重 |
| 重复几何 | 0 | 无需去重 |
| 多部件要素 | 8 | 属于合法MultiPolygon，不拆分，保持一个DGUID对应一个CT |
| 目标城市筛选 | 已完成 | `CSDUID='3520005'`提取市界，CT采用`are within`筛选 |

全国原始CT边界中存在2个无效几何，分别为`CTUID 4210160.05`（Quebec）和`CTUID 9300023.02`（British Columbia），均不在Toronto City目标子集中。因此Toronto最终585个CT全部有效，不需要为了形式上“执行修复”而改写合法几何。

## 5. Toronto CT面积尺度

`LANDAREA`为Statistics Canada原始属性字段，单位为平方公里。本阶段在完成Toronto City筛选后得到以下面积统计：

| 统计项 | 结果 |
|---|---:|
| CT数量 | 585 |
| 最小陆地面积 | 0.0129 km² |
| 中位陆地面积 | 0.7469 km² |
| 平均陆地面积 | 1.0788 km² |
| 最大陆地面积 | 19.9096 km² |

这些统计仅针对Toronto City的585个CT，不是Toronto CMA或加拿大全国CT统计。后续如使用QGIS字段计算器计算几何面积，应继续使用EPSG:3347，并将平方米除以1,000,000转换为平方公里。

## 6. 永久成果与复现路径

GeoPackage：

```text
Toronto_data/processed/toronto_stage4.gpkg
├── toronto_city_boundary_2021   # 1个Toronto City CSD边界
└── toronto_ct_2021_raw          # 585个Toronto City CT
```

QGIS工程：

```text
stage1_data_cleaning/qgis/toronto_stage1.qgz
```

复现步骤：

1. 在QGIS中加载2021全国CSD与CT Shapefile，工程CRS设为EPSG:3347。
2. 使用`"CSDUID" = '3520005'`筛选Toronto City并导出到GeoPackage。
3. 运行“按位置提取”，从全国CT中选择`are within` Toronto City边界的要素。
4. 确认输出为585个CT，不使用会产生622个候选要素的`intersect`结果。
5. 使用GEOS检查几何有效性，并检查`DGUID`、`CTUID`的空值和唯一值。
6. 保存GeoPackage和QGIS工程，不修改原始Shapefile。

## 7. 汇报证据文件

本阶段的QGIS界面证据已保存在`Toronto_data/evidence/`：

| 文件 | 证据内容 |
|---|---|
| `qgis_check1.png` | 全国CSD与CT图层成功加载及图层面板 |
| `qgis_check2.png` | 全国CT图层信息：6,247个要素、EPSG:3347 |
| `qgis_check3.png` | 全国CSD图层信息：5,161个要素、EPSG:3347 |
| `qgis_check4.png` | Toronto筛选结果：`CSDUID 3520005`、`CSDNAME Toronto`、1个要素 |
| `qgis_check5.png` | `toronto_ct_2021_raw`空间提取结果及Toronto局部边界 |
| `qgis_check6.png` | 几何有效性检查输出：有效、无效和错误三个结果图层 |
| `qgis_check7.png` | `DGUID`统计：计数585、不重复585、缺失0 |
| `qgis_check8.png` | `CTUID`统计：计数585、不重复585、缺失0 |

上述截图与永久GeoPackage相互印证。`qgis_check6.png`用于证明QGIS中实际运行了“检查有效性”；585个有效、0个无效的精确数量同时由GeoPackage的GEOS检查结果确认。

## 阶段4验收总结

Toronto City官方2021 CSD边界已经提取，CSD与CT均使用EPSG:3347。通过`are within`空间关系从全国6,247个CT中获得585个Toronto City CT。目标子集无空几何、无效几何、重复ID或重复几何，8个多部件要素保持原状。阶段4空间质量检查通过，可进入阶段5的DGUID属性连接与匹配率统计。
