# Toronto数据任务阶段1—3质量报告

## 边界数据检查摘要

| 项目 | 检查结果 |
|---|---|
| 产品 | 2021 Census Tract Cartographic Boundary File |
| 发布机构 | Statistics Canada |
| 原始文件 | `boundary/lct_000b21a_e.zip` |
| ZIP完整性 | 通过 |
| Shapefile组件 | `.shp`、`.shx`、`.dbf`、`.prj`齐全，另有`.xml`元数据 |
| SHP几何数 / SHX索引数 / DBF记录数 | 6,247 / 6,247 / 6,247，一致 |
| 关键字段 | `DGUID`、`CTUID`、`CTNAME`、`LANDAREA` |
| 唯一性 | `DGUID`与`CTUID`均为6,247个唯一值，无重复 |
| CRS | NAD83 Statistics Canada Lambert，EPSG:3347，metre |
| 边界年份 | 2021 |
| 下载日期 | 2026-07-13 |
| 当前范围 | 加拿大全国Census Tract |
| 许可证 | Statistics Canada Open Licence |

边界下载页面：

https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?Year=21

许可证：

https://www.statcan.gc.ca/en/terms-conditions/open-licence

## 1. 为什么Census Tract可视为tract-like？

Census Tract是Statistics Canada建立的小型、相对稳定统计区，通常人口2,500—7,500人，推荐平均约5,000人，具有稳定编码并承载丰富的小地域统计。它与美国Census Tract在统计性质、人口规模、边界稳定性和数据用途上高度相似，因此是本项目最合适的tract-like单元。CT不是行政区。

官方定义：

https://www12.statcan.gc.ca/census-recensement/2021/ref/dict/az/definition-eng.cfm?ID=geo013

## 2. CT是否足够细？

对比较Toronto城市内部社会经济差异而言，CT足够细：它明显小于Toronto CMA和Toronto Census Subdivision，又能获得较稳定、内容丰富的官方统计。更小单元可能提高空间细节，但很多抽样型社会经济指标无法以同等稳定性和完整度获得。

## 3. 指标与边界是否为同一尺度？

是。10个指标的原始`GEO_LEVEL`全部为`Census tract`；边界也是2021 Census Tract边界。所有指标`join_method`均为`direct_join`，连接字段为`DGUID`。不存在把CMA、市级或省级数据强行下推到CT。

当前阶段没有执行实际连接，因此连接匹配率标记为：**由下一阶段完成**。

## 4. 哪些指标最可靠？

人口、人口密度、年龄、家庭规模、收入中位数及LIM-AT主要属于100% data，通常比25%抽样指标有更低的抽样不确定性。其中人口与人口密度的覆盖率最高（99.9%，各缺7个CT）。但“100% data”不表示绝对无误；随机舍入、抑制、不适用和质量标识仍需保留。

租房、住房负担、教育和失业率属于25% sample data，适合CT比较，但在小人口CT中更容易出现抽样误差、质量限制或抑制。

## 5. 哪些指标是partial或derived？

当前10项均为Statistics Canada在Census Profile的CT层级正式直接发布，不标记为`derived`，也没有在本项目中根据其他字段自行推算。百分比直接取`C10_RATE_TOTAL`，没有再计算。

若将`partial`理解为数据完整性，10项均有少量缺失；若将其理解为抽样基础，租房、住房负担、教育和失业率属于25% sample data。后续派生指标：**由下一阶段完成**。

## 6. 哪些指标缺失，为什么？

| 指标 | 缺失CT数 | 覆盖率 |
|---|---:|---:|
| population_2021 | 7 | 99.9% |
| population_density_km2 | 7 | 99.9% |
| age_65_plus_pct | 81 | 98.7% |
| average_household_size | 86 | 98.6% |
| median_total_income_2020 | 147 | 97.6% |
| low_income_lim_at_pct | 147 | 97.6% |
| renter_households_pct | 89 | 98.6% |
| shelter_cost_30pct_plus_pct | 148 | 97.6% |
| bachelor_or_higher_age25_64_pct | 89 | 98.6% |
| unemployment_rate_pct | 89 | 98.6% |

