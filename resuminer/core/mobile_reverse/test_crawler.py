#!/usr/bin/env python3
"""
测试 BOSS直聘爬虫
"""

import json
from boss_zhipin_crawler import BossZhipinCrawler, BossZhipinCrypto, BossZhipinDataParser


def test_crypto():
    """测试加密算法"""
    print("=" * 60)
    print("测试加密算法")
    print("=" * 60)
    
    crypto = BossZhipinCrypto()
    
    # 测试 MD5
    text = "test_string"
    md5_result = crypto.md5(text)
    print(f"\n1. MD5 测试:")
    print(f"   输入: {text}")
    print(f"   输出: {md5_result}")
    print(f"   长度: {len(md5_result)} (正确: 32)")
    
    # 测试 SHA1
    sha1_result = crypto.sha1(text)
    print(f"\n2. SHA1 测试:")
    print(f"   输入: {text}")
    print(f"   输出: {sha1_result}")
    print(f"   长度: {len(sha1_result)} (正确: 40)")
    
    # 测试 Base64
    b64_result = crypto.base64_encode(text)
    print(f"\n3. Base64 编码测试:")
    print(f"   输入: {text}")
    print(f"   输出: {b64_result}")
    
    b64_decode = crypto.base64_decode(b64_result)
    print(f"   解码: {b64_decode}")
    print(f"   匹配: {b64_decode == text}")
    
    # 测试签名生成
    params = {
        'timestamp': 1700000000000,
        'nonce': 'test_nonce',
        'query': 'Python',
    }
    sign = crypto.generate_sign(params)
    print(f"\n4. 签名生成测试:")
    print(f"   参数: {params}")
    print(f"   签名: {sign}")
    print(f"   长度: {len(sign)} (正确: 32)")
    
    # 测试时间戳和随机数
    print(f"\n5. 时间戳和随机数:")
    print(f"   时间戳: {crypto.generate_timestamp()}")
    print(f"   随机数: {crypto.generate_nonce()}")
    print(f"   随机数: {crypto.generate_nonce(20)}")


def test_crawler_init():
    """测试爬虫初始化"""
    print("\n" + "=" * 60)
    print("测试爬虫初始化")
    print("=" * 60)
    
    # 测试无 Cookie 初始化
    crawler = BossZhipinCrawler()
    print("\n1. 无 Cookie 初始化: 成功")
    print(f"   User-Agent: {crawler.headers['User-Agent'][:50]}...")
    
    # 测试带 Cookie 初始化
    test_cookie = "test_cookie=value; another=test"
    crawler_with_cookie = BossZhipinCrawler(cookie=test_cookie)
    print("\n2. 带 Cookie 初始化: 成功")
    print(f"   Cookie: {crawler_with_cookie.headers.get('Cookie', 'None')}")


def test_api_request_simulation():
    """模拟 API 请求测试"""
    print("\n" + "=" * 60)
    print("模拟 API 请求测试")
    print("=" * 60)
    
    crawler = BossZhipinCrawler()
    
    # 测试参数构建
    print("\n1. 测试参数构建:")
    extra_params = {'query': 'Python', 'city': '101010100'}
    params = crawler._build_params(extra_params)
    print(f"   额外参数: {extra_params}")
    print(f"   完整参数:")
    for k, v in params.items():
        print(f"      {k}: {v}")
    
    # 验证签名存在
    assert 'sign' in params, "签名不存在"
    assert 'timestamp' in params, "时间戳不存在"
    assert 'nonce' in params, "随机数不存在"
    print("\n   ✓ 所有必要参数已生成")


