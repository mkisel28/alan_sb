"""
Вспомогательные функции для генерации отчетов
"""


def format_number(value: int | float, decimals: int = 0) -> str:
    """Форматирует число с разделителями тысяч"""
    if isinstance(value, float):
        return f"{value:,.{decimals}f}".replace(",", " ")
    return f"{value:,}".replace(",", " ")


def format_percent(value: float, decimals: int = 2) -> str:
    """Форматирует процент"""
    return f"{value:.{decimals}f}%"


def format_delta(
    value: float, absolute: int | float = None, is_percent: bool = False
) -> str:
    """Форматирует изменение со знаком"""
    sign = "+" if value > 0 else ""
    if is_percent:
        result = f"{sign}{value:.2f}%"
    else:
        result = f"{sign}{format_number(value, 2 if isinstance(value, float) else 0)}"

    if absolute is not None:
        result += f" ({sign}{format_number(absolute)})"

    return result


def get_platform_name(platform: str) -> str:
    """Возвращает человекочитаемое название платформы"""
    platform_names = {
        "tiktok": "TikTok",
        "youtube": "YouTube (длинные видео)",
        "youtube_shorts": "YouTube Shorts",
        "instagram": "Instagram",
        "vk": "ВКонтакте",
    }
    return platform_names.get(platform, platform)


def get_metric_description(metric: str) -> str:
    """Возвращает описание метрики"""
    descriptions = {
        "F": "подписчиков",
        "P": "публикаций",
        "V": "просмотров",
        "V_avg": "средних просмотров на пост",
        "E": "вовлечений (лайки + комментарии + репосты + сохранения)",
        "ER_view": "уровень вовлеченности по просмотрам",
        "ER_fol": "уровень вовлеченности по подписчикам",
        "SR": "Share Rate (коэффициент репостов)",
        "CR": "Comment Rate (коэффициент комментариев)",
        "PS": "Presence Score (степень присутствия)",
        "MS": "Momentum Score (импульс роста)",
    }
    return descriptions.get(metric, metric)


def interpret_ps(ps: float) -> str:
    """Интерпретирует значение Presence Score"""
    if ps >= 80:
        return "отличный уровень присутствия и влияния"
    elif ps >= 60:
        return "хороший уровень присутствия"
    elif ps >= 40:
        return "средний уровень присутствия"
    elif ps >= 20:
        return "низкий уровень присутствия"
    else:
        return "очень низкий уровень присутствия"


def interpret_ms(ms: float) -> str:
    """Интерпретирует значение Momentum Score"""
    if ms >= 80:
        return "очень высокий темп роста"
    elif ms >= 60:
        return "хороший темп роста"
    elif ms >= 40:
        return "умеренный темп роста"
    elif ms >= 20:
        return "низкий темп роста"
    else:
        return "отрицательная динамика"


def interpret_er(er: float) -> str:
    """Интерпретирует уровень вовлеченности"""
    er_percent = er * 100
    if er_percent >= 5:
        return "превосходная вовлеченность аудитории"
    elif er_percent >= 3:
        return "высокая вовлеченность аудитории"
    elif er_percent >= 1:
        return "средняя вовлеченность аудитории"
    elif er_percent >= 0.5:
        return "низкая вовлеченность аудитории"
    else:
        return "очень низкая вовлеченность аудитории"


def get_trend_description(delta_percent: float) -> str:
    """Описывает тренд изменения"""
    if delta_percent > 50:
        return "значительный рост"
    elif delta_percent > 20:
        return "существенный рост"
    elif delta_percent > 5:
        return "умеренный рост"
    elif delta_percent > 0:
        return "незначительный рост"
    elif delta_percent == 0:
        return "стабильность"
    elif delta_percent > -5:
        return "незначительное снижение"
    elif delta_percent > -20:
        return "умеренное снижение"
    elif delta_percent > -50:
        return "существенное снижение"
    else:
        return "значительное снижение"
