#!/usr/bin/env python3
"""
BOSS 直聘移动端 API 爬虫
基于逆向工程实现的签名算法
"""

import requests
import time
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# 导入签名模块（步骤5实现）
try:
    from crypto_reversed.boss_mobile_signer import BossMobileSigner
except ImportError:
    BossMobileSigner = None
    print("警告: 签名模块未找到，请完成步骤5")

logger = logging.getLogger(__name__)


@dataclass
class JobItem:
    """职位信息数据类"""
    job_id: str
    title: str
    company: str
    salary: str
    location: str
    experience: str
    education: str
    description: str = ""
    

class BossMobileCrawler:
    """
    BOSS 直聘移动端爬虫
    
    基于逆向工程实现的移动端 API 调用
    """
    
    # 移动端 API 端点（根据抓包结果填写）
    BASE_URL = "https://api.zhipin.com"  # TODO: 确认实际域名
    
    ENDPOINTS = {
        "search": "/search/joblist",      # TODO: 确认实际路径
        "detail": "/job/detail",          # TODO: 确认实际路径
        "suggest": "/search/suggest",     # TODO: 确认实际路径
    }
    
    def __init__(self, 
                 app_key: str = "",
                 app_secret: str = "",
                 token: str = "",
                 proxy: Optional[str] = None):
        """
        初始化爬虫
        
        Args:
            app_key: APP 密钥
            app_secret: APP 密钥
            token: 用户登录 token（需要抓包获取）
            proxy: 代理地址
        """
        self.signer = BossMobileSigner(app_key, app_secret) if BossMobileSigner else None
        self.token = token
        self.proxy = {"https": proxy} if proxy else None
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "BossZhipin/11.000 (iPhone; iOS 16.0; Scale/3.00)",  # TODO: 更新
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9",
        })
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict:
        """
        发送带签名的请求
        
        Args:
            endpoint: API 端点
            params: 请求参数
            
        Returns:
            响应数据
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        # 生成签名
        if self.signer:
            timestamp = int(time.time() * 1000)
            sign = self.signer.generate_sign(params, timestamp)
            params["sign"] = sign
            params["timestamp"] = timestamp
        
        # 添加请求头
        headers = {}
        if self.signer:
            headers.update(self.signer.get_headers(self.token))
        
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                proxies=self.proxy,
                timeout=30
            )
            
            logger.info(f"请求: {url}, 状态: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"请求失败: {response.status_code}, {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"请求异常: {e}")
            return {}
    
    def search_jobs(self, 
                    keyword: str = "实习",
                    city: str = "101020100",
                    page: int = 1,
                    page_size: int = 20) -> List[JobItem]:
        """
        搜索职位
        
        Args:
            keyword: 搜索关键词
            city: 城市代码
            page: 页码
            page_size: 每页数量
            
        Returns:
            职位列表
        """
        params = {
            "query": keyword,
            "city": city,
            "page": page,
            "pageSize": page_size,
            # TODO: 添加其他必要参数
        }
        
        data = self._make_request(self.ENDPOINTS["search"], params)
        
        # TODO: 根据实际响应格式解析
        jobs = []
        if data and "data" in data:
            for item in data["data"].get("list", []):
                job = JobItem(
                    job_id=item.get("jobId", ""),
                    title=item.get("jobName", ""),
                    company=item.get("companyName", ""),
                    salary=item.get("salaryDesc", ""),
                    location=item.get("locationName", ""),
                    experience=item.get("experienceName", ""),
                    education=item.get("degreeName", ""),
                )
                jobs.append(job)
        
        return jobs
    
    def get_job_detail(self, job_id: str) -> Optional[JobItem]:
        """
        获取职位详情
        
        Args:
            job_id: 职位ID
            
        Returns:
            职位详情
        """
        params = {
            "jobId": job_id,
            # TODO: 添加其他必要参数
        }
        
        data = self._make_request(self.ENDPOINTS["detail"], params)
        
        # TODO: 根据实际响应格式解析
        if data and "data" in data:
            item = data["data"]
            return JobItem(
                job_id=item.get("jobId", ""),
                title=item.get("jobName", ""),
                company=item.get("companyName", ""),
                salary=item.get("salaryDesc", ""),
                location=item.get("locationName", ""),
                experience=item.get("experienceName", ""),
                education=item.get("degreeName", ""),
                description=item.get("description", ""),
            )
        
        return None
    
    def crawl_all(self, 
                  keywords: List[str] = None,
                  max_pages: int = 10) -> List[JobItem]:
        """
        全量爬取
        
        Args:
            keywords: 关键词列表
            max_pages: 每个关键词最大页数
            
        Returns:
            所有职位列表
        """
        if keywords is None:
            keywords = ["实习", "日常实习", "暑期实习"]
        
        all_jobs = []
        
        for keyword in keywords:
            logger.info(f"开始爬取关键词: {keyword}")
            
            for page in range(1, max_pages + 1):
                jobs = self.search_jobs(keyword=keyword, page=page)
                
                if not jobs:
                    logger.info(f"关键词 {keyword} 第 {page} 页无数据，停止")
                    break
                
                all_jobs.extend(jobs)
                logger.info(f"关键词 {keyword} 第 {page} 页: {len(jobs)} 条")
                
                # 添加延迟，避免被封
                time.sleep(2)
        
        logger.info(f"总计爬取: {len(all_jobs)} 条")
        return all_jobs


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # TODO: 填写实际的密钥和 token
    crawler = BossMobileCrawler(
        app_key="your_app_key",
        app_secret="your_app_secret",
        token="your_token",
        proxy="http://127.0.0.1:7890"  # 可选
    )
    
    # 搜索职位
    jobs = crawler.search_jobs(keyword="实习", page=1)
    print(f"找到 {len(jobs)} 个职位")
    
    for job in jobs[:5]:
        print(f"- {job.title} | {job.company} | {job.salary}")
