from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseCompanyAdapter(ABC):
    company: str = ""
    source: str = ""

    @abstractmethod
    def fetch_list(self, page: int) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def parse(self, raw_item: Dict[str, Any]) -> Dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    def get_27_signal(self, parsed_item: Dict[str, str]) -> Dict[str, Any]:
        raise NotImplementedError
