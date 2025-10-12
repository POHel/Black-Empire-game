import sys
import random
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QPalette, QKeyEvent, QFont


class FloatingText(QLabel):
    def __init__(self, text, color, parent=None):
        super().__init__(text, parent)
        self.color = color
        self.setStyleSheet(f"""
            color: {color}; 
            font-weight: 700; 
            font-size: 20px; 
            background: transparent;
            padding: 4px 12px;
            border-radius: 12px;
            background-color: rgba(255,255,255,0.1);
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # Анимация движения и исчезновения
        self.pos_animation = QPropertyAnimation(self, b"geometry")
        self.pos_animation.setDuration(1000)
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(1000)
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        
        self.pos_animation.finished.connect(self.deleteLater)
        
    def start_animation(self, start_pos):
        start_x, start_y = start_pos
        end_rect = QRect(start_x, start_y - 100, self.width(), self.height())
        
        self.pos_animation.setStartValue(self.geometry())
        self.pos_animation.setEndValue(end_rect)
        
        self.pos_animation.start()
        self.opacity_animation.start()


class Particle(QWidget):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        size = random.randint(4, 8)
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(800)
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(800)
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        
        self.animation.finished.connect(self.deleteLater)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setBrush(QColor(*self.color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self.width(), self.height())
        
    def start_animation(self, start_pos, angle, distance):
        start_x, start_y = start_pos
        end_x = start_x + math.cos(angle) * distance
        end_y = start_y + math.sin(angle) * distance
        
        end_geometry = QRect(int(end_x), int(end_y), self.width(), self.height())
        
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(end_geometry)
        
        self.animation.start()
        self.opacity_animation.start()


class AnimatedButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scale = 1.0
        
    def get_scale(self):
        return self._scale
        
    def set_scale(self, value):
        self._scale = value
        self.update()
        
    scale = pyqtProperty(float, get_scale, set_scale)
        
    def mousePressEvent(self, event):
        # Анимация нажатия
        self.animation = QPropertyAnimation(self, b"scale")
        self.animation.setDuration(150)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.98)
        self.animation.start()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        self.animation = QPropertyAnimation(self, b"scale")
        self.animation.setDuration(150)
        self.animation.setStartValue(0.98)
        self.animation.setEndValue(1.0)
        self.animation.start()
        super().mouseReleaseEvent(event)


class ClickerGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.money = 0
        self.per_click = 1
        self.total_clicks = 0
        
        # Современная цветовая схема
        self.colors = {
            'bg': '#0f172a',
            'panel': '#1e293b',
            'card': '#334155',
            'primary': '#3b82f6',
            'primary_hover': '#2563eb',
            'success': '#10b981',
            'text_primary': '#f8fafc',
            'text_secondary': '#cbd5e1',
            'text_muted': '#64748b',
            'border': '#475569'
        }
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Finance Clicker • Инвестиционный симулятор')
        self.setFixedSize(1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Устанавливаем фон
        central_widget.setStyleSheet(f"background: {self.colors['bg']};")
        
        # Основной layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Панель игры
        self.game_panel = QFrame()
        self.game_panel.setObjectName("gamePanel")
        self.game_panel.setStyleSheet(f"""
            QFrame#gamePanel {{
                background: {self.colors['panel']};
                border-radius: 20px;
                border: 1px solid {self.colors['border']};
            }}
        """)
        
        panel_layout = QVBoxLayout(self.game_panel)
        panel_layout.setContentsMargins(40, 40, 40, 40)
        panel_layout.setSpacing(30)
        
        # Заголовок
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        self.title_label = QLabel("Finance Clicker")
        self.title_label.setStyleSheet(f"""
            color: {self.colors['text_primary']};
            font-weight: 700;
            font-size: 36px;
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.subtitle_label = QLabel("Создайте свою финансовую империю")
        self.subtitle_label.setStyleSheet(f"""
            color: {self.colors['text_secondary']};
            font-weight: 400;
            font-size: 18px;
        """)
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.subtitle_label)
        panel_layout.addLayout(header_layout)
        
        # Статистика
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.money_stat = self.create_stat_widget("💰 Капитал", "$0", self.colors['success'])
        self.per_click_stat = self.create_stat_widget("📈 Доход за клик", "$1", self.colors['primary'])
        self.total_clicks_stat = self.create_stat_widget("👆 Всего кликов", "0", self.colors['text_secondary'])
        
        stats_layout.addWidget(self.money_stat)
        stats_layout.addWidget(self.per_click_stat)
        stats_layout.addWidget(self.total_clicks_stat)
        panel_layout.addLayout(stats_layout)
        
        # Область клика
        click_layout = QVBoxLayout()
        click_layout.setSpacing(25)
        
        # Основная кнопка
        self.click_button = AnimatedButton()
        self.click_button.setFixedHeight(300)
        self.click_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.click_button.setStyleSheet(f"""
            AnimatedButton {{
                background: {self.colors['primary']};
                border-radius: 20px;
                border: none;
                color: white;
                font-weight: 600;
                font-size: 18px;
            }}
            AnimatedButton:hover {{
                background: {self.colors['primary_hover']};
            }}
            AnimatedButton:pressed {{
                background: {self.colors['primary_hover']};
            }}
        """)
        
        # Внутренний layout кнопки
        button_layout = QVBoxLayout(self.click_button)
        button_layout.setSpacing(15)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Иконка и текст кнопки
        button_icon = QLabel("💼")
        button_icon.setStyleSheet("""
            font-size: 64px;
            background: transparent;
        """)
        button_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        button_label = QLabel("Инвестировать")
        button_label.setStyleSheet("""
            color: white;
            font-weight: 600;
            font-size: 28px;
            background: transparent;
        """)
        button_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Доход за клик
        gain_layout = QVBoxLayout()
        gain_layout.setSpacing(5)
        
        self.click_gain_label = QLabel("+$1")
        self.click_gain_label.setStyleSheet("""
            color: rgba(255,255,255,0.9);
            font-weight: 600;
            font-size: 20px;
            background: transparent;
        """)
        self.click_gain_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        click_subtitle = QLabel("за клик")
        click_subtitle.setStyleSheet(f"""
            color: rgba(255,255,255,0.7);
            font-size: 14px;
            background: transparent;
        """)
        click_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        gain_layout.addWidget(self.click_gain_label)
        gain_layout.addWidget(click_subtitle)
        
        button_layout.addWidget(button_icon)
        button_layout.addWidget(button_label)
        button_layout.addLayout(gain_layout)
        
        click_layout.addWidget(self.click_button)
        
        # Прогресс бар для следующего улучшения
        self.progress_container = QWidget()
        self.progress_container.setStyleSheet("background: transparent;")
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setSpacing(8)
        
        progress_text = QLabel("До следующего улучшения:")
        progress_text.setStyleSheet(f"""
            color: {self.colors['text_secondary']};
            font-size: 14px;
            background: transparent;
        """)
        progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.progress_bar = QFrame()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['card']};
                border-radius: 4px;
            }}
        """)
        
        self.progress_fill = QFrame(self.progress_bar)
        self.progress_fill.setFixedHeight(8)
        self.progress_fill.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['success']};
                border-radius: 4px;
            }}
        """)
        self.update_progress_bar()
        
        progress_layout.addWidget(progress_text)
        progress_layout.addWidget(self.progress_bar)
        
        click_layout.addWidget(self.progress_container)
        
        # Инструкции
        instructions = QLabel("💡 Нажимайте на кнопку или используйте Пробел для инвестирования")
        instructions.setStyleSheet(f"""
            color: {self.colors['text_muted']};
            font-size: 14px;
            padding: 12px;
            background: {self.colors['card']};
            border-radius: 10px;
        """)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setMaximumHeight(50)
        click_layout.addWidget(instructions)
        
        panel_layout.addLayout(click_layout)
        layout.addWidget(self.game_panel)
        
        # Подключаем обработчики
        self.click_button.clicked.connect(self.handle_click)
        
    def create_stat_widget(self, label, value, color):
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['card']};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            color: {color};
            font-weight: 700;
            font-size: 24px;
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_label = QLabel(label)
        label_label.setStyleSheet(f"""
            color: {self.colors['text_secondary']};
            font-size: 14px;
        """)
        label_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(label_label)
        
        return widget
    
    def update_progress_bar(self):
        clicks_to_next = 50 - (self.total_clicks % 50)
        progress = (50 - clicks_to_next) / 50 * 100
        
        fill_width = int(self.progress_bar.width() * progress / 100)
        self.progress_fill.setFixedWidth(fill_width)
        self.progress_fill.move(0, 0)
    
    def format_number(self, n):
        if n >= 1000000:
            return f'${n/1000000:.1f}M'
        elif n >= 1000:
            return f'${n/1000:.1f}K'
        return f'${math.floor(n)}'
    
    def update_ui(self):
        # Обновляем статистику
        money_widget = self.money_stat.layout()
        per_click_widget = self.per_click_stat.layout()
        total_clicks_widget = self.total_clicks_stat.layout()
        
        if money_widget and money_widget.itemAt(0):
            money_value = money_widget.itemAt(0).widget()
            if money_value:
                money_value.setText(self.format_number(self.money))
        
        if per_click_widget and per_click_widget.itemAt(0):
            per_click_value = per_click_widget.itemAt(0).widget()
            if per_click_value:
                per_click_value.setText(self.format_number(self.per_click))
        
        if total_clicks_widget and total_clicks_widget.itemAt(0):
            total_clicks_value = total_clicks_widget.itemAt(0).widget()
            if total_clicks_value:
                total_clicks_value.setText(str(self.total_clicks))
        
        self.click_gain_label.setText(f"+{self.format_number(self.per_click)}")
        self.update_progress_bar()
    
    def handle_click(self):
        self.money += self.per_click
        self.total_clicks += 1
        self.update_ui()
        
        # Создаем визуальные эффекты
        button_center = self.click_button.rect().center()
        global_pos = self.click_button.mapToGlobal(button_center)
        self.create_floating_text((global_pos.x(), global_pos.y()), f"+{self.format_number(self.per_click)}", "#10b981")
        self.create_particles((global_pos.x(), global_pos.y()))
        
        # Увеличиваем доход каждые 50 кликов
        if self.total_clicks % 50 == 0:
            self.per_click += 1
            self.update_ui()
            self.create_floating_text((global_pos.x(), global_pos.y()), "✨ Уровеньアップ!", "#f59e0b")
    
    def create_floating_text(self, position, text, color):
        floating = FloatingText(text, color, self)
        floating.move(int(position[0] - 60), int(position[1] - 20))
        floating.show()
        floating.start_animation((int(position[0] - 60), int(position[1] - 20)))
    
    def create_particles(self, position, count=12):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            distance = 40 + random.uniform(0, 60)
            
            # Случайный цвет из палитры
            colors = [
                (59, 130, 246),  # primary blue
                (16, 185, 129),  # success green
                (245, 158, 11),  # amber
                (139, 92, 246),  # violet
            ]
            color = random.choice(colors)
            
            particle = Particle(color, self)
            particle.move(int(position[0] - 3), int(position[1] - 3))
            particle.show()
            particle.start_animation((position[0], position[1]), angle, distance)
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            event.accept()
            self.handle_click()
            
            # Визуальная обратная связь для клавиатуры
            self.click_button.setStyleSheet(f"""
                AnimatedButton {{
                    background: {self.colors['primary_hover']};
                    border-radius: 20px;
                    border: 2px solid rgba(255,255,255,0.3);
                    color: white;
                    font-weight: 600;
                    font-size: 18px;
                }}
            """)
            
            QTimer.singleShot(100, self.reset_button_style)
        else:
            super().keyPressEvent(event)
    
    def reset_button_style(self):
        self.click_button.setStyleSheet(f"""
            AnimatedButton {{
                background: {self.colors['primary']};
                border-radius: 20px;
                border: none;
                color: white;
                font-weight: 600;
                font-size: 18px;
            }}
            AnimatedButton:hover {{
                background: {self.colors['primary_hover']};
            }}
        """)


def main():
    app = QApplication(sys.argv)
    
    # Устанавливаем стиль приложения
    app.setStyle('Fusion')
    
    # Настраиваем палитру для темной темы
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(15, 23, 42))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(248, 250, 252))
    app.setPalette(palette)
    
    # Устанавливаем глобальный шрифт
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    game = ClickerGame()
    game.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()