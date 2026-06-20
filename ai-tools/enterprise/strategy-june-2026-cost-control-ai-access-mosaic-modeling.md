---
title: "Strategy 2026 年 6 月更新：智能成本控制、AI 治理访问与更强大的 Mosaic 建模"
tags:
  - strategy
  - bi
  - enterprise
  - cost-control
  - mcp
  - mosaic-modeling
date: 2026-06-20
source: "https://www.strategy.com/pl/software/blog/june-2026-smarter-cost-control-governed-ai-access-richer-mosaic-modeling"
authors: "Strategy"
---

# Strategy 2026 年 6 月更新：智能成本控制、治理化 AI 访问与更强大的 Mosaic 建模

> **来源：** [Smarter Cost Control, Governed AI Access & Richer Mosaic Modeling](https://www.strategy.com/pl/software/blog/june-2026-smarter-cost-control-governed-ai-access-richer-mosaic-modeling)

---

## 概要

Strategy 2026 年 6 月版本聚焦三大方向：

1. **智能成本控制** — 跨 Snowflake 和 Databricks 的云成本可见性
2. **治理化的 AI 访问** — 可重复使用的 Agent 提示词、MCP 协议支持
3. **更强大的建模能力** — 灵活 Join、自定义日历、列命名控制

本次发布让通用语义层（Universal Semantic Layer）更加**可操作化**——不仅是定义可信度量的地方，更是团队看清成本、按真实业务方式建模、并安全地将其扩展至 AI 代理的地方。

---

## 一、成本控制、完整分析与治理化 AI 访问

### AI 驱动的跨平台成本智能（Sentinel Cost Intelligence）

云数据成本在不透明时容易失控。Sentinel Cost Intelligence 通过将平台开销归因到治理化的分析资产来解决这一问题——首先支持 Snowflake 和 Databricks。

**工作原理：**
- 管理员在 Workstation 中连接账单源
- Sentinel 应用查询标记（query tagging），在数据集级别归因开销
- 每日刷新成本洞察
- 专用成本洞察视图突出显示主要成本驱动因素，并给出 AI 驱动的优化建议

**建议类型：**
- 卸载非活跃数据集
- 调整刷新频率
- 在实时（live）和内存（in-memory）模式之间切换

**价值：** 更清晰的成本问责，更少的闲置或过度刷新资产，更自信的云成本优化决策。

---

### Mosaic 模型中的灵活 Join

标准 Join 在匹配事实或参考数据缺失时会排除记录。这可能导致分析结果不完整或误导——比如某个客户本季度没有订单，但不代表他不存在；某商店上月无交易，但仍在区域报告中。

现在建模者可以在 Mosaic Models 和 Mosaic Schema（原 Project Schema）中定义**属性级别的 Join 行为**，四种选项：

| 选项 | 说明 |
|------|------|
| 仅匹配记录 | 标准 inner join |
| 所有参考值 | 保留所有 lookup 端记录 |
| 所有事实/关系记录 | 保留所有事实端 |
| 所有记录（无论是否匹配） | full outer |

**价值：** 可以展示缺失活跃度的业务实体，更干净地处理含空值的数据集，围绕真实业务问题而非底层数据默认形态构建分析。

---

### 可复用的 Agent 上下文与提示词

新 Agent 不应每次都重新创建相同的列描述、指令和提示词模式。随着组织跨业务领域部署越来越多 Agent，复用问题变成了**治理和一致性**问题，而不仅仅是生产力问题。

**新功能：**
- 导入/导出列描述和自定义指令
- 提示词库（prompt library），最多 25 个可复用提示词
- 多个推理路径处理复杂查询后再响应

**价值：** 用户更快访问常见分析问题；跨 Agent 获得更一致的回答。

---

### MTDI 和 Intelligent Cubes 的 MCP 支持

如果没有治理化的语义访问，AI 代理会退回到原始模式（raw schema）——没有业务逻辑、访问控制和一致定义的数据。

Model Context Protocol (MCP) 今年早些时候已支持 Mosaic 模型语义。本次发布将支持范围扩展到：
- **MTDI（Multi-Table Data Import）**
- **Intelligent Cubes**（包括内存和实时分析资产）

**能力：**
- MCP 兼容的 AI 应用可发现可用项目和 Cube
- 检索语义描述
- 通过 Mosaic 端点运行语义查询
- 现有安全策略和审计控制自动生效

**价值：** 无需暴露原始模式，较少为每个 AI 工具做自定义集成工作。

---

## 二、Mosaic 建模生命周期更全面的控制

### Mosaic AI 自动建模的精细化控制

自动建模可以通过自动链接属性、合并匹配列和创建多格式属性来加速建模。但在受监管行业或严格治理要求下，意外的自动链接或合并可能引入风险。

**新增按模型级别的开关：**
- AI 命名
- 自动属性链接
- 自动列合并
- 自动创建多格式属性

原始列名可保留。AI 生成的建议仍可用于人工审查和选择性应用，而非自动应用。所有控制在文档中清晰记录并可审计。

---

### 支持灵活周和年的自定义日历

大多数分析平台假设 1 月到 12 月的日历。但许多企业并不用这个：
- 零售商用 **4-4-5 日历**
- 金融服务公司在 3 月/6 月/9 月/10 月关账
- 学术机构用 **9 月到 8 月**的周期

**新功能：** 团队可上传 CSV 定义日期的组织实际日历。Mosaic 验证结构，确保周期连续，自动创建熟悉的时间属性（ISO 风格显示格式）。基于这些模型的报表和仪表盘反映企业实际使用的日历。

---

### 通用语义层中的自定义列命名

当 MCP 客户端、Power BI 和 SQL 工具通过通用语义层连接 Mosaic 时，它们看到的列名决定了连接的有用程度。自动生成或源系统的列名会对 AI 代理和下游分析师造成困惑。

建模者现在可以在 Mosaic 模型级别定义列命名约定。属性格式和度量可以使用基础数据源的别名作为 USL 列名，当别名空白或不适合时提供智能 fallback。

**价值：** MCP 客户端和连接的 AI 工具看到的是业务意图的列名，而非源系统随意使用的名字。

---

## 三、简化 BI 管理、报表与交付

### 基于浏览器的 Workstation Web

对于混合操作系统团队、分布式的管理员或锁定的终端，基于浏览器的 Workstation 减少了核心管理和建模工作对 IT 的依赖。

- 从 Library 一键启动，无需单独安装
- 覆盖用户管理、Schema 设计、数据源配置和核心管理流程
- 减少桌面部署开销，避免版本冲突，通过平台升级获得最新功能

---

### 用 Python 现代化 Command Manager 脚本

许多管理员在 Command Manager 中积累了多年自动化脚本。转向 Python 和 Workstation 自动化时，手动重写耗时且有风险。

**Command Manager to mstrio-py Migration Assistant** 提供引导路径：
- 上传现有 Command Manager 脚本
- 生成可审查的 Python 工作流
- 逐步检查、细化和验证输出

**价值：** 更安全地过渡，保留现有自动化投资，降低运营风险，在 Command Manager 废弃前逐步现代化。

---

### 企业级租户隔离

对于 SaaS 提供商、OEM 场景或管理跨业务部门分析的企业，租户隔离通常意味着独立部署、重复管理和更高的运营开销。

现在**多个租户可以在单个 Strategy 环境中运行**，而内容、用户、项目和管理的设计上保持分离。

---

### Modern Grid 的财务行集

财务团队构建 P&L 报表、资产负债表和现金流报告时，通常需要在一个视图中组合多个行集，每个行集有不同的筛选器、聚合和格式。

**Financial Row Sets**：
- 在单个 Modern Grid 中堆叠多个行集
- 每个行集有自己的数据集、筛选器、页眉、小计和格式
- 共享相同的列，支持 drill-through，可导出为 PDF 或 Excel

---

### Strategy Web 的个人视图现可在 Library 中打开

用户在 Strategy Web 中保存的带有筛选器、提示词和布局变更的 Personal Views，现在可以从 Library 的订阅面板中直接打开，所有保存的偏好自动生效。

Personal Views 会自动删除，团队可按自己的节奏过渡，消除了 Web 和 Library 之间的切换摩擦。

---

### 向 Google Drive 投递订阅内容

使用 Google Workspace 的团队现在可以将计划的分析内容自动投递到 Google Drive：

- 管理员在 Workstation 中配置 Google Drive 为目标投递目的地
- 支持目标文件夹、收件人路由和输出格式（Google Sheets、Excel、CSV、HTML）
- 用户可从 Library 订阅任何仪表盘或报表
- 在现有 Strategy 访问控制内运行，不创建平台外的数据路径

**价值：** 移除了手动导出步骤，让可信分析保持在 Google Workspace 团队的工作流中。

---

## 总结

2026 年 6 月版本让 Strategy 的语义层更加可操作：
- 模型反映真实业务周期
- 云成本在模型级别可见
- 可信上下文被投递到 AI 代理、财务报表、Google Workspace 和基于浏览器的工作流

从成本治理到 AI 集成再到建模灵活性，这是一个全面的企业 BI 平台更新。

---

*处理时间：2026-06-20 | 来源：strategy.com*
