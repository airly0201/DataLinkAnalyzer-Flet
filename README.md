# 📱 数据关联分析平台 (Flet版)

基于 Flet 框架构建的原生 Android App，支持多表数据关联分析和 Excel 数据处理。

## 功能特点

- 📂 **文件选择**: 扫描文件夹，选择多个 Excel 文件
- 🔗 **多表关联**: 配置表之间的关联关系（内连接、左连接、全连接）
- 📤 **字段选择**: 选择需要输出的字段
- 📊 **查询执行**: 执行关联查询并预览结果
- 📥 **导出功能**: 导出查询结果为 Excel 文件

## 项目结构

```
DataLinkAnalyzer-Flet/
├── main.py              # 主入口
├── pages/
│   ├── file_selector.py # 文件选择页面
│   ├── linker.py        # 多表关联页面
│   ├── output_fields.py # 输出字段选择
│   └── result.py        # 结果展示
├── core/                # 核心逻辑
│   ├── excel_reader.py  # Excel 读取
│   └── linker.py        # 关联引擎
├── utils/               # 工具函数
│   ├── cleaner.py       # 数据清洗
│   └── file_scanner.py  # 文件扫描
├── requirements.txt     # Python 依赖
└── flet-app.yml        # 云打包配置
```

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

依赖包括:
- flet >= 0.21.0
- pandas >= 2.0.0
- openpyxl >= 3.1.0

### 2. 运行应用

#### 桌面调试模式
```bash
python main.py
# 或者使用 Web 模式
flet main.py
```

#### Android 打包

使用 Flet Cloud Build:
```bash
flet build android -y
```

或在 [Flet Cloud](https://flet.dev/build) 上传项目进行打包。

## 使用流程

1. **选择文件夹**: 输入包含 Excel 文件的文件夹路径，点击扫描
2. **选择文件**: 勾选需要分析的 Excel 文件
3. **配置关联**: 选择主表和关联表，设置关联字段和连接方式
4. **选择字段**: 选择需要输出的字段
5. **执行查询**: 点击执行查询并查看结果
6. **导出结果**: 导出查询结果到 Excel

## UI 预览

应用采用 Material Design 3 设计，支持:
- 移动端适配（竖屏优先）
- 响应式布局
- 中文界面

## 注意事项

- 支持 .xlsx 和 .xls 格式的 Excel 文件
- 建议文件大小不超过 50MB 以获得最佳性能
- 关联字段建议使用编号、ID 等唯一标识字段