# Markdown Bridge 📝 ↔️ 🌐

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Markdown](https://img.shields.io/badge/Markdown-Supported-brightgreen.svg)](https://daringfireball.net/projects/markdown/)

一个强大的 Markdown 文档翻译工具，支持保留 LaTeX 公式、代码块、图片链接等特殊元素，适用于学术论文和技术文档的翻译。

## ✨ 特性

- 🔄 支持多种翻译服务：Google Translate、DeepL、OpenAI 和 DeepSeek
- 📊 智能保护 LaTeX 公式、代码块、链接和图片等特殊元素
- 💾 翻译缓存功能，避免重复翻译相同内容
- 🧠 自定义提示模板，优化 AI 翻译效果
- 🛠️ 自动修复翻译后的 Markdown 格式问题
- 📄 支持文件翻译和文本翻译两种模式
- 🔐 支持从 .env 文件读取 API 密钥和配置

## 🚀 安装

```bash
# 克隆仓库
git clone git@github.com:cacity/Markdown-Bridge.git
cd Markdown-Bridge

# 安装依赖
pip install -r requirements.txt
```

## 📋 依赖

- Python 3.6+
- googletrans (Google 翻译)
- deepl (DeepL 翻译)
- openai (OpenAI 翻译)
- python-dotenv (环境变量配置)
- tqdm (进度条显示)
- requests (HTTP 请求)

## 🔧 使用方法

### 命令行参数

工具提供两种子命令：

1. `translate-file`: 翻译 Markdown 文件
2. `translate-text`: 翻译 Markdown 文本

#### 翻译文件

```bash
python markdown_translator.py translate-file input.md output.md [options]
```

#### 翻译文本

```bash
python markdown_translator.py translate-text "Your markdown text here" [options]
```

### 选项参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--lang-in` | 源语言代码 | en (英语) |
| `--lang-out` | 目标语言代码 | zh (中文) |
| `--service` | 翻译服务 (google, deepl, openai, deepseek) | google |
| `--model` | 模型名称 (仅 OpenAI 和 DeepSeek) | gpt-3.5-turbo |
| `--api-key` | API 密钥 (DeepL、OpenAI 或 DeepSeek) | 无 |
| `--base-url` | API 基础 URL (仅 OpenAI 和 DeepSeek) | 无 |
| `--ignore-cache` | 忽略缓存 | False |
| `--prompt-template` | 提示模板 (仅 OpenAI 和 DeepSeek) | 无 |

### 环境变量配置

可以在 `.env` 文件中配置 API 密钥和其他参数：

```env
# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1

# DeepL 配置
DEEPL_API_KEY=your_deepl_api_key

# DeepSeek 配置
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-r1-250120
```

### 示例

#### 使用 Google 翻译 (默认)

```bash
python markdown_translator.py translate-file paper.md paper_zh.md
```

#### 使用 DeepL 翻译

```bash
python markdown_translator.py translate-file paper.md paper_zh.md --service deepl --api-key YOUR_DEEPL_API_KEY
```

#### 使用 OpenAI 翻译

```bash
python markdown_translator.py translate-file paper.md paper_zh.md --service openai --api-key YOUR_OPENAI_API_KEY --model gpt-4
```

#### 使用 DeepSeek 翻译

```bash
python markdown_translator.py translate-file paper.md paper_zh.md --service deepseek
```

如果已配置 `.env` 文件，则无需指定 API 密钥和 URL。

#### 自定义提示模板

```bash
python markdown_translator.py translate-file paper.md paper_zh.md --service openai --api-key YOUR_OPENAI_API_KEY --prompt-template "你是一个学术翻译专家，请将以下文本从{source_lang}翻译成{target_lang}，保持学术术语的准确性和专业性。"
```

## 🧩 核心功能模块

### 1. 特殊元素保护 (protect_special_elements)

在翻译前保护以下元素，避免被翻译服务修改：

- LaTeX 公式 (行内公式和块级公式)
- 代码块和行内代码
- 图片链接 (有标题和无标题)
- 超链接
- HTML 标签

### 2. LaTeX 公式处理 (LatexFormulaHandler)

专门处理各种复杂的 LaTeX 公式，包括：

- 行内公式和块级公式的识别与保护
- 复杂公式模式的匹配 (包含 mathbf, mathrm, frac 等)
- 公式格式的修复和恢复

### 3. 翻译缓存 (TranslationCache)

提供翻译结果的缓存功能：

- 基于文件的持久化缓存
- 避免重复翻译相同内容
- 提高翻译效率

### 4. Markdown 格式修复 (fix_markdown_format)

修复翻译后的 Markdown 格式问题：

- 标题格式修复 (确保 # 后有空格，使用英文 #)
- 图片链接修复 (保持正确的图片链接格式)
- 特殊元素占位符的恢复

### 5. 翻译服务 (translate_markdown)

支持多种翻译服务：

- Google Translate (免费，无需 API 密钥)
- DeepL (需要 API 密钥)
- OpenAI (需要 API 密钥，支持自定义提示模板)
- DeepSeek (需要 API 密钥，支持自定义提示模板)

## 🔍 特殊处理

本工具对以下情况进行了特殊处理：

1. **LaTeX 公式**：识别和保护各种复杂的 LaTeX 公式，确保公式不被翻译服务破坏
2. **图片链接**：正确处理有标题和无标题的图片链接，确保翻译后保留原始图片路径和标题
3. **标题格式**：自动修复标题格式，确保使用英文 # 且后面有空格
4. **翻译服务适配**：针对不同翻译服务的特点进行适配，如语言代码转换
5. **占位符恢复**：智能处理翻译服务可能引入的占位符变体问题
6. **兼容性处理**：针对 googletrans 库可能出现的兼容性问题提供了备选方案，确保翻译服务的稳定性

## 📝 注意事项

- 对于 OpenAI 和 DeepSeek 翻译，建议使用更高级的模型获得更好的翻译质量
- DeepL、OpenAI 和 DeepSeek 服务需要有效的 API 密钥
- 翻译缓存文件保存在当前目录下，格式为 `translation_cache_{service}_{lang_in}_{lang_out}.json`
- 对于大型文档，建议分段翻译以避免超出 API 限制
- 可以通过 `.env` 文件配置 API 密钥和其他参数，避免在命令行中暴露敏感信息
- 如果遇到 `googletrans` 库的兼容性问题，程序会自动切换到使用 requests 直接调用 Google 翻译 API

## 🆕 最近更新

### 2025-03-16

- 🛠️ 修复了图片链接处理问题，确保所有图片在翻译后都能正确显示，不再显示为占位符
- 🔄 增强了图片占位符的识别和替换逻辑，支持更多可能的占位符变体
- 🌐 改进了 Google 翻译服务的兼容性，解决了 `httpcore.SyncHTTPTransport` 相关的错误
- 🧰 添加了 Google 翻译的备选实现，当 `googletrans` 库出现问题时自动切换到直接 API 调用

## 🤝 贡献

欢迎提交 Issues 和 Pull Requests 来改进这个工具！

## 📄 许可证

[MIT License](LICENSE)