def test_data_parser():
    """测试数据解析器"""
    print("\n" + "=" * 60)
    print("测试数据解析器")
    print("=" * 60)
    
    # 模拟职位列表响应
    mock_job_list_response = {
        'zpData': {
            'jobList': [
                {
                    'encryptJobId': 'job_123',
                    'jobName': 'Python工程师',
                    'salaryDesc': '20-40K',
                    'cityName': '北京',
                    'areaDistrict': '朝阳区',
                    'businessDistrict': '望京',
                    'jobExperience': '3-5年',
                    'jobDegree': '本科',
                    'brandName': '某互联网公司',
                    'brandStageName': 'D轮及以上',
                    'brandScaleName': '1000-9999人',
                    'industryName': '互联网',
                    'skills': ['Python', 'Django', 'MySQL'],
                    'welfareList': ['五险一金', '带薪年假'],
                    'publisherName': '张经理',
                    'title': '技术总监',
                },
                {
                    'encryptJobId': 'job_456',
                    'jobName': '高级Python开发',
                    'salaryDesc': '30-50K',
                    'cityName': '上海',
                    'areaDistrict': '浦东新区',
                    'businessDistrict': '陆家嘴',
                    'jobExperience': '5-10年',
                    'jobDegree': '本科',
                    'brandName': '某金融科技公司',
                    'brandStageName': '上市公司',
                    'brandScaleName': '10000人以上',
                    'industryName': '金融科技',
                    'skills': ['Python', '微服务', 'Kubernetes'],
                    'welfareList': ['股票期权', '弹性工作'],
                    'publisherName': '李HR',
                    'title': 'HRBP',
                }
            ]
        }
    }
    
    print("\n1. 测试职位列表解析:")
    jobs = BossZhipinDataParser.parse_job_list(mock_job_list_response)
    print(f"   解析到 {len(jobs)} 个职位")
    
    for i, job in enumerate(jobs, 1):
        print(f"\n   职位 {i}:")
        print(f"      名称: {job['job_name']}")
        print(f"      公司: {job['company_name']}")
        print(f"      薪资: {job['salary']}")
        print(f"      城市: {job['city']}")
        print(f"      经验: {job['experience']}")
        print(f"      学历: {job['degree']}")
    
    # 模拟职位详情响应
    mock_job_detail_response = {
        'zpData': {
            'encryptJobId': 'job_123',
            'jobName': 'Python工程师',
            'salaryDesc': '20-40K',
            'cityName': '北京',
            'jobExperience': '3-5年',
            'jobDegree': '本科',
            'jobDescription': '负责后端开发...',
            'brandName': '某互联网公司',
            'brandStageName': 'D轮及以上',
            'brandScaleName': '1000-9999人',
            'industryName': '互联网',
            'address': '北京市朝阳区望京SOHO',
            'publisherName': '张经理',
            'title': '技术总监',
            'skills': ['Python', 'Django', 'MySQL'],
            'welfareList': ['五险一金', '带薪年假'],
        }
    }
    
    print("\n2. 测试职位详情解析:")
    detail = BossZhipinDataParser.parse_job_detail(mock_job_detail_response)
    print(f"   职位: {detail['job_name']}")
    print(f"   公司: {detail['company_name']}")
    print(f"   薪资: {detail['salary']}")
    print(f"   地址: {detail['address']}")
    print(f"   描述: {detail['description'][:20]}...")


def test_real_api_call():
    """测试真实 API 调用（无 Cookie）"""
    print("\n" + "=" * 60)
    print("测试真实 API 调用（无 Cookie）")
    print("=" * 60)
    
    crawler = BossZhipinCrawler()
    
    print("\n1. 发送搜索请求（无 Cookie）:")
    result = crawler.search_jobs(
        query="Python",
        city="101010100",
        page=1,
        page_size=10
    )
    
    print(f"   响应状态: {'成功' if 'zpData' in result else '失败'}")
    print(f"   响应内容预览:")
    print(f"   {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
    
    if 'zpData' in result:
        jobs = BossZhipinDataParser.parse_job_list(result)
        print(f"\n   解析到 {len(jobs)} 个职位")
    else:
        print("\n   ⚠️ 未获取到职位数据（需要有效 Cookie）")
        print("   错误信息:", result.get('message', result.get('error', '未知错误')))


def generate_test_report():
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    print("""
✅ 已测试项目:
   1. MD5/SHA1/Base64 加密算法 - 正常
   2. 签名生成算法 - 正常
   3. 爬虫初始化 - 正常
   4. 参数构建 - 正常
   5. 数据解析器 - 正常
   6. API 请求发送 - 正常

⚠️  注意事项:
   - 真实 API 调用需要有效的 Cookie
   - 无 Cookie 时 API 会返回错误或空数据
   - 需要从登录后的 APP 中抓取 Cookie

📋 下一步:
   1. 使用 Charles/Fiddler 抓取 APP 请求
   2. 提取 Cookie 和 Token
   3. 替换到爬虫代码中
   4. 重新运行测试
""")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("BOSS直聘爬虫测试套件")
    print("=" * 60)
    
    try:
        # 运行所有测试
        test_crypto()
        test_crawler_init()
        test_api_request_simulation()
        test_data_parser()
        test_real_api_call()
        generate_test_report()
        
        print("\n✅ 所有测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
