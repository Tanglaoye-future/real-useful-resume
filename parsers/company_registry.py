from typing import Dict, Type

from parsers.base_adapter import BaseCompanyAdapter
from parsers.company_adapters import AlibabaAdapter, BilibiliAdapter, KuaishouAdapter, MeituanAdapter, TencentAdapter, XiaohongshuAdapter


ADAPTER_REGISTRY: Dict[str, Type[BaseCompanyAdapter]] = {
    "kuaishou": KuaishouAdapter,
    "tencent": TencentAdapter,
    "xiaohongshu": XiaohongshuAdapter,
    "alibaba": AlibabaAdapter,
    "meituan": MeituanAdapter,
    "bilibili": BilibiliAdapter,
}


def get_adapter(company_key: str):
    key = (company_key or "").strip().lower()
    cls = ADAPTER_REGISTRY.get(key)
    if cls is None:
        return None
    return cls()
