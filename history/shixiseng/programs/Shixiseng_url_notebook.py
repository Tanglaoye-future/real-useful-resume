import pandas as pd
import requests
import time
import random
import os
import urllib.parse
from bs4 import BeautifulSoup
import re
try:
    from IPython.display import display
    HAS_IPY = True
except Exception:
    HAS_IPY = False

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
header = {'User-Agent': USER_AGENT}

def crawl_listing_urls(search_keyword: str, start_page: int, pages_to_fetch: int) -> pd.DataFrame:
    encoded_kw = urllib.parse.quote(search_keyword)
    end_page = start_page + pages_to_fetch - 1
    print(f"\n正在抓取: {search_keyword}")
    print(f"起始页: {start_page}")
    print(f"抓取页数: {pages_to_fetch}")
    data = []
    for i in range(start_page, end_page + 1):
        url_of_page_i = f'https://www.shixiseng.com/interns?page={i}&type=intern&keyword={encoded_kw}&area=&months=&days=&degree=&official=&enterprise=&salary=-0&publishTime=&sortType=&city=%E5%85%A8%E5%9B%BD&internExtend='
        try:
            response = requests.get(url_of_page_i, headers=header, timeout=10)
            if response.status_code != 200:
                print(f"列表页 {i} 状态码: {response.status_code}")
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.select('a[href*="/intern/"]')
            for link in links:
                url = link.get('href')
                if not url:
                    continue
                if url.startswith('/intern/'):
                    url = 'https://www.shixiseng.com' + url
                if 'pcm=pc_SearchList' not in url:
                    continue
                try:
                    detail_response = requests.get(url, headers=header, timeout=10)
                    if detail_response.status_code != 200:
                        print(f"详情页错误: {url}")
                        continue
                    detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                    company_tag = detail_soup.select_one('.com_intro .com-name') or detail_soup.select_one('.com-name')
                    company_name = company_tag.get_text(strip=True) if company_tag else 'Unknown'
                    city_tag = detail_soup.find('div', class_='job_msg') or detail_soup.find('div', class_='job_city')
                    city_text = city_tag.get_text(strip=True) if city_tag else ''
                    data.append({'url': url, 'company_name': company_name, 'city': city_text})
                    print(f"已处理: {url}")
                    time.sleep(random.uniform(0.5, 1))
                except Exception as e:
                    print(f"详情页异常: {e}")
            if i % 10 == 0:
                print(f"已处理 {i} 页, 累计 {len(data)} 条")
                time.sleep(random.uniform(2, 5))
        except Exception as e:
            print(f"列表页异常 {i}: {e}")
    df = pd.DataFrame(data)
    return df

def _extract_text(soup, selectors):
    for sel in selectors:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    return ''

def _extract_by_regex(texts, patterns):
    for t in texts:
        if not t:
            continue
        s = t.strip()
        for p in patterns:
            m = re.search(p, s)
            if m:
                return m.group(0)
    return ''

def crawl_details_from_urls(df_urls: pd.DataFrame) -> pd.DataFrame:
    rows = []
    print("\n开始爬取详情数据")
    for idx, row in df_urls.iterrows():
        url = row.get('url')
        if not url:
            continue
        try:
            resp = requests.get(url, headers=header, timeout=10)
            if resp.status_code != 200:
                print(f"详情页状态码异常: {resp.status_code} {url}")
                continue
            soup = BeautifulSoup(resp.text, 'html.parser')
            job_title = _extract_text(soup, ['.job_name', '.job-name', '.job-title', 'h1', 'h2'])
            company_name = _extract_text(soup, ['.com_intro .com-name', '.com-name']) or row.get('company_name', '')
            city_text = _extract_text(soup, ['div.job_msg', 'div.job_city']) or row.get('city', '')
            salary_text = _extract_text(soup, ['.job_money', '.job-salary', '.salary'])
            if not salary_text:
                salary_text = _extract_by_regex([soup.get_text()], [r'\d+[kK]\s*/\s*月', r'\d+\s*元\s*/\s*天', r'\d+\s*元\s*/\s*小时'])
            publish_time = _extract_text(soup, ['.release_time', '.job-date', '.time'])
            address = _extract_text(soup, ['.job_address', '.job-addr', '.address'])
            desc = _extract_text(soup, ['.job_detail', '.job-detail', '.job_des', '.job-text', '.description'])
            if len(desc) > 300:
                desc = desc[:300]
            rows.append({
                'url': url,
                'job_title': job_title,
                'company_name': company_name,
                'city': city_text,
                'salary': salary_text,
                'publish_time': publish_time,
                'address': address,
                'description': desc
            })
            print(f"详情完成: {url}")
            time.sleep(random.uniform(0.5, 1))
        except Exception as e:
            print(f"详情页异常: {e}")
        if (idx + 1) % 20 == 0:
            print(f"已完成 {idx + 1} 条详情, 总计 {len(rows)} 条")
            time.sleep(random.uniform(2, 5))
    return pd.DataFrame(rows)

SEARCH_KEYWORD = "上海"
START_PAGE = 1
PAGES_TO_FETCH = 20
SAVE_TO_CSV = False

df_urls = crawl_listing_urls(SEARCH_KEYWORD, START_PAGE, PAGES_TO_FETCH)

end_page = START_PAGE + PAGES_TO_FETCH - 1
if SAVE_TO_CSV:
    output_filename_urls = f'urls_and_companies_{SEARCH_KEYWORD}_pages_{START_PAGE}_to_{end_page}.csv'
    output_path_urls = os.path.join(os.getcwd(), output_filename_urls)
    df_urls.to_csv(output_path_urls, index=False, encoding='utf-8-sig')
    print(f"URL列表保存位置: {output_path_urls}")
print(f"总计采集URL: {len(df_urls)} 条")
if HAS_IPY:
    display(df_urls.head(20))
else:
    print(df_urls.head(20))

df_details = crawl_details_from_urls(df_urls)
if SAVE_TO_CSV:
    output_filename_details = f'details_{SEARCH_KEYWORD}_pages_{START_PAGE}_to_{end_page}.csv'
    output_path_details = os.path.join(os.getcwd(), output_filename_details)
    df_details.to_csv(output_path_details, index=False, encoding='utf-8-sig')
    print(f"详情保存位置: {output_path_details}")
print(f"总计采集详情: {len(df_details)} 条")
if HAS_IPY:
    display(df_details.head(20))
else:
    print(df_details.head(20))
