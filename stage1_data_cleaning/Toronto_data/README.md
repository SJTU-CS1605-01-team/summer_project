# Toronto Census Tract数据准备（阶段1—3）

> **文档定位：**本README专门记录阶段1—3交付物及其生成时的职责边界。团队`second`分支现已包含阶段4—6文件；跨阶段总览见上一级`../README.md`，阶段4、5、6的最新验收状态分别见`stage4_qgis_quality_report.md`、`stage5_join_quality_report.md`和`stage5_6_current_status.md`。

## 1. 项目目的与当前范围

本文记录Toronto城市内部社会经济空间分析的阶段1—3成果：确定研究单元、整理官方边界及元数据、筛选并说明10个CT层级指标。

本阶段不筛选或裁剪Toronto City，不操作QGIS，不连接边界与指标，不计算匹配率，不制作专题地图，也不评价AI或神经网络应用。

> **重要：`canada_ct_10_indicators_2021.csv`覆盖加拿大所有Census Tract，不是Toronto City最终子集。不得仅按535前缀将Toronto CMA视为Toronto City。阶段4已另行使用Toronto City市界获得585个市内CT；不得反向把该城市结果冒充阶段3全国宽表。**

## 2. tract-like选择结论

推荐使用Statistics Canada的2021 **Census tract（CT）**。CT是小型、相对稳定的普查统计区，不是行政区；通常人口2,500—7,500人，推荐平均约5,000人。它与美国Census Tract在性质、统计用途、稳定性和人口规模上高度相似。完整说明见`CT_definition/tract_like_selection.md`。

CT只存在于Census Metropolitan Areas，以及符合条件的Census Agglomerations，不覆盖加拿大全部国土。Toronto属于有CT覆盖的CMA。

Toronto City的2021 Census Subdivision（CSD）ID为`3520005`。该市级标识与Toronto CMA代码不是同一概念，不能用CMA前缀`535`代替Toronto City范围判断。

官方定义：

https://www12.statcan.gc.ca/census-recensement/2021/ref/dict/az/definition-eng.cfm?ID=geo013

## 3. 官方数据来源

### 3.1 边界

| 元数据项 | 内容 |
|---|---|
| 数据产品 | 2021 Census Tract Cartographic Boundary File |
| 发布机构 | Statistics Canada |
| 边界年份 | 2021 |
| 文件类型 | Cartographic Boundary File |
| 文件格式 | Shapefile |
| 原始文件名 | `lct_000b21a_e.zip` |
| CRS | NAD83 Statistics Canada Lambert（EPSG:3347） |
| 坐标单位 | metre |
| 唯一编号 | `DGUID` |
| 备用编号 | `CTUID` |
| 名称字段 | `CTNAME` |
| 面积字段 | `LANDAREA` |
| 下载日期 | 2026-07-13 |
| 许可证 | Statistics Canada Open Licence |
| 当前空间范围 | 加拿大全国Census Tract |
| 后续操作 | 下一阶段使用Toronto City市界筛选市内CT |

边界下载页面：

https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?Year=21

页面选择路径：选择2021 Census边界文件，地理层级选Census tract，文件类型选Cartographic Boundary File，格式选Shapefile，投影选Statistics Canada Lambert。下载后保留原ZIP，并解压成套Shapefile组件。

下载记录中的URL角色：

- `source_url`（官方产品介绍/选择页面）：https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?Year=21
- `download_url`：该页面根据选择项动态生成下载请求，本项目未获得可保证长期稳定的文件直链，因此不把选择页面伪装成实际文件直链。
- 页面选择步骤：2021 Census → Census tract → Cartographic Boundary File → Shapefile → Statistics Canada Lambert。
- 实际下载文件名：`lct_000b21a_e.zip`
- 下载日期：2026-07-13
- 文件大小：13,403,271 bytes（约12.78 MiB）
- 无稳定直链原因：官方下载地址由网页选择参数动态生成，可能包含会话或可变请求参数；官方选择页面、操作路径和本地文件信息已保留以便审计。

已做结构检查：`.shp`、`.shx`、`.dbf`、`.prj`均存在；DBF含6,247条记录及`CTUID`、`DGUID`、`CTNAME`、`LANDAREA`字段；PRJ声明NAD83 Statistics Canada Lambert，单位为metre。本阶段未启动QGIS，也未修改边界。

### 3.2 指标

来源产品：Statistics Canada, **Census Profile, 2021 Census of Population**。

指标来源/下载页面：

https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm?DGUIDlist=2021A000210&GENDERlist=1&HEADERlist=0&Lang=E&STATISTIClist=1%2C4

页面选择路径：进入2021 Census Profile下载页面，选择Census Metropolitan Areas、Tracted Census Agglomerations and Census Tracts的英文CSV产品，下载`98-401-X2021007_eng_CSV.zip`。原始下载页面涉及手动选择，但本文件记录了URL、产品编号、原始文件名和处理脚本。

下载记录中的URL角色：

