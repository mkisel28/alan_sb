"""
Генерация графиков для отчета
"""

import matplotlib

matplotlib.use("Agg")  # Используем backend без GUI
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from typing import List, Dict, Tuple


class ChartsBlock:
    """Генерирует графики для отчета"""

    @staticmethod
    def create_bar_chart(
        labels: List[str],
        values: List[float],
        title: str,
        ylabel: str,
        color: str = "#4A90E2",
        figsize: Tuple[int, int] = (10, 6),
    ) -> BytesIO:
        """
        Создает столбчатую диаграмму

        Args:
            labels: Подписи для столбцов
            values: Значения
            title: Заголовок графика
            ylabel: Подпись оси Y
            color: Цвет столбцов
            figsize: Размер графика

        Returns:
            BytesIO с изображением графика
        """
        fig, ax = plt.subplots(figsize=figsize)

        x = np.arange(len(labels))
        bars = ax.bar(
            x, values, color=color, alpha=0.7, edgecolor="black", linewidth=1.2
        )

        ax.set_xlabel("Авторы", fontsize=11, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=11, fontweight="bold")
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.grid(axis="y", alpha=0.3, linestyle="--")

        # Добавляем значения на столбцы
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:,.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

        plt.tight_layout()

        # Сохраняем в BytesIO
        img_stream = BytesIO()
        plt.savefig(img_stream, format="png", dpi=150, bbox_inches="tight")
        img_stream.seek(0)
        plt.close(fig)

        return img_stream

    @staticmethod
    def create_grouped_bar_chart(
        labels: List[str],
        current_values: List[float],
        previous_values: List[float],
        title: str,
        ylabel: str,
        figsize: Tuple[int, int] = (10, 6),
    ) -> BytesIO:
        """
        Создает сгруппированную столбчатую диаграмму для сравнения периодов

        Args:
            labels: Подписи
            current_values: Значения текущего периода
            previous_values: Значения предыдущего периода
            title: Заголовок
            ylabel: Подпись оси Y
            figsize: Размер графика

        Returns:
            BytesIO с изображением
        """
        fig, ax = plt.subplots(figsize=figsize)

        x = np.arange(len(labels))
        width = 0.35

        bars1 = ax.bar(
            x - width / 2,
            current_values,
            width,
            label="Текущий период",
            color="#4A90E2",
            alpha=0.8,
            edgecolor="black",
        )
        bars2 = ax.bar(
            x + width / 2,
            previous_values,
            width,
            label="Предыдущий период",
            color="#909397",
            alpha=0.6,
            edgecolor="black",
        )

        ax.set_xlabel("Авторы", fontsize=11, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=11, fontweight="bold")
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.legend(fontsize=10)
        ax.grid(axis="y", alpha=0.3, linestyle="--")

        plt.tight_layout()

        img_stream = BytesIO()
        plt.savefig(img_stream, format="png", dpi=150, bbox_inches="tight")
        img_stream.seek(0)
        plt.close(fig)

        return img_stream

    @staticmethod
    def create_metrics_comparison(
        author_name: str, metrics: Dict, prev_metrics: Dict = None
    ) -> BytesIO:
        """
        Создает график сравнения метрик автора

        Args:
            author_name: Имя автора
            metrics: Метрики текущего периода
            prev_metrics: Метрики предыдущего периода

        Returns:
            BytesIO с изображением
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(
            f"Детальный анализ метрик: {author_name}", fontsize=16, fontweight="bold"
        )

        # График 1: Просмотры
        if prev_metrics:
            ax1.bar(
                ["Предыдущий\nпериод", "Текущий\nпериод"],
                [prev_metrics["V"], metrics["V"]],
                color=["#909397", "#4A90E2"],
                alpha=0.7,
            )
        else:
            ax1.bar(["Текущий период"], [metrics["V"]], color="#4A90E2", alpha=0.7)
        ax1.set_title("Просмотры", fontweight="bold")
        ax1.set_ylabel("Количество", fontweight="bold")
        ax1.grid(axis="y", alpha=0.3)

        # График 2: Engagement Rate
        if prev_metrics:
            ax2.bar(
                ["Предыдущий\nпериод", "Текущий\nпериод"],
                [prev_metrics["ER_view"] * 100, metrics["ER_view"] * 100],
                color=["#909397", "#67C23A"],
                alpha=0.7,
            )
        else:
            ax2.bar(
                ["Текущий период"],
                [metrics["ER_view"] * 100],
                color="#67C23A",
                alpha=0.7,
            )
        ax2.set_title("Engagement Rate", fontweight="bold")
        ax2.set_ylabel("Процент (%)", fontweight="bold")
        ax2.grid(axis="y", alpha=0.3)

        # График 3: Подписчики
        if prev_metrics and prev_metrics["F"] > 0:
            ax3.bar(
                ["Предыдущий\nпериод", "Текущий\nпериод"],
                [prev_metrics["F"], metrics["F"]],
                color=["#909397", "#8A2BE2"],
                alpha=0.7,
            )
        else:
            ax3.bar(["Текущий период"], [metrics["F"]], color="#8A2BE2", alpha=0.7)
        ax3.set_title("Подписчики", fontweight="bold")
        ax3.set_ylabel("Количество", fontweight="bold")
        ax3.grid(axis="y", alpha=0.3)

        # График 4: Публикации
        if prev_metrics:
            ax4.bar(
                ["Предыдущий\nпериод", "Текущий\nпериод"],
                [prev_metrics["P"], metrics["P"]],
                color=["#909397", "#E6A23C"],
                alpha=0.7,
            )
        else:
            ax4.bar(["Текущий период"], [metrics["P"]], color="#E6A23C", alpha=0.7)
        ax4.set_title("Публикации", fontweight="bold")
        ax4.set_ylabel("Количество", fontweight="bold")
        ax4.grid(axis="y", alpha=0.3)

        plt.tight_layout()

        img_stream = BytesIO()
        plt.savefig(img_stream, format="png", dpi=150, bbox_inches="tight")
        img_stream.seek(0)
        plt.close(fig)

        return img_stream
