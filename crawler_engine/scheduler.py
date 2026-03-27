import os
import redis
import json
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RedisScheduler:
    """
    基于 Redis 的分布式任务调度器
    负责：任务队列管理、已抓取链接去重、代理 IP 和 Cookie 状态管理
    """
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        try:
            self.redis_client = redis.Redis(
                host=host, port=port, db=db, password=password, decode_responses=True
            )
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {host}:{port}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

        # Redis Keys
        self.queue_key = "spider:tasks:queue"
        self.dupefilter_key = "spider:tasks:dupefilter"
        self.proxy_pool_key = "spider:proxies:pool"
        
        # 初始化隧道代理配置
        self.tunnel_proxy = self._build_tunnel_proxy()

    def _build_tunnel_proxy(self) -> Optional[str]:
        """
        从环境变量构建隧道代理的 URL
        格式如: http://username:password@tps123.kdlapi.com:15818
        """
        proxy_server = os.environ.get("PROXY_SERVER")
        if not proxy_server:
            return None
            
        user = os.environ.get("PROXY_USER", "")
        pwd = os.environ.get("PROXY_PASS", "")
        
        if user and pwd:
            # 假设 proxy_server 格式为 http://ip:port
            if "://" in proxy_server:
                scheme, address = proxy_server.split("://", 1)
                return f"{scheme}://{user}:{pwd}@{address}"
            return f"http://{user}:{pwd}@{proxy_server}"
            
        return proxy_server

    def is_connected(self) -> bool:
        return self.redis_client is not None

    def add_task(self, task: Dict[str, Any]) -> bool:
        """
        向队列添加任务（如果任务包含 url，则进行去重校验）
        """
        if not self.is_connected():
            return False

        task_str = json.dumps(task)
        url = task.get("url")

        if url:
            # SADD 成功返回 1 表示新元素，0 表示已存在
            is_new = self.redis_client.sadd(self.dupefilter_key, url)
            if not is_new:
                logger.debug(f"Task filtered as duplicate: {url}")
                return False

        self.redis_client.lpush(self.queue_key, task_str)
        return True

    def get_task(self) -> Optional[Dict[str, Any]]:
        """
        从队列获取任务 (RPOP)
        """
        if not self.is_connected():
            return None

        task_str = self.redis_client.rpop(self.queue_key)
        if task_str:
            return json.loads(task_str)
        return None

    def get_proxy(self) -> Optional[str]:
        """
        优先返回隧道代理配置。如果没有，再尝试从 Redis 代理池随机获取。
        隧道代理服务商会自动在后端轮换 IP，因此只需要每次请求使用这个固定的入口地址。
        """
        if self.tunnel_proxy:
            return self.tunnel_proxy
            
        if not self.is_connected():
            return None
        return self.redis_client.srandmember(self.proxy_pool_key)

    def remove_proxy(self, proxy: str):
        """
        移除失效代理
        """
        if self.is_connected():
            self.redis_client.srem(self.proxy_pool_key, proxy)

    def throttle(self, domain: str, delay: float):
        """
        简单的分布式节流：利用 Redis SETNX 和 EXPIRE
        如果某个域的锁存在，则当前线程 sleep 直到锁释放
        """
        if not self.is_connected():
            time.sleep(delay)
            return

        lock_key = f"spider:throttle:{domain}"
        while True:
            # 尝试设置锁，并附带过期时间
            acquired = self.redis_client.set(lock_key, "locked", nx=True, ex=int(delay))
            if acquired:
                break
            time.sleep(0.5) # 自旋等待
