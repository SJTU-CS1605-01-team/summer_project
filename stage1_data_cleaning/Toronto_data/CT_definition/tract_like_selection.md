# Toronto研究的tract-like空间单元选择

- country：Canada
- city：Toronto
- recommended_tract_like_unit：Census tract
- recommended_year：2021
- similarity_to_us_census_tract：High

## 结论

本项目推荐使用加拿大统计局（Statistics Canada）发布的 **2021 Census tract（CT）** 作为Toronto城市内部社会经济分析的tract-like空间单元。

| 项目 | 选择结果 |
|---|---|
| 官方名称 | Census tract |
| 缩写 | CT |
| 发布机构 | Statistics Canada |
| 推荐年份 | 2021 |
| 单元性质 | 普查统计区/统计区，不是行政区 |
| 与美国Census Tract相似度 | 高 |

## 选择理由

Statistics Canada将CT定义为小型、相对稳定的地理区域。2021年规则下，CT人口通常为2,500—7,500人，推荐平均人口约5,000人；边界通常沿永久且容易识别的地物设置，并尽量保持社会经济特征相对同质。CT拥有稳定的唯一标识符：人口普查产品和边界文件均提供`DGUID`，边界文件还提供`CTUID`。2021 Census Profile直接在CT层级发布人口、家庭、收入、住房、教育和就业等指标，因此CT适合比较城市内部的社会经济差异。

官方定义：

https://www12.statcan.gc.ca/census-recensement/2021/ref/dict/az/definition-eng.cfm?ID=geo013

## 覆盖范围

CT不覆盖加拿大全部国土。2021 CT位于全部Census Metropolitan Areas（CMA），以及前次普查核心人口达到50,000人的Census Agglomerations（CA）；一旦CMA或CA进入CT计划，即使核心人口后来降至阈值以下，其CT通常仍会保留。Toronto属于有CT覆盖的Toronto CMA。

这一区分对本项目很重要：Toronto CMA包含Toronto City之外的周边城市，不能把Toronto CMA或代码前缀`535`直接当作Toronto City。Toronto City的官方2021 Census Subdivision（CSD）ID为`3520005`，但本阶段不据此假定CMA内CT全部属于该CSD。本阶段保留全国全部6,247个CT，下一阶段再使用Toronto City市界获得市内DGUID清单。

## 为什么不用更粗空间单元

- **Census Metropolitan Area（CMA）**：范围过大，Toronto CMA包含Toronto City及周边多个城市，不能呈现城市内部差异。
- **Census Subdivision（CSD）**：大致对应城市、市镇或其他市级实体，可用于识别Toronto City整体，但不能展示其内部差异。
- **Census tract（CT）**：粒度位于CMA/CA与更小普查单元之间，直接承载丰富的社会经济指标，更适合作为城市内部分析的基本单元。

## 面积尺度与LANDAREA字段

2021 Census Tract边界属性表中的`LANDAREA`表示每个CT的陆地面积，单位为平方公里（km²）。该字段可以在完成目标城市空间筛选后，用于计算Toronto City范围内CT的平均面积、中位面积、最小—最大面积范围等面积尺度指标。

当前边界仍覆盖加拿大全国Census Tract，尚未完成Toronto City空间筛选，因此不得把全国CT面积统计或Toronto CMA面积统计冒充Toronto City结果。即使后续为了理解数据分布而计算全国CT或Toronto CMA的面积统计，也只能标记为“背景参考”，不能标记为Toronto City最终结果。

> **Toronto City CT平均面积、中位面积、面积范围及城市CT数量，需由下一阶段在完成Toronto City空间筛选后补充。**

## 加拿大与美国Census Tract比较

| 比较项 | 加拿大Census tract | 美国Census Tract |
|---|---|---|
| 单元性质 | Statistics Canada划定的统计地理单元，不是行政区 | U.S. Census Bureau划定的县或同等实体内统计分区，不是行政区 |
| 统计用途 | 发布人口普查及社会经济统计，支持市政规划、研究和市场分析 | 提供稳定的小地域单元，用于发布人口普查及ACS等统计数据 |
| 典型人口规模 | 通常2,500—7,500人，推荐平均约5,000人 | 通常1,200—8,000人，最优约4,000人 |
| 边界稳定性 | 相对稳定；非必要不调整，可因增长拆分并支持历史重聚合 | 相对永久；为跨期比较而维持，可能因人口增长拆分或衰退合并 |
| 唯一编码 | `DGUID`为全国唯一连接标识；`CTUID`结合CMA/CA代码与CT名称 | 完整`GEOID`由州、县和tract代码组成，可唯一识别tract |
| 指标丰富度 | 2021 Census Profile提供人口、家庭、收入、住房、教育、就业等CT指标 | Decennial Census、ACS等提供丰富的人口、住房及社会经济指标 |
| 覆盖方式 | 位于CMA及符合条件的CA，不覆盖全国全部国土 | 标准county-based tracts覆盖县或同等实体体系；另有独立的tribal tract体系 |
| 最终相似度 | **高**：概念、用途、人口规模、稳定性和指标承载方式均高度对应 | **高** |

美国官方参考：

https://www.census.gov/programs-surveys/geography/about/glossary.html

https://www.census.gov/programs-surveys/geography/guidance/geo-identifiers.html

## 使用限制

CT适用于统计分析和城市内部差异比较，但不是具有治理权限的行政区。边界的“相对稳定”也不代表跨普查年份完全不变；开展跨期比较时仍需检查边界变更和对应表。
