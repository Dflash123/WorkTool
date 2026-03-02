"""
자동 계산 지표 패널 컴포넌트
"""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QFrame, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette

from src.modules.metrics_calculator import MetricsResult


class MetricBar(QWidget):
    """단일 지표 진행 바"""

    def __init__(self, label: str, value: float, danger_high: bool = False):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        lbl = QLabel(f"{label}")
        lbl.setFixedWidth(110)
        lbl.setStyleSheet("font-size: 12px;")

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(int(value))
        bar.setFixedHeight(18)
        bar.setTextVisible(True)
        bar.setFormat(f"{value:.0f}")

        # 색상: danger_high=True면 높을수록 빨강 (억까가능성)
        if danger_high:
            color = "#e74c3c" if value > 60 else "#f39c12" if value > 40 else "#27ae60"
        else:
            color = "#27ae60" if value >= 70 else "#f39c12" if value >= 50 else "#e74c3c"

        bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #ccc;
                border-radius: 4px;
                background: #f0f0f0;
                text-align: center;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background: {color};
                border-radius: 3px;
            }}
        """)

        val_lbl = QLabel(f"{value:.0f}")
        val_lbl.setFixedWidth(30)
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        val_lbl.setStyleSheet(f"font-weight: bold; color: {color}; font-size: 12px;")

        layout.addWidget(lbl)
        layout.addWidget(bar, 1)
        layout.addWidget(val_lbl)


class MetricsPanel(QGroupBox):
    """5개 지표 표시 패널"""

    def __init__(self):
        super().__init__("자동 계산 지표")
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(4)
        self._warning_label = QLabel("")
        self._warning_label.setWordWrap(True)
        self._warning_label.setStyleSheet("color: #e74c3c; font-size: 11px;")
        self._layout.addWidget(self._warning_label)
        self.setMinimumWidth(280)

    def update_metrics(self, result: MetricsResult):
        # 기존 바 제거
        while self._layout.count() > 1:
            item = self._layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        items = [
            ("반응 여유 지수", result.reaction_margin, False),
            ("타이밍 공정성", result.fairness_score, False),
            ("억까 가능성", result.unfair_hit_index, True),
            ("설계 적중률", result.design_intent_rate, False),
            ("학습 가능성", result.learnability_score, False),
        ]
        for label, value, danger_high in items:
            self._layout.addWidget(MetricBar(label, value, danger_high))

        # 위험/경고 메시지
        messages = []
        for flag in result.danger_flags:
            messages.append(f"🔴 {flag}")
        for w in result.warnings:
            messages.append(f"🟡 {w}")

        if messages:
            self._warning_label.setText("\n".join(messages))
        else:
            self._warning_label.setText("🟢 위험 패턴 없음")
            self._warning_label.setStyleSheet("color: #27ae60; font-size: 11px;")
