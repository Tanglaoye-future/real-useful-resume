"""
技能提取器模块

从岗位信息中自动提取技能标签
"""

import re
import logging
from typing import List, Set, Dict

logger = logging.getLogger(__name__)


class SkillExtractor:
    """技能提取器"""

    # 技能关键词库 - 按类别组织
    SKILL_KEYWORDS = {
        # 编程语言
        'languages': [
            'Python', 'Java', 'Go', 'Golang', 'C++', 'C', 'C#', 'Rust',
            'JavaScript', 'JS', 'TypeScript', 'TS', 'PHP', 'Ruby', 'Swift',
            'Kotlin', 'Scala', 'R', 'MATLAB', 'Shell', 'Bash', 'SQL',
        ],
        # 前端技术
        'frontend': [
            'Vue', 'Vue.js', 'React', 'ReactJS', 'Angular', 'HTML', 'CSS',
            'jQuery', 'Bootstrap', 'ElementUI', 'Ant Design', 'Webpack',
            'Vite', 'Node.js', 'NodeJS', '前端', 'Frontend',
        ],
        # 后端框架
        'backend': [
            'Spring', 'Spring Boot', 'SpringBoot', 'SpringCloud', 'Django',
            'Flask', 'FastAPI', 'Tornado', 'Express', 'Koa', 'NestJS',
            'MyBatis', 'Hibernate', '后端', 'Backend',
        ],
        # 数据库
        'database': [
            'MySQL', 'PostgreSQL', 'Oracle', 'SQL Server', 'MongoDB',
            'Redis', 'Elasticsearch', 'ES', 'ClickHouse', 'TiDB',
            'SQLite', 'MariaDB', 'DynamoDB', 'Cassandra', 'Neo4j',
        ],
        # 大数据/数据工程
        'data_engineering': [
            'Hadoop', 'Spark', 'Flink', 'Kafka', 'Hive', 'HBase',
            'Storm', 'Zookeeper', '数据仓库', 'ETL', '数据挖掘',
            '数据分析', '数据工程', '数据管道', '数据治理',
        ],
        # AI/机器学习
        'ai_ml': [
            '机器学习', '深度学习', 'AI', '人工智能', 'NLP', '计算机视觉',
            'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas',
            'NumPy', 'OpenCV', '模型部署', '大模型', 'LLM',
        ],
        # 爬虫/数据采集
        'crawler': [
            '爬虫', '数据采集', '数据抓取', 'Scrapy', 'Selenium',
            'Playwright', 'BeautifulSoup', '反爬', '逆向',
        ],
        # 运维/DevOps
        'devops': [
            'Linux', 'Docker', 'Kubernetes', 'K8s', 'Jenkins', 'GitLab CI',
            'GitHub Actions', 'Ansible', 'Terraform', 'Prometheus',
            'Grafana', 'ELK', 'Nginx', '运维', 'DevOps', 'SRE',
        ],
        # 云服务
        'cloud': [
            'AWS', '阿里云', '腾讯云', '华为云', 'Azure', 'GCP',
            '云计算', '云原生', 'Serverless', '微服务',
        ],
        # 版本控制/工具
        'tools': [
            'Git', 'SVN', 'GitHub', 'GitLab', 'Bitbucket',
            'Jira', 'Confluence', '禅道', 'Maven', 'Gradle',
            'npm', 'pip', 'conda', 'Makefile',
        ],
        # 测试
        'testing': [
            '测试', '单元测试', '集成测试', '自动化测试', 'Selenium',
            'JUnit', 'Pytest', 'Jest', 'Postman', 'JMeter',
        ],
        # 产品相关
        'product': [
            '产品', '产品经理', 'PM', '产品设计', '产品规划', '需求分析',
            '用户研究', '竞品分析', '原型设计', 'Axure', 'Figma', 'Sketch',
            'PRD', '产品文档', '数据分析', '数据产品', 'B端产品', 'C端产品',
            '增长', '运营', '策略产品', '商业化', '用户体验', 'UX',
        ],
        # 财务/金融相关
        'finance': [
            '财务', '会计', '审计', '金融', '投资', '理财', '证券',
            '基金', '银行', '保险', '风控', '合规', '财务分析',
            '财务报表', '成本管理', '预算', '税务', 'CPA', 'CFA',
            'ACCA', 'CMA', '中级会计', '初级会计', '财务建模',
            '估值', '尽调', 'IPO', '并购', '融资', '资金管理',
        ],
        # 其他技术
        'others': [
            'RESTful', 'API', 'GraphQL', 'gRPC', 'WebSocket',
            'RPC', '消息队列', 'MQ', 'RabbitMQ', 'RocketMQ',
            '高并发', '分布式', '负载均衡', '缓存', 'CDN',
            '设计模式', '算法', '数据结构',
        ],
    }

    # 技能同义词映射
    SKILL_SYNONYMS = {
        'Python': ['Python', 'python', 'py', 'Python编程', 'Python开发'],
        'Java': ['Java', 'java', 'Java编程', 'Java开发'],
        'Go': ['Go', 'Golang', 'go', 'Golang开发', 'Go语言'],
        'Vue': ['Vue', 'Vue.js', 'vue', 'Vue2', 'Vue3'],
        'React': ['React', 'ReactJS', 'react', 'React.js'],
        'Spring Boot': ['Spring Boot', 'SpringBoot', 'springboot'],
        'MySQL': ['MySQL', 'mysql', 'MySql'],
        'Redis': ['Redis', 'redis'],
        '爬虫': ['爬虫', '数据采集', '数据抓取', '网络爬虫'],
        'AI': ['AI', '人工智能', '机器学习', '深度学习', '模型部署'],
        'Docker': ['Docker', 'docker', '容器'],
        'Kubernetes': ['Kubernetes', 'K8s', 'k8s'],
    }

    # 技术岗位关键词
    TECH_JOB_KEYWORDS = [
        '开发', '工程师', '研发', '程序员', '架构师', '算法',
        'DevOps', 'SRE', '测试', '运维', '技术', 'IT',
        'Java', 'Python', '前端', '后端', '全栈', '数据分析',
        'AI', '人工智能', '爬虫', '数据挖掘', '大数据',
    ]

    # 产品岗位关键词
    PRODUCT_JOB_KEYWORDS = [
        '产品', '产品经理', 'PM', '产品专员', '产品助理',
        '产品运营', '策略产品', '数据产品', '商业产品',
        '用户研究', '需求分析', '产品设计',
    ]

    # 财务/金融岗位关键词
    FINANCE_JOB_KEYWORDS = [
        '财务', '会计', '审计', '金融', '投资', '理财',
        '证券', '基金', '银行', '保险', '风控', '合规',
        '财务分析', '财务BP', '财务产品', '金融产品经理',
    ]

    # 目标岗位类型（技术 + 产品 + 财务相关）
    TARGET_JOB_KEYWORDS = TECH_JOB_KEYWORDS + PRODUCT_JOB_KEYWORDS + FINANCE_JOB_KEYWORDS

    # 非技术岗位关键词（用于排除）
    NON_TECH_KEYWORDS = [
        '销售', '市场', '运营', '人事', 'HR', '行政', '财务',
        '客服', '助理', '文员', '前台', '保安', '保洁',
        '主播', '模特', '演员', '歌手', '舞蹈', '礼仪',
        '送餐', '快递', '外卖', '司机', '普工', '操作工',
    ]

    def __init__(self):
        # 构建所有技能的集合
        self.all_skills = set()
        for category_skills in self.SKILL_KEYWORDS.values():
            self.all_skills.update(category_skills)

        # 构建同义词反向映射
        self.synonym_to_standard = {}
        for standard, synonyms in self.SKILL_SYNONYMS.items():
            for syn in synonyms:
                self.synonym_to_standard[syn.lower()] = standard

    def extract_from_text(self, text: str) -> List[str]:
        """
        从文本中提取技能标签

        Args:
            text: 输入文本

        Returns:
            技能标签列表
        """
        if not text:
            return []

        text_lower = text.lower()
        found_skills = set()

        # 1. 直接匹配技能关键词
        for skill in self.all_skills:
            # 使用单词边界匹配
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                # 转换为标准名称
                standard = self.synonym_to_standard.get(skill.lower(), skill)
                found_skills.add(standard)

        # 2. 匹配同义词
        for synonym, standard in self.synonym_to_standard.items():
            if synonym in text_lower:
                found_skills.add(standard)

        return list(found_skills)

    def extract_from_job(self, job: Dict) -> List[str]:
        """
        从岗位数据中提取技能标签

        Args:
            job: 岗位数据字典

        Returns:
            技能标签列表
        """
        # 合并所有文本字段
        texts = []

        # 岗位名称
        job_name = job.get('job_name', '')
        if job_name:
            texts.append(job_name)

        # 岗位描述
        job_desc = job.get('job_description', '')
        if job_desc:
            texts.append(job_desc)

        # 岗位要求
        job_req = job.get('job_requirement', '')
        if job_req:
            texts.append(job_req)

        # JD 内容（原始 HTML 或文本）
        jd_content = job.get('jd_content', '')
        if jd_content:
            texts.append(jd_content)

        # 技能标签字段（如果已有）
        existing_tags = job.get('skill_tags', [])
        if isinstance(existing_tags, str):
            # 如果是字符串，尝试解析
            try:
                import json
                existing_tags = json.loads(existing_tags.replace("'", '"'))
            except:
                existing_tags = [tag.strip() for tag in existing_tags.split(',') if tag.strip()]

        # 合并所有文本
        combined_text = ' '.join(texts)

        # 提取技能
        extracted_skills = self.extract_from_text(combined_text)

        # 合并已有标签和提取的标签
        all_skills = set(extracted_skills)
        if isinstance(existing_tags, list):
            all_skills.update(existing_tags)

        return list(all_skills)

    def is_target_job(self, job: Dict) -> tuple:
        """
        判断是否为目标岗位（技术/产品/财务相关）

        Args:
            job: 岗位数据

        Returns:
            (是否匹配, 岗位类型, 匹配关键词)
        """
        job_name = job.get('job_name', '').lower()
        job_desc = job.get('job_description', '').lower()

        combined_text = job_name + ' ' + job_desc

        # 检查岗位类型
        job_type = None
        matched_keywords = []

        # 1. 检查技术岗
        for keyword in self.TECH_JOB_KEYWORDS:
            if keyword.lower() in combined_text:
                job_type = 'tech'
                matched_keywords.append(keyword)
                break

        # 2. 检查产品岗
        if not job_type:
            for keyword in self.PRODUCT_JOB_KEYWORDS:
                if keyword.lower() in combined_text:
                    job_type = 'product'
                    matched_keywords.append(keyword)
                    break

        # 3. 检查财务/金融岗
        if not job_type:
            for keyword in self.FINANCE_JOB_KEYWORDS:
                if keyword.lower() in combined_text:
                    job_type = 'finance'
                    matched_keywords.append(keyword)
                    break

        # 4. 如果没有明确匹配，检查技能标签
        if not job_type:
            skills = self.extract_from_job(job)
            tech_skills = [s for s in skills if self._get_skill_category(s) in 
                          ['languages', 'frontend', 'backend', 'ai_ml', 'data_engineering']]
            product_skills = [s for s in skills if self._get_skill_category(s) == 'product']
            finance_skills = [s for s in skills if self._get_skill_category(s) == 'finance']

            if tech_skills:
                job_type = 'tech'
                matched_keywords.extend(tech_skills[:2])
            elif product_skills:
                job_type = 'product'
                matched_keywords.extend(product_skills[:2])
            elif finance_skills:
                job_type = 'finance'
                matched_keywords.extend(finance_skills[:2])

        return (job_type is not None, job_type, matched_keywords)

    def _get_skill_category(self, skill: str) -> str:
        """获取技能所属类别"""
        normalized = self.normalize_skill(skill)
        for cat, skills in self.SKILL_KEYWORDS.items():
            if normalized in skills:
                return cat
        return 'others'

    def is_tech_job(self, job: Dict) -> bool:
        """
        判断是否为技术岗位（向后兼容）
        """
        is_match, job_type, _ = self.is_target_job(job)
        return is_match and job_type == 'tech'

    def normalize_skill(self, skill: str) -> str:
        """
        将技能名称归一化为标准名称

        Args:
            skill: 技能名称

        Returns:
            标准技能名称
        """
        skill_lower = skill.lower()
        return self.synonym_to_standard.get(skill_lower, skill)

    def calculate_skill_match(self, resume_skills: List[str], job_skills: List[str]) -> float:
        """
        计算技能匹配度

        Args:
            resume_skills: 简历技能列表
            job_skills: 岗位技能列表

        Returns:
            匹配度分数 (0-1)
        """
        if not job_skills:
            return 0.3  # 岗位没有技能要求，给予基础分 0.3，避免非技术岗得分过高

        if not resume_skills:
            return 0.0

        # 归一化技能名称
        normalized_resume = set(self.normalize_skill(s) for s in resume_skills)
        normalized_job = set(self.normalize_skill(s) for s in job_skills)

        # 计算匹配数量
        matched = normalized_resume & normalized_job

        # 计算匹配度
        match_ratio = len(matched) / len(normalized_job)

        # 如果有核心技能匹配，给予加分
        core_skills = {'Python', 'Java', 'Go', '爬虫', 'AI', '数据分析'}
        core_matched = matched & core_skills
        if core_matched:
            bonus = len(core_matched) * 0.05  # 每个核心技能加 5%
            match_ratio = min(1.0, match_ratio + bonus)

        return match_ratio

    def get_skill_categories(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        按类别组织技能

        Args:
            skills: 技能列表

        Returns:
            按类别分组的技能字典
        """
        categories = {cat: [] for cat in self.SKILL_KEYWORDS.keys()}
        categories['others'] = []

        for skill in skills:
            normalized = self.normalize_skill(skill)
            found = False
            for cat, cat_skills in self.SKILL_KEYWORDS.items():
                if normalized in cat_skills:
                    categories[cat].append(normalized)
                    found = True
                    break
            if not found:
                categories['others'].append(normalized)

        return categories
