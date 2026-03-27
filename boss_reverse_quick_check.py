#!/usr/bin/env python3
"""
Boss直聘逆向快速验证脚本
4-6小时完成可行性评估
"""

import requests
import re
import os
import sys
from pathlib import Path

class BossReverseChecker:
    """Boss直聘逆向可行性检查器"""
    
    def __init__(self):
        self.report = []
        self.score = 0
        self.max_score = 100
        
    def log(self, step, result, detail="", score=0):
        """记录检查结果"""
        self.report.append({
            'step': step,
            'result': result,
            'detail': detail,
            'score': score
        })
        self.score += score
        print(f"\n[{result}] {step}")
        if detail:
            print(f"  └─ {detail}")
        
    # ==================== 步骤1：检查APK下载 ====================
    def check_apk_download(self):
        """检查是否能下载Boss直聘APK"""
        print("\n" + "="*60)
        print("步骤1: 检查APK下载可行性")
        print("="*60)
        
        # 尝试从apkpure下载
        urls = [
            "https://apkpure.com/cn/boss%E7%9B%B4%E8%81%98/com.hpbr.bosszhipin",
            "https://www.wandoujia.com/apps/com.hpbr.bosszhipin",
        ]
        
        for url in urls:
            try:
                response = requests.get(url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    self.log(
                        "APK下载源检查",
                        "✅ 通过",
                        f"可从 {url.split('/')[2]} 获取APK",
                        20
                    )
                    return True
            except Exception as e:
                continue
        
        self.log(
            "APK下载源检查",
            "⚠️ 警告",
            "需要手动下载APK文件",
            10
        )
        return False
    
    # ==================== 步骤2：检查反编译工具 ====================
    def check_decompile_tools(self):
        """检查反编译工具是否可用"""
        print("\n" + "="*60)
        print("步骤2: 检查反编译工具")
        print("="*60)
        
        tools = {
            'jadx': 'JADX反编译工具',
            'apktool': 'Apktool工具',
        }
        
        available_tools = []
        for cmd, name in tools.items():
            result = os.system(f"where {cmd} >nul 2>&1")
            if result == 0:
                available_tools.append(name)
        
        if available_tools:
            self.log(
                "反编译工具检查",
                "✅ 通过",
                f"已安装: {', '.join(available_tools)}",
                20
            )
            return True
        else:
            self.log(
                "反编译工具检查",
                "⚠️ 警告",
                "需要安装JADX: https://github.com/skylot/jadx",
                10
            )
            return False
    
    # ==================== 步骤3：分析APK（如果存在） ====================
    def analyze_apk_if_exists(self):
        """分析本地APK文件"""
        print("\n" + "="*60)
        print("步骤3: 分析APK代码结构")
        print("="*60)
        
        # 查找本地APK
        apk_paths = [
            "boss.apk",
            "com.hpbr.bosszhipin.apk",
            "downloads/boss.apk",
        ]
        
        apk_file = None
        for path in apk_paths:
            if os.path.exists(path):
                apk_file = path
                break
        
        if not apk_file:
            self.log(
                "APK文件检查",
                "⚠️ 跳过",
                "未找到APK文件，请手动放置到项目目录",
                0
            )
            return None
        
        print(f"找到APK: {apk_file}")
        
        # 尝试反编译
        output_dir = "boss_source"
        if os.system(f"jadx -d {output_dir} {apk_file} >nul 2>&1") == 0:
            print(f"反编译成功，输出目录: {output_dir}")
            return self._analyze_source_code(output_dir)
        else:
            self.log(
                "APK反编译",
                "❌ 失败",
                "反编译过程出错，可能需要手动操作",
                0
            )
            return None
    
    def _analyze_source_code(self, source_dir):
        """分析源代码"""
        print(f"\n分析源代码目录: {source_dir}")
        
        # 搜索关键文件
        keywords = {
            'sign': '签名相关',
            'stoken': 'Boss Token',
            'encrypt': '加密算法',
            'md5': 'MD5哈希',
            'sha1': 'SHA1哈希',
            'sha256': 'SHA256哈希',
            'Interceptor': 'OKHttp拦截器',
            'getHeaders': '请求头构造',
        }
        
        findings = {}
        
        # 遍历Java文件
        java_files = list(Path(source_dir).rglob("*.java"))
        print(f"找到 {len(java_files)} 个Java文件")
        
        # 只分析前100个文件（加快速度）
        for java_file in java_files[:100]:
            try:
                with open(java_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    for keyword, desc in keywords.items():
                        if keyword in content.lower():
                            if desc not in findings:
                                findings[desc] = 0
                            findings[desc] += 1
            except:
                continue
        
        # 评估结果
        if findings:
            detail = " | ".join([f"{k}: {v}处" for k, v in findings.items()])
            self.log(
                "代码分析",
                "✅ 通过",
                f"发现关键代码 - {detail}",
                30
            )
            
            # 评估复杂度
            if '加密算法' in findings or findings.get('签名相关', 0) > 10:
                print("\n⚠️ 警告: 发现加密/签名代码较多，逆向难度较高")
            
            return findings
        else:
            self.log(
                "代码分析",
                "⚠️ 警告",
                "未找到明显的签名/加密代码，可能混淆严重",
                10
            )
            return {}
    
    # ==================== 步骤4：网络环境检查 ====================
    def check_network_environment(self):
        """检查网络环境"""
        print("\n" + "="*60)
        print("步骤4: 检查网络环境")
        print("="*60)
        
        # 检查代理工具
        proxy_tools = ['charles', 'fiddler', 'proxifier']
        has_proxy = any(os.system(f"where {tool} >nul 2>&1") == 0 for tool in proxy_tools)
        
        # 检查adb
        has_adb = os.system("where adb >nul 2>&1") == 0
        
        if has_proxy and has_adb:
            self.log(
                "网络环境检查",
                "✅ 通过",
                "已安装抓包工具和ADB",
                15
            )
        elif has_adb:
            self.log(
                "网络环境检查",
                "⚠️ 部分",
                "有ADB但缺少抓包工具，建议安装Charles",
                10
            )
        else:
            self.log(
                "网络环境检查",
                "⚠️ 警告",
                "需要安装ADB和抓包工具",
                5
            )
        
        return has_adb
    
    # ==================== 生成报告 ====================
    def generate_report(self):
        """生成可行性报告"""
        print("\n" + "="*60)
        print("快速验证完成 - 可行性评估报告")
        print("="*60)
        
        print(f"\n总分: {self.score}/{self.max_score}")
        
        # 评估等级
        if self.score >= 80:
            level = "✅ 高可行性"
            suggestion = "建议进行逆向，成功率较高"
        elif self.score >= 60:
            level = "🟡 中等可行性"
            suggestion = "可以尝试，但需要解决一些问题"
        elif self.score >= 40:
            level = "🟠 低可行性"
            suggestion = "难度较大，建议先完善环境"
        else:
            level = "🔴 不可行"
            suggestion = "当前环境不支持，建议采用其他方案"
        
        print(f"\n评估等级: {level}")
        print(f"建议: {suggestion}")
        
        # 详细报告
        print("\n详细检查项:")
        print("-" * 60)
        for item in self.report:
            status = "✅" if item['score'] >= 15 else "⚠️" if item['score'] > 0 else "❌"
            print(f"{status} {item['step']}: {item['result']}")
            if item['detail']:
                print(f"   {item['detail']}")
        
        # 下一步建议
        print("\n" + "="*60)
        print("下一步建议")
        print("="*60)
        
        if self.score >= 80:
            print("""
1. 下载Boss直聘APK
2. 使用JADX反编译
3. 搜索签名相关代码
4. 使用Frida Hook验证
5. 实现Python调用
            """)
        elif self.score >= 60:
            print("""
1. 安装缺失的工具（JADX/Charles）
2. 配置安卓模拟器
3. 下载APK并反编译
4. 分析代码复杂度后再决定
            """)
        else:
            print("""
建议采用替代方案：
1. 使用猎聘爬虫（已成功）
2. 使用前程无忧爬虫
3. Boss直聘使用种子数据
4. 后续再考虑逆向
            """)
        
        return self.score, level


def main():
    """主函数"""
    print("="*60)
    print("Boss直聘逆向快速验证工具")
    print("预计时间: 5-10分钟")
    print("="*60)
    
    checker = BossReverseChecker()
    
    # 执行检查
    checker.check_apk_download()
    checker.check_decompile_tools()
    checker.analyze_apk_if_exists()
    checker.check_network_environment()
    
    # 生成报告
    score, level = checker.generate_report()
    
    # 保存报告
    report_file = "boss_reverse_feasibility_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"Boss直聘逆向可行性评估报告\n")
        f.write(f"时间: {__import__('datetime').datetime.now()}\n")
        f.write(f"总分: {score}/100\n")
        f.write(f"评估: {level}\n\n")
        f.write("详细结果:\n")
        for item in checker.report:
            f.write(f"- {item['step']}: {item['result']}\n")
            if item['detail']:
                f.write(f"  {item['detail']}\n")
    
    print(f"\n报告已保存: {report_file}")
    
    return score


if __name__ == '__main__':
    score = main()
    sys.exit(0 if score >= 60 else 1)
