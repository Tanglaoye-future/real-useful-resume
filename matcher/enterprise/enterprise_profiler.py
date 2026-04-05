# -*- coding: utf-8 -*-
"""
企业画像提取模块
针对中小微企业，从JD和官网文本中提取标准化企业画像
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class CompanyScale(Enum):
    """企业规模分级"""
    MICRO = "微型"      # <10人
    SMALL = "小型"      # 10-50人
    MEDIUM = "中型"     # 50-200人
    LARGE = "大型"      # >200人
    UNKNOWN = "未知"


class DevelopmentStage(Enum):
    """企业发展阶段"""
    STARTUP = "初创期"      # 0-3年
    GROWTH = "成长期"       # 3-7年
    MATURE = "成熟期"       # 7-15年
    LISTED = "上市期"       # >15年或已上市
    UNKNOWN = "未知"


@dataclass
class EnterpriseProfile:
    """企业画像数据结构"""
    company_name: str = ""              # 企业全称
    company_short_name: str = ""        # 企业简称（剔除后缀）
    gb_industry: str = ""               # 国标行业分类
    segment: str = ""                   # 细分赛道
    scale: str = ""                     # 企业规模
    development_stage: str = ""         # 发展阶段
    found_year: int = 0                 # 成立年份
    culture: str = ""                   # 企业文化
    core_products: List[str] = None     # 核心产品
    
    def __post_init__(self):
        if self.core_products is None:
            self.core_products = []
    
    def to_dict(self) -> Dict:
        return asdict(self)


class EnterpriseProfiler:
    """
    企业画像提取器
    从JD文本和官网文本中提取标准化企业画像
    """
    
    # 行业关键词映射
    INDUSTRY_KEYWORDS = {
        "互联网/电商": ["电商", "跨境电商", "淘宝", "天猫", "京东", "拼多多", "亚马逊"],
        "互联网/SaaS": ["SaaS", "云服务", "企业软件", "管理系统", "平台"],
        "互联网/游戏": ["游戏", "手游", "网游", "电竞", "游戏开发"],
        "互联网/社交": ["社交", "社区", "直播", "短视频", "内容"],
        "互联网/金融科技": ["金融科技", "支付", "区块链", "数字货币", "保险科技"],
        "互联网/教育": ["教育", "在线教育", "培训", "K12", "职业教育"],
        "互联网/医疗": ["医疗", "健康", "互联网医疗", "医药", "医疗器械"],
        "互联网/物流": ["物流", "供应链", "仓储", "配送", "快递"],
        "软件和信息技术服务业": ["软件", "信息技术", "IT服务", "技术开发"],
        "人工智能": ["AI", "人工智能", "机器学习", "深度学习", "大模型", "算法"],
        "新能源": ["新能源", "光伏", "储能", "电动汽车", "锂电池"],
        "生物医药": ["生物医药", "制药", "生物技术", "基因", "CRO"],
        "先进制造": ["智能制造", "工业自动化", "机器人", "精密制造"],
    }
    
    # 细分赛道关键词
    SEGMENT_KEYWORDS = {
        "企业服务/HR SaaS": ["HR", "人力资源", "招聘", "考勤", "薪酬"],
        "企业服务/财务SaaS": ["财务", "会计", "报销", "发票", "税务"],
        "企业服务/CRM": ["CRM", "客户管理", "销售管理", "客户"],
        "企业服务/协同办公": ["协同", "办公", "OA", "文档", "会议"],
        "企业服务/营销SaaS": ["营销", "投放", "广告", "推广", "增长"],
        "电商/跨境电商": ["跨境", "出海", "海外", "Amazon", "eBay"],
        "电商/直播电商": ["直播", "带货", "主播", "直播间"],
        "电商/社交电商": ["社交", "分销", "拼团", "社群"],
        "游戏/手游": ["手游", "手机游戏", "iOS", "Android游戏"],
        "游戏/页游": ["页游", "H5游戏", "小游戏"],
        "AI/大模型": ["大模型", "LLM", "GPT", "AIGC", "生成式AI"],
        "AI/计算机视觉": ["CV", "视觉", "图像识别", "人脸识别"],
        "AI/自然语言处理": ["NLP", "自然语言", "文本", "语音识别"],
    }
    
    # 企业文化关键词
    CULTURE_KEYWORDS = {
        "扁平化": ["扁平", "扁平化", "无层级", "直接沟通"],
        "创业氛围": ["创业", "初创", "早期", "从0到1", "all in"],
        "狼性文化": ["狼性", "拼搏", "奋斗", "996", "大小周"],
        "技术驱动": ["技术", "工程师文化", "极客", "技术导向"],
        "弹性工作": ["弹性", "灵活", "不打卡", "远程"],
        "结果导向": ["结果", "KPI", "OKR", "数据驱动"],
    }
    
    # 公司后缀模式
    COMPANY_SUFFIX_PATTERN = re.compile(
        r'(有限公司|有限责任公司|股份公司|股份有限公司|集团|企业集团|合伙企业|'
        r'工作室|中心|研究院|研究所|分公司|子公司)$'
    )
    
    def __init__(self):
        pass
    
    def extract_from_jd(self, jd_text: str, company_name: str = "") -> EnterpriseProfile:
        """
        从JD文本中提取企业画像
        
        Args:
            jd_text: JD文本
            company_name: 公司名称（如果已知）
            
        Returns:
            EnterpriseProfile: 企业画像
        """
        profile = EnterpriseProfile()
        
        # 1. 提取企业名称
        if company_name:
            profile.company_name = company_name
            profile.company_short_name = self._extract_short_name(company_name)
        
        # 2. 提取行业分类
        profile.gb_industry, profile.segment = self._extract_industry(jd_text)
        
        # 3. 提取企业规模
        profile.scale = self._extract_scale(jd_text)
        
        # 4. 提取发展阶段
        profile.development_stage = self._extract_stage(jd_text)
        
        # 5. 提取成立时间
        profile.found_year = self._extract_founded_year(jd_text)
        
        # 6. 提取企业文化
        profile.culture = self._extract_culture(jd_text)
        
        # 7. 提取核心产品
        profile.core_products = self._extract_products(jd_text)
        
        return profile
    
    def extract_from_website(self, website_text: str, company_name: str = "") -> EnterpriseProfile:
        """
        从官网文本中提取企业画像
        
        Args:
            website_text: 官网文本
            company_name: 公司名称
            
        Returns:
            EnterpriseProfile: 企业画像
        """
        # 官网文本通常更丰富，使用相同逻辑但权重更高
        return self.extract_from_jd(website_text, company_name)
    
    def _extract_short_name(self, company_name: str) -> str:
        """提取企业简称（剔除后缀）"""
        # 剔除常见后缀
        short_name = self.COMPANY_SUFFIX_PATTERN.sub('', company_name)
        return short_name.strip()
    
    def _extract_industry(self, text: str) -> Tuple[str, str]:
        """提取行业分类和细分赛道"""
        text_lower = text.lower()
        
        # 匹配行业
        best_industry = "软件和信息技术服务业"
        best_industry_score = 0
        
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text_lower)
            if score > best_industry_score:
                best_industry_score = score
                best_industry = industry
        
        # 匹配细分赛道
        best_segment = "其他"
        best_segment_score = 0
        
        for segment, keywords in self.SEGMENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text_lower)
            if score > best_segment_score:
                best_segment_score = score
                best_segment = segment
        
        return best_industry, best_segment
    
    def _extract_scale(self, text: str) -> str:
        """提取企业规模"""
        text_lower = text.lower()
        
        # 直接匹配规模描述
        if any(kw in text_lower for kw in ["少于10人", "<10人", "几人", "10人以内"]):
            return CompanyScale.MICRO.value
        
        if any(kw in text_lower for kw in ["10-50人", "10到50人", "几十人", "小型企业"]):
            return CompanyScale.SMALL.value
        
        if any(kw in text_lower for kw in ["50-200人", "50到200人", "上百人", "中型企业"]):
            return CompanyScale.MEDIUM.value
        
        if any(kw in text_lower for kw in [">200人", "200人以上", "上千人", "大型企业", "万人"]):
            return CompanyScale.LARGE.value
        
        # 从团队描述推断
        if "团队" in text:
            # 尝试匹配团队规模
            team_match = re.search(r'团队[：:]?\s*(\d+)', text)
            if team_match:
                team_size = int(team_match.group(1))
                if team_size < 10:
                    return CompanyScale.MICRO.value
                elif team_size < 50:
                    return CompanyScale.SMALL.value
                elif team_size < 200:
                    return CompanyScale.MEDIUM.value
                else:
                    return CompanyScale.LARGE.value
        
        # 从参保人数推断（如果文本中有）
        insured_match = re.search(r'参保[人数]*[：:]?\s*(\d+)', text)
        if insured_match:
            insured = int(insured_match.group(1))
            if insured < 10:
                return CompanyScale.MICRO.value
            elif insured < 50:
                return CompanyScale.SMALL.value
            elif insured < 200:
                return CompanyScale.MEDIUM.value
            else:
                return CompanyScale.LARGE.value
        
        return CompanyScale.UNKNOWN.value
    
    def _extract_stage(self, text: str) -> str:
        """提取发展阶段"""
        text_lower = text.lower()
        
        # 从融资信息推断
        if any(kw in text_lower for kw in ["天使轮", "种子轮", "pre-a", "刚成立", "初创"]):
            return DevelopmentStage.STARTUP.value
        
        if any(kw in text_lower for kw in ["a轮", "b轮", "c轮", "d轮", "快速成长期", "扩张期"]):
            return DevelopmentStage.GROWTH.value
        
        if any(kw in text_lower for kw in ["e轮", "f轮", "pre-ipo", "成熟", "稳定", "行业领先"]):
            return DevelopmentStage.MATURE.value
        
        if any(kw in text_lower for kw in ["上市", "ipo", "股票代码", "上市公司"]):
            return DevelopmentStage.LISTED.value
        
        # 从成立时间推断
        found_year = self._extract_founded_year(text)
        if found_year > 0:
            import datetime
            years = datetime.datetime.now().year - found_year
            if years <= 3:
                return DevelopmentStage.STARTUP.value
            elif years <= 7:
                return DevelopmentStage.GROWTH.value
            elif years <= 15:
                return DevelopmentStage.MATURE.value
            else:
                return DevelopmentStage.LISTED.value
        
        return DevelopmentStage.UNKNOWN.value
    
    def _extract_founded_year(self, text: str) -> int:
        """提取成立年份"""
        # 匹配成立年份
        patterns = [
            r'成立于?(\d{4})年?',
            r'(\d{4})年.?成立',
            r'成立时间[：:]?\s*(\d{4})',
            r'(\d{4}).{0,5}年.{0,10}创立',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                year = int(match.group(1))
                # 合理性检查
                import datetime
                current_year = datetime.datetime.now().year
                if 1980 <= year <= current_year:
                    return year
        
        return 0
    
    def _extract_culture(self, text: str) -> str:
        """提取企业文化"""
        text_lower = text.lower()
        cultures = []
        
        for culture, keywords in self.CULTURE_KEYWORDS.items():
            if any(kw.lower() in text_lower for kw in keywords):
                cultures.append(culture)
        
        return "、".join(cultures) if cultures else "未明确"
    
    def _extract_products(self, text: str) -> List[str]:
        """提取核心产品"""
        products = []
        
        # 匹配产品描述
        product_patterns = [
            r'(?:主营|核心)?产品[：:]\s*([^。\n]+)',
            r'(?:主要)?业务[：:]\s*([^。\n]+)',
            r'(?:提供)?服务[：:]\s*([^。\n]+)',
        ]
        
        for pattern in product_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # 分割多个产品
                items = re.split(r'[、,，；;]', match)
                for item in items:
                    item = item.strip()
                    if len(item) > 2 and len(item) < 50:
                        products.append(item)
        
        # 去重并限制数量
        products = list(dict.fromkeys(products))[:5]
        
        return products
    
    def batch_extract(self, jobs: List[Dict]) -> Dict[str, EnterpriseProfile]:
        """
        批量提取企业画像
        
        Args:
            jobs: 岗位列表，每个岗位包含company_name和job_description
            
        Returns:
            Dict[str, EnterpriseProfile]: 企业名称到画像的映射
        """
        profiles = {}
        
        for job in jobs:
            company_name = job.get('company_name', '')
            if not company_name or company_name in profiles:
                continue
            
            jd_text = job.get('job_description', '') + ' ' + job.get('requirements', '')
            profile = self.extract_from_jd(jd_text, company_name)
            profiles[company_name] = profile
        
        return profiles


# 测试代码
if __name__ == "__main__":
    profiler = EnterpriseProfiler()
    
    # 测试JD文本
    test_jd = """
    杭州XX科技有限公司成立于2020年，是一家专注于HR SaaS服务的初创企业。
    团队规模30人，已获得A轮融资。
    主营产品：智能招聘系统、简历匹配平台、员工管理系统。
    企业文化：扁平化、弹性工作制、创业氛围。
    我们正在寻找一位Java开发工程师...
    """
    
    profile = profiler.extract_from_jd(test_jd, "杭州XX科技有限公司")
    
    print("企业画像提取结果：")
    print(json.dumps(profile.to_dict(), ensure_ascii=False, indent=2))
