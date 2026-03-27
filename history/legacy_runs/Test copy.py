import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import csv

# 读取URL列表
df = pd.read_csv('urls for internships.csv')
urls = df['url']

# 初始化写入器
results = []

# 使用一个标准的 User-Agent（可手动替换为其他浏览器标识）
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
}

# 定义字段映射关系
FIELD_MAP = {
    'name': None,
    'company': None,
    'city': None,
    'day': None,
    'salary': None,
    'academic': None,  # 注意：你提供的HTML中未包含学历信息
    'duration': None,
    'industry': None,
    'company_size': None,  # 注意：你提供的HTML中未包含公司规模信息
    'good_list': [],
    'info': None
}

for idx, url in enumerate(urls, 1):
    try:
        # 随机延迟（1-3秒），避免触发反爬
        time.sleep(random.uniform(1, 3))

        response = requests.get(url, headers=header, timeout=10)
        if response.status_code != 200:
            print(f"访问失败: {url}")
            continue

        # 保存部分HTML内容用于调试，每个URL单独保存，避免覆盖
        debug_filename = f"debug_response_{idx}.html"
        with open(debug_filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"已保存 {url} 的部分HTML到 {debug_filename}")
        print("部分HTML内容预览：")
        print(response.text[:1000])  # 打印前1000字符，避免刷屏

        soup = BeautifulSoup(response.text, 'html.parser')

        # 初始化字段值
        field_values = FIELD_MAP.copy()

        # 提取职位名称
        name_tag = soup.select_one('.job-title .title')
        field_values['name'] = name_tag.text.strip() if name_tag else None

        # 提取公司名称
        company_tag = soup.select_one('.company-name')
        field_values['company'] = company_tag.text.strip() if company_tag else None

        # 提取城市、工作天数、实习时长
        job_detail = soup.select('.job-detail .content')
        for item in job_detail:
            text = item.text.strip()
            if "个月" in text:
                field_values['duration'] = text
            elif "/" in text and "周" in text:
                field_values['day'] = text
            else:
                field_values['city'] = text

        # 提取薪资
        salary_tag = soup.select_one('.salary')
        field_values['salary'] = salary_tag.text.strip() if salary_tag else None

        # 提取福利标签
        good_tags = soup.select('.job-tags-text')
        field_values['good_list'] = [tag.text.strip() for tag in good_tags] if good_tags else []

        # 提取行业信息
        industry_tag = soup.select_one('.company-detail span')
        field_values['industry'] = industry_tag.text.strip() if industry_tag else None

        # 提取岗位描述（需根据实际页面结构调整选择器）
        info_tag = soup.select_one('.job-description')  # 示例选择器，请根据实际页面调整
        field_values['info'] = info_tag.text.strip() if info_tag else None

        results.append(field_values)

        # 每100条批量写入CSV
        if len(results) % 100 == 0:
            df_result = pd.DataFrame(results)
            df_result.to_csv('internship_data.csv', mode='a', header=False, index=False, encoding='utf-8-sig')
            results = []

    except Exception as e:
        print(f"处理 {url} 出错: {e}")

# 写入剩余数据
if results:
    df_result = pd.DataFrame(results)
    df_result.to_csv('internship_data.csv', mode='a', header=False, index=False, encoding='utf-8-sig')

print("✅ 数据抓取完成！")