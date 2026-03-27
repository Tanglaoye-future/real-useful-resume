

import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
import math
import logging
from logging import handlers
import random
try:
    from requests_html import HTMLSession
except Exception:
    HTMLSession = None

# 自动切换到脚本所在目录，保证相对路径读取csv文件无误
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs('logs', exist_ok=True)

logger = logging.getLogger('crawler')
logger.setLevel(logging.INFO)
if not logger.handlers:
    fh = handlers.RotatingFileHandler('logs/crawler.log', maxBytes=2_000_000, backupCount=3, encoding='utf-8')
    sh = logging.StreamHandler()
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fh.setFormatter(fmt)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'https://www.shixiseng.com/',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

USE_JS_RENDER = True
RETRY_MAX = 2
SLEEP_LIST = (2.0, 5.0)


def is_cookie_stale(resp_text, status):
    if status in (401, 403, 429, 500, 503):
        return True
    if not resp_text:
        return True
    # 反爬提示或结构缺失
    if 'verify' in resp_text.lower() or '访问过于频繁' in resp_text or '抱歉' in resp_text:
        return True
    soup = BeautifulSoup(resp_text, 'html.parser')
    if not soup.find('div', class_='job-content'):
        return True
    return False

def get_soup(url, use_render=False):
    t0 = time.time()
    try:
        if use_render and HTMLSession is not None and USE_JS_RENDER:
            hs = HTMLSession()
            r = hs.get(url, headers=HEADERS, timeout=20)
            r.html.render(timeout=20, sleep=1)
            text = r.html.html
            status = 200
        else:
            r = SESSION.get(url, timeout=15)
            r.encoding = 'utf-8'
            text = r.text
            status = r.status_code
        t1 = int((time.time() - t0) * 1000)
        logger.info(f'fetch url={url} status={status} ms={t1} cookies={len([c.name for c in SESSION.cookies])} render={use_render}')
        return BeautifulSoup(text, 'html.parser'), text, status
    except requests.RequestException as e:
        logger.warning(f'fetch error url={url} err={e}')
        return None, '', 0

def parse_job_page(url):
    result = {'url': url}
    
    # 第一次尝试：普通请求
    soup, text, status = get_soup(url, use_render=False)
    if soup is None or is_cookie_stale(text, status):
        logger.info('primary fetch looks stale -> bootstrap cookies and retry')
        bootstrap_cookies()
        time.sleep(random.uniform(*SLEEP_LIST))
        soup, text, status = get_soup(url, use_render=False)
    
    # 第二次尝试：如果仍然失败，使用JS渲染
    if soup is None or is_cookie_stale(text, status):
        logger.info('fallback to JS render')
        time.sleep(random.uniform(*SLEEP_LIST))
        soup, text, status = get_soup(url, use_render=True)
        
        # 如果JS渲染也失败，再次刷新cookie并重试
        if soup is None or is_cookie_stale(text, status):
            logger.info('JS render also failed -> refresh cookies and retry')
            bootstrap_cookies()
            time.sleep(random.uniform(*SLEEP_LIST))
            soup, text, status = get_soup(url, use_render=True)
    job_content = soup.find('div', class_='job-content') if soup else None
    if job_content:
        company_tag = job_content.find('div', class_='com-name')
        if not company_tag:
            company_tag = job_content.find('div', class_='com_intro')
        if not company_tag:
            company_tag = job_content.find('div', class_='job-about')
        result['company'] = company_tag.get_text(strip=True) if company_tag else None

        detail_tag = job_content.find('div', class_='job_detail')
        result['info'] = detail_tag.get_text(strip=True) if detail_tag else None

        city_tag = job_content.find('div', class_='con-job job_city')
        result['city'] = city_tag.get_text(strip=True) if city_tag else None

        name_tag = job_content.find('div', class_='job-about')
        if not name_tag:
            name_tag = job_content.find('div', class_='title')
        result['name'] = name_tag.get_text(strip=True) if name_tag else None

        salary_tag = job_content.find('span', class_='salary')
        result['salary'] = salary_tag.get_text(strip=True) if salary_tag else None

        company_intro_tag = job_content.find('div', class_='com_intro')
        if not company_intro_tag:
            company_intro_tag = job_content.find('div', class_='job-about')
        company_intro_text = company_intro_tag.get_text(strip=True) if company_intro_tag else ''
        size_match = re.search(r'(\d+\s*-\s*\d+人|少于\d+人|\d+人以上)', company_intro_text)
        if not size_match:
            size_match = re.search(r'(\d+\s*-\s*\d+人|少于\d+人|\d+人以上)', str(company_intro_tag))
        result['company_size'] = size_match.group(1).replace(' ', '') if size_match else None

        if result.get('info'):
            week_days = re.search(r'(每周[出勤上班工作]?[：: ]?(\d{1,2})天)', result['info'])
            months = re.search(r'(实习|连续实习|至少实习|不少于|可实习|实习期为)?([一二三四五六七八九十\d]{1,3})个月', result['info'])
            weeks = re.search(r'([一二三四五六七八九十\d]{1,3})周', result['info'])
            days = re.search(r'([一二三四五六七八九十\d]{1,3})天', result['info'])

            duration_list = []
            if week_days:
                duration_list.append(week_days.group(0))
            if months:
                duration_list.append(months.group(0))
            if weeks:
                duration_list.append(weeks.group(0))
            if days and (not week_days or days.group(0) != week_days.group(2) + '天'):
                duration_list.append(days.group(0))

            result['duration'] = '，'.join(duration_list) if duration_list else None

            m2 = re.search(r'(本科及以上|硕士及以上|大专及以上|不限学历|本科|硕士|大专)', result['info'])
            result['academic'] = m2.group(1) if m2 else None
        else:
            result['duration'] = None
            result['academic'] = None
    else:
        result['company'] = result['info'] = result['city'] = result['name'] = result['salary'] = result['duration'] = result['academic'] = None

    return result

