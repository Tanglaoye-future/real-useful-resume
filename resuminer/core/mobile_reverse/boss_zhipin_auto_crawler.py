#!/usr/bin/env python3
"""
BOSS直聘自动登录爬虫
基于反编译代码分析实现
"""

import hashlib
import base64
import json
import time
import random
import string
import re
from urllib.parse import urlencode, quote, urlparse
from typing import Dict, Any, Optional, List, Tuple
import requests
from dataclasses import dataclass


@dataclass
class BossZhipinConfig:
    """BOSS直聘配置 - 基于反编译代码"""
    
    # API基础URL (来自 com.hpbr.bosszhipin.config.m)
    BASE_URL = "https://www.zhipin.com"
    API_BASE = "https://www.zhipin.com/api"
    PASSPORT_API = "https://www.zhipin.com/api/zppassport"
    
    # 登录相关端点 (来自 gr.a 类)
    ENDPOINTS = {
        # 登录相关
        'send_sms_code': '/phone/smsCode',  # 发送短信验证码
        'verify_code_login': '/user/codeLogin',  # 验证码登录
        'get_image_code': '/captcha/getType',  # 获取图形验证码
        'verify_image_code': '/phone/imgCode',  # 验证图形验证码
        
        # 用户信息
        'get_user_info': '/zpgeek/user/getUserInfo',
        'refresh_token': '/user/getTicket',
        
        # 职位相关
        'search_jobs': '/zpgeek/search/joblist',
        'job_detail': '/zpgeek/job/detail',
        'company_jobs': '/zpgeek/company/joblist',
        
        # 设备相关
        'report_device': '/device/report',
        'generate_device_id': '/zpCommon/app/generateDeviceId',
    }
    
    # APP配置
    APP_VERSION = "15.8.10"
    PLATFORM = "android"
    
    # 请求头
    DEFAULT_HEADERS = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }


class BossZhipinCrypto:
    """BOSS直聘加密工具 - 逆向实现"""
    
    @staticmethod
    def md5(text: str) -> str:
        """MD5加密"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sha1(text: str) -> str:
        """SHA1加密"""
        return hashlib.sha1(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def base64_encode(text: str) -> str:
        """Base64编码"""
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def base64_decode(text: str) -> str:
        """Base64解码"""
        return base64.b64decode(text).decode('utf-8')
    
    @staticmethod
    def generate_sign(params: Dict[str, Any], secret_key: str = "") -> str:
        """
        生成API请求签名
        根据反编译代码，签名算法：
        1. 参数按key排序
        2. key=value拼接，用&连接
        3. MD5加密
        """
        # 过滤空值并排序
        sorted_params = sorted([(k, v) for k, v in params.items() if v is not None])
        
        # 拼接字符串
        param_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # 添加密钥（如果有）
        if secret_key:
            param_str += f"&key={secret_key}"
        
        # MD5加密
        return BossZhipinCrypto.md5(param_str)
    
    @staticmethod
    def generate_timestamp() -> int:
        """生成毫秒时间戳"""
        return int(time.time() * 1000)
    
    @staticmethod
    def generate_nonce(length: int = 16) -> str:
        """生成随机字符串"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def encrypt_phone(phone: str) -> str:
        """
        手机号加密（根据反编译代码）
        使用Base64或其他算法
        """
        # 简单的Base64编码，实际可能更复杂
        return BossZhipinCrypto.base64_encode(phone)


