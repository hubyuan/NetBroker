# NetBroker v2.0
> 📈 反脆弱结构洞套利与增信引擎 (Anti-fragile Structural Hole Arbitrage Engine)

NetBroker 是一个针对跨域信息套利打造的、基于高并发异步架构（`asyncio` + 全局令牌桶限流）的事件驱动型守护引擎。

它能够通过持续监听外网的单焦点或分布式源头（如 arXiv 论文流、GitHub、Reddit 等），将数据汇入后台网络拓扑图中识别具有高信息套利价值的“结构洞”实体，最后经由轻量光速大语言模型（Gemini 3.1 Flash Lite API）转化为具有商业包装或知识降维价值的端到端产物。

## 🌟 当前第一期内建链路示范
- **学术科研结构洞套利 (arXiv -> Obsidian Vault)**
  全自动监控 arXiv 库中最新的 CS.AI 类原版英文论文，通过 API 无缝摄取后送入引擎。网关利用 LLM 自动将其原汁原味的学术词汇降维并翻译为流利标准的中文高干简报、评判其复现难度与技术影响力，并最终自动化按天在您的 Obsidian 笔记本目录中建立带标签的优美 Markdown 原生笔记！

---

## 📦 环境配置与部署

1. **运行环境准备**
   推荐使用 Python 3.10+，执行以下命令初始化虚拟隔离环境（Windows）：
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **配置网关秘钥**
   根目录下已存在或请您自行拷贝 `.env.example` 为 `.env`：
   ```env
   # 必填，用于在 cognitive 层唤醒 Gemini 网关的结构化输出
   GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxx
   ```

3. **极速一键点火启动**
   ```powershell
   python main.py
   ```
   > 引擎将作为后台 Daemon（守护进程）不间断常驻运行！引擎默认使用 `logging.INFO` 防止刷屏。如果要观测内部分布式微服务的每一秒健康心跳或查看 AST 安全截断明细，可进入 `main.py` 修改为 `logging.DEBUG`。

---

## 🏗️ 核心管道架构 (5-Layer Pipeline)

1. **Sensory (摄取合规层)**: `aio_crawler.py` 基于 `aiohttp` 封装，并强制绑定底层 `AsyncTokenBucket` 防御 IP 黑名单封禁。
2. **Graph (图谱层)**: 基于 NetworkX 进行异步锁保护。维系实体数据的生命网络（计算 Burt 约束、执行 TTL 删除和 $v_{decay}$ 塌陷熔断）。
3. **Cognitive (认知决策层)**: `llm_gateway.py` 运用 JSON Schema Native 保证大模型 100% 吐出精准的 Pydantic 决策数据，抛弃了脆弱的正则截取。
4. **Engineering (工程增信层)**: `ast_scanner.py` 和 `native_runner.py`。在不使用 Docker 的情况下阻断原生系统命令渗透并使用系统进程运行 `pytest` 用例打分。
5. **Execution (执行终端层)**: 例如本期挂载的 `obsidian_writer.py`，负责打包跨边界输出、人类在环 (HITL) 阻断以及输出状态终结。

---

## 📖 核心业务扩展开发
代码由外到内严格遵循开闭原则。新增任何一端的上下游业务（例如自动把 GitHub 榜单变成 TikTok 短视频 30s 分镜脚本）只需照猫画虎继承对应模块接口！如果您想自己二创修改业务链路：

👉 **[强烈建议先阅读：《NetBroker 可拓展性与插件开发指南》](./可拓展性与插件开发指南.md)**