缺失主要来自官方数据抑制、不适用或质量限制。缺失值保留为空，不替换为0。当前`quality_flag`统一记为`available`，表示指标正式发布且可按DGUID直接连接，不表示每个CT都有非缺失值。

## 7. 是否存在跨年数据混用？

存在明确记录的参考年份差异，但不存在未说明的产品或空间版本混用。收入中位数和LIM-AT指标参考年份为2020；其余指标主要参考2021。全部指标均由2021 Census Profile按2021 CT发布。分析时应把“参考年份”和“产品/边界年份”分开解释。

## 8. 边界和指标年份是否一致？

一致。边界产品版本为2021，指标产品版本也为2021，二者均使用2021 Census Tract体系。2020收入参考期不改变其2021 CT空间发布版本。

## 9. 是否存在无法自动复现的下载步骤？

存在网页手动选择步骤。边界下载页需要选择Census tract、Cartographic Boundary File、Shapefile及Statistics Canada Lambert；Census Profile下载页需要选择相应地理产品和英文CSV。项目已经记录官方URL、选择路径、产品编号和原始文件名，因此下载来源可审计，但网页交互本身未写成自动下载程序。

指标下载页：

https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm?DGUIDlist=2021A000210&GENDERlist=1&HEADERlist=0&Lang=E&STATISTIClist=1%2C4

## 10. 其他人如何复现？

1. 从README记录的Statistics Canada官方页面下载`lct_000b21a_e.zip`和`98-401-X2021007_eng_CSV.zip`。
2. 保持原始ZIP不变，将指标ZIP放入`Toronto_data/indicators/`。
3. 在`Toronto_data`目录运行`python3 process_ct_indicators.py`。
4. 检查`processed/processing_report.md`中的ZIP完整性、原始表头、筛选条件、重复检查、缺失统计、范围检查和5个CT抽查。
5. 核对输出应为6,247行、DGUID唯一、恰好10个指标列，且`GEO_LEVEL`均为`Census tract`。

脚本使用`zipfile + csv`流式读取ZIP内部2.63GB CSV并用临时SQLite聚合，不使用Pandas整表加载。

## 当前阶段边界与未完成事项

当前全国CSV不是Toronto City最终子集。`535`只表示Toronto CMA，不能据此认定记录属于Toronto City。以下项目均不得从现有结果中虚构，统一标记为**由下一阶段完成**：

- Toronto City最终CT数量；
- 城市裁剪结果；
- 属性连接匹配率；
- 未匹配区域；
- 派生指标；
- 专题地图；
- AI应用最终判断。

## 阶段1—3验收总结

阶段1—3已经完成数据对象确定、加拿大全国CT边界获取和CT层级十指标收集。边界与指标均使用2021 Census Tract空间体系，全国宽表保留6,247个CT，每个DGUID一行。

`LANDAREA`为边界属性表中的陆地面积字段，单位为平方公里，可在城市空间筛选后用于计算面积尺度。当前未计算或报告Toronto City CT平均面积、中位面积、面积范围和城市CT数量；全国CT或Toronto CMA面积统计即使被计算，也只能作为背景参考。

Toronto City范围筛选、Toronto City CT面积统计、城市CT数量、边界—指标连接匹配率和专题地图均由阶段4以后完成。本阶段没有伪造上述结果。

文档、全国CT指标CSV、真实数据证据图、`indicator_inventory.xlsx`与`data_dictionary.xlsx`均已完成。由于标准`@oai/artifact-tool`运行时不可用，在用户明确授权后使用`openpyxl 3.1.5`生成工作簿；随后重新载入验证工作表、数据行列、表格、筛选、冻结窗格和百分比格式，并将所有工作表分区渲染为高分辨率PNG完成视觉检查。未发现空白工作表、严重截断或公式错误（工作簿不包含公式）。阶段1—3文件验收通过。
