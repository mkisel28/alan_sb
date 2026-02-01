"""
Инициализация блоков отчета
"""

from .cover_page import CoverPageBlock
from .summary_block import SummaryBlock
from .platform_block import PlatformBlock
from .author_block import AuthorBlock
from .charts_block import ChartsBlock

__all__ = [
    "CoverPageBlock",
    "SummaryBlock",
    "PlatformBlock",
    "AuthorBlock",
    "ChartsBlock",
]
