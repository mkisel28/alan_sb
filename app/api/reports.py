"""
API endpoints для генерации отчетов
"""

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
from api.comparative_analytics import calculate_comparative_analytics
from reports import WordReportGenerator, ExcelReportGenerator

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/word")
async def generate_word_report(
    platforms: List[str] = Query(..., description="Список платформ"),
    period: str = Query("30d", description="Период анализа"),
    custom_start: Optional[str] = Query(None),
    custom_end: Optional[str] = Query(None),
    include_previous: bool = Query(True, description="Включить предыдущий период"),
):
    """
    Генерирует детальный отчет в формате Word

    Параметры:
    - platforms: Список платформ (tiktok, youtube, youtube_shorts и т.д.)
    - period: Период анализа (7d, 30d, 90d, 365d, custom)
    - custom_start: Начальная дата для custom периода
    - custom_end: Конечная дата для custom периода
    - include_previous: Включить ли предыдущий период для сравнения

    Возвращает:
    - Word документ (.docx) с детальным анализом
    """
    # Получаем данные аналитики
    data = await calculate_comparative_analytics(
        platforms=platforms,
        period=period,
        custom_start=custom_start,
        custom_end=custom_end,
        include_previous=include_previous,
    )

    # Генерируем Word отчет
    generator = WordReportGenerator()
    doc_stream = generator.generate(data)

    # Формируем имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    platforms_str = "_".join(platforms)
    filename = f"analytics_report_{platforms_str}_{period}_{timestamp}.docx"

    return StreamingResponse(
        doc_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/excel")
async def generate_excel_report(
    platforms: List[str] = Query(..., description="Список платформ"),
    period: str = Query("30d", description="Период анализа"),
    custom_start: Optional[str] = Query(None),
    custom_end: Optional[str] = Query(None),
    include_previous: bool = Query(True, description="Включить предыдущий период"),
):
    """
    Генерирует сводный отчет в формате Excel

    Параметры:
    - platforms: Список платформ (tiktok, youtube, youtube_shorts и т.д.)
    - period: Период анализа (7d, 30d, 90d, 365d, custom)
    - custom_start: Начальная дата для custom периода
    - custom_end: Конечная дата для custom периода
    - include_previous: Включить ли предыдущий период для сравнения

    Возвращает:
    - Excel файл (.xlsx) с табличными данными
    """
    # Получаем данные аналитики
    data = await calculate_comparative_analytics(
        platforms=platforms,
        period=period,
        custom_start=custom_start,
        custom_end=custom_end,
        include_previous=include_previous,
    )

    # Генерируем Excel отчет
    generator = ExcelReportGenerator()
    excel_stream = generator.generate(data)

    # Формируем имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    platforms_str = "_".join(platforms)
    filename = f"analytics_data_{platforms_str}_{period}_{timestamp}.xlsx"

    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
