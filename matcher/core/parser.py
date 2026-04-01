"""
简历解析模块

支持 JSON/PDF/Word 格式的简历解析
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ResumeParser:
    """简历解析器"""

    def __init__(self):
        self.parsed_data = None

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        解析简历文件

        Args:
            file_path: 简历文件路径

        Returns:
            结构化简历数据
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"简历文件不存在: {file_path}")

        suffix = path.suffix.lower()

        if suffix == '.json':
            return self._parse_json(file_path)
        elif suffix in ['.pdf', '.docx', '.doc']:
            return self._parse_document(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")

    def _parse_json(self, file_path: str) -> Dict[str, Any]:
        """解析 JSON 格式简历"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"成功解析 JSON 简历: {file_path}")
        self.parsed_data = data
        return data

    def _parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        解析 PDF/Word 文档简历
        使用简单的文本提取，后续可接入 LLM 做结构化提取
        """
        path = Path(file_path)
        suffix = path.suffix.lower()

        try:
            if suffix == '.pdf':
                text = self._extract_pdf_text(file_path)
            elif suffix in ['.docx', '.doc']:
                text = self._extract_docx_text(file_path)
            else:
                raise ValueError(f"不支持的文档格式: {suffix}")

            # TODO: 接入 LLM 做结构化提取
            # 目前返回原始文本
            return {
                "raw_text": text,
                "file_path": file_path,
                "format": suffix.lstrip('.')
            }

        except ImportError as e:
            logger.error(f"缺少必要的依赖库: {e}")
            raise

    def _extract_pdf_text(self, file_path: str) -> str:
        """提取 PDF 文本"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"PDF 解析失败: {e}")
            return ""

    def _extract_docx_text(self, file_path: str) -> str:
        """提取 Word 文档文本"""
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"Word 解析失败: {e}")
            return ""

    def get_basic_info(self) -> Optional[Dict[str, Any]]:
        """获取基本信息"""
        if not self.parsed_data:
            return None
        return self.parsed_data.get('basic_info', {})

    def get_skills(self) -> list:
        """获取技能列表"""
        if not self.parsed_data:
            return []
        return self.parsed_data.get('skills', [])

    def get_work_experience(self) -> list:
        """获取工作经历"""
        if not self.parsed_data:
            return []
        return self.parsed_data.get('work_experience', [])

    def get_project_experience(self) -> list:
        """获取项目经历"""
        if not self.parsed_data:
            return []
        return self.parsed_data.get('project_experience', [])
