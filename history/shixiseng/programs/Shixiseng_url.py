import pandas as pd
import requests
import time
import random
import os
from bs4 import BeautifulSoup

# 请求头
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
}

data = []  # 用于保存 url 和 company name

# 多公司批量抓取
target_companies = [
    "腾讯", "字节跳动", "阿里巴巴", "百度", "小米", "京东", "美团", "拼多多", "快手", "哔哩哔哩", "360", "小红书", "滴滴", "知乎", "微博", "搜狗", "商汤科技", "旷视科技", "依图科技", "寒武纪", "地平线", "大疆创新", "科大讯飞", "蔚来", "小鹏汽车", "理想汽车", "比亚迪", "宁德时代", "特斯拉", "华为", "中兴通讯", "海康威视", "大华股份", "烽火通信", "奇虎360", "美团云", "商汤科技", "旷视科技", "依图科技", "寒武纪", "地平线", "科大讯飞", "大疆创新", "海康威视", "大华股份", "烽火通信", "中芯国际", "台积电（中国大陆业务）", "海思半导体", "紫光集团", "长江存储", "京东方", "TCL华星", "美的集团", "海尔智家", "格力电器", "比亚迪半导体", "宁德时代", "蔚来", "小鹏汽车", "理想汽车", "特斯拉", "比亚迪", "宁德时代", "大疆创新", "科大讯飞", "商汤科技", "旷视科技", "依图科技", "寒武纪", "地平线", "海康威视", "大华股份", "中芯国际", "台积电", "海思半导体", "紫光集团", "长江存储", "京东方", "TCL华星", "美的集团", "海尔智家", "格力电器"
]
data = []

for company_keyword in target_companies:
    search_keyword = f"上海 {company_keyword}"
    encoded_search_keyword = requests.utils.quote(search_keyword)
    print(f"\n🔍 正在抓取公司: {company_keyword} 上海地区")
    for i in range(1, 7):
        url_of_page_i = f'https://www.shixiseng.com/interns?page={i}&type=intern&keyword={encoded_search_keyword}&area=&months=&days=&degree=&official=&enterprise=&salary=-0&publishTime=&sortType=&city=%E5%85%A8%E5%9B%BD&internExtend='
        try:
            response = requests.get(url_of_page_i, headers=header, timeout=10)
            if response.status_code != 200:
                print(f"Page {i} returned status code: {response.status_code}")
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.select('a[href*="/intern/"]')
            for link_idx, link in enumerate(links):
                if link_idx >= 5:
                    break
                url = link.get('href')
                if url.startswith('/intern/'):
                    url = 'https://www.shixiseng.com' + url
                if 'pcm=pc_SearchList' in url:
                    try:
                        detail_response = requests.get(url, headers=header, timeout=10)
                        if detail_response.status_code != 200:
                            print(f"Detail page error: {url}")
                            continue
                        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                        company_tag = detail_soup.select_one('.com_intro .com-name')
                        if not company_tag:
                            company_tag = detail_soup.select_one('.com-name')
                        company_name = company_tag.get_text(strip=True) if company_tag else 'Unknown'
                        city_tag = detail_soup.find('div', class_='job_msg')
                        if not city_tag:
                            city_tag = detail_soup.find('div', class_='job_city')
                        city_text = city_tag.get_text(strip=True) if city_tag else ''
                        if company_keyword in company_name:
                            data.append({
                                'url': url,
                                'company_name': company_name,
                                'city': city_text
                            })
                        print(f"已处理: {url}")
                        time.sleep(random.uniform(0.5, 1))
                    except Exception as e:
                        print(f"Error fetching detail page {url}: {e}")
            if i % 5 == 0:
                print(f"Processed {i} pages for {company_keyword}, total URLs collected: {len(data)}")
                time.sleep(random.uniform(2, 5))
        except Exception as e:
            print(f"Error on summary page {i}: {e}")

# 保存为 CSV 文件
df = pd.DataFrame(data)
output_path = os.path.join(os.getcwd(), f'urls_and_companies_{search_keyword}_first_100_pages.csv')
df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"✅ Crawling completed. Saved to: {output_path}")