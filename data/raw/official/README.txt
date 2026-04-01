官网CDP爬虫说明
================

官网爬虫需要在Docker外部运行，因为它们需要Chrome浏览器通过CDP协议连接。

在Docker外部运行爬虫的方法：
1. 启动Chrome浏览器并开启CDP调试端口:
   chrome.exe --remote-debugging-port=9222

2. 打开各公司招聘官网:
   - 腾讯: https://join.qq.com
   - 美团: https://zhaopin.meituan.com
   - 阿里: https://talent.alibaba.com
   - 京东: https://zhaopin.jd.com
   - 快手: https://zhaopin.kuaishou.com
   - 哔哩哔哩: https://jobs.bilibili.com
   - 字节跳动: https://jobs.bytedance.com

3. 运行爬虫脚本:
   python crawlers/official/cdp_tencent.py
   python crawlers/official/cdp_meituan.py
   ...

4. 爬虫会将数据保存到 data/raw/official/ 目录

5. 然后可以在Docker中运行匹配流程:
   docker-compose up resuminer-full
