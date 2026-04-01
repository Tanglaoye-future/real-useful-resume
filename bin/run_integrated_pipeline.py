#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ResuMiner 整合流水线
双线程并行架构：官网CDP爬虫 + 第三方平台爬虫 + 简历匹配
"""

import os
import sys
import json
import time
import queue
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
import logging
log_dir = project_root / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f'integrated_pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    """爬取结果"""
    source: str  # 'official' 或 'third_party'
    jobs: List[Dict] = field(default_factory=list)
    success: bool = False
    message: str = ""
    crawl_time: float = 0.0


class OfficialCrawlerThread(threading.Thread):
    """官网CDP爬虫线程 - 爬取8大厂"""
    
    def __init__(self, result_queue: queue.Queue, companies: List[str] = None):
        super().__init__(name="OfficialCrawler")
        self.result_queue = result_queue
        self.companies = companies or ['tencent', 'meituan', 'alibaba', 'jd', 'kuaishou', 'bilibili', 'bytedance']
        self.daemon = True
        
    def run(self):
        """执行官网爬虫"""
        logger.info("="*80)
        logger.info("🚀 启动官网CDP爬虫线程")
        logger.info("="*80)
        
        start_time = time.time()
        all_jobs = []
        
        try:
            # 导入CDP爬虫
            sys.path.insert(0, str(project_root / 'crawlers' / 'official'))
            
            company_crawlers = {
                'tencent': 'cdp_tencent',
                'meituan': 'cdp_meituan',
                'alibaba': 'cdp_alibaba',
                'jd': 'cdp_jd',
                'kuaishou': 'cdp_kuaishou',
                'bilibili': 'cdp_bilibili',
                'bytedance': 'cdp_bytedance',
            }
            
            for company in self.companies:
                if company not in company_crawlers:
                    logger.warning(f"⚠️ 未知公司: {company}")
                    continue
                
                try:
                    logger.info(f"\n📍 开始爬取: {company}")
                    
                    # 动态导入爬虫模块
                    module_name = company_crawlers[company]
                    module_path = project_root / 'crawlers' / 'official' / f'{module_name}.py'
                    
                    if not module_path.exists():
                        logger.warning(f"⚠️ 爬虫文件不存在: {module_path}")
                        continue
                    
                    # 使用subprocess运行爬虫
                    import subprocess
                    result = subprocess.run(
                        [sys.executable, str(module_path)],
                        capture_output=True,
                        text=True,
                        timeout=300,
                        cwd=str(project_root)
                    )
                    
                    if result.returncode == 0:
                        logger.info(f"   ✅ {company} 爬取成功")
                        # 读取输出的CSV文件
                        output_file = project_root / 'data' / 'raw' / 'official' / f'{company}_jobs.json'
                        if output_file.exists():
                            with open(output_file, 'r', encoding='utf-8') as f:
                                jobs = json.load(f)
                                all_jobs.extend(jobs)
                                logger.info(f"   📊 获取 {len(jobs)} 条岗位")
                    else:
                        logger.error(f"   ❌ {company} 爬取失败: {result.stderr}")
                        
                except Exception as e:
                    logger.error(f"   ❌ {company} 异常: {e}")
                    continue
            
            crawl_time = time.time() - start_time
            
            result = CrawlResult(
                source='official',
                jobs=all_jobs,
                success=True,
                message=f"成功爬取 {len(self.companies)} 家公司，共 {len(all_jobs)} 条岗位",
                crawl_time=crawl_time
            )
            
        except Exception as e:
            logger.error(f"❌ 官网爬虫线程异常: {e}")
            result = CrawlResult(
                source='official',
                jobs=all_jobs,
                success=False,
                message=str(e),
                crawl_time=time.time() - start_time
            )
        
        self.result_queue.put(result)
        logger.info(f"\n✅ 官网爬虫线程完成: {len(all_jobs)} 条岗位，耗时 {result.crawl_time:.1f}s")


class ThirdPartyCrawlerThread(threading.Thread):
    """第三方平台爬虫线程 - 爬取51job和猎聘"""
    
    def __init__(self, result_queue: queue.Queue, platforms: List[str] = None):
        super().__init__(name="ThirdPartyCrawler")
        self.result_queue = result_queue
        self.platforms = platforms or ['job51', 'liepin']
        self.daemon = True
        
    def run(self):
        """执行第三方平台爬虫"""
        logger.info("="*80)
        logger.info("🚀 启动第三方平台爬虫线程")
        logger.info("="*80)
        
        start_time = time.time()
        all_jobs = []
        
        try:
            # 设置环境变量
            os.environ['JOB51_JOB_AREA'] = '020000'  # 上海
            os.environ['JOB51_CAMPUS_KEYWORDS'] = '实习,秋招'
            os.environ['JOB51_MAX_SAFETY_PAGES'] = '100'
            os.environ['JOB51_THROTTLE_MIN_SECONDS'] = '3'
            os.environ['JOB51_THROTTLE_MAX_SECONDS'] = '8'
            
            os.environ['LIEPIN_KEYWORD'] = '实习'
            os.environ['LIEPIN_CITY'] = '020'  # 上海
            os.environ['LIEPIN_MAX_PAGES'] = '100'
            os.environ['LIEPIN_THROTTLE_MIN'] = '5'
            os.environ['LIEPIN_THROTTLE_MAX'] = '10'
            
            for platform in self.platforms:
                try:
                    logger.info(f"\n📍 开始爬取: {platform}")
                    
                    if platform == 'job51':
                        jobs = self._crawl_job51()
                    elif platform == 'liepin':
                        jobs = self._crawl_liepin()
                    else:
                        logger.warning(f"⚠️ 未知平台: {platform}")
                        continue
                    
                    all_jobs.extend(jobs)
                    logger.info(f"   ✅ {platform} 完成: {len(jobs)} 条岗位")
                    
                except Exception as e:
                    logger.error(f"   ❌ {platform} 异常: {e}")
                    continue
            
            crawl_time = time.time() - start_time
            
            result = CrawlResult(
                source='third_party',
                jobs=all_jobs,
                success=True,
                message=f"成功爬取 {len(self.platforms)} 个平台，共 {len(all_jobs)} 条岗位",
                crawl_time=crawl_time
            )
            
        except Exception as e:
            logger.error(f"❌ 第三方平台爬虫线程异常: {e}")
            result = CrawlResult(
                source='third_party',
                jobs=all_jobs,
                success=False,
                message=str(e),
                crawl_time=time.time() - start_time
            )
        
        self.result_queue.put(result)
        logger.info(f"\n✅ 第三方平台爬虫线程完成: {len(all_jobs)} 条岗位，耗时 {result.crawl_time:.1f}s")
    
    def _crawl_job51(self) -> List[Dict]:
        """爬取前程无忧"""
        from core.crawler_engine.scheduler import RedisScheduler
        from core.crawler_engine.spiders.job51_v2 import Job51SpiderV2
        
        scheduler = RedisScheduler()
        spider = Job51SpiderV2(scheduler)
        jobs = spider.run()
        
        # 转换为统一格式
        unified_jobs = []
        for job in jobs:
            unified_jobs.append({
                'source_job_id': job.get('job_id', ''),
                'job_name': job.get('job_name', ''),
                'company_name': job.get('company_name', ''),
                'location': job.get('location', ''),
                'city': job.get('city', '上海'),
                'salary': job.get('salary', ''),
                'job_description': job.get('job_description', ''),
                'job_requirement': job.get('job_requirement', ''),
                'experience_requirement': job.get('experience', ''),
                'education_requirement': job.get('education', ''),
                'source': '51job',
                'platform': '51job',
                'crawled_at': datetime.now().isoformat(),
            })
        
        return unified_jobs
    
    def _crawl_liepin(self) -> List[Dict]:
        """爬取猎聘"""
        from core.crawler_engine.scheduler import RedisScheduler
        from core.crawler_engine.spiders.liepin_v6 import LiepinSpiderV6
        
        scheduler = RedisScheduler()
        spider = LiepinSpiderV6(scheduler)
        jobs = spider.run()
        
        # 转换为统一格式
        unified_jobs = []
        for job in jobs:
            unified_jobs.append({
                'source_job_id': job.get('job_id', ''),
                'job_name': job.get('job_name', ''),
                'company_name': job.get('company_name', ''),
                'location': job.get('location', ''),
                'city': job.get('city', '上海'),
                'salary': job.get('salary', ''),
                'job_description': job.get('job_description', ''),
                'job_requirement': job.get('job_requirement', ''),
                'experience_requirement': job.get('experience', ''),
                'education_requirement': job.get('education', ''),
                'source': 'liepin',
                'platform': 'liepin',
                'crawled_at': datetime.now().isoformat(),
            })
        
        return unified_jobs


def merge_and_deduplicate(jobs1: List[Dict], jobs2: List[Dict]) -> List[Dict]:
    """合并并去重"""
    logger.info("\n" + "="*80)
    logger.info("🔄 合并数据并去重")
    logger.info("="*80)
    
    all_jobs = jobs1 + jobs2
    logger.info(f"合并前: {len(jobs1)} + {len(jobs2)} = {len(all_jobs)} 条")
    
    # 去重：基于公司名+岗位名
    seen = set()
    unique_jobs = []
    
    for job in all_jobs:
        key = f"{job.get('company_name', '')}_{job.get('job_name', '')}"
        if key and key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    logger.info(f"去重后: {len(unique_jobs)} 条 (去重 {len(all_jobs) - len(unique_jobs)} 条)")
    
    return unique_jobs


def save_raw_data(jobs: List[Dict], output_dir: Path):
    """保存原始数据"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'integrated_crawled_jobs_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 原始数据已保存: {output_file}")
    return output_file


