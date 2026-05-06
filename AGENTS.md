# AiCustomer — AI 扫地机器人客服助手

## 项目概述

AiCustomer 是一个面向扫地机器人 / 扫拖一体机器人的中文智能客服系统。它基于 **ReAct（思考→行动→观察→再思考）** 架构，通过大语言模型自主判断何时调用工具，并结合 RAG（检索增强生成）知识库、外部天气数据、用户位置信息以及个人使用记录，为用户提供专业的产品咨询、故障排查、保养建议和个性化使用报告。

项目主要使用场景：
- 解答扫地/扫拖机器人的常见问题
- 根据用户所在城市天气给出环境适配建议
- 查询并生成用户个人月度使用报告

## 技术栈

- **Python**: >= 3.13
- **包管理器**: `uv`（`pyproject.toml` + `uv.lock`）
- **LLM 框架**: LangChain / LangGraph（`langchain>=1.2.15`）
- **大语言模型**: DeepSeek（`langchain-deepseek`，模型 `deepseek-v4-flash`）
- **向量数据库**: ChromaDB（`chromadb>=1.5.8`，`langchain-chroma`）
- **文本嵌入**: 阿里云 DashScope（`text-embedding-v4`）
- **环境变量**: `python-dotenv`（`.env` 文件存放 API Key）

## 项目结构

```
.
├── main.py                      # 入口文件（当前为占位实现）
├── pyproject.toml               # 项目依赖配置（uv 管理）
├── uv.lock                      # 锁定依赖版本
├── .env                         # 环境变量（API Key，勿提交）
│
├── agent/                       # ReAct 智能体核心
│   ├── react_agent.py           # 主代理类 ReactAgent，编排工具与中间件
│   └── tools/
│       ├── agent_tools.py       # 7 个工具函数（RAG、天气、用户信息、外部数据等）
│       └── middleware.py        # 3 个中间件（工具监控、模型前日志、动态提示词切换）
│
├── rag/                         # 检索增强生成模块
│   ├── vector_store.py          # ChromaDB 向量库封装（文档加载、分片、去重、检索）
│   └── rag_service.py           # RAG 问答链路（检索 → 提示词模板 → LLM → 输出）
│
├── model/                       # 模型工厂
│   └── factory.py               # ChatModelFactory（DeepSeek）和 EmbeddingsFactory（DashScope）
│
├── utils/                       # 通用工具库
│   ├── config_handler.py        # YAML 配置加载器
│   ├── prompt_loader.py         # 提示词文本文件加载器
│   ├── logger_handler.py        # 日志管理（控制台 + 按日文件）
│   ├── file_handler.py          # 文件操作（MD5、PDF/TXT 加载、目录过滤）
│   └── path_tool.py             # 绝对路径解析（基于项目根目录）
│
├── config/                      # YAML 配置文件
│   ├── agent.yml                # 外部数据路径
│   ├── chroma.yml               # 向量库参数（分片、分隔符、检索数量等）
│   ├── rag.yml                  # 模型名称配置
│   └── prompts.yml              # 提示词文件路径映射
│
├── prompts/                     # 提示词文本（全部为中文）
│   ├── main_prompt.txt          # 主系统提示词（客服 ReAct 指令）
│   ├── rag_summarize.txt        # RAG 问答提示词模板
│   └── report_prompt.txt        # 报告生成专用提示词
│
├── data/                        # 数据目录
│   ├── external/
│   │   └── records.csv          # 用户月度使用记录（10 用户 × 4 个月）
│   ├── 扫拖议题机器人100问.txt   # 知识库：常见问题
│   ├── 故障排查.txt             # 知识库：故障检测与修复
│   ├── 维护保养.txt             # 知识库：日常维护保养
│   └── 选购指南.txt             # 知识库：选购建议
│
├── chroma_db/                   # ChromaDB 持久化存储（自动生成）
└── logs/                        # 运行日志（按天切割）
```

## 运行方式

### 1. 安装依赖

项目使用 `uv` 管理依赖：

```bash
uv sync
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件，写入必要的 API Key：

```bash
# DeepSeek API Key
DEEPSEEK_API_KEY=your_deepseek_api_key

# DashScope API Key（阿里云灵积模型服务）
DASHSCOPE_API_KEY=your_dashscope_api_key
```

> **安全提醒**: `.env` 已加入 `.gitignore`，请勿将其提交到版本控制。

### 3. 启动知识库加载

首次运行或知识库文件有更新时，需要加载文档到向量库：

```bash
python -m rag.vector_store
```

该命令会：
- 扫描 `data/` 目录下允许的文本类型（`.txt`、`.pdf`）
- 按 `config/chroma.yml` 中的参数进行文本分片
- 计算文件 MD5 做去重，避免重复入库
- 将分片后的文档存入 `chroma_db/`

### 4. 运行主程序

```bash
python main.py
```

或单独测试某个模块：

```bash
# 测试 RAG 问答
python -m rag.rag_service

# 测试 Agent 流式输出
python -m agent.react_agent

