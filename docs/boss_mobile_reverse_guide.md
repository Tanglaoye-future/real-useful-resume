# Boss直聘移动端API逆向教程

## 一、准备工作

### 1.1 需要的工具

| 工具 | 用途 | 下载地址 |
|------|------|----------|
| Charles/Fiddler | HTTP/HTTPS抓包 | https://www.charlesproxy.com/ |
| Android Studio | 安卓模拟器/调试 | https://developer.android.com/studio |
| Frida | 动态插桩工具 | https://frida.re/ |
| JADX | APK反编译工具 | https://github.com/skylot/jadx |
| Postman | API测试 | https://www.postman.com/ |

### 1.2 环境配置

#### 1.2.1 安装Charles抓包工具

```bash
# 1. 下载并安装Charles
# 2. 安装SSL证书
# 3. 配置代理端口（默认8888）
```

#### 1.2.2 配置安卓模拟器

```bash
# 使用Android Studio创建模拟器
# 或者使用夜神/雷电模拟器

# 设置代理
设置 -> WLAN -> 长按网络 -> 修改网络 -> 代理 -> 手动
服务器: 电脑IP地址
端口: 8888
```

#### 1.2.3 安装Frida

```bash
# 电脑端安装
pip install frida frida-tools

# 安卓端安装frida-server
# 1. 下载对应架构的frida-server
# 2. push到手机 /data/local/tmp
# 3. chmod 755 frida-server
# 4. ./frida-server
```

---

## 二、抓包分析流程

### 2.1 配置HTTPS抓包

```bash
# 1. 在Charles中安装证书
Help -> SSL Proxying -> Install Charles Root Certificate

# 2. 配置SSL代理
Proxy -> SSL Proxying Settings -> Add
Host: *
Port: 443

# 3. 手机安装证书
# 访问 chls.pro/ssl 下载证书并安装
```

### 2.2 抓取Boss直聘APP请求

```bash
# 1. 打开Charles，开始抓包
# 2. 打开Boss直聘APP
# 3. 进行搜索操作（搜索"实习"，选择上海）
# 4. 观察Charles中的请求
```

### 2.3 关键API识别

通常Boss直聘的API域名：
- `www.zhipin.com` (Web)
- `api.zhipin.com` (移动端API)
- `m.zhipin.com` (M站)

关注以下接口：
```
/joblist.json      # 职位列表
/jobdetail.json    # 职位详情
/search.json       # 搜索接口
```

---

## 三、逆向分析步骤

### 3.1 获取APK文件

```bash
# 方法1: 从手机导出
adb shell pm path com.hpbr.bosszhipin
adb pull /data/app/xxx/base.apk boss.apk

# 方法2: 从应用商店下载APK
# 使用apkpure等网站下载
```

### 3.2 反编译APK

```bash
# 使用JADX反编译
jadx -d boss_source boss.apk

# 或者使用GUI版本
# 打开JADX GUI -> File -> Open -> 选择APK
```

### 3.3 搜索关键代码

在反编译后的代码中搜索：

```java
// 搜索关键词
"sign"          // 签名算法
"token"         // Token生成
"stoken"        // Boss的stoken
"encrypt"       // 加密逻辑
"md5"           // MD5相关
"sha"           // SHA相关
"getHeaders"    // 请求头构造
"Interceptor"   // OKHttp拦截器
```

### 3.4 使用Frida Hook关键函数

```javascript
// hook_sign.js
Java.perform(function() {
    // Hook StringBuilder（构造签名字符串）
    var StringBuilder = Java.use('java.lang.StringBuilder');
    StringBuilder.toString.implementation = function() {
        var result = this.toString();
        if (result.includes('sign') || result.includes('stoken')) {
            console.log('StringBuilder:', result);
        }
        return result;
    };
    
    // Hook MD5
    var MessageDigest = Java.use('java.security.MessageDigest');
    MessageDigest.getInstance.overload('java.lang.String').implementation = function(algorithm) {
        console.log('MD5 Algorithm:', algorithm);
        return this.getInstance(algorithm);
    };
    
    // Hook Base64
    var Base64 = Java.use('android.util.Base64');
    Base64.encodeToString.overload('[B', 'int').implementation = function(input, flags) {
        var result = this.encodeToString(input, flags);
        console.log('Base64 Input:', bytesToHex(input));
        console.log('Base64 Output:', result);
        return result;
    };
});

function bytesToHex(bytes) {
    var result = '';
    for (var i = 0; i < bytes.length; i++) {
        result += ('0' + (bytes[i] & 0xFF).toString(16)).slice(-2);
    }
    return result;
}
```

