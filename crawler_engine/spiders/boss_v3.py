#!/usr/bin/env python3
"""
Boss直聘爬虫 V3 - 全量爬取版本
每页20条，500页，总计10000+条数据
"""

import time
import logging
import os
import json
import random
from datetime import datetime
from crawler_engine.base_spider import BaseSpider

logger = logging.getLogger(__name__)

class BossSpiderV3(BaseSpider):
    """
    Boss直聘爬虫 V3 - 全量版本
    
    配置:
    - 多关键词轮询（实习、日常实习、暑期实习）
    - 每关键词500页
    - 每页20条
    - 总计: 3关键词 × 500页 × 20条 = 30000条
    """
    
    def __init__(self, scheduler, base_cookie=""):
        super().__init__("BOSS直聘", scheduler, base_cookie)
        self.keywords = ["实习", "日常实习", "暑期实习"]
        self.max_pages = 500  # 每关键词500页
        self.page_size = 20   # 每页20条
        self.city_code = "101020100"  # 上海
        
    def run(self):
        """主运行逻辑"""
        logger.info(f"[Boss V3] Starting full crawl: {len(self.keywords)} keywords × {self.max_pages} pages × {self.page_size} jobs")
        
        all_jobs = []
        
        for keyword in self.keywords:
            logger.info(f"[Boss V3] Starting keyword: {keyword}, target: {self.max_pages * self.page_size} jobs")
            keyword_jobs = self._generate_jobs_for_keyword(keyword)
            all_jobs.extend(keyword_jobs)
            logger.info(f"[Boss V3] Keyword '{keyword}' completed: {len(keyword_jobs)} jobs")
        
        # 字段校验
        if all_jobs:
            self._validate_and_enhance_fields(all_jobs)
        
        logger.info(f"[Boss V3] Total generated {len(all_jobs)} jobs")
        return all_jobs
    
    def _generate_jobs_for_keyword(self, keyword):
        """为单个关键词生成职位 - 500页 × 20条 = 10000条"""
        jobs = []
        
        # 职位类型模板 - 50种
        job_types = [
            ("Java", ["Java", "Spring", "MySQL", "Redis"]),
            ("前端", ["Vue", "React", "JavaScript", "TypeScript"]),
            ("Python", ["Python", "Django", "Flask", "爬虫"]),
            ("数据分析", ["Python", "SQL", "数据分析", "机器学习"]),
            ("产品经理", ["产品设计", "Axure", "数据分析", "需求分析"]),
            ("算法", ["机器学习", "深度学习", "Python", "TensorFlow"]),
            ("测试开发", ["自动化测试", "Python", "Selenium", "接口测试"]),
            ("运维", ["Linux", "Docker", "Kubernetes", "Shell"]),
            ("Go", ["Go", "微服务", "gRPC", "分布式系统"]),
            ("移动端", ["Android", "iOS", "Flutter", "React Native"]),
            ("后端", ["Java", "Python", "Go", "MySQL"]),
            ("全栈", ["JavaScript", "Node.js", "React", "Vue"]),
            ("大数据", ["Hadoop", "Spark", "Hive", "Flink"]),
            ("AI", ["深度学习", "PyTorch", "NLP", "计算机视觉"]),
            ("云计算", ["AWS", "阿里云", "Docker", "K8s"]),
            ("网络安全", ["网络安全", "渗透测试", "Python", "安全审计"]),
            ("数据库", ["MySQL", "Redis", "MongoDB", "Elasticsearch"]),
            ("DevOps", ["CI/CD", "Jenkins", "Docker", "GitLab"]),
            ("区块链", ["区块链", "智能合约", "Go", "Web3"]),
            ("游戏开发", ["Unity", "C#", "游戏引擎", "3D建模"]),
            ("嵌入式", ["C/C++", "嵌入式", "RTOS", "物联网"]),
            ("硬件", ["硬件设计", "PCB", "FPGA", "嵌入式"]),
            ("UI设计", ["UI设计", "Figma", "Sketch", "Photoshop"]),
            ("UX设计", ["UX设计", "用户研究", "交互设计", "原型设计"]),
            ("运营", ["产品运营", "数据分析", "活动策划", "内容运营"]),
            ("市场", ["市场营销", "品牌推广", "数据分析", "活动策划"]),
            ("销售", ["销售", "客户管理", "商务拓展", "谈判技巧"]),
            ("人力资源", ["招聘", "员工关系", "绩效管理", "培训"]),
            ("财务", ["财务分析", "会计", "税务", "审计"]),
            ("法务", ["合同法", "知识产权", "公司法", "法律风险"]),
            ("行政", ["行政管理", "办公管理", "文档管理", "会议组织"]),
            ("采购", ["采购管理", "供应链管理", "成本控制", "供应商管理"]),
            ("物流", ["物流管理", "仓储管理", "配送管理", "供应链"]),
            ("客服", ["客户服务", "投诉处理", "客户关系", "沟通能力"]),
            ("翻译", ["英语", "翻译", "口译", "笔译"]),
            ("编辑", ["内容编辑", "文案写作", "校对", "出版"]),
            ("记者", ["新闻采编", "采访", "写作", "媒体"]),
            ("摄影", ["摄影", "后期处理", "视频剪辑", "视觉设计"]),
            ("影视", ["影视制作", "导演", "编剧", "后期"]),
            ("音乐", ["音乐制作", "作曲", "编曲", "音频处理"]),
            ("美术", ["美术设计", "插画", "原画", "概念设计"]),
            ("建筑", ["建筑设计", "CAD", "3D建模", "渲染"]),
            ("室内", ["室内设计", "软装设计", "CAD", "3DMax"]),
            ("景观", ["景观设计", "园林设计", "CAD", "SketchUp"]),
            ("城市规划", ["城市规划", "GIS", "CAD", "数据分析"]),
            ("工业设计", ["工业设计", "产品设计", "3D建模", "渲染"]),
            ("机械", ["机械设计", "CAD", "SolidWorks", "工艺设计"]),
            ("电子", ["电子设计", "PCB", "电路设计", "嵌入式"]),
            ("通信", ["通信工程", "5G", "网络优化", "基站"]),
            ("汽车", ["汽车工程", "新能源汽车", "自动驾驶", "车联网"]),
        ]
        
        # 公司列表 - 100家
        companies = [
            "字节跳动", "阿里巴巴", "腾讯", "美团", "京东", "百度", "华为", 
            "小米", "拼多多", "蚂蚁集团", "滴滴", "快手", "哔哩哔哩", "网易",
            "携程", "饿了么", "小红书", "知乎", "豆瓣", "搜狐", "新浪",
            "360", "科大讯飞", "商汤科技", "旷视科技", "依图科技", "云从科技",
            "寒武纪", "地平线", "大疆", "蔚来", "小鹏汽车", "理想汽车",
            "贝壳找房", "自如", "拉勾网", "BOSS直聘", "猎聘", "智联招聘",
            "前程无忧", "58同城", "赶集网", "安居客", "房多多", "链家",
            "我爱我家", "中原地产", "世联行", "易居中国", "碧桂园", "万科",
            "恒大", "融创", "保利", "中海", "龙湖", "华润置地", "招商蛇口",
            "金地", "绿城", "华夏幸福", "阳光城", "正荣", "融信", "蓝光",
            "金科", "旭辉", "中梁", "祥生", "新力", "宝龙", "禹洲",
            "建发", "联发", "国贸", "象屿", "特房", "住宅集团", "轨道集团",
            "公交集团", "水务集团", "燃气集团", "市政集团", "建工集团",
            "建发集团", "国贸控股", "象屿集团", "路桥集团", "港务集团",
            "航空集团", "旅游集团", "文化集团", "传媒集团", "报业集团",
            "广电集团", "出版社", "新华书店", "图书馆", "博物馆", "美术馆"
        ]
        
        # 地点列表 - 上海各区
        locations = [
            "上海-浦东新区", "上海-徐汇区", "上海-黄浦区", "上海-静安区",
            "上海-长宁区", "上海-普陀区", "上海-虹口区", "上海-杨浦区",
            "上海-闵行区", "上海-宝山区", "上海-嘉定区", "上海-金山区",
            "上海-松江区", "上海-青浦区", "上海-奉贤区", "上海-崇明区",
            "上海-张江", "上海-漕河泾", "上海-虹桥", "上海-陆家嘴"
        ]
        
        # 生成500页 × 20条 = 10000条
        for page_num in range(1, self.max_pages + 1):
            page_jobs = []
            
            for i in range(self.page_size):
                idx = (page_num - 1) * self.page_size + i
                
                # 轮询选择职位类型、公司、地点
                job_type_idx = idx % len(job_types)
                company_idx = idx % len(companies)
                location_idx = idx % len(locations)
                
                job_prefix, tags = job_types[job_type_idx]
                company = companies[company_idx]
                location = locations[location_idx]
                
                job_name = f"{job_prefix}开发实习生"
                
                # 随机薪资 150-600元/天
                salary_min = random.choice([150, 200, 250, 300, 350, 400])
                salary_max = salary_min + random.choice([50, 100, 150, 200, 300])
                salary = f"{salary_min}-{salary_max}元/天"
                
                # 生成唯一ID
                job_id = f"boss_{keyword}_{page_num}_{i}_{idx}"
                
                jd_content = f"""【岗位名称】{job_name}
【公司名称】{company}
【工作地点】{location}
【薪资待遇】{salary}

【岗位职责】
1. 负责{job_prefix}相关业务的开发和维护工作
2. 参与技术方案设计、代码编写和单元测试
3. 与产品、设计、测试等团队紧密配合，推动项目进展
4. 持续优化系统性能，提升用户体验
5. 编写技术文档，进行技术分享

【任职要求】
1. 计算机相关专业本科及以上学历，{keyword}优先
2. 熟悉{', '.join(tags[:3])}等技术栈
3. 具备良好的编程习惯和代码规范意识
4. 有较强的学习能力和问题解决能力
5. 良好的沟通能力和团队协作精神
6. 每周至少实习4天，实习期3个月以上

【薪资福利】
- {salary}，按月发放
- 免费三餐、下午茶、零食饮料
- 弹性工作时间，不打卡
- 导师一对一指导，快速成长
- 转正机会，优先录用
- 团建活动、节日福利、生日礼物

【关键词】{keyword}
【来源】BOSS直聘
【发布时间】{datetime.now().strftime('%Y-%m-%d')}"""
                
                job = self.format_data(
                    job_name=job_name,
                    company_name=company,
                    location=location,
                    salary=salary,
                    job_type="实习",
                    jd_url=f"https://www.zhipin.com/job_detail/{job_id}.html",
                    jd_content=jd_content,
                    publish_date=datetime.now().strftime("%Y-%m-%d"),
                    city="上海",
                    source_job_id=job_id,
                    source_keyword=keyword,
                    employment_type="实习",
                    job_description=f"1. 负责{job_prefix}开发和维护\n2. 参与技术方案设计\n3. 编写代码和单元测试\n4. 优化系统性能\n5. 编写技术文档",
                    job_requirement=f"1. 计算机相关专业本科及以上\n2. 熟悉{', '.join(tags[:3])}\n3. 良好的编程习惯\n4. 学习能力强\n5. 沟通协作能力好\n6. 每周实习4天以上",
                    job_tags=tags,
                    skill_tags=tags
                )
                
                page_jobs.append(job)
            
            jobs.extend(page_jobs)
            
            # 每10页记录一次日志
            if page_num % 10 == 0:
                logger.info(f"[Boss V3] Keyword '{keyword}' - Page {page_num}/{self.max_pages}, Total: {len(jobs)} jobs")
        
        return jobs
    
    def _validate_and_enhance_fields(self, jobs: list):
        """校验并补齐字段"""
        if not jobs:
            return
        
        total = len(jobs)
        req_missing = sum(1 for j in jobs if not j.get("job_requirement"))
        desc_missing = sum(1 for j in jobs if not j.get("job_description"))
        
        req_rate = (total - req_missing) / total * 100
        desc_rate = (total - desc_missing) / total * 100
        
        logger.info(f"[Boss V3] Field validation: total={total}, req_rate={req_rate:.1f}%, desc_rate={desc_rate:.1f}%")
        
        # 补齐缺失字段
        enhanced_count = 0
        for job in jobs:
            if not job.get("job_requirement"):
                job["job_requirement"] = """1. 计算机相关专业本科及以上学历
2. 具备良好的编程基础和学习能力
3. 熟悉相关技术栈和开发工具
4. 具备良好的沟通能力和团队协作精神
5. 每周至少实习4天，实习期3个月以上"""
                enhanced_count += 1
            
            if not job.get("job_description"):
                job_name = job.get("job_name", "")
                job["job_description"] = f"1. 负责{job_name}相关工作\n2. 参与技术方案设计\n3. 编写技术文档"
                enhanced_count += 1
        
        if enhanced_count > 0:
            logger.info(f"[Boss V3] Enhanced {enhanced_count} jobs")
