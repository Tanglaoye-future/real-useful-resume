# BOSS 直聘移动端逆向工程分析报告

## 📋 执行摘要

- **APK 文件**: 125_4c16e20eae9276cf6c55e6a799bac12c.apk
- **文件大小**: 138.28 MB
- **分析时间**: 2026-03-27
- **DEX 文件数**: 9 个
- **总类数**: 20,000+

---

## 🔍 关键发现

### 1. 网络架构

**发现的关键网络类:**
- `com/hpbr/bosszhipin/net/request/*` - 请求封装
- `com/hpbr/bosszhipin/net/response/*` - 响应封装
- `com/hpbr/apm/common/net/*` - APM 网络监控
- `com/boss/sdk/hybridim/NetRequestManager` - IM 网络管理

**使用的网络库:**
- Retrofit2 (REST API 框架)
- OkHttp (HTTP 客户端)
- Apache HttpClient (遗留支持)

### 2. 加密相关

**发现的加密字符串:**
- `aesEncrypt` - AES 加密
- `RSA/ECB/PKCS1Padding` - RSA 加密
- `SHA1PRNG` - 随机数生成
- `getSignature` - 签名获取

**可能的加密位置:**
- `com/hpbr/bosszhipin/security/*` (推测)
- `com/hpbr/bosszhipin/crypto/*` (推测)
- Native 库中的加密函数

### 3. 核心 API 端点

**从类名推断的 API:**
- `/homepage/api/BossHPGetJobListFromGeekBatch` - 职位列表
- `/get/homepage/api/*` - 首页相关
- `/interviews/network/*` - 面试相关
- `/live/net/*` - 直播相关

### 4. 关键类列表

**高优先级分析目标:**
```
com/hpbr/bosszhipin/net/request/GeekF1FastStartChatRecommendJobListRequest
com/hpbr/bosszhipin/geekresume/net/response/ResumeParserResultListResponse
com/hpbr/bosszhipin/interviews/network/GeekInterviewGetResultStatusRequest
com/hpbr/apm/common/net/UrlConfig
com/boss/sdk/hybridim/NetRequestManager
```

---

## 🛠️ 逆向步骤

### 步骤 1: JADX 反编译 (等待中)

```bash
cd c:\Users\Lenovo\projects\jadx
.\gradlew dist

# 反编译
jadx -d decompiled apk/xxx.apk
```

### 步骤 2: 关键类分析

**优先分析的包:**
1. `com.hpbr.bosszhipin.net.*` - 网络层
2. `com.hpbr.bosszhipin.security.*` - 安全/加密
3. `com.hpbr.bosszhipin.api.*` - API 接口
4. `com.hpbr.apm.common.net.*` - 网络监控

### 步骤 3: Frida Hook 脚本

**目标方法:**
- 网络请求发送前的方法
- 签名生成方法
- 加密/解密方法

### 步骤 4: 抓包分析

**配置:**
- Charles/Fiddler 代理
- SSL Pinning 绕过
- 过滤域名: `*.zhipin.com`

---

## 📊 成功概率评估

| 阶段 | 难度 | 成功率 | 时间预估 |
|------|------|--------|----------|
| APK 分析 | 低 | 100% | ✅ 完成 |
| JADX 反编译 | 低 | 95% | ⏳ 等待中 |
| 加密算法定位 | 中 | 70% | 2-3 天 |
| 算法还原 | 高 | 50% | 3-5 天 |
| 爬虫实现 | 中 | 80% | 1-2 天 |

**总体成功率: 35-40%**

---

## 🚀 下一步行动

### 立即执行:
1. ✅ APK 结构分析 - 完成
2. ✅ 类名提取 - 完成
3. ⏳ 等待 JADX 构建完成
4. 🔄 反编译关键类

### 后续步骤:
5. 🔍 分析网络请求封装类
6. 🔍 定位签名/加密方法
7. 📝 编写 Frida Hook 脚本
8. 📱 配置抓包环境
9. 🧪 测试 API 调用
10. 🐍 实现 Python 爬虫

---

## 📁 生成的文件

```
apk_analysis/
├── apk_analysis.json          # APK 基础信息
├── detailed_analysis.md       # 详细分析报告
└── class_analysis.txt         # 完整类列表

mobile_reverse/
├── step1_download_apk.py      # APK 下载
├── step2_decompile.py         # JADX 反编译
├── step3_frida_setup.py       # Frida 配置
├── step4_capture_api.py       # 抓包分析
├── step5_crypto_reverse.py    # 加密逆向
├── step6_mobile_crawler.py    # 爬虫实现
├── apk_quick_analyze.py       # APK 快速分析
├── apk_deep_analysis.py       # APK 深度分析
└── find_crypto_classes.py     # 类名分析
```

---

## ⚠️ 风险提示

1. **法律风险**: 逆向工程可能违反服务条款
2. **技术风险**: APP 更新后加密算法可能变更
3. **维护成本**: 需要持续跟进 APP 版本更新
4. **封号风险**: 高频 API 调用可能触发风控

---

## 💡 建议

**替代方案:**
- 优先考虑 Web 端优化（成功率 60-70%）
- 移动端作为补充方案
- 关注官方开放平台 API

**如果坚持移动端:**
- 准备真机环境（模拟器检测严格）
- 使用高质量代理 IP
- 控制请求频率
- 准备多个账号轮换

---

*报告生成时间: 2026-03-27*
*分析师: AI Assistant*
