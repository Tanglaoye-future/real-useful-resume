// BOSS直聘超级隐形Hook - 终极隐藏方案
// 结合: 极简设计 + 内核级隐藏 + 完整反检测
console.log("[*] 启动超级隐形模式...");

var CONFIG = {
    initDelay: 10000,      // 初始延迟10秒
    hookDelay: 3000,       // Hook间隔3秒
    maxLog: 20             // 最大日志数
};

var logCount = 0;

// ========== 第一层: 内核级隐藏 (Native层) ==========

function hideNative() {
    try {
        // Hook getpid - 返回假PID
        var getpid = Module.findExportByName(null, "getpid");
        if (getpid) {
            Interceptor.attach(getpid, {
                onLeave: function(retval) {
                    retval.replace(0x7FFFFFFF);
                }
            });
        }
        
        // Hook getppid - 返回init进程
        var getppid = Module.findExportByName(null, "getppid");
        if (getppid) {
            Interceptor.attach(getppid, {
                onLeave: function(retval) {
                    retval.replace(1);
                }
            });
        }
        
        // Hook ptrace - 反调试
        var ptrace = Module.findExportByName(null, "ptrace");
        if (ptrace) {
            Interceptor.attach(ptrace, {
                onEnter: function(args) {
                    var request = args[0].toInt32();
                    if (request === 0) { // PTRACE_TRACEME
                        args[0] = ptr(0xFFFFFFFF);
                    }
                },
                onLeave: function(retval) {
                    retval.replace(0);
                }
            });
        }
        
        console.log("[✓] Native隐藏启用");
    } catch(e) {}
}

// ========== 第二层: Java层深度隐藏 ==========

function hideJava() {
    Java.perform(function() {
        try {
            // 1. 防止退出
            var System = Java.use("java.lang.System");
            System.exit.implementation = function() { 
                if (logCount < CONFIG.maxLog) {
                    console.log("[!] 阻止exit");
                    logCount++;
                }
            };
            
            var Runtime = Java.use("java.lang.Runtime");
            Runtime.halt.implementation = function() {
                if (logCount < CONFIG.maxLog) {
                    console.log("[!] 阻止halt");
                    logCount++;
                }
            };
            
            var Process = Java.use("android.os.Process");
            Process.killProcess.implementation = function() {
                if (logCount < CONFIG.maxLog) {
                    console.log("[!] 阻止kill");
                    logCount++;
                }
            };
            
            var Activity = Java.use("android.app.Activity");
            Activity.finish.overload().implementation = function() {
                if (logCount < CONFIG.maxLog) {
                    console.log("[!] 阻止finish");
                    logCount++;
                }
            };
            Activity.finishAffinity.implementation = function() {
                if (logCount < CONFIG.maxLog) {
                    console.log("[!] 阻止finishAffinity");
                    logCount++;
                }
            };
            
            console.log("[✓] 退出保护启用");
        } catch(e) {}
        
        try {
            // 2. 隐藏Frida/Xposed类
            var ClassLoader = Java.use("java.lang.ClassLoader");
            var loadClass = ClassLoader.loadClass.overload("java.lang.String", "boolean");
            
            loadClass.implementation = function(name, resolve) {
                var lower = name.toLowerCase();
                if (lower.indexOf("frida") !== -1 || 
                    lower.indexOf("xposed") !== -1 ||
                    lower.indexOf("substrate") !== -1 ||
                    lower.indexOf("edxp") !== -1) {
                    if (logCount < CONFIG.maxLog) {
                        console.log("[!!!] 隐藏: " + name);
                        logCount++;
                    }
                    throw Java.use("java.lang.ClassNotFoundException").$new(name);
                }
                return loadClass.call(this, name, resolve);
            };
            
            // 3. 隐藏堆栈中的Hook痕迹
            var StackTraceElement = Java.use("java.lang.StackTraceElement");
            var getClassName = StackTraceElement.getClassName;
            
            getClassName.implementation = function() {
                var name = getClassName.call(this);
                if (name.indexOf("frida") !== -1 || name.indexOf("Hook") !== -1) {
                    return "android.app.Activity";
                }
                return name;
            };
            
            console.log("[✓] Java隐藏启用");
        } catch(e) {}
    });
}

// ========== 第三层: API捕获 ==========

function hookAPI() {
    Java.perform(function() {
        try {
            // Hook URL - 捕获API请求
            var URL = Java.use("java.net.URL");
            var toString = URL.toString;
            
            toString.implementation = function() {
                var url = toString.call(this);
                
                // 只捕获关键API
                if (url.indexOf("zhipin.com") !== -1) {
                    if (url.indexOf("smsCode") !== -1 || 
                        url.indexOf("codeLogin") !== -1 ||
                        url.indexOf("mobileSdk4Ali") !== -1) {
                        
                        console.log("\n[API] " + url.substring(0, 600));
                        
                        // 提取sp参数
                        if (url.indexOf("?sp=") !== -1) {
                            var sp = url.split("?sp=")[1];
                            if (sp.indexOf("&") !== -1) {
                                sp = sp.split("&")[0];
                            }
                            console.log("[SP] " + sp.substring(0, 150));
                        }
                    }
                }
                
                return url;
            };
            
            console.log("[✓] API捕获启用");
        } catch(e) {}
        
        try {
            // Hook HttpURLConnection - 备用捕获
            var HUC = Java.use("java.net.HttpURLConnection");
            var connect = HUC.connect;
            
            connect.implementation = function() {
                var url = this.getURL().toString();
                
                if (url.indexOf("zhipin.com") !== -1 && 
                    (url.indexOf("smsCode") !== -1 || url.indexOf("codeLogin") !== -1)) {
                    console.log("\n[HTTP] " + url.substring(0, 400));
                }
                
                return connect.call(this);
            };
        } catch(e) {}
    });
}

// ========== 第四层: 系统调用欺骗 ==========

function spoofSystem() {
    try {
        // Hook open - 隐藏文件访问
        var open = Module.findExportByName(null, "open");
        if (open) {
            Interceptor.attach(open, {
                onEnter: function(args) {
                    try {
                        var path = Memory.readUtf8String(args[0]);
                        if (path.indexOf("frida") !== -1 || 
                            path.indexOf("/data/local/tmp/re.frida") !== -1 ||
                            path.indexOf("/proc/self/maps") !== -1) {
                            if (logCount < CONFIG.maxLog) {
                                console.log("[*] 隐藏文件: " + path);
                                logCount++;
                            }
                            args[0] = Memory.allocUtf8String("/dev/null");
                        }
                    } catch(e) {}
                }
            });
        }
        
        console.log("[✓] 系统调用欺骗启用");
    } catch(e) {}
}

// ========== 启动序列 ==========

setTimeout(function() {
    console.log("[*] 第一阶段: Native隐藏");
    hideNative();
    spoofSystem();
}, CONFIG.initDelay);

setTimeout(function() {
    console.log("[*] 第二阶段: Java隐藏");
    hideJava();
}, CONFIG.initDelay + CONFIG.hookDelay);

setTimeout(function() {
    console.log("[*] 第三阶段: API捕获");
    hookAPI();
    console.log("[*] 超级隐形模式就绪!");
}, CONFIG.initDelay + CONFIG.hookDelay * 2);

// 心跳 - 证明还在运行
setInterval(function() {
    console.log("[*] 运行中...");
}, 30000);

console.log("[*] 等待 " + (CONFIG.initDelay/1000) + " 秒后启动...");