运行Frida脚本：
```bash
frida -U -f com.hpbr.bosszhipin -l hook_sign.js --no-pause
```

---

## 四、分析签名算法

### 4.1 常见签名方式

Boss直聘可能使用的签名方式：

1. **简单MD5**
```python
import hashlib
sign = hashlib.md5(f"{params}{secret_key}".encode()).hexdigest()
```

2. **带时间戳的签名**
```python
import time
import hashlib

timestamp = str(int(time.time()))
sign_str = f"param1=value1&param2=value2&timestamp={timestamp}&key={secret_key}"
sign = hashlib.md5(sign_str.encode()).hexdigest()
```

3. **HMAC-SHA256**
```python
import hmac
import hashlib

sign = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
```

### 4.2 从抓包数据反推

```python
# 假设抓包得到以下请求：
GET /api/joblist?city=101020100&query=实习&page=1&sign=abc123&timestamp=1234567890

# 分析步骤：
# 1. 记录多组请求参数和对应的sign
# 2. 尝试各种组合计算MD5
# 3. 对比结果找到正确的签名算法

import hashlib
import itertools

params = {
    'city': '101020100',
    'query': '实习',
    'page': '1',
    'timestamp': '1234567890'
}

# 尝试不同排序和组合
keys = list(params.keys())
for perm in itertools.permutations(keys):
    sign_str = '&'.join([f"{k}={params[k]}" for k in perm])
    md5_result = hashlib.md5(sign_str.encode()).hexdigest()
    print(f"{sign_str} -> {md5_result}")
```

---

## 五、Python实现

### 5.1 基础请求类

```python
import requests
import hashlib
import time
import json

class BossMobileAPI:
    def __init__(self):
        self.base_url = "https://api.zhipin.com"
        self.session = requests.Session()
        
        # 设置请求头（从抓包获取）
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G960U)',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/json',
            # ... 其他header从抓包获取
        }
    
    def generate_sign(self, params):
        """生成签名 - 需要根据逆向结果实现"""
        # 示例：简单MD5
        sorted_params = sorted(params.items())
        sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_str += '&key=your_secret_key'
        return hashlib.md5(sign_str.encode()).hexdigest()
    
    def search_jobs(self, keyword, city_code, page=1):
        """搜索职位"""
        params = {
            'query': keyword,
            'city': city_code,
            'page': page,
            'pageSize': 30,
            'timestamp': str(int(time.time()))
        }
        
        # 添加签名
        params['sign'] = self.generate_sign(params)
        
        url = f"{self.base_url}/joblist.json"
        response = self.session.get(url, params=params, headers=self.headers)
        
        return response.json()

# 使用示例
api = BossMobileAPI()
jobs = api.search_jobs('实习', '101020100')
print(jobs)
```

---

## 六、常见问题

### 6.1 SSL Pinning绕过

如果APP启用SSL Pinning，需要绕过：

```javascript
// ssl_bypass.js
Java.perform(function() {
    var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
    var SSLContext = Java.use('javax.net.ssl.SSLContext');
    
    // 创建空的TrustManager
    var TrustManager = Java.registerClass({
        name: 'com.example.TrustManager',
        implements: [X509TrustManager],
        methods: {
            checkClientTrusted: function() {},
            checkServerTrusted: function() {},
            getAcceptedIssuers: function() { return []; }
        }
    });
    
    // 替换SSLContext
    var TrustManagers = [TrustManager.$new()];
    var SSLContext_init = SSLContext.init.overload(
        '[Ljavax.net.ssl.KeyManager;', 
        '[Ljavax.net.ssl.TrustManager;', 
        'java.security.SecureRandom'
    );
    SSLContext_init.implementation = function(keyManager, trustManager, secureRandom) {
        SSLContext_init.call(this, keyManager, TrustManagers, secureRandom);
    };
});
```

### 6.2 设备指纹绕过

```javascript
// 修改设备信息
Java.perform(function() {
    var Build = Java.use('android.os.Build');
    Build.FINGERPRINT.value = 'google/sdk_gphone_x86/generic_x86:10/QPP6.190730.005.B1/5775370:userdebug/dev-keys';
    Build.MANUFACTURER.value = 'Google';
    Build.MODEL.value = 'Pixel 3';
});
```

---

## 七、下一步操作

请按以下步骤进行：

1. **安装Charles并配置抓包环境**
2. **下载Boss直聘APP并安装到模拟器**
3. **配置模拟器代理，开始抓包**
4. **在APP中搜索职位，观察API请求**
5. **导出APK，使用JADX反编译**
6. **搜索签名相关代码**
7. **使用Frida Hook验证签名算法**
8. **用Python实现签名逻辑**

需要我详细讲解其中某个步骤吗？
