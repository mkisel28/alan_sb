"""
Модуль генерации отчетов в различных форматах
"""

from .word_generator import WordReportGenerator
from .excel_generator import ExcelReportGenerator

__all__ = ["WordReportGenerator", "ExcelReportGenerator"]