class BossZhipinAutoCrawler:
    """BOSS直聘自动登录爬虫"""
    
    def __init__(self):
        self.config = BossZhipinConfig()
        self.crypto = BossZhipinCrypto()
        self.session = requests.Session()
        
        # 生成设备信息
        self.device_info = self._generate_device_info()
        
        # 设置请求头
        self.headers = self.config.DEFAULT_HEADERS.copy()
        self.headers['User-Agent'] = self._generate_user_agent()
        self.session.headers.update(self.headers)
        
        # 状态
        self.is_logged_in = False
        self.user_info = None
        self.token = None
        self.cookies = None
    
    def _generate_device_info(self) -> Dict[str, str]:
        """生成设备信息（模拟真实设备）"""
        android_versions = ['10', '11', '12', '13', '14']
        devices = [
            {'model': 'SM-G9910', 'brand': 'samsung'},
            {'model': 'MI 11', 'brand': 'xiaomi'},
            {'model': 'ONEPLUS A6010', 'brand': 'oneplus'},
            {'model': 'V2055A', 'brand': 'vivo'},
            {'model': 'PCRT00', 'brand': 'oppo'},
        ]
        
        device = random.choice(devices)
        
        return {
            'device_id': self._generate_device_id(),
            'model': device['model'],
            'brand': device['brand'],
            'android_version': random.choice(android_versions),
            'screen_width': '1080',
            'screen_height': '2400',
        }
    
    def _generate_device_id(self) -> str:
        """生成设备ID"""
        # 32位十六进制字符串
        return ''.join(random.choices('0123456789abcdef', k=32))
    
    def _generate_user_agent(self) -> str:
        """生成User-Agent"""
        android_ver = self.device_info['android_version']
        model = self.device_info['model']
        
        return (
            f"Mozilla/5.0 (Linux; Android {android_ver}; {model}) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/122.0.0.0 Mobile Safari/537.36"
        )
    
    def _build_params(self, extra_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """构建请求参数"""
        params = {
            'timestamp': self.crypto.generate_timestamp(),
            'nonce': self.crypto.generate_nonce(),
            'version': self.config.APP_VERSION,
            'platform': self.config.PLATFORM,
        }
        
        # 添加设备信息
        params.update({
            'deviceId': self.device_info['device_id'],
            'deviceModel': self.device_info['model'],
            'deviceBrand': self.device_info['brand'],
        })
        
        if extra_params:
            params.update(extra_params)
        
        # 生成签名
        params['sign'] = self.crypto.generate_sign(params)
        
        return params
    
    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None,
                      data: Optional[Dict[str, Any]] = None,
                      method: str = 'GET') -> Dict[str, Any]:
        """发送HTTP请求"""
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=30)
            else:
                response = self.session.post(url, data=data, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return {'error': str(e)}
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return {'error': 'JSON decode error'}
    
    def send_sms_code(self, phone: str, region_code: str = "+86") -> Dict[str, Any]:
        """
        发送短信验证码
        
        Args:
            phone: 手机号
            region_code: 区号，默认+86
            
        Returns:
            发送结果
        """
        url = f"{self.config.PASSPORT_API}{self.config.ENDPOINTS['send_sms_code']}"
        
        params = self._build_params({
            'phone': phone,
            'regionCode': region_code,
        })
        
        result = self._make_request(url, params=params, method='POST')
        
        if result.get('code') == 0:
            print(f"✅ 验证码已发送到 {phone}")
            return {'success': True, 'data': result}
        else:
            print(f"❌ 发送失败: {result.get('message', '未知错误')}")
            return {'success': False, 'error': result.get('message')}
    
    def login_with_code(self, phone: str, code: str, region_code: str = "+86") -> Dict[str, Any]:
        """
        使用验证码登录
        
        Args:
            phone: 手机号
            code: 短信验证码
            region_code: 区号
            
        Returns:
            登录结果
        """
        url = f"{self.config.PASSPORT_API}{self.config.ENDPOINTS['verify_code_login']}"
        
        params = self._build_params({
            'phone': phone,
            'code': code,
            'regionCode': region_code,
        })
        
        result = self._make_request(url, params=params, method='POST')
        
        if result.get('code') == 0:
            print("✅ 登录成功")
            self.is_logged_in = True
            
            # 保存用户信息
            if 'zpData' in result:
                self.user_info = result['zpData']
                
                # 提取token
                if 'token' in result['zpData']:
                    self.token = result['zpData']['token']
                
                # 保存cookies
                self.cookies = self.session.cookies.get_dict()
                
            return {'success': True, 'data': result}
        else:
            print(f"❌ 登录失败: {result.get('message', '未知错误')}")
            return {'success': False, 'error': result.get('message')}
    
    def login(self, phone: str, code: str) -> bool:
        """
        完整的登录流程
        
        Args:
            phone: 手机号
            code: 验证码
            
        Returns:
            是否登录成功
        """
        # 先发送验证码（如果需要）
        # send_result = self.send_sms_code(phone)
        # if not send_result['success']:
        #     return False
        
        # 使用验证码登录
        login_result = self.login_with_code(phone, code)
        return login_result['success']
    
    def search_jobs(self, query: str = "", city: str = "101010100",
                   page: int = 1, page_size: int = 30) -> Dict[str, Any]:
        """
        搜索职位（需要登录）
        
        Args:
            query: 搜索关键词
            city: 城市代码
            page: 页码
            page_size: 每页数量
            
        Returns:
            职位列表
        """
        if not self.is_logged_in:
            print("❌ 请先登录")
            return {'error': 'Not logged in'}
        
        url = f"{self.config.API_BASE}{self.config.ENDPOINTS['search_jobs']}.json"
        
        params = self._build_params({
            'query': query,
            'city': city,
            'page': page,
            'pageSize': page_size,
        })
        
        return self._make_request(url, params=params)
    
    def get_job_detail(self, job_id: str) -> Dict[str, Any]:
        """
        获取职位详情
        
        Args:
            job_id: 职位ID
            
        Returns:
            职位详情
        """
        if not self.is_logged_in:
            print("❌ 请先登录")
            return {'error': 'Not logged in'}
        
        url = f"{self.config.API_BASE}{self.config.ENDPOINTS['job_detail']}.json"
        
        params = self._build_params({
            'jobId': job_id,
        })
        
        return self._make_request(url, params=params)
    
    def save_session(self, filepath: str = "boss_session.json"):
        """保存登录会话"""
        session_data = {
            'user_info': self.user_info,
            'token': self.token,
            'cookies': self.cookies,
            'device_info': self.device_info,
            'timestamp': time.time(),
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 会话已保存到 {filepath}")
    
    def load_session(self, filepath: str = "boss_session.json") -> bool:
        """加载登录会话"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            self.user_info = session_data.get('user_info')
            self.token = session_data.get('token')
            self.cookies = session_data.get('cookies')
            self.device_info = session_data.get('device_info', self.device_info)
            
            # 恢复cookies
            if self.cookies:
                self.session.cookies.update(self.cookies)
            
            self.is_logged_in = True
            print(f"✅ 会话已从 {filepath} 加载")
            return True
            
        except FileNotFoundError:
            print(f"❌ 会话文件 {filepath} 不存在")
            return False
        except Exception as e:
            print(f"❌ 加载会话失败: {e}")
            return False


def interactive_login():
    """交互式登录"""
    print("=" * 60)
    print("BOSS直聘自动登录")
    print("=" * 60)
    
    crawler = BossZhipinAutoCrawler()
    
    # 输入手机号
    phone = input("\n请输入手机号: ").strip()
    
    if not phone:
        print("❌ 手机号不能为空")
        return
    
    # 发送验证码
    print(f"\n正在发送验证码到 {phone}...")
    send_result = crawler.send_sms_code(phone)
    
    if not send_result['success']:
        print("❌ 发送验证码失败")
        return
    
    # 输入验证码
    code = input("\n请输入收到的验证码: ").strip()
    
    if not code:
        print("❌ 验证码不能为空")
        return
    
    # 登录
    print("\n正在登录...")
    if crawler.login(phone, code):
        print("\n✅ 登录成功！")
        
        # 保存会话
        crawler.save_session()
        
        # 测试搜索
        print("\n测试搜索职位...")
        result = crawler.search_jobs(query="Python", page=1, page_size=5)
        
        if 'zpData' in result and 'jobList' in result['zpData']:
            jobs = result['zpData']['jobList']
            print(f"\n找到 {len(jobs)} 个职位:")
            for i, job in enumerate(jobs, 1):
                print(f"{i}. {job.get('jobName', 'N/A')} | "
                      f"{job.get('brandName', 'N/A')} | "
                      f"{job.get('salaryDesc', 'N/A')}")
        else:
            print("搜索失败:", result.get('message', '未知错误'))
    else:
        print("\n❌ 登录失败")


def demo():
    """演示（使用已保存的会话）"""
    print("=" * 60)
    print("BOSS直聘爬虫演示")
    print("=" * 60)
    
    crawler = BossZhipinAutoCrawler()
    
    # 尝试加载已有会话
    if crawler.load_session():
        print("\n使用已保存的会话")
        
        # 搜索职位
        print("\n搜索Python职位...")
        result = crawler.search_jobs(query="Python", city="101010100", page=1, page_size=10)
        
        if 'zpData' in result:
            jobs = result['zpData'].get('jobList', [])
            print(f"\n✅ 找到 {len(jobs)} 个职位")
            
            for job in jobs[:5]:
                print(f"\n  📌 {job.get('jobName', 'N/A')}")
                print(f"     公司: {job.get('brandName', 'N/A')}")
                print(f"     薪资: {job.get('salaryDesc', 'N/A')}")
                print(f"     地点: {job.get('cityName', 'N/A')} {job.get('areaDistrict', 'N/A')}")
        else:
            print("❌ 搜索失败:", result.get('message', '未知错误'))
            print("响应:", result)
    else:
        print("\n没有已保存的会话，请先运行交互式登录")
        print("命令: python boss_zhipin_auto_crawler.py --login")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--login":
        interactive_login()
    else:
        demo()