# 测试外部数据读取
python -m agent.tools.agent_tools
```

## 核心模块说明

### Agent（`agent/`）

`ReactAgent` 是系统的核心入口，使用 LangChain 的 `create_agent` 构建。它组合了 7 个工具和 3 个中间件：

**工具列表**（`agent/tools/agent_tools.py`）：
- `rag_summarize(query)` — 从向量库检索扫地机器人相关知识并生成回答
- `get_weather(city)` — 获取指定城市天气（当前为模拟数据）
- `get_user_location()` — 获取用户当前城市（随机模拟）
- `get_user_id()` — 获取用户 ID（随机模拟）
- `get_current_month()` — 获取当前月份（`YYYY-MM`）
- `fetch_external_data(user_id, month)` — 从 CSV 读取用户月度使用记录
- `fill_context_for_report()` — 触发报告生成上下文切换（无入参）

**中间件列表**（`agent/tools/middleware.py`）：
- `monitor_tool` — 包装工具调用，记录入参、结果和异常；当调用 `fill_context_for_report` 时，将 `runtime.context["report"]` 设为 `True`
- `log_before_model` — 在模型调用前输出日志，记录消息数量
- `report_prompt_switch` — 动态提示词切换中间件。若上下文标记为报告生成场景，则注入 `report_prompt.txt`，否则使用 `main_prompt.txt`

### RAG（`rag/`）

- `VectorStoreService` 封装 ChromaDB，支持基于 MD5 的文件级去重加载。
- `RagSummarizeService` 构建 LCEL 链路：`PromptTemplate | ChatModel | StrOutputParser()`。
- 检索时会拼接多篇参考资料及其元数据，传入提示词模板生成最终回答。

### Model Factory（`model/factory.py`）

- `ChatModelFactory`：生成 `ChatDeepSeek` 实例，模型名从 `config/rag.yml` 读取（默认 `deepseek-v4-flash`）。
- `EmbeddingsFactory`：生成 `DashScopeEmbeddings` 实例，模型名从 `config/rag.yml` 读取（默认 `text-embedding-v4`）。
- 模块加载时会自动读取项目根目录的 `.env` 文件。

## 代码风格与约定

- **语言**: 代码注释、日志、提示词、文档全部使用**中文**。
- **路径处理**: 禁止直接使用相对路径操作项目内文件，统一通过 `utils.path_tool.get_abs_path()` 获取绝对路径。
- **配置管理**: 所有可变参数（模型名、路径、分片大小等）统一放在 `config/*.yml` 中，通过 `utils.config_handler` 加载。
- **日志规范**: 统一使用 `utils.logger_handler.logger` 记录日志。日志格式包含时间、名称、级别、文件名、行号。
- **单例模式**: `RagSummarizeService` 通过全局变量 `rag` 实现懒加载单例（`get_rag_service()`）。
- **工具装饰器**: 工具函数使用 `@tool(description=...)` 装饰器注册，description 必须为中文，明确说明入参、出参和使用场景。
- **报告生成强约束**: 当用户请求生成个人报告时，Agent 必须严格遵循以下调用链：
  `get_user_id → get_current_month → fill_context_for_report → fetch_external_data`。
  未调用 `fill_context_for_report` 前，禁止调用 `fetch_external_data`。

## 测试策略

**当前项目暂未建立自动化测试套件。** 现有验证方式：
- 各模块的 `if __name__ == '__main__':` 块提供手动运行入口，可用于本地快速验证。
- 典型验证路径：
  1. 运行 `python -m rag.vector_store` 确认知识库加载无异常
  2. 运行 `python -m rag.rag_service` 验证 RAG 链路输出
  3. 运行 `python -m agent.react_agent` 验证 Agent 流式响应

建议后续补充 `pytest` 单元测试，重点覆盖：
- `file_handler.py` 的 MD5 和文件类型过滤
- `vector_store.py` 的文档加载与去重逻辑
- `agent_tools.py` 中 `fetch_external_data` 的数据解析

## 部署与安全注意事项

- **API Key 保护**: 所有密钥存储在 `.env` 中，该文件已被 `.gitignore` 排除。生产部署时请通过环境变量或密钥管理服务注入。
- **向量库**: `chroma_db/` 为本地持久化存储，生产环境若需多实例部署，应替换为远程 Chroma 服务或其他向量数据库。
- **外部数据**: `data/external/records.csv` 为模拟数据，生产环境应替换为真实的数据库或 API 调用。
- **天气与位置**: 当前 `get_weather` 和 `get_user_location` 返回模拟数据，生产环境应接入真实的气象 API 和定位服务。
- **日志文件**: `logs/` 目录下的日志按天生成，长期运行需配置日志轮转或定期清理。

## 快速参考命令

| 操作 | 命令 |
|------|------|
| 安装依赖 | `uv sync` |
| 加载知识库 | `python -m rag.vector_store` |
| 运行主程序 | `python main.py` |
| 测试 RAG | `python -m rag.rag_service` |
| 测试 Agent | `python -m agent.react_agent` |