def run_resume_matching(jobs: List[Dict]) -> Dict[str, Any]:
    """执行简历匹配"""
    logger.info("\n" + "="*80)
    logger.info("🎯 开始简历匹配")
    logger.info("="*80)
    
    try:
        # 导入匹配系统
        from matcher.core.matcher import JobMatcher
        from matcher.strategy.strength_first_strategy import StrengthFirstStrategy
        
        # 加载简历
        resume_file = project_root / 'resumes' / 'my_resume.json'
        if not resume_file.exists():
            # 尝试其他路径
            resume_file = project_root / 'my_resume.json'
        
        if not resume_file.exists():
            logger.error(f"❌ 简历文件不存在")
            return {'success': False, 'message': '简历文件不存在'}
        
        with open(resume_file, 'r', encoding='utf-8') as f:
            resume = json.load(f)
        
        logger.info(f"📄 加载简历: {resume.get('basic_info', {}).get('name', '未知')}")
        
        # 创建匹配器
        config = {
            'model': {'embedding_model': 'paraphrase-multilingual-MiniLM-L12-v2'},
            'match': {
                'weights': {
                    'skill': 0.40,
                    'semantic': 0.35,
                    'experience': 0.25
                }
            }
        }
        
        matcher = JobMatcher(config)
        
        # 执行匹配
        result = matcher.match(resume, jobs, top_k=100)
        
        if result.get('success'):
            logger.info(f"✅ 匹配完成: {len(result.get('matched_jobs', []))} 个匹配岗位")
        else:
            logger.warning(f"⚠️ 匹配未完成: {result.get('message')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 匹配过程出错: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {'success': False, 'message': str(e)}


def generate_reports(result: Dict[str, Any]):
    """生成报告"""
    logger.info("\n" + "="*80)
    logger.info("📊 生成匹配报告")
    logger.info("="*80)
    
    try:
        from matcher.report.application_report import ApplicationReportGenerator
        
        generator = ApplicationReportGenerator()
        report_path = generator.generate_report(result)
        
        if report_path:
            logger.info(f"✅ 报告已生成: {report_path}")
        else:
            logger.warning("⚠️ 报告生成失败")
            
    except Exception as e:
        logger.error(f"❌ 生成报告出错: {e}")


def main():
    """主函数"""
    print("="*80)
    print("🚀 ResuMiner 整合流水线")
    print("双线程并行: 官网CDP爬虫 + 第三方平台爬虫 + 简历匹配")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建结果队列
    result_queue = queue.Queue()
    
    # 创建并启动线程
    official_thread = OfficialCrawlerThread(result_queue)
    third_party_thread = ThirdPartyCrawlerThread(result_queue)
    
    print("\n🚀 启动双线程爬虫...")
    official_thread.start()
    third_party_thread.start()
    
    # 等待两个线程完成
    print("\n⏳ 等待爬虫线程完成...")
    official_thread.join()
    third_party_thread.join()
    
    # 收集结果
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())
    
    # 分析结果
    official_jobs = []
    third_party_jobs = []
    
    for result in results:
        if result.source == 'official':
            official_jobs = result.jobs
            logger.info(f"\n📊 官网爬虫: {result.message}, 耗时 {result.crawl_time:.1f}s")
        else:
            third_party_jobs = result.jobs
            logger.info(f"📊 第三方平台: {result.message}, 耗时 {result.crawl_time:.1f}s")
    
    # 合并数据
    all_jobs = merge_and_deduplicate(official_jobs, third_party_jobs)
    
    if not all_jobs:
        print("\n❌ 没有采集到任何岗位数据")
        return 1
    
    # 保存原始数据
    raw_dir = project_root / 'data' / 'raw'
    save_raw_data(all_jobs, raw_dir)
    
    # 执行简历匹配
    result = run_resume_matching(all_jobs)
    
    # 生成报告
    if result.get('success'):
        generate_reports(result)
    
    print("\n" + "="*80)
    print("✅ 整合流水线执行完成！")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
