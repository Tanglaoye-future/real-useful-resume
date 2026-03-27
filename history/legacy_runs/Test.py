import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import csv

# 读取之前爬到的 URL 列表
df = pd.read_csv('urls for internships.csv')
urls = df['url']

# 打开 CSV 文件准备写入数据
with open('internship data.csv', 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file)
    # 写入表头
    colnames = ['name', 'company', 'city', 'day', 'salary', 'academic', 'duration',
                'industry', 'company_size', 'good_list', 'info']
    writer.writerow(colnames)

# 请求头
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
}

i = 0  # 计数器

# 开始遍历每个实习链接
for url in urls:
    try:
        response = requests.get(url, headers=header, timeout=10)
        if response.status_code != 200:
            print(f"访问失败: {url}")
            continue

        text = response.text
        soup = BeautifulSoup(text, 'html.parser')

        # 职位名称
        name_tag = soup.select_one('.job-name span.new_job_name')
        name = name_tag.text.strip() if name_tag else None

        # 公司名称
        company_tag = soup.select_one('.com-name')
        company = company_tag.text.strip() if company_tag else None

        # 城市、薪资、学历、出勤天数、实习时长
        job_info_tag = soup.select_one('.job-msg')
        if job_info_tag:
            info_texts = [item.text.strip() for item in job_info_tag.find_all('span')]
            city, salary, academic, day, duration = None, None, None, None, None
            for idx, text in enumerate(info_texts):
                if "元/天" in text:
                    salary = text
                elif any(s in text for s in ["本科", "硕士", "博士"]):
                    academic = text
                elif "/" in text and "周" in text:
                    day = text
                elif "实习" in text and "个月" in text:
                    duration = text
                else:
                    city = text
            
        # 福利标签
        good_tags = soup.select('.job_good_list span')
        good_list = [tag.text.strip() for tag in good_tags] if good_tags else []

        # 行业和公司规模
        intro_tags = soup.select('.com-desc li')
        industry, company_size = None, None
        for tag in intro_tags:
            if "行业" in tag.text:
                industry = tag.text.replace("行业", "").strip()
            elif "规模" in tag.text:
                company_size = tag.text.replace("规模", "").strip()

        # 岗位描述
        info_tag = soup.select_one('.job-detail .content')
        info = info_tag.text.strip() if info_tag else None

        # 构建数据列表
        row = [
            name,
            company,
            city,
            day,
            salary,
            academic,
            duration,
            industry,
            company_size,
            ', '.join(good_list) if good_list else None,
            info
        ]

        with open('internship data.csv', 'a', encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)
        i += 1

        if i % 100 == 0:
            time.sleep(5)
            print(f'已处理 {i} 个岗位')

    except Exception as e:
        print(f"处理 {url} 出错: {e}")

print("✅ 数据抓取完成！")