def is_complete(item):
    # 检查关键字段是否完整：公司信息、职位描述、薪资、城市、职位名称
    ok = bool(item.get('company')) and bool(item.get('info')) and bool(item.get('salary')) and bool(item.get('city')) and bool(item.get('name'))
    return ok

# 读取新的csv文件，假设url列名为'url'
    csv_file = 'urls_and_companies_上海_first_100_pages.csv'
    df = pd.read_csv(csv_file)
    urls = df['url'].tolist()
    total = len(urls)
    batch_size = 100
    num_batches = math.ceil(total / batch_size)

    bootstrap_cookies()
    for batch_idx in range(num_batches):
        start = batch_idx * batch_size
        end = min((batch_idx + 1) * batch_size, total)
        batch_urls = urls[start:end]
        batch_results = []
        print(f'正在处理第{batch_idx+1}批（{start+1}-{end}）...')
        
        # 每批开始时刷新cookie，防止长时间运行cookie过期
        bootstrap_cookies()
        
        for i, url in enumerate(batch_urls):
            try:
                logger.info(f'Processing {start+i+1}/{total}: {url}')
                result = parse_job_page(url)
                
                # 如果数据不完整，进行重试
                if not is_complete(result):
                    logger.warning(f'Incomplete data -> retrying url={url}')
                    for retry_count in range(RETRY_MAX):
                        time.sleep(random.uniform(*SLEEP_LIST))
                        logger.info(f'Retry {retry_count+1} for {url}')
                        result = parse_job_page(url)
                        if is_complete(result):
                            logger.info(f'Retry successful for {url}')
                            break
                        else:
                            logger.warning(f'Still incomplete after retry {retry_count+1}')
                
                # 即使重试后仍不完整，也记录但标记
                if not is_complete(result):
                    logger.error(f'FAILED to get complete data for {url}')
                    result['_status'] = 'incomplete'
                else:
                    result['_status'] = 'complete'
                
                batch_results.append(result)
                time.sleep(random.uniform(*SLEEP_LIST))
                
                # 每处理10个URL后刷新一次cookie
                if (i + 1) % 10 == 0:
                    logger.info('Refreshing cookies after 10 URLs')
                    bootstrap_cookies()
                    
            except Exception as e:
                logger.error(f'Error for {url}: {e}')
                error_result = {'url': url, '_status': 'error', 'error': str(e)}
                batch_results.append(error_result)
                continue

        out_file = f'internship_results_{start+1}_{end}.csv'
        pd.DataFrame(batch_results).to_csv(out_file, index=False, encoding='utf-8-sig')
        
        # 统计本批次的成功率
        complete_count = sum(1 for r in batch_results if r.get('_status') == 'complete')
        incomplete_count = sum(1 for r in batch_results if r.get('_status') == 'incomplete')
        error_count = sum(1 for r in batch_results if r.get('_status') == 'error')
        
        logger.info(f'第{batch_idx+1}批已完成: {complete_count}成功, {incomplete_count}不完整, {error_count}错误 -> {out_file}')
        
        # 批次间休息更长时间，避免被封
        if batch_idx < num_batches - 1:
            sleep_time = random.uniform(10, 20)
            logger.info(f'等待{sleep_time:.1f}秒后处理下一批...')
            time.sleep(sleep_time)
            
    logger.info('全部完成！')
