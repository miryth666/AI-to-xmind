# Markdown to XMind Converter

![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.0.0-orange)

一个将Markdown格式内容转换为XMind思维导图的Python工具。特别适合将AI生成的Markdown内容快速可视化为思维导图。

## 功能特点

- 🚀 **一键转换**：将Markdown文本转换为结构化的XMind思维导图
- 🧠 **智能解析**：自动识别Markdown标题层级结构（H1-H4）
- 📊 **表格支持**：将Markdown表格转换为思维导图节点
- ✨ **内容优化**：智能处理冒号分隔的内容，创建父子节点关系
- 🛠️ **用户友好**：提供简洁的GUI界面，也可作为脚本运行
- 🔍 **内容校验**：自动检测转换过程中遗漏的内容

## 安装使用

### 前置要求

- Python 3.7+
- json>=2.0.9
- re>=2.2.1
- markdown>=3.5
- emoji>=1.2.0
- beautifulsoup4>=4.12.2
- colorama>=0.4.6
- xmind>=2.4.1


### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python md_to_xmind.py
```

## 使用说明

1. 运行程序后，会出现图形界面
2. 在"中心主题以及文件名"输入框中输入思维导图的中心主题（也是文件名）
3. 在"Markdown文本"区域粘贴或输入Markdown格式内容
4. 点击"转换"按钮
5. 程序会自动生成XMind文件并在桌面打开

## 高级配置

在代码中可以通过修改以下配置参数调整程序行为：

```python
# 配置参数
self.config = {
    'enter_allowed': True,       # 是否允许思维导图有多行的字符串（若False则会劈分为平级）
    'right_arrow_allowed': True, # 是否允许含有右箭头（若False则会劈分为父子级）
    'code_split_allowed': False, # 是否允许代码块被分裂
    'table_split_allowed': True, # 是否允许表格被转换
    'test_mode': False,          # 测试模式
    'emoji_allowed': False       # 是否允许emoji表情
}
```

## 技术实现

### 核心流程

1. **Markdown解析**：使用`markdown`库将Markdown转换为HTML
2. **HTML处理**：使用BeautifulSoup解析HTML结构
3. **内容提取**：递归提取HTML中的标题层级和内容
4. **结构转换**：将提取的内容转换为树状结构
5. **XMind生成**：使用xmind库创建思维导图文件
6. **内容校验**：使用difflib检测转换过程中遗漏的内容

### 特殊处理

- **冒号分隔内容**：自动将"标题: 内容"转换为父子节点
- **表格处理**：将Markdown表格转换为结构化数据节点
- **代码块保护**：可配置是否保留代码块的完整性

## 作者

miryth666 - 1239812409@qq.com

---

**提示**：生成的思维导图为默认风格，可在XMind软件中更改风格（推荐"田园"风格）。部分特殊格式（如以短横线开头的级别）可能需要手动调整。
