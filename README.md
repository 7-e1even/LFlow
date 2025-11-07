# LFlow - LLM驱动的流量安全分析工作流

<div align="center">

**基于大模型的Web流量威胁检测与漏洞识别引擎**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Status](https://img.shields.io/badge/status-beta-orange.svg)

</div>

---

## 📖 项目简介

LFlow 受微步 XGPT 启发，通过轻量级 RAG 技术，实现**无需微调**即可达到专业级精度的 Web 流量威胁检测。

### 核心价值

- 🎯 **零微调方案**：通过上下文优化让通用大模型具备专业安全分析能力
- 🚀 **实时漏洞情报**：基于 Nuclei POC 库的自动化检索匹配
- 🔍 **精准攻击研判**：五级分类（攻击成功/失败/攻击/未知/安全）
- 💡 **工程化落地**：可集成到 SIEM、WAF、AI SOC 等安全产品

---

## 🏗️ 技术架构

**工作流程**：HTTP日志输入 → URL提取 → POC检索（Meilisearch） → LLM分析（带/不带POC上下文） → 结构化输出

**核心组件**：
- **轻量级 RAG**：Meilisearch 混合搜索，支持 10,000+ POC 秒级检索
- **双路径分析**：匹配 POC 时提供漏洞上下文，未匹配时基于通用规则
- **多模型支持**：DeepSeek-Chat（主）、Kimi-K2-Instruct（备选）

---

## 🚀 快速开始

### 1. 部署 Meilisearch

```bash
docker run -d -p 7700:7700 \
  -e MEILI_MASTER_KEY=your_master_key \
  -v $(pwd)/meili_data:/meili_data \
  getmeili/meilisearch:v1.7
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置项目

编辑 `app/config.py` 配置 Meilisearch 连接信息。

### 4. 索引 POC 库

```bash
# 下载 Nuclei POC 模板
git clone https://github.com/projectdiscovery/nuclei-templates.git

# 索引所有 POC
python index_pocs.py
```

### 5. 导入 Dify 工作流

1. 登录 Dify 平台，创建新应用 → 选择「工作流」
2. 导入 `waftest.yml` 文件
3. 配置插件：Meilisearch、DeepSeek、SiliconFlow

### 6. 开始分析

输入 HTTP 请求包即可获得威胁分析结果。

---

## 📊 项目结构

```
LFlow/
├── app/
│   └── config.py           # 配置文件
├── index_pocs.py           # POC索引脚本
├── delete_index.py         # 索引管理工具
├── waftest.yml             # Dify工作流配置
├── requirements.txt        # 依赖包
└── README.md               # 项目文档
```

---

## 💡 使用场景

- **渗透测试**：批量分析 Burp Suite 日志
- **WAF 集成**：实时流量威胁检测与拦截
- **SOC 审计**：历史流量分析、威胁狩猎、溯源取证

---

## 📈 性能对比

| 测试场景 | 微步XGPT（微调） | LFlow（零微调） | 通用LLM |
|---------|-----------------|----------------|---------|
| 历史CVE | ✅ | ✅ | ✅ |
| 新漏洞 | ⚠️ 需更新 | ✅ | ⚠️ 不稳定 |
| 变种攻击 | ✅ | ✅ | ❌ |
| 更新成本 | 高（重训练） | 低（更新POC） | 无 |

---

## 🔧 高级配置

### 自定义提示词

编辑 `waftest.yml` 中的 LLM 节点，添加业务特定规则。

### 搜索精度调整

修改 Meilisearch 工具配置中的 `matchingStrategy`：
- `last`：提高召回率（可能误匹配）
- `all`：提高准确率（可能遗漏变种）
- `frequency`：平衡模式（推荐）

---

## 🛣️ 未来规划

- [ ] 漏洞情报自动更新流水线（GitHub RSS）
- [ ] 视觉压缩方案（DeepSeek-OCR）
- [ ] Multi-Agent 编排（威胁评估、修复建议、自动响应）
- [ ] 可视化分析面板
- [ ] 插件化架构

---

## 🤝 参考资料

- **灵感来源**：[微步情报社区 XGPT](https://x.threatbook.com/)
- **技术文章**：[从微步XGPT提示词到越权检测工作流](./文章)从%20微步XGPT%20提示词到越权检测工作流：LLM%20安全分析的工程化实践(流量分析篇).md)
- **POC 库**：[Nuclei Templates](https://github.com/projectdiscovery/nuclei-templates)
- **AI SOC 项目**：[DeepSOC](https://github.com/flagify-com/deepsoc) | [AI SOC Framework](https://github.com/FunnyWolf/ai-soc-framework)

---

## 📜 许可证

MIT 许可证开源

**⚠️ 免责声明**：本工具仅供安全研究和授权测试使用，请勿用于非法攻击。

---

<div align="center">

**⭐ 如果这个项目对你有帮助，欢迎 Star 支持！⭐**

Made with ❤️ by Security Researchers

</div>