- `source_url`（官方产品介绍/选择页面）：https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm?DGUIDlist=2021A000210&GENDERlist=1&HEADERlist=0&Lang=E&STATISTIClist=1%2C4
- `download_url`：下载请求由官方页面根据地理层级、语言、统计量和格式选择动态生成，本项目未获得可保证长期稳定的文件直链。
- 页面选择步骤：2021 Census Profile → Census Metropolitan Areas, Tracted Census Agglomerations and Census Tracts → English → CSV。
- 实际下载文件名：`98-401-X2021007_eng_CSV.zip`
- 下载日期：2026-07-13
- 文件大小：249,720,408 bytes（约238.15 MiB）
- 无稳定直链原因：下载端点由网页动态生成；项目保留了官方选择页面、产品编号、选择路径、文件名、大小、日期及可复现的处理脚本。

## 4. 原始文件说明

- `boundary/lct_000b21a_e.zip`：2021全国CT制图边界ZIP。
- `boundary/lct_000b21a_e/`：解压后的Shapefile组件。
- `indicators/98-401-X2021007_eng_CSV.zip`：2021 Census Profile原始指标ZIP，约249 MB。
- ZIP内部主CSV为`98-401-X2021007_English_CSV_data.csv`，约2.63 GB。
- `processed/canada_ct_10_indicators_2021.csv`：全国6,247个CT的十指标宽表。

原始ZIP及解压的大CSV不应加入普通Git历史；应通过上述官方页面重新下载。

## 5. 文件夹结构

```text
Toronto_data/
├── CT_definition/            # tract-like定义、官方URL与定义页截图
├── boundary/                 # 原始边界ZIP、Shapefile组件、URL与下载页截图
├── indicators/               # 原始Census Profile ZIP、URL与下载页截图
├── processed/                # 全国CT十指标CSV及处理报告
├── evidence/                 # 真实指标表证据图
├── STAGE1_3_RESPONSIBILITY_ANSWERS.txt # 职责问题答案与证据位置
├── GITHUB_UPLOAD_MANIFEST.txt          # GitHub上传结构和文件清单
├── process_ct_indicators.py  # 低内存处理脚本
├── build_workbooks.py        # 生成并验证两个XLSX交付物
├── indicator_inventory.xlsx # 指标清单
├── data_dictionary.xlsx     # 输出字段字典
├── quality_report.md         # 阶段1—3质量说明
└── README.md
```

主要文件用途：

| 文件 | 用途 |
|---|---|
| `CT_definition/tract_like_selection.md` | 记录研究对象、CT选择依据、覆盖范围和阶段4待补面积统计 |
| `CT_definition/url.txt`、`definition_page.png` | 官方CT定义来源及页面证据 |
| `boundary/url.txt`、`boundary_download_page.png` | 边界来源、下载选择、CRS、编码和页面证据 |
| `boundary/lct_000b21a_e.zip`及解压目录 | 2021 Canada-wide CT制图边界 |
| `indicators/url.txt`、`indicator_download_page.png` | Census Profile下载来源、选择方式和页面证据 |
| `process_ct_indicators.py` | 低内存筛选、重复检查、宽表生成及验证脚本 |
| `processed/canada_ct_10_indicators_2021.csv` | Canada-wide CT十指标宽表，供下一阶段筛选与连接 |
| `processed/processing_report.md` | 处理过程、缺失、范围、重复和抽查记录 |
| `evidence/indicator_data_sample.png` | 处理后真实数据表的可视证据 |
| `STAGE1_3_RESPONSIBILITY_ANSWERS.txt` | 逐题回答阶段1—3职责问题并标注证据位置 |
| `GITHUB_UPLOAD_MANIFEST.txt` | 给出可上传目录结构、绝对路径及本地排除文件 |
| `build_workbooks.py` | 使用经用户授权的openpyxl生成两个工作簿并渲染检查 |
| `indicator_inventory.xlsx` | 10项指标清单、来源信息和质量汇总，已生成并视觉检查 |
| `data_dictionary.xlsx` | 全国CT宽表全部16个字段的数据字典，已生成并视觉检查 |

## 6. 十个指标

| 字段 | ID | 主题 | 数据基础 | 参考年份 |
|---|---:|---|---|---:|
| population_2021 | 1 | 人口 | 100% data | 2021 |
| population_density_km2 | 6 | 人口密度 | 100% data | 2021 |
| age_65_plus_pct | 37 | 年龄结构 | 100% data | 2021 |
| average_household_size | 57 | 家庭 | 100% data | 2021 |
| median_total_income_2020 | 113 | 收入 | 100% data | 2020 |
| low_income_lim_at_pct | 345 | 低收入 | 100% data | 2020 |
| renter_households_pct | 1416 | 住房 | 25% sample data | 2021 |
| shelter_cost_30pct_plus_pct | 1467 | 住房负担 | 25% sample data | 2021 |
| bachelor_or_higher_age25_64_pct | 2024 | 教育 | 25% sample data | 2021 |
| unemployment_rate_pct | 2230 | 就业 | 25% sample data | 2021 |

教育指标必须使用ID 2024，统计对象为25—64岁人口，不使用ID 2008。

