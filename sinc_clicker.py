import sys
import math
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QFrame)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QPalette, QColor, QLinearGradient, QRadialGradient, QPainter


class AnimatedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._scale = 1.0
        
    def get_scale(self):
        return self._scale
        
    def set_scale(self, value):
        self._scale = value
        self.update()
        
    scale = pyqtProperty(float, get_scale, set_scale)
    
    def paintEvent(self, event):
        if self._scale != 1.0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.translate(self.width() / 2, self.height() / 2)
            painter.scale(self._scale, self._scale)
            painter.translate(-self.width() / 2, -self.height() / 2)
            
        super().paintEvent(event)


class ClickerGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.money = 0
        self.per_click = 1
        self.total_clicks = 0
        self.floating_texts = []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Black Empire — Кликер")
        self.setFixedSize(800, 600)
        
        # Устанавливаем тёмный фон с градиентами
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(spread:pad, x1:0.1, y1:0.2, x2:0.9, y2:0.8, 
                                          stop:0 rgba(122, 47, 255, 0.05), stop:1 transparent),
                          qlineargradient(spread:pad, x1:0.9, y1:0.8, x2:0.1, y2:0.2, 
                                          stop:0 rgba(60, 20, 100, 0.04), stop:1 transparent),
                          #070613;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Game panel
        self.game_panel = QFrame()
        self.game_panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(spread:pad, x1:0.5, y1:0, x2:0.5, y2:1,
                                          stop:0 rgba(255, 255, 255, 0.02),
                                          stop:1 rgba(255, 255, 255, 0.01));
                border-radius: 24px;
                border: 1px solid rgba(255, 255, 255, 0.03);
            }
        """)
        self.game_panel.setMinimumHeight(500)
        
        panel_layout = QVBoxLayout(self.game_panel)
        panel_layout.setContentsMargins(30, 30, 30, 30)
        panel_layout.setSpacing(20)
        
        # Header
        header_layout = QVBoxLayout()
        self.brand_label = QLabel("Black Empire")
        self.brand_label.setStyleSheet("""
            QLabel {
                color: #7a2fff;
                font-weight: 800;
                font-size: 14px;
                letter-spacing: 1px;
            }
        """)
        self.brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.title_label = QLabel("Корпоративный Кликер")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #f7f7fb;
                font-weight: 800;
                font-size: 32px;
                margin: 10px 0px;
            }
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(self.brand_label)
        header_layout.addWidget(self.title_label)
        panel_layout.addLayout(header_layout)
        
        # Stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.money_stat = self.create_stat_widget("Капитал", "$0")
        self.per_click_stat = self.create_stat_widget("Доход за клик", "$1")
        self.total_clicks_stat = self.create_stat_widget("Всего кликов", "0")
        
        stats_layout.addWidget(self.money_stat)
        stats_layout.addWidget(self.per_click_stat)
        stats_layout.addWidget(self.total_clicks_stat)
        panel_layout.addLayout(stats_layout)
        
        # Click area
        click_layout = QVBoxLayout()
        click_layout.setSpacing(20)
        
        self.click_button = QFrame()
        self.click_button.setStyleSheet("""
            QFrame {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                          stop:0 rgba(122, 47, 255, 0.18),
                                          stop:1 rgba(58, 14, 88, 0.12));
                border-radius: 40px;
                border: 1px solid rgba(255, 255, 255, 0.02);
            }
        """)
        self.click_button.setMinimumHeight(300)
        self.click_button.mousePressEvent = self.handle_click
        
        # Добавляем анимацию пульсации
        self.pulse_animation = QPropertyAnimation(self.click_button, b"windowOpacity")
        self.pulse_animation.setDuration(2000)
        self.pulse_animation.setLoopCount(-1)
        self.pulse_animation.setStartValue(0.9)
        self.pulse_animation.setEndValue(1.0)
        self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.pulse_animation.start()
        
        button_layout = QVBoxLayout(self.click_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.setSpacing(20)
        
        # Play icon simulation
        play_icon = QLabel("▶")
        play_icon.setStyleSheet("""
            QLabel {
                background: qlineargradient(spread:pad, x1:0.5, y1:0, x2:0.5, y2:1,
                                          stop:0 #7a2fff, stop:1 #3b0f5e);
                border-radius: 20px;
                color: white;
                font-size: 24px;
                padding: 20px;
                min-width: 80px;
                min-height: 80px;
                max-width: 80px;
                max-height: 80px;
            }
        """)
        play_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.button_label = QLabel("Инвестировать")
        self.button_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: 800;
                font-size: 32px;
            }
        """)
        self.button_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        gain_layout = QVBoxLayout()
        self.click_gain = QLabel("+$1")
        self.click_gain.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: 800;
                font-size: 28px;
            }
        """)
        self.click_gain.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.click_subtitle = QLabel("За клик")
        self.click_subtitle.setStyleSheet("""
            QLabel {
                color: #9aa0ad;
                font-size: 16px;
            }
        """)
        self.click_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        gain_layout.addWidget(self.click_gain)
        gain_layout.addWidget(self.click_subtitle)
        
        button_layout.addWidget(play_icon)
        button_layout.addWidget(self.button_label)
        button_layout.addLayout(gain_layout)
        
        click_layout.addWidget(self.click_button)
        
        # Instructions
        instructions = QLabel("Нажимайте на кнопку или используйте пробел для инвестирования")
        instructions.setStyleSheet("""
            QLabel {
                color: #9aa0ad;
                font-size: 14px;
            }
        """)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        click_layout.addWidget(instructions)
        
        panel_layout.addLayout(click_layout)
        layout.addWidget(self.game_panel)
        
        # Таймер для анимаций
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animations)
        self.animation_timer.start(16)  # ~60 FPS
        
    def create_stat_widget(self, label, value):
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: 800;
                font-size: 24px;
                margin-bottom: 5px;
            }
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_label = QLabel(label)
        label_label.setStyleSheet("""
            QLabel {
                color: #9aa0ad;
                font-size: 12px;
            }
        """)
        label_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(label_label)
        
        return widget
    
    def format_money(self, amount):
        if amount >= 1000000:
            return f"${amount / 1000000:.1f}M"
        elif amount >= 1000:
            return f"${amount / 1000:.1f}K"
        return f"${int(amount)}"
    
    def update_ui(self):
        # Обновляем статистику
        money_widget = self.money_stat.layout().itemAt(0).widget()
        money_widget.setText(self.format_money(self.money))
        
        per_click_widget = self.per_click_stat.layout().itemAt(0).widget()
        per_click_widget.setText(self.format_money(self.per_click))
        
        total_clicks_widget = self.total_clicks_stat.layout().itemAt(0).widget()
        total_clicks_widget.setText(str(self.total_clicks))
        
        # Обновляем отображение дохода за клик
        self.click_gain.setText(f"+{self.format_money(self.per_click)}")
    
    def handle_click(self, event):
        self.money += self.per_click
        self.total_clicks += 1
        
        # Анимация кнопки
        self.animate_button_click()
        
        # Создаем плавающий текст
        button_pos = self.click_button.mapTo(self, self.click_button.rect().center())
        self.create_floating_text(button_pos.x(), button_pos.y(), f"+{self.format_money(self.per_click)}")
        
        # Проверяем улучшение
        if self.total_clicks % 50 == 0:
            self.per_click += 1
            self.create_floating_text(button_pos.x(), button_pos.y(), "Доход увеличен!", "#7aff7a")
        
        self.update_ui()
    
    def animate_button_click(self):
        # Анимация нажатия кнопки
        self.click_button.setStyleSheet("""
            QFrame {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                          stop:0 rgba(122, 47, 255, 0.25),
                                          stop:1 rgba(58, 14, 88, 0.18));
                border-radius: 40px;
                border: 1px solid rgba(255, 255, 255, 0.03);
            }
        """)
        
        QTimer.singleShot(150, lambda: self.click_button.setStyleSheet("""
            QFrame {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                          stop:0 rgba(122, 47, 255, 0.18),
                                          stop:1 rgba(58, 14, 88, 0.12));
                border-radius: 40px;
                border: 1px solid rgba(255, 255, 255, 0.02);
            }
        """))
    
    def create_floating_text(self, x, y, text, color="#bda8ff"):
        text_label = AnimatedLabel(text)
        text_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: 800;
                font-size: 24px;
                background: transparent;
                border: none;
            }}
        """)
        text_label.move(x - 50, y - 50)
        text_label.show()
        
        # Анимация движения вверх и исчезновения
        anim = QPropertyAnimation(text_label, b"scale")
        anim.setDuration(900)
        anim.setStartValue(1.0)
        anim.setEndValue(1.15)
        anim.setEasingCurve(QEasingCurve.Type.OutBack)
        anim.start()
        
        # Сохраняем для управления анимацией
        self.floating_texts.append({
            'label': text_label,
            'start_y': y - 50,
            'start_time': self.get_current_time(),
            'duration': 900
        })
    
    def get_current_time(self):
        return QTimer().remainingTime()  # Примерное время
    
    def update_animations(self):
        current_time = self.get_current_time()
        texts_to_remove = []
        
        for i, text_data in enumerate(self.floating_texts):
            label = text_data['label']
            start_y = text_data['start_y']
            start_time = text_data['start_time']
            duration = text_data['duration']
            
            # Вычисляем прогресс анимации
            progress = (current_time - start_time) / duration
            
            if progress >= 1.0:
                label.deleteLater()
                texts_to_remove.append(i)
            else:
                # Двигаем текст вверх и изменяем прозрачность
                new_y = start_y - progress * 120
                opacity = 1.0 - progress
                
                label.move(label.x(), int(new_y))
                label.setStyleSheet(label.styleSheet() + f" opacity: {opacity};")
        
        # Удаляем завершенные анимации
        for i in reversed(texts_to_remove):
            if i < len(self.floating_texts):
                self.floating_texts.pop(i)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.handle_click(None)
            # Визуальная обратная связь для клавиатуры
            self.click_button.setStyleSheet("""
                QFrame {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                              stop:0 rgba(122, 47, 255, 0.3),
                                              stop:1 rgba(58, 14, 88, 0.22));
                    border-radius: 40px;
                    border: 2px solid rgba(122, 47, 255, 0.3);
                }
            """)
            QTimer.singleShot(100, lambda: self.click_button.setStyleSheet("""
                QFrame {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                              stop:0 rgba(122, 47, 255, 0.18),
                                              stop:1 rgba(58, 14, 88, 0.12));
                    border-radius: 40px;
                    border: 1px solid rgba(255, 255, 255, 0.02);
                }
            """))
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Устанавливаем шрифт
    font = QFont("Inter", 10)
    app.setFont(font)
    
    game = ClickerGame()
    game.show()
    
    sys.exit(app.exec())