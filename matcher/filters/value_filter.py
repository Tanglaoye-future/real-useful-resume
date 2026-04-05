"""
高价值岗位筛选模块 V2

基于「规则引擎 + 加权打分」的评估方式
第三步：高价值评估层（核心逻辑）
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CompanyTier(Enum):
    """公司分级 - S/A/B/C四级"""
    S = "S级"      # 顶级
    A = "A级"      # 头部
    B = "B级"      # 中腰部
    C = "C级"      # 补充赛道
    UNKNOWN = "未知"


class JobValueLevel(Enum):
    """岗位价值等级"""
    HIGH = "高价值"
    MEDIUM = "中价值"
    LOW = "低价值"
    FILTERED = "已过滤"


@dataclass
class ValueFilterConfig:
    """高价值筛选配置"""
    
    # 公司维度权重
    company_weight: float = 0.5  # 50%
    
    # 岗位维度权重
    job_weight: float = 0.5  # 50%
    
    # 最低总分要求（低于此分数视为低价值）
    min_total_score: float = 60.0
    
    # 高价值岗位阈值
    high_value_threshold: float = 75.0
    
    # 岗位类型评分配置
    high_value_job_types: List[str] = field(default_factory=lambda: [
        "Go后端开发", "产品经理", "数据分析师", "数据工程师",
        "策略产品", "增长产品", "商业化产品", "AI产品"
    ])
    
    medium_value_job_types: List[str] = field(default_factory=lambda: [
        "Java后端", "前端开发", "运营", "产品运营", "用户运营"
    ])
    
    # 核心业务部门关键词
    core_departments: List[str] = field(default_factory=lambda: [
        "抖音", "淘宝", "天猫", "微信支付", "阿里云", "腾讯云",
        "核心", "主力", "主站", "搜索", "推荐", "广告"
    ])
    
    # 技能匹配关键词
    skill_keywords: List[str] = field(default_factory=lambda: [
        "Go", "Golang", "产品", "数据分析", "Python", "SQL"
    ])
    
    # ========== 外企加分项 ==========
    # 落户支持关键词
    foreign_hukou_keywords: List[str] = field(default_factory=lambda: [
        "落户", "户口", "上海户口", "积分落户", "人才引进落户"
    ])
    # 培训体系关键词
    foreign_training_keywords: List[str] = field(default_factory=lambda: [
        "培训", "培养", "mentor", "导师", "轮岗", "rotation",
        "培训体系", "完善的培训", "系统培训"
    ])
    # 全球轮岗关键词
    foreign_global_keywords: List[str] = field(default_factory=lambda: [
        "全球轮岗", "海外轮岗", "国际轮岗", "global rotation",
        "海外工作", "海外机会", "国际交流", "global opportunity"
    ])
    
    # ========== 独角兽加分项 ==========
    # 核心业务岗关键词
    unicorn_core_keywords: List[str] = field(default_factory=lambda: [
        "核心业务", "核心部门", "核心业务线", "战略业务",
        "主力业务", "核心业务团队"
    ])
    # 期权激励关键词
    unicorn_equity_keywords: List[str] = field(default_factory=lambda: [
        "期权", "股权", "股权激励", "stock option", "期权激励",
        "员工持股", "ESOP", "股份"
    ])
    # 赛道前景关键词
    unicorn_prospect_keywords: List[str] = field(default_factory=lambda: [
        "风口", "赛道", "前景", "高增长", "高速发展",
        "行业领先", "头部企业", "独角兽", "pre-ipo"
    ])
    
    # ========== 国企加分项 ==========
    # 稳定编制关键词
    state_stable_keywords: List[str] = field(default_factory=lambda: [
        "正式编制", "事业编制", "国企编制", "正式员工",
        "稳定", "长期发展", "铁饭碗"
    ])
    # 落户保障关键词
    state_hukou_keywords: List[str] = field(default_factory=lambda: [
        "落户保障", "解决户口", "协助落户", "优先落户",
        "上海户口", "户籍", "人才引进"
    ])
    # 福利完善关键词
    state_welfare_keywords: List[str] = field(default_factory=lambda: [
        "五险一金", "补充公积金", "补充医疗", "企业年金",
        "福利完善", "福利好", "高温补贴", "节日福利",
        "带薪年假", "体检", "食堂", "班车"
    ])


class CompanyClassifier:
    """公司分级分类器 - S/A/B/C四级（扩展版，兼容互联网大厂、外企、独角兽、国企）"""

    # ========== S级（顶级）- 100分 ==========
    # 互联网大厂
    S_TIER_COMPANIES = {
        "腾讯": 100, "Tencent": 100, "微信": 100, "QQ": 100,
        "阿里巴巴": 100, "Alibaba": 100, "淘宝": 100, "天猫": 100,
        "字节跳动": 100, "ByteDance": 100, "抖音": 100, "TikTok": 100,
        "百度": 100, "Baidu": 100
    }
    
    # S级外企 - 世界500强科技/金融外企、全球头部跨国公司
    S_TIER_FOREIGN = {
        "Google": 100, "谷歌": 100,
        "Microsoft": 100, "微软": 100,
        "Amazon": 100, "亚马逊": 100,
        "Apple": 100, "苹果": 100,
        "Meta": 100, "Facebook": 100, "脸书": 100,
        "Netflix": 100, "奈飞": 100,
        "Goldman Sachs": 100, "高盛": 100,
        "Morgan Stanley": 100, "摩根士丹利": 100,
        "JPMorgan": 100, "摩根大通": 100,
        "McKinsey": 100, "麦肯锡": 100,
        "BCG": 100, "波士顿咨询": 100,
        "Bain": 100, "贝恩": 100
    }

    # ========== A级（头部）- 85分 ==========
    # 互联网大厂
    A_TIER_COMPANIES = {
        "美团": 85, "Meituan": 85,
        "拼多多": 85, "PDD": 85,
        "京东": 85, "JD": 85,
        "网易": 85, "NetEase": 85,
        "快手": 85, "Kuaishou": 85,
        "滴滴出行": 85, "滴滴": 85, "Didi": 85,
        "蚂蚁集团": 85, "蚂蚁金服": 85, "Ant": 85,
        "阿里云": 85, "Alibaba Cloud": 85,
        "腾讯云": 85, "Tencent Cloud": 85
    }
    
    # A级外企 - 行业头部外企
    A_TIER_FOREIGN = {
        "Oracle": 85, "甲骨文": 85,
        "IBM": 85,
        "SAP": 85,
        "Salesforce": 85,
        "Adobe": 85, "奥多比": 85,
        "Nvidia": 85, "英伟达": 85,
        "Intel": 85, "英特尔": 85,
        "AMD": 85, "超威": 85,
        "Qualcomm": 85, "高通": 85,
        "Cisco": 85, "思科": 85,
        "LinkedIn": 85, "领英": 85,
        "Twitter": 85, "X": 85, "推特": 85,
        "Uber": 85, "优步": 85,
        "Airbnb": 85, "爱彼迎": 85,
        "PayPal": 85, "贝宝": 85,
        "Stripe": 85
    }
    
    # A级独角兽 - 估值超10亿美元的独角兽
    A_TIER_UNICORNS = {
        "字节跳动": 85, "ByteDance": 85,  # 已包含在S级，这里作为独角兽也标记
        "蚂蚁集团": 85, "Ant": 85,
        "Shein": 85, "希音": 85,
        "微众银行": 85,
        "菜鸟网络": 85,
        "滴滴": 85, "Didi": 85,
        "快手": 85, "Kuaishou": 85,
        "商汤": 85, "SenseTime": 85,
        "大疆": 85, "DJI": 85,
        "比特大陆": 85,
        "柔宇科技": 85
    }
    
    # A级金融科技 - 头部金融科技企业
    A_TIER_FINTECH = {
        "陆金所": 85,
        "京东数科": 85, "京东科技": 85,
        "度小满": 85,
        "招联金融": 85,
        "微众银行": 85,
        "网商银行": 85,
        "平安科技": 85,
        "金融壹账通": 85
    }
    
    # A级国企 - 上海重点国企
    A_TIER_STATE = {
        "浦发银行": 85, "浦发银行科技岗": 85,
        "上海银行": 85,
        "国泰君安": 85,
        "海通证券": 85,
        "申万宏源": 85,
        "中国太保": 85,
        "上海保险交易所": 85,
        "上海票据交易所": 85,
        "跨境清算公司": 85,
        "中国银联": 85,
        "上海证券交易所": 85,
        "上海期货交易所": 85,
        "中国金融期货交易所": 85
    }

    # ========== B级（中腰部）- 70分 ==========
    # 互联网中厂
    B_TIER_COMPANIES = {
        "哔哩哔哩": 70, "Bilibili": 70, "B站": 70,
        "小红书": 70, "Xiaohongshu": 70,
        "小米": 70, "Xiaomi": 70,
        "携程": 70, "Ctrip": 70,
        "金山软件": 70, "Kingsoft": 70,
        "360": 70, "奇虎": 70,
        "华为云": 70, "Huawei Cloud": 70,
        "米哈游": 70, "MiHoYo": 70,
        "得物": 70, "Dewu": 70
    }
    
    # B级外企 - 优质外资企业
    B_TIER_FOREIGN = {
        "Dell": 70, "戴尔": 70,
        "HP": 70, "惠普": 70,
        "VMware": 70,
        "Red Hat": 70, "红帽": 70,
        "Atlassian": 70,
        "ServiceNow": 70,
        "Workday": 70,
        "Snowflake": 70,
        "Datadog": 70,
        "Splunk": 70,
        "Elastic": 70,
        "MongoDB": 70,
        "Confluent": 70,
        "Cloudflare": 70,
        "Shopify": 70,
        "Square": 70, "Block": 70,
        "Robinhood": 70,
        "Coinbase": 70,
        "DoorDash": 70,
        "Lyft": 70
    }
    
    # B级准独角兽 - 估值1-10亿美元的准独角兽
    B_TIER_UNICORNS = {
        "旷视": 70, "Megvii": 70,
        "依图": 70, "Yitu": 70,
        "云从": 70, "CloudWalk": 70,
        "地平线": 70, "Horizon": 70,
        "寒武纪": 70, "Cambricon": 70,
        "蔚来": 70, "NIO": 70,
        "理想汽车": 70, "Li Auto": 70,
        "小鹏汽车": 70, "XPeng": 70,
        "威马汽车": 70,
        "零跑汽车": 70,
        "哪吒汽车": 70,
        "极氪": 70, "ZEEKR": 70,
        "Momenta": 70,
        "小马智行": 70, "Pony.ai": 70,
        "文远知行": 70, "WeRide": 70,
        "AutoX": 70,
        "图森未来": 70, "TuSimple": 70,
        "智加科技": 70, "Plus": 70,
        "嬴彻科技": 70,
        "燧原科技": 70,
        "壁仞科技": 70,
        "摩尔线程": 70,
        "沐曦集成电路": 70,
        "芯驰科技": 70,
        "黑芝麻智能": 70,
        "速腾聚创": 70,
        "禾赛科技": 70
    }
    
    # B级细分赛道头部
    B_TIER_LEADERS = {
        "BOSS直聘": 70, "BOSS Zhipin": 70,
        "猎聘": 70, "Liepin": 70,
        "拉勾": 70, "Lagou": 70,
        "智联招聘": 70, "Zhaopin": 70,
        "前程无忧": 70, "51job": 70,
        "脉脉": 70, "Maimai": 70,
        "看准网": 70,
        "牛客网": 70,
        "力扣": 70, "LeetCode": 70,
        "CSDN": 70,
        "掘金": 70, "Juejin": 70,
        "InfoQ": 70,
        "SegmentFault": 70, "思否": 70,
        "开源中国": 70, "OSChina": 70,
        "Gitee": 70, "码云": 70
    }
    
    # B级地方国企科技岗
    B_TIER_STATE = {
        "上汽集团": 70, "上汽集团软件中心": 70,
        "上海电气": 70,
        "上海仪电": 70,
        "上海华谊": 70,
        "光明食品": 70,
        "百联集团": 70,
        "锦江国际": 70,
        "东方国际": 70,
        "上海建工": 70,
        "上海隧道": 70,
        "上海地铁": 70,
        "上海机场": 70,
        "上海港务": 70,
        "上海航空": 70,
        "上海邮政": 70,
        "上海电信": 70,
        "上海移动": 70,
        "上海联通": 70
    }

    # ========== C级（补充赛道）- 60分 ==========
    # 小而美初创公司、其他优质中小企
    C_TIER_COMPANIES = {
        # 游戏行业
        "莉莉丝": 60, "Lilith": 60,
        "叠纸游戏": 60,
        "鹰角网络": 60,
        "散爆网络": 60,
        "库洛游戏": 60,
        "英雄体育": 60, "VSPO": 60,
        # 内容平台
        "喜马拉雅": 60, "Ximalaya": 60,
        "荔枝": 60, "Lizhi": 60,
        "蜻蜓FM": 60, "Qingting": 60,
        "樊登读书": 60,
        "得到": 60,
        "混沌学园": 60,
        # 工具类
        "WPS": 60, "金山办公": 60,
        "福昕软件": 60,
        "万兴科技": 60,
        "广联达": 60,
        "用友": 60, "Yonyou": 60,
        "金蝶": 60, "Kingdee": 60,
        # 安全类
        "奇安信": 60, "QiAnXin": 60,
        "深信服": 60, "Sangfor": 60,
        "启明星辰": 60,
        "绿盟科技": 60,
        "天融信": 60,
        "安恒信息": 60,
        "山石网科": 60,
        "迪普科技": 60,
        # 其他优质企业
        "容联云": 60,
        "声网": 60, "Agora": 60,
        "融云": 60,
        "极光": 60, "JPush": 60,
        "个推": 60,
        "友盟+": 60,
        "TalkingData": 60,
        "神策数据": 60,
        "GrowingIO": 60,
        "诸葛IO": 60
    }

    @classmethod
    def classify(cls, company_name: str) -> Tuple[CompanyTier, int, str]:
        """
        根据公司名称判断等级、分数和企业类型
        
        Returns:
            (等级, 分数, 企业类型)
        """
        if not company_name:
            return CompanyTier.UNKNOWN, 30, "未知"

        company_name = company_name.strip()

        # 检查S级 - 互联网大厂
        for name, score in cls.S_TIER_COMPANIES.items():
            if name in company_name or company_name in name:
                return CompanyTier.S, score, "互联网大厂"
        
        # 检查S级 - 外企
        for name, score in cls.S_TIER_FOREIGN.items():
            if name in company_name or company_name in name:
                return CompanyTier.S, score, "外企"

        # 检查A级 - 互联网大厂
        for name, score in cls.A_TIER_COMPANIES.items():
            if name in company_name or company_name in name:
                return CompanyTier.A, score, "互联网大厂"
        
        # 检查A级 - 外企
        for name, score in cls.A_TIER_FOREIGN.items():
            if name in company_name or company_name in name:
                return CompanyTier.A, score, "外企"
        
        # 检查A级 - 独角兽
        for name, score in cls.A_TIER_UNICORNS.items():
            if name in company_name or company_name in name:
                return CompanyTier.A, score, "独角兽"
        
        # 检查A级 - 金融科技
        for name, score in cls.A_TIER_FINTECH.items():
            if name in company_name or company_name in name:
                return CompanyTier.A, score, "金融科技"
        
        # 检查A级 - 国企
        for name, score in cls.A_TIER_STATE.items():
            if name in company_name or company_name in name:
                return CompanyTier.A, score, "国企"

        # 检查B级 - 互联网中厂
        for name, score in cls.B_TIER_COMPANIES.items():
            if name in company_name or company_name in name:
                return CompanyTier.B, score, "互联网中厂"
        
        # 检查B级 - 外企
        for name, score in cls.B_TIER_FOREIGN.items():
            if name in company_name or company_name in name:
                return CompanyTier.B, score, "外企"
        
        # 检查B级 - 准独角兽
        for name, score in cls.B_TIER_UNICORNS.items():
            if name in company_name or company_name in name:
                return CompanyTier.B, score, "准独角兽"
        
        # 检查B级 - 细分赛道头部
        for name, score in cls.B_TIER_LEADERS.items():
            if name in company_name or company_name in name:
                return CompanyTier.B, score, "细分赛道头部"
        
        # 检查B级 - 地方国企
        for name, score in cls.B_TIER_STATE.items():
            if name in company_name or company_name in name:
                return CompanyTier.B, score, "地方国企"

        # 检查C级
        for name, score in cls.C_TIER_COMPANIES.items():
            if name in company_name or company_name in name:
                return CompanyTier.C, score, "小而美/中小企"

        return CompanyTier.UNKNOWN, 30, "未知"


class ValueFilter:
    """高价值岗位筛选器 V2"""

    def __init__(self, config: ValueFilterConfig = None):
        self.config = config or ValueFilterConfig()
        self.classifier = CompanyClassifier()
        self.stats = {
            'high_value': 0,
            'medium_value': 0,
            'low_value': 0,
            'filtered': 0
        }

    def filter(self, jobs: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        执行高价值筛选

        Args:
            jobs: 已通过硬性过滤的岗位列表

        Returns:
            (高价值岗位列表, 低价值/已过滤岗位列表)
        """
        evaluated_jobs = []

        for job in jobs:
            result = self._evaluate_job(job)
            job['value_level'] = result['level'].value
            job['total_score'] = result['total_score']
            job['company_score'] = result['company_score']
            job['job_score'] = result['job_score']
            job['score_details'] = result['details']
            evaluated_jobs.append(job)

        # 按总分排序
        evaluated_jobs.sort(key=lambda x: x['total_score'], reverse=True)

        # 分类
        high_value = []
        medium_value = []
        low_value = []
        filtered = []

        for job in evaluated_jobs:
            level = job['value_level']
            if level == JobValueLevel.HIGH.value:
                high_value.append(job)
                self.stats['high_value'] += 1
            elif level == JobValueLevel.MEDIUM.value:
                medium_value.append(job)
                self.stats['medium_value'] += 1
            elif level == JobValueLevel.LOW.value:
                low_value.append(job)
                self.stats['low_value'] += 1
            else:
                filtered.append(job)
                self.stats['filtered'] += 1

        logger.info(f"高价值筛选完成: 高价值{len(high_value)}, "
                   f"中价值{len(medium_value)}, "
                   f"低价值{len(low_value)}, "
                   f"已过滤{len(filtered)}")

        # 返回高价值+中价值作为推荐岗位
        return high_value + medium_value, low_value + filtered

    def _evaluate_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """评估单个岗位的价值 - 新算法（支持外企、独角兽、国企加分项）"""
        
        # ========== 1. 公司维度打分（权重 50%）==========
        company_name = job.get('company_name', '')
        company_tier, company_score, company_type = self.classifier.classify(company_name)
        
        # 公司维度最终得分
        company_final_score = company_score * self.config.company_weight
        
        # ========== 2. 岗位维度打分（权重 50%）==========
        job_details = self._evaluate_job_dimensions(job)
        job_score = job_details['total']
        
        # ========== 3. 企业类型加分项（在岗位维度内）==========
        bonus_score = self._evaluate_company_type_bonus(job, company_type)
        job_score = min(job_score + bonus_score, 100)  # 岗位维度满分100
        
        # 岗位维度最终得分
        job_final_score = job_score * self.config.job_weight
        
        # ========== 4. 总分计算 ==========
        total_score = company_final_score + job_final_score
        
        # ========== 5. 确定价值等级 ==========
        if total_score >= self.config.high_value_threshold:
            level = JobValueLevel.HIGH
        elif total_score >= self.config.min_total_score:
            level = JobValueLevel.MEDIUM
        else:
            level = JobValueLevel.LOW

        return {
            'level': level,
            'total_score': round(total_score, 1),
            'company_score': round(company_final_score, 1),
            'job_score': round(job_final_score, 1),
            'details': {
                'company': {
                    'tier': company_tier.value,
                    'type': company_type,
                    'raw_score': company_score,
                    'weighted_score': round(company_final_score, 1)
                },
                'job_dimensions': job_details,
                'company_type_bonus': bonus_score
            },
            'reason': None
        }
    
    def _evaluate_company_type_bonus(self, job: Dict[str, Any], company_type: str) -> int:
        """
        根据企业类型评估加分项（5-10分）
        
        外企加分项：明确标注落户支持、完善培训体系、全球轮岗机会
        独角兽加分项：核心业务岗、带期权激励、赛道前景好
        国企加分项：稳定编制、落户保障、福利完善
        """
        bonus = 0
        job_text = (
            str(job.get('job_name', '')) + ' ' + 
            str(job.get('job_description', '')) + ' ' + 
            str(job.get('requirements', '')) + ' ' +
            str(job.get('benefits', ''))
        ).lower()
        
        if company_type == "外企":
            # 外企加分项
            # 落户支持 (+5分)
            if any(kw.lower() in job_text for kw in self.config.foreign_hukou_keywords):
                bonus += 5
            # 培训体系 (+3分)
            if any(kw.lower() in job_text for kw in self.config.foreign_training_keywords):
                bonus += 3
            # 全球轮岗 (+5分)
            if any(kw.lower() in job_text for kw in self.config.foreign_global_keywords):
                bonus += 5
                
        elif company_type == "独角兽":
            # 独角兽加分项
            # 核心业务岗 (+5分)
            if any(kw.lower() in job_text for kw in self.config.unicorn_core_keywords):
                bonus += 5
            # 期权激励 (+5分)
            if any(kw.lower() in job_text for kw in self.config.unicorn_equity_keywords):
                bonus += 5
            # 赛道前景 (+3分)
            if any(kw.lower() in job_text for kw in self.config.unicorn_prospect_keywords):
                bonus += 3
                
        elif company_type == "国企" or company_type == "地方国企":
            # 国企加分项
            # 稳定编制 (+5分)
            if any(kw.lower() in job_text for kw in self.config.state_stable_keywords):
                bonus += 5
            # 落户保障 (+5分)
            if any(kw.lower() in job_text for kw in self.config.state_hukou_keywords):
                bonus += 5
            # 福利完善 (+3分)
            if any(kw.lower() in job_text for kw in self.config.state_welfare_keywords):
                bonus += 3
        
        # 加分项上限10分
        return min(bonus, 10)

    def _evaluate_job_dimensions(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        岗位维度打分（满分100分）
        
        评估项:
        - 薪资竞争力 (30%)
        - 岗位类型 (25%)
        - 部门含金量 (20%)
        - 发布时效性 (15%)
        - 任职要求匹配度 (10%)
        """
        details = {}
        
        # 1. 薪资竞争力 (30分)
        salary_score = self._evaluate_salary_competitiveness(job.get('salary', ''))
        details['salary'] = {'score': salary_score, 'max': 30, 'weight': '30%'}
        
        # 2. 岗位类型 (25分)
        job_type_score = self._evaluate_job_type(job.get('job_name', ''))
        details['job_type'] = {'score': job_type_score, 'max': 25, 'weight': '25%'}
        
        # 3. 部门含金量 (20分)
        dept_score = self._evaluate_department(job.get('job_description', ''))
        details['department'] = {'score': dept_score, 'max': 20, 'weight': '20%'}
        
        # 4. 发布时效性 (15分)
        time_score = self._evaluate_timeliness(job.get('publish_time', ''))
        details['timeliness'] = {'score': time_score, 'max': 15, 'weight': '15%'}
        
        # 5. 任职要求匹配度 (10分)
        skill_score = self._evaluate_skill_match(job.get('requirements', ''))
        details['skill_match'] = {'score': skill_score, 'max': 10, 'weight': '10%'}
        
        # 计算岗位维度总分
        total_job_score = salary_score + job_type_score + dept_score + time_score + skill_score
        details['total'] = total_job_score
        
        return details

    def _evaluate_salary_competitiveness(self, salary_text: str) -> int:
        """
        薪资竞争力评分 (0-30分)
        
        评分规则:
        - 月薪≥25k：30分
        - 20-25k：25分
        - 15-20k：20分
        - <15k：10分
        """
        if not salary_text:
            return 10  # 默认最低分
        
        salary_text = salary_text.lower()
        
        # 尝试提取月薪
        monthly_salary = None
        
        # 匹配 "25k-30k" 格式
        k_match = re.search(r'(\d+)[-~]+(\d+)[k千]', salary_text, re.IGNORECASE)
        if k_match:
            min_sal = int(k_match.group(1))
            max_sal = int(k_match.group(2))
            monthly_salary = (min_sal + max_sal) / 2
        
        # 匹配 "25000-30000" 格式
        num_match = re.search(r'(\d{4,5})\s*[-~]\s*\d{4,5}', salary_text)
        if num_match:
            monthly_salary = int(num_match.group(1)) / 1000  # 转换为k
        
        # 匹配单个数字 "25k"
        single_match = re.search(r'(\d+)[k千]', salary_text, re.IGNORECASE)
        if single_match:
            monthly_salary = int(single_match.group(1))
        
        # 评分
        if monthly_salary is None:
            return 10
        elif monthly_salary >= 25:
            return 30
        elif monthly_salary >= 20:
            return 25
        elif monthly_salary >= 15:
            return 20
        else:
            return 10

    def _evaluate_job_type(self, job_name: str) -> int:
        """
        岗位类型评分 (0-25分)
        
        评分规则:
        - Go后端开发、产品经理、数据分析师/工程师：25分
        - Java后端、前端开发、运营：15分
        - 其他：5分
        """
        if not job_name:
            return 5
        
        job_name_lower = job_name.lower()
        
        # 高价值岗位类型 (25分)
        for job_type in self.config.high_value_job_types:
            if job_type.lower() in job_name_lower:
                return 25
        
        # 中价值岗位类型 (15分)
        for job_type in self.config.medium_value_job_types:
            if job_type.lower() in job_name_lower:
                return 15
        
        # 检查是否包含"产品"关键词
        if '产品' in job_name:
            return 25
        
        # 其他 (5分)
        return 5

    def _evaluate_department(self, job_description: str) -> int:
        """
        部门含金量评分 (0-20分)
        
        评分规则:
        - 核心业务部门（如抖音、淘宝、微信支付）：20分
        - 一般业务部门：10分
        - 未明确：5分
        """
        if not job_description:
            return 5
        
        jd_lower = job_description.lower()
        
        # 核心业务部门 (20分)
        for dept in self.config.core_departments:
            if dept.lower() in jd_lower:
                return 20
        
        # 检查是否提到部门
        dept_keywords = ['部门', '事业部', '业务线', '团队']
        has_dept_info = any(kw in jd_lower for kw in dept_keywords)
        
        if has_dept_info:
            return 10  # 有部门信息但不是核心部门
        
        return 5  # 未明确

    def _evaluate_timeliness(self, publish_time: str) -> int:
        """
        发布时效性评分 (0-15分)
        
        评分规则:
        - 一周内发布：15分
        - 一个月内：10分
        - 超过一个月：5分
        """
        if not publish_time:
            return 10  # 默认中等分数
        
        try:
            # 尝试解析时间
            # 支持多种格式
            time_formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%Y/%m/%d %H:%M:%S',
                '%Y/%m/%d',
                '%m-%d',
                '%m月%d日'
            ]
            
            pub_date = None
            for fmt in time_formats:
                try:
                    pub_date = datetime.strptime(publish_time, fmt)
                    # 如果没有年份，假设为今年
                    if pub_date.year == 1900:
                        pub_date = pub_date.replace(year=datetime.now().year)
                    break
                except ValueError:
                    continue
            
            if pub_date is None:
                # 尝试相对时间
                if '小时前' in publish_time or '今天' in publish_time:
                    return 15
                elif '昨天' in publish_time or '天前' in publish_time:
                    days = re.search(r'(\d+)', publish_time)
                    if days and int(days.group(1)) <= 7:
                        return 15
                    else:
                        return 10
                elif '周前' in publish_time:
                    return 10
                elif '月前' in publish_time:
                    return 5
                else:
                    return 10
            
            # 计算时间差
            now = datetime.now()
            days_diff = (now - pub_date).days
            
            if days_diff <= 7:
                return 15
            elif days_diff <= 30:
                return 10
            else:
                return 5
                
        except Exception as e:
            logger.warning(f"解析发布时间失败: {e}")
            return 10

    def _evaluate_skill_match(self, requirements: str) -> int:
        """
        任职要求匹配度评分 (0-10分)
        
        评分规则:
        - 明确要求Go/产品/数据相关技能：10分
        - 未明确但相关：5分
        - 不相关：0分
        """
        if not requirements:
            return 5  # 未明确
        
        req_lower = requirements.lower()
        
        # 检查是否明确要求目标技能
        skill_found = False
        for skill in self.config.skill_keywords:
            if skill.lower() in req_lower:
                skill_found = True
                break
        
        if skill_found:
            return 10
        
        # 检查是否有技术要求
        tech_keywords = ['编程', '开发', '代码', '技术', '工程']
        has_tech = any(kw in req_lower for kw in tech_keywords)
        
        if has_tech:
            return 5  # 有技术要求但不明确
        
        return 0  # 不相关

    def get_stats(self) -> Dict[str, int]:
        """获取筛选统计信息"""
        return self.stats.copy()

    def get_tier_distribution(self, jobs: List[Dict[str, Any]]) -> Dict[str, int]:
        """获取公司等级分布统计"""
        distribution = {tier.value: 0 for tier in CompanyTier}
        
        for job in jobs:
            details = job.get('score_details', {})
            company_info = details.get('company', {})
            tier = company_info.get('tier', '未知')
            distribution[tier] = distribution.get(tier, 0) + 1
        
        return distribution

    def get_top_companies(self, jobs: List[Dict[str, Any]], top_n: int = 50) -> List[Dict[str, Any]]:
        """
        获取高价值公司清单（前N家）
        
        Returns:
            按公司总分排序的公司列表
        """
        company_scores = {}
        
        for job in jobs:
            company = job.get('company_name', 'Unknown')
            score = job.get('total_score', 0)
            
            if company not in company_scores:
                company_scores[company] = {
                    'name': company,
                    'total_score': 0,
                    'job_count': 0,
                    'high_value_jobs': 0
                }
            
            company_scores[company]['total_score'] += score
            company_scores[company]['job_count'] += 1
            
            if job.get('value_level') == JobValueLevel.HIGH.value:
                company_scores[company]['high_value_jobs'] += 1
        
        # 计算平均分并排序
        for company in company_scores.values():
            company['avg_score'] = company['total_score'] / company['job_count']
        
        sorted_companies = sorted(
            company_scores.values(),
            key=lambda x: x['avg_score'],
            reverse=True
        )
        
        return sorted_companies[:top_n]

    def get_top_jobs(self, jobs: List[Dict[str, Any]], top_n: int = 100) -> List[Dict[str, Any]]:
        """
        获取高价值岗位清单（前N个）
        
        Returns:
            按总分排序的岗位列表
        """
        sorted_jobs = sorted(jobs, key=lambda x: x.get('total_score', 0), reverse=True)
        return sorted_jobs[:top_n]