“100% data”主要来自覆盖全体人口或行政数据整合的普查指标，通常没有抽样误差，但仍可能存在随机舍入、抑制或不适用。“25% sample data”来自长表抽样，除抑制和不适用外还具有抽样误差，解读小人口CT时应更谨慎。两类指标均是Statistics Canada正式发布的CT级指标，本项目没有自行拆分或下推。

## 7. 大CSV处理方法与运行

`process_ct_indicators.py`使用Python标准库`zipfile + csv`直接流式读取ZIP内部CSV，并用临时SQLite完成重复检查和宽表聚合。它不使用Pandas一次性载入2.63GB文件，也不要求Excel/WPS打开原始CSV。

在`Toronto_data`目录运行：

```bash
python3 process_ct_indicators.py
```

脚本严格筛选`GEO_LEVEL = Census tract`和10个指定`CHARACTERISTIC_ID`，检测`DGUID + CHARACTERISTIC_ID`重复，保留质量标识，输出UTF-8 CSV和处理报告。

## 8. DGUID连接与空间尺度一致性

边界和十个指标的原始空间层级均为Census Tract。连接方法为`direct_join`，首选连接字段为文本型`DGUID`；`ALT_GEO_CODE`在CT层级对应边界`CTUID`，可作备用核对字段。不存在把CMA、市级或省级数据下推到CT的处理。

本阶段没有实际执行属性连接，因此不报告连接匹配率或未匹配区域。

## 9. 年份说明

边界产品版本和Census Profile产品版本均为2021。人口、密度、年龄、家庭、住房、教育和就业指标主要对应2021；收入中位数和LIM-AT参考年份为2020，但由2021 Census Profile按2021 CT边界体系发布，不是空间版本混用。

## 10. 缺失值和百分比规则

空白、`...`、`..`以及官方抑制、不适用或质量限制值均保存为缺失，不改成0。百分比保持源数据0—100尺度，例如`17.8`表示17.8%，不除以100。当前CSV每行一个CT，DGUID唯一。

## 11. 数据许可证

边界和指标适用Statistics Canada Open Licence：

https://www.statcan.gc.ca/en/terms-conditions/open-licence

使用数据时应准确注明来源，不得暗示Statistics Canada为本项目背书。

## 12. 当前输出与下一阶段交接

当前输出为加拿大所有CT，共6,247行，不是Toronto City最终子集。下一阶段应：

1. 获取权威Toronto City行政边界；
2. 在QGIS中加载Toronto City边界和全国CT边界，核对两者CRS并定义清晰的空间筛选规则；
3. 根据课程要求选择“质心位于市界内”“最大面积归属”或其他明确规则，生成Toronto City市内CT的DGUID清单；
4. 以该DGUID清单筛选全国指标表；
5. 使用文本型`DGUID`执行属性连接，并报告匹配率、未匹配区域及边界相交处理；
6. 完成城市CT数量和`LANDAREA`面积统计后，再制作专题地图。

Toronto City最终CT数量、裁剪结果、连接匹配率、派生指标、专题地图和AI应用判断均不属于本阶段成果。

## 13. 阶段1—3验收表

### 阶段1

| 验收项 | 状态/结果 |
|---|---|
| 国家 | Canada |
| 城市 | Toronto |
| tract-like单元 | Census tract |
| 官方定义 | 已记录 |
| 单元性质 | 统计/普查单元，不是行政区 |
| 人口尺度 | 已记录：通常2,500—7,500人，推荐平均约5,000人 |
| 面积字段 | `LANDAREA`，单位km² |
| Toronto City最终面积统计 | 待下一阶段完成城市空间筛选后补充 |
| 唯一编码 | `DGUID`、`CTUID` |
| 单元选择结论 | 已完成 |

### 阶段2

| 验收项 | 状态/结果 |
|---|---|
| 官方页面 | 已记录 |
| 下载路径 | 已记录 |
| 边界年份 | 2021 |
| CRS | NAD83 Statistics Canada Lambert |
| 常用EPSG | 3347 |
| 许可证 | Statistics Canada Open Licence |
| Shapefile完整性 | 已检查，`.shp/.shx/.dbf/.prj`齐全 |
| 原始ZIP | 已保留且未修改 |

### 阶段3

| 验收项 | 状态/结果 |
|---|---|
| 实际CSV | 已保留：`processed/canada_ct_10_indicators_2021.csv` |
| 空间层级 | Census tract |
| 空间ID | `DGUID` |
| 指标数量 | 10 |
| `indicator_inventory.xlsx` | 已生成：3个工作表、10个指标，已重新读取并视觉检查 |
| `data_dictionary.xlsx` | 已生成：16个输出字段，已重新读取并视觉检查 |
| 真实数据表证据图 | 已生成：`evidence/indicator_data_sample.png` |
| 缺失值规则 | 已说明 |
| 空间尺度一致性 | 已说明：边界和全部指标均为2021 CT尺度，连接方法为`direct_join` |

阶段1—3的数据对象确定、全国CT边界获取、CT层级十指标收集、指标清单、数据字典及相关说明已经完成。两个XLSX使用经用户明确授权的`openpyxl`替代方案生成，并经过重新载入、结构检查和逐工作表高分辨率视觉检查。
