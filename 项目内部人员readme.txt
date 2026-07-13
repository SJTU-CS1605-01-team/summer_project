AI 推荐的项目目录架构，我先按照这样来建了

project/
├── .gitignore                     # 全局忽略文件（配置在最外层）
├── README.md                      # 整个项目的总门户（写团队简介、各阶段速览、网盘链接）
│
├── stage1_data_cleaning/          # 【阶段1：数据获取与清洗】（当前重点）
│   ├── README.md                  # 阶段1小结：数据可行性分级结论（A/B/C/D）
│   ├── data/                      # 阶段1的数据流
│   │   ├── raw/                   # 原始Shapefile和统计Excel（本地存放，不传GitHub）
│   │   └── processed/             # 最终的 city_tract_indicators.gpkg
│   ├── docs/                      # 阶段1要求的表格
│   │   └── indicator_inventory.xlsx 
│   ├── qgis/                      # QGIS工程文件夹
│   │   └── project.qgz
│   ├── maps/                      # 导出的2张+正式专题地图 (.png)
│   └── presentation/              # 阶段1的答辩PPT
│       └── stage1_report.pptx
│
└── stage2_ai_modeling/            # 【阶段2：AI建模与应用】（后续推进）
    ├── README.md                  # 阶段2小结：模型表现、城市分析结论
    ├── src/                       # 阶段2的代码（如 Python 脚本、Jupyter Notebooks）
    │   └── train_model.py
    ├── models/                    # 存放训练好的 AI 模型权重文件（如 .pth, .pkl）
    ├── output/                    # AI 预测结果、图表、评估曲线
    └── presentation/              # 最终结课总答辩PPT
        └── final_report.pptx



目前已知的注意点：

GitHub 网页端单文件上传不能超过 25MB，命令行（Git）上传单文件绝对不能超过 100MB。
全国或大城市的 Shapefile（.shp）或 GeoPackage（.gpkg）动辄几百 MB，直接 Push 会直接报错导致整个同步失败！
大的原始地理数据包不要传到 GitHub。可以把它们传到百度网盘、OneDrive 或阿里云盘，在 GitHub 的 README.md 里写一句话：“原始数据请在此链接下载，下载后放入 /data 文件夹”。




.gitignore

# 忽略系统自动生成的垃圾文件
.DS_Store
Thumbs.db

# ==========================================
# 阶段 1 (Stage 1) 忽略规则
# ==========================================
# 忽略 QGIS 产生的本地临时备份和锁定文件
*.qgz~
*.qgd
*.bak
.qgis/

# 忽略阶段 1 的本地原始大数据（防止超过 100MB 限制报错）
# 组员通过网盘下载后，手动放入该目录下即可
stage1_data_cleaning/data/raw/


# ==========================================
# 阶段 2 (Stage 2) 忽略规则
# ==========================================
# 忽略 Python 虚拟环境及缓存
__pycache__/
*.pyc
.venv/
venv/
env/

# 忽略大型 AI 模型权重文件（如果大于 50MB，建议通过网盘共享，不传 GitHub）
stage2_ai_modeling/models/

