# 阶段 2：核心逆向分析与实现架构

根据 Prompt 的要求，我已经设计并初始化了 `crypto-engine` 项目结构，用于统一管理和对外提供 8 个目标招聘网站的加密/指纹/反爬破解服务。

## 1. 架构设计 (`crypto_engine/`)

`crypto_engine` 被设计为一个独立的参数生成引擎，可作为本地服务（如 Flask/FastAPI 或 gRPC）供主调度器调用，或直接作为 Python 模块引入。

目录结构：
- `platforms/`: 各平台的具体逆向实现模块。
- `ast_tools/`: 基于 Node.js 和 Babel 的抽象语法树（AST）解混淆工具链。
- `js/`: 存放从各平台提取并经过初步脱壳的核心 JavaScript 算法（如 BOSS 的 `__zp_stoken__` 算法）。

## 2. 核心模块实现说明

### 2.1 BOSS直聘 (`platforms/boss.py`)
- **核心逻辑**: 通过 `execjs` 或 `PyExecJS2` 挂载本地 V8 引擎，执行还原后的 `boss_stoken.js`，传入 `seed` 和时间戳等参数，动态计算 `__zp_stoken__`。
- **指纹防封**: 强制指定了 `get_ja3_fingerprint` 接口，要求下游使用 `curl_cffi` 并设置 `impersonate="chrome120"` 以绕过 TLS 校验。

### 2.2 实习僧 (`platforms/shixiseng.py`)
- **核心逻辑**: 针对字体反爬，实现了 `update_font_mapping` 和 `decrypt_text` 方法。
- **技术栈**: 预留了 `fontTools.ttLib` 接口，通过解析动态下载的 `.woff` 字体文件，提取 Glyph 映射，将返回的 JSON 数据中的乱码 Unicode（如 `&#xee4a;`）实时替换为正确的中文或数字。

### 2.3 拉勾网 (`platforms/lagou.py`)
- **核心逻辑**: 逆向了 `X-Anit-Forge-Code` 的生成逻辑。
- **实现**: 模拟了前端基于时间戳、特定盐值和请求类型拼接字符串后进行 MD5 / Hash 运算的过程，并封装了合法 Header 的生成方法，强调了 `Origin` 和 `Referer` 的严格匹配。

### 2.4 前程无忧 (51job) (`platforms/job51.py`)
- **核心逻辑**: 针对阿里云盾 `acw_sc__v2` 的挑战响应机制进行了封装。
- **实现**: 提供 `solve_acw_sc_v2` 方法，提取服务器首次返回的混淆 JS 和 `arg1`，通过内部 JS 引擎执行脱壳后的计算代码，直接生成合法的 Cookie 以完成无感重定向。预留了 `solve_slider` 接口对接 PaddleOCR 过滑块。

### 2.5 智联招聘 (`platforms/zhaopin.py`)
- 难点在于 `x-zp-token` 的生成。此部分与 BOSS 类似，需要在 `ast_tools` 中清洗 JS 后，封装对应的执行逻辑（尚未在本次写出具体脚本，模式同 BOSS）。

### 2.6 LinkedIn 领英中国 / 应届生求职网 / 猎聘
- 这些平台的逆向重点偏向于**网络协议层指纹 (JA3/JA4)** 和 **会话/IP 高频轮换策略**，而非单一的 JS 加密。因此这部分逻辑将主要实现在后续的 `fetcher` 和 `scheduler` 模块中（阶段 3）。

## 3. AST 脱壳工具 (`ast_tools/deobfuscator_template.js`)
提供了一个基于 `@babel/parser`、`@babel/traverse` 和 `@babel/generator` 的通用解混淆脚手架。
- 支持**字符串解密替换**：自动查找加密函数调用并还原真实字符串。
- 预留了**控制流平坦化还原**：针对嵌套 `switch-case` 和 `while` 循环的代码结构重组能力。
这些工具是解决 BOSS、智联和 51job 高度混淆 JS 的基础。

---
> 阶段 2 的核心骨架已经搭建完毕。接下来的工作（阶段 3）是将这些 `crypto-engine` 模块与 `curl_cffi` 请求器以及 Redis 调度器整合，形成完整的工业级爬虫系统。