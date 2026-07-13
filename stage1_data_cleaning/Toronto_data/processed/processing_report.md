# Canada Census Tract 10指标处理报告

## 源数据与完整性

- 源文件：`98-401-X2021007_eng_CSV.zip`
- ZIP大小：249,720,408 bytes（238.15 MiB）
- ZIP内部主CSV：`98-401-X2021007_English_CSV_data.csv`，2,634,464,532 bytes
- ZIP完整性检查：通过（所有成员CRC可读取）
- 实际读取编码：`cp1252`
- 原始CSV表头：

```text
CENSUS_YEAR,DGUID,ALT_GEO_CODE,GEO_LEVEL,GEO_NAME,TNR_SF,TNR_LF,DATA_QUALITY_FLAG,CHARACTERISTIC_ID,CHARACTERISTIC_NAME,CHARACTERISTIC_NOTE,C1_COUNT_TOTAL,SYMBOL,C2_COUNT_MEN+,SYMBOL,C3_COUNT_WOMEN+,SYMBOL,C10_RATE_TOTAL,SYMBOL,C11_RATE_MEN+,SYMBOL,C12_RATE_WOMEN+,SYMBOL
```

## 处理方法与筛选条件

使用Python标准库`zipfile + csv`直接从ZIP内流式读取CSV，未解压2.63GB主CSV，未使用Pandas整表加载。符合`GEO_LEVEL = Census tract`且`CHARACTERISTIC_ID`属于1、6、37、57、113、345、1416、1467、2024、2230的记录写入临时SQLite，再经条件聚合生成宽表。DGUID和ALT_GEO_CODE全程按字符串处理；名称仅去除首尾空格并用于核对，筛选以ID为准。空白、`...`、`..`及抑制/不适用符号写为缺失，不替换为0；百分比保留0—100尺度。

共扫描原始数据行16,567,407条；CT层级长表行16,435,857条；入选指标长表行62,470条；输出CT数6,247。

### 指标ID、官方名称和取值列核对

| CHARACTERISTIC_ID | 输出字段 | 官方原始名称（去除首尾空格） | 取值列 |
|---:|---|---|---|
| 1 | population_2021 | Population, 2021 | C1_COUNT_TOTAL |
| 6 | population_density_km2 | Population density per square kilometre | C1_COUNT_TOTAL |
| 37 | age_65_plus_pct | 65 years and over | C10_RATE_TOTAL |
| 57 | average_household_size | Average household size | C1_COUNT_TOTAL |
| 113 | median_total_income_2020 | Median total income in 2020 among recipients ($) | C1_COUNT_TOTAL |
| 345 | low_income_lim_at_pct | Prevalence of low income based on the Low-income measure, after tax (LIM-AT) (%) | C10_RATE_TOTAL |
| 1416 | renter_households_pct | Renter | C10_RATE_TOTAL |
| 1467 | shelter_cost_30pct_plus_pct | Spending 30% or more of income on shelter costs | C10_RATE_TOTAL |
| 2024 | bachelor_or_higher_age25_64_pct | Bachelor's degree or higher | C10_RATE_TOTAL |
| 2230 | unemployment_rate_pct | Unemployment rate | C10_RATE_TOTAL |

ID 57在官方原始数据中的实际名称为`Average household size`，因此采用该名称，而不是泛化的“Average size of census families/households”。ID 2024与ID 2008虽显示相同简短名称，但ID 2024位于25—64岁统计对象下，本项目严格使用ID 2024。

## 指标完整性与范围

| 指标字段 | 非缺失 | 缺失 | 覆盖率 | 最小值 | 最大值 | 明显异常值数 |
|---|---:|---:|---:|---:|---:|---:|
| population_2021 | 6,240 | 7 | 99.9% | 0 | 29669 | 0 |
| population_density_km2 | 6,240 | 7 | 99.9% | 0 | 77545.3 | 0 |
| age_65_plus_pct | 6,166 | 81 | 98.7% | 0 | 91.7 | 0 |
| average_household_size | 6,161 | 86 | 98.6% | 1.2 | 4.9 | 0 |
| median_total_income_2020 | 6,100 | 147 | 97.6% | 20600 | 94000 | 0 |
| low_income_lim_at_pct | 6,100 | 147 | 97.6% | 0.8 | 61 | 0 |
| renter_households_pct | 6,158 | 89 | 98.6% | 0 | 100 | 0 |
| shelter_cost_30pct_plus_pct | 6,099 | 148 | 97.6% | 0 | 63.4 | 0 |
| bachelor_or_higher_age25_64_pct | 6,158 | 89 | 98.6% | 0 | 86.7 | 0 |
| unemployment_rate_pct | 6,158 | 89 | 98.6% | 0 | 44.4 | 0 |

明显异常值规则：百分比不在0—100，或人口、人口密度、收入、家庭规模及其他数值为负数。没有把高但合法的密度等主观判为异常。

## 重复、质量标识与字段一致性

- `DGUID + CHARACTERISTIC_ID`重复组：0
- 输出DGUID重复：0；DGUID唯一性：通过
- 同一CT内质量标识不一致的DGUID：0
- 指标名称与指定官方名称不一致记录：0
- 未识别的非数值代码记录：0

## 质量验证

- 输出CSV记录数与唯一DGUID数一致：通过（6,247）
- 指标列恰好10列：通过
- 所有输出`GEO_LEVEL`均为`Census tract`：通过
- 随机抽查5个CT、逐一核对10个指标与原始ZIP长表：通过
  - `2021S05075050841.04`：一致
  - `2021S05075350057.00`：一致
  - `2021S05075350063.04`：一致
  - `2021S05075350410.15`：一致
  - `2021S05075550036.00`：一致
- 示例Toronto CMA CT DGUID `2021S05075350001.00`：存在。该前缀只表示Toronto CMA，不能据此判断属于Toronto City。
- 百分比0—100范围检查：通过
- 非负值检查：通过

## 空间覆盖说明

当前输出覆盖加拿大所有Census Tract，并非Toronto City最终子集。未按`535`前缀筛选或声称记录属于Toronto City；`535`仅表示Toronto CMA。后续空间处理应使用Toronto市界派生的市内DGUID清单，以`DGUID`为首选连接字段进一步筛选；`ALT_GEO_CODE`在CT层级对应边界文件的`CTUID`。

## 运行环境与复现

- 处理日期：2026-07-13
- 运行环境：macOS，Python 3.14.2
- 主要依赖：Python标准库`zipfile`、`csv`、`sqlite3`、`decimal`；未使用Pandas整表加载
- 复现工作目录：`/Users/william/Documents/cs1605/Toronto_data`
- 复现命令：`python3 process_ct_indicators.py`
- 输出范围：Canada-wide Census Tract dataset；Toronto City筛选待阶段4完成
