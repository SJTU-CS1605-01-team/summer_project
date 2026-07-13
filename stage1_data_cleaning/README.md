# Stage 1 data collection and cleaning

本阶段目录中的 `Toronto_data/` 是 Toronto 2021 Census Tract 项目阶段1—3的完整、可复现交付包，包括空间单元选择、Statistics Canada全国CT边界、10项CT级指标、数据字典、质量报告和证据图片。

## 当前完成范围

- 确定研究对象：Canada、Toronto、2021 Census tract。
- 获取并验证 Statistics Canada 2021 Census Tract Cartographic Boundary File。
- 从 Census Profile 2021 的大型长表中流式筛选10项指标，生成6,247行全国CT宽表。
- 生成指标清单、数据字典、处理报告和阶段1—3职责问题答案。

当前数据尚未筛选为 Toronto City。Toronto CMA代码前缀 `535` 不能替代Toronto City市界。城市裁剪、边界连接、匹配率、QGIS地图和AI分析由后续阶段完成。

## 主要文件

- `Toronto_data/README.md`：完整项目说明及阶段1—3验收表。
- `Toronto_data/CT_definition/tract_like_selection.md`：tract-like单元选择结论。
- `Toronto_data/boundary/`：2021全国CT Shapefile、原始ZIP及来源证据。
- `Toronto_data/processed/canada_ct_10_indicators_2021.csv`：6,247个全国CT、10项指标。
- `Toronto_data/indicator_inventory.xlsx`：指标清单、来源信息和质量汇总。
- `Toronto_data/data_dictionary.xlsx`：输出CSV全部16个字段的数据字典。
- `Toronto_data/evidence/indicator_data_sample.png`：真实数据表证据图。
- `Toronto_data/STAGE1_3_RESPONSIBILITY_ANSWERS.txt`：职责问题答案及证据位置。

仓库既有的 `docs/indicator_inventory.xlsx` 和 `docs/data_dictionary.xlsx` 是上述两个工作簿的便捷副本。

## 未上传的大文件

以下文件仅保留在本地，不进入普通Git历史：

- `98-401-X2021007_eng_CSV.zip`（约238 MiB）；
- ZIP解压后的约2.63 GB原始主CSV目录。

官方重新下载页面、文件名、选择步骤、访问日期和处理脚本均记录在 `Toronto_data/indicators/url.txt` 与 `Toronto_data/README.md` 中。
