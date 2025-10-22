import sys
import os
import math
import random
import time
import json
import sqlite3
import coreLogic
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Tuple
from PyQt6.QtWidgets import (               #pyright: ignore[reportMissingImports]
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame, QScrollArea, 
    QGridLayout, QLineEdit, QSlider, QComboBox, QProgressBar,
    QGroupBox, QTabWidget, QTextEdit, QListWidget, QListWidgetItem,
    QDialog, QMessageBox, QSplitter, QToolBar, QStatusBar,
    QSizePolicy, QSpacerItem, QButtonGroup, QRadioButton,
    QCheckBox, QDoubleSpinBox, QSpinBox, QFormLayout
)
from PyQt6.QtCore import (                  #pyright: ignore[reportMissingImports]
    Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, 
    QRect, QPoint, QSize, QDateTime, QSequentialAnimationGroup, 
    QParallelAnimationGroup, qInstallMessageHandler
)
from PyQt6.QtGui import (                   #pyright: ignore[reportMissingImports]
    QFont, QPalette, QColor, QPainter, QLinearGradient, 
    QRadialGradient, QPen, QBrush, QFontDatabase, QPixmap,
    QGuiApplication,QIcon, QMovie, QKeyEvent, QCursor
)

class OpenType:
    def __init__(self):
        self.loaded_fonts = []
        self.main_font_family = None
    
    def init_fonts(self):
        """Инициализация системы шрифтов с поддержкой OpenType"""
        font_priority = [
            "Segoe UI Variable",
            "Segoe UI", 
            "Arial",
            "system-ui",
            "Tahoma",
            "MS UI Gothic",
            "SimSun",
            "Segoe UI Emoji",
            "Segoi UI Simbol"
        ]
        
        # ФИКС: используем статический метод
        available_fonts = QFontDatabase.families()
        selected_font = "Arial"
        
        for font_name in font_priority:
            if font_name in available_fonts:
                selected_font = font_name
                break
        
        print(f"🎨 Основной шрифт: {selected_font}")
        return selected_font
    
    def create_font(self, size=12, weight=QFont.Weight.Normal, italic=False):
        """Создает шрифт с настройками OpenType"""
        font = QFont(self.main_font_family, size, weight, italic)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        return font
    
    def apply_styles(self, widget, font_size=12, weight=QFont.Weight.Normal):
        """Применяет шрифт к виджету"""
        font = self.create_font(font_size, weight)
        widget.setFont(font)

# Глобальный экземпляр (теперь будет работать)
OPENTYPE_MANAGER = OpenType()

AppLogic = coreLogic.AppLogic()
Settings = coreLogic.Settings()
ExportDB = coreLogic.ExportDB()
UpdateDB = coreLogic.UpdateDB()


# Константы игры
GAME_VERSION = AppLogic.version
SCREEN_WIDTH = Settings.get_current_window_size()[0]
SCREEN_HEIGHT = Settings.get_current_window_size()[1]

# Цветовая палитра
WHITE = QColor(255, 255, 255)
BLACK = QColor(0, 0, 0)
DARK_BG = QColor(5, 5, 20)
PANEL_BG = QColor(15, 15, 40)
DEEP_PURPLE = QColor(55, 0, 110)
PURPLE_PRIMARY = QColor(120, 20, 220)
PURPLE_ACCENT = QColor(160, 60, 255)
LIGHT_PURPLE = QColor(180, 120, 240)
BAR_BASE = QColor(90, 30, 180)
BAR_HIGHLIGHT = QColor(140, 80, 230)
TEXT_PRIMARY = QColor(245, 245, 255)
TEXT_SECONDARY = QColor(180, 180, 200)
TEXT_TERTIARY = QColor(140, 140, 160)
CARD_BG = QColor(11, 17, 23)
ACCENT1 = QColor(106, 44, 255)
ACCENT2 = QColor(20, 231, 209)
TEXT_MUTED = QColor(159, 176, 195)

class ScreenState(Enum):
    LOADING = 0
    MAIN_MENU = 1
    CLICKER = 2
    INVESTMENTS = 3
    SHOP_SELECTION = 4
    LIGHT_SHOP = 5
    BUSINESS_MENU = 6
    PROFILE_MENU = 7
    SETTINGS_MENU = 8

class GameConfig:
    def __init__(self):
        self.screen_width = Settings.get_current_window_size()[0]
        self.screen_height = Settings.get_current_window_size()[1]
        self.button_height = 70
        self.font_sizes = {
            "small": 14,
            "medium": 18,
            "large": 24,
            "xlarge": 32,
            "title": 36
        }

class AnimatedButton(QPushButton):
    """Анимированная кнопка с эффектами"""
    
    def __init__(self, text, icon=None, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(50)
        
        self.setStyleSheet(self.get_normal_style())
        
    def get_normal_style(self):
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {DEEP_PURPLE.name()}, stop:1 {PURPLE_PRIMARY.name()});
                border: 2px solid {PURPLE_ACCENT.name()};
                border-radius: 15px;
                color: {TEXT_PRIMARY.name()};
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {PURPLE_PRIMARY.name()}, stop:1 {PURPLE_ACCENT.name()});
                border: 2px solid {LIGHT_PURPLE.name()};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {DEEP_PURPLE.name()}, stop:1 {PURPLE_PRIMARY.name()});
            }}
        """
    
    def enterEvent(self, event):
        self.animate_hover()
        super().enterEvent(event)
    
    def leaveEvent(self, a0):
        self.animate_leave()
        super().leaveEvent(a0)
    
    def animate_hover(self):
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(200)
        anim.setStartValue(self.geometry())
        anim.setEndValue(QRect(self.x()-2, self.y()-2, self.width()+4, self.height()+4))
        anim.start()
    
    def animate_leave(self):
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(200)
        anim.setStartValue(self.geometry())
        anim.setEndValue(QRect(self.x()+2, self.y()+2, self.width()-4, self.height()-4))
        anim.start()

class MenuButton(AnimatedButton):
    """Специальная кнопка для главного меню"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(300, 70)
        self.setStyleSheet(self.get_menu_style())
        
    def get_menu_style(self):
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {PURPLE_PRIMARY.name()}, stop:1 {DEEP_PURPLE.name()});
                border: 3px solid {PURPLE_ACCENT.name()};
                border-radius: 35px;
                color: {TEXT_PRIMARY.name()};
                font-size: 20px;
                font-weight: bold;
                padding: 15px 30px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {PURPLE_ACCENT.name()}, stop:1 {PURPLE_PRIMARY.name()});
                border: 3px solid {LIGHT_PURPLE.name()};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {DEEP_PURPLE.name()}, stop:1 {PURPLE_PRIMARY.name()});
            }}
        """

class NavigationButton(AnimatedButton):
    """Кнопка навигации в левой панели"""
    
    def __init__(self, text, icon_name, parent=None):
        super().__init__(text, parent)
        self.icon_name = icon_name
        self.setFixedSize(180, 60)
        self.setCheckable(True)
        
    def get_icon_style(self):
        icons = {
            "clicker": "🎮",
            "shop": "🏪", 
            "investments": "📈",
            "business": "🏢",
            "profile": "👤",
            "settings": "⚙️"
        }
        return icons.get(self.icon_name, "●")

class GradientWidget(QWidget):
    """Виджет с анимированным градиентным фоном и падающими звездами"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stars = []
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_stars)
        self.animation_timer.start(50)  # Обновление каждые 50ms
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.init_stars()
        
    def init_stars(self):
        """Инициализация звезд"""
        for _ in range(100):  # Увеличил количество звезд
            star = {
                'x': random.randint(0, self.width()),
                'y': random.randint(0, self.height()),
                'size': random.uniform(0.5, 3),
                'speed': random.uniform(0.1, 2),
                'alpha': random.randint(50, 255),
                'twinkle_speed': random.uniform(0.02, 0.1),
                'twinkle_direction': 1
            }
            self.stars.append(star)
    
    def update_stars(self):
        """Обновление позиций и анимации звезд"""
        for star in self.stars:
            # Движение вниз
            star['y'] += star['speed']
            
            # Мерцание
            star['alpha'] += star['twinkle_speed'] * star['twinkle_direction']
            if star['alpha'] >= 255:
                star['alpha'] = 255
                star['twinkle_direction'] = -1
            elif star['alpha'] <= 50:
                star['alpha'] = 50
                star['twinkle_direction'] = 1
            
            # Если звезда ушла за нижнюю границу, создаем новую сверху
            if star['y'] > self.height():
                star['y'] = 0
                star['x'] = random.randint(0, self.width())
        
        self.update()
    
    def resizeEvent(self, a0):
        """Пересоздаем звезды при изменении размера окна"""
        super().resizeEvent(a0)
        self.stars.clear()
        self.init_stars()
    
    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Улучшенный градиентный фон
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(2, 2, 15))  # Более темный синий
        gradient.setColorAt(0.3, QColor(8, 8, 40))  # Фиолетовый оттенок
        gradient.setColorAt(0.7, QColor(15, 5, 35))  # Пурпурный
        gradient.setColorAt(1, QColor(2, 2, 15))  # Более темный синий
        
        painter.fillRect(self.rect(), gradient)
        
        # Добавляем туманность/небулярность
        self.draw_nebula(painter)
        
        # Рисуем звезды
        self.draw_stars(painter)
        
        # Добавляем легкий градиент поверх для глубины
        overlay_gradient = QLinearGradient(0, 0, 0, self.height())
        overlay_gradient.setColorAt(0, QColor(0, 0, 0, 80))
        overlay_gradient.setColorAt(1, QColor(80, 20, 120, 40))
        painter.fillRect(self.rect(), overlay_gradient)
    
    def draw_nebula(self, painter):
        """Рисует туманности для глубины"""
        # Большая туманность в центре
        radial = QRadialGradient(self.width() // 2, self.height() // 2, self.width() // 2)
        radial.setColorAt(0, QColor(30, 10, 60, 30))
        radial.setColorAt(0.7, QColor(10, 5, 30, 10))
        radial.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), radial)
        
        # Несколько маленьких туманностей
        nebulae = [
            (self.width() // 4, self.height() // 3, 200, QColor(40, 20, 80, 40)),
            (self.width() * 3 // 4, self.height() * 2 // 3, 150, QColor(60, 10, 40, 30)),
            (self.width() // 5, self.height() * 4 // 5, 180, QColor(20, 30, 70, 35))
        ]
        
        for x, y, radius, color in nebulae:
            radial = QRadialGradient(x, y, radius)
            radial.setColorAt(0, color)
            radial.setColorAt(1, QColor(0, 0, 0, 0))
            painter.fillRect(self.rect(), radial)
    
    def draw_stars(self, painter):
        """Рисует анимированные звезды"""
        for star in self.stars:
            star_color = QColor(255, 255, 255, int(star['alpha']))
            painter.setPen(QPen(star_color, star['size']))
            
            # Основная точка звезды
            painter.drawPoint(int(star['x']), int(star['y']))
            
            # Добавляем свечение для больших звезд
            if star['size'] > 1.5:
                glow_color = QColor(255, 255, 255, int(star['alpha'] * 0.3))
                painter.setPen(QPen(glow_color, star['size'] * 2))
                painter.drawPoint(int(star['x']), int(star['y']))

class MainMenuScreen(QWidget):
    """Главное меню игры"""
    
    playClicked = pyqtSignal()
    settingsClicked = pyqtSignal()
    exitClicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Фоновый виджет с градиентом
        background = GradientWidget(self)
        layout.addWidget(background)
        
        # Основной контент поверх фона
        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.setSpacing(40)
        content_layout.setContentsMargins(100, 100, 100, 100)
        
        # Логотип и заголовок
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.setSpacing(10)
        
        # Логотип SKATT x R3DAX
        logo_label = QLabel("SKATT x R3DAX")
        OPENTYPE_MANAGER.apply_styles(logo_label, 36, QFont.Weight.Bold)
        logo_label.setStyleSheet(f"""
            color: {ACCENT2.name()};
            font-size: 36px;
            font-weight: bold;
            font-family: 'Arial';
            letter-spacing: 3px;
        """)
        header_layout.addWidget(logo_label)
        
        # Название игры
        GAME_NAME = AppLogic.name
        title_label = QLabel(GAME_NAME)
        OPENTYPE_MANAGER.apply_styles(title_label, 72, QFont.Weight.Bold)
        title_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY.name()};
            font-size: 72px;
            font-weight: bold;
            font-family: 'Arial';
            margin: 20px 0;
            
        """)
        header_layout.addWidget(title_label)
        
        # Описание игры
        desc_label = QLabel("Построй империю от старта до корпорации")
        desc_label.setStyleSheet(f"""
            color: {TEXT_SECONDARY.name()};
            font-size: 24px;
            font-weight: normal;
            font-family: 'Arial';
            text-align: center;
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)
        
        content_layout.addLayout(header_layout)
        
        # Разделительная линия
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet(f"""
            background-color: {PURPLE_PRIMARY.name()};
            color: {PURPLE_PRIMARY.name()};
            min-height: 2px;
            max-height: 2px;
            margin: 40px 100px;
        """)
        content_layout.addWidget(line)
        
        # Описание геймплея
        gameplay_desc = QLabel("""Стартуй маленьким бизнесом: закупи сырье, управляй активами, инвестируй в улучшения своего бизнеса. Пройди — это вызов — старт.""")
        gameplay_desc.setStyleSheet(f"""
            color: {TEXT_SECONDARY.name()};
            font-size: 18px;
            font-weight: normal;
            font-family: 'Arial';
            text-align: center;
            line-height: 1.5;
        """)
        gameplay_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gameplay_desc.setWordWrap(True)
        gameplay_desc.setMaximumWidth(800)
        content_layout.addWidget(gameplay_desc)
        
        # Кнопки меню
        buttons_layout = QVBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttons_layout.setSpacing(20)
        
        # Кнопка Играть
        play_btn = MenuButton("🎮 Играть")
        play_btn.setFixedSize(350, 80)
        play_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {ACCENT2.name()}, stop:1 {ACCENT1.name()});
                border: 3px solid {LIGHT_PURPLE.name()};
                border-radius: 40px;
                color: {DARK_BG.name()};
                font-size: 24px;
                font-weight: bold;
                padding: 20px 40px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {ACCENT1.name()}, stop:1 {ACCENT2.name()});
                border: 3px solid {WHITE.name()};
            }}
        """)
        play_btn.clicked.connect(self.playClicked.emit)
        buttons_layout.addWidget(play_btn)
        
        # Дополнительные кнопки
        menu_buttons = [
            ("⚙️ Настройки", self.settingsClicked),
            ("🚪 Выход", self.exitClicked)
        ]
        
        for text, signal in menu_buttons:
            btn = MenuButton(text)
            btn.clicked.connect(signal.emit)
            buttons_layout.addWidget(btn)
        
        content_layout.addLayout(buttons_layout)
        
        # Футер с версией
        footer_label = QLabel(f"Version {GAME_VERSION}")
        footer_label.setStyleSheet(f"""
            color: {TEXT_TERTIARY.name()};
            font-size: 14px;
            font-family: 'Arial';
            margin-top: 50px;
        """)
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(footer_label)
        
        # Устанавливаем layout для background
        background_layout = QVBoxLayout()
        background_layout.addLayout(content_layout)
        background.setLayout(background_layout)

        self.setLayout(layout)

class LoadingScreen(QWidget):
    """Экран загрузки с улучшенной анимацией"""
    
    loadingFinished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.progress = 0
        self.dots = 0
        self.rotation_angle = 0
        
        # Используем один таймер для всех анимаций
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animations)
        self.animation_timer.start(30)  # 30 FPS для плавной анимации
        
    def update_animations(self):
        """Обновление всех анимаций"""
        # Прогресс загрузки
        if self.progress < 100:
            self.progress += 2 # Замедляем загрузку для демонстрации
        else:
            self.animation_timer.stop()
            self.loadingFinished.emit()
        
        # Вращение
        self.rotation_angle = (self.rotation_angle + 3) % 360
        
        # Мерцание точек
        self.dots = (self.dots + 1) % 4
        
        self.update()
    
    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Фон как в GradientWidget
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(2, 2, 15))
        gradient.setColorAt(0.3, QColor(8, 8, 40))
        gradient.setColorAt(0.7, QColor(15, 5, 35))
        gradient.setColorAt(1, QColor(2, 2, 15))
        painter.fillRect(self.rect(), gradient)
        
        # Вращающийся логотип
        painter.save()
        painter.translate(self.width() // 2, self.height() // 2 - 100)
        painter.rotate(self.rotation_angle)
        
        # Круг логотипа
        gradient = QRadialGradient(0, 0, 60)
        gradient.setColorAt(0, PURPLE_PRIMARY)
        gradient.setColorAt(1, DEEP_PURPLE)
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(PURPLE_ACCENT, 3))
        painter.drawEllipse(-60, -60, 120, 120)
        
        # Внутренний круг
        gradient_inner = QRadialGradient(0, 0, 30)
        gradient_inner.setColorAt(0, LIGHT_PURPLE)
        gradient_inner.setColorAt(1, PURPLE_PRIMARY)
        painter.setBrush(QBrush(gradient_inner))
        painter.drawEllipse(-30, -30, 60, 60)
        
        painter.restore()
        
        painter.setPen(QPen(TEXT_PRIMARY))
        font = QFont("Arial", 24, QFont.Weight.Bold)
        painter.setFont(font)

        # Всегда используем максимальную длину текста
        base_text = "Загрузка..."
        text_width = painter.fontMetrics().horizontalAdvance(base_text)
        
        # Рисуем текст в фиксированной позиции
        text_x = (self.width() - text_width) // 2
        text_y = self.height() // 2 + 10
        
        # Текущий текст (без дергания)
        loading_texts = ["Загрузка", "Загрузка.", "Загрузка..", "Загрузка..."]
        current_text = loading_texts[self.dots]
        
        painter.drawText(text_x, text_y, current_text)

        
        # Создаем фиксированную область для текста
        # loading_rect = QRect(0, self.height() // 2 - 20, self.width(), 60)
        
        # Используем выравнивание по центру и фиксированную ширину
        # painter.drawText(loading_rect, Qt.AlignmentFlag.AlignCenter, current_text)
        
        # Прогресс-бар
        bar_width = 500
        bar_height = 25
        bar_x = (self.width() - bar_width) // 2
        bar_y = self.height() // 2 + 50
        
        # Фон прогресс-бара
        painter.setBrush(QBrush(DEEP_PURPLE))
        painter.setPen(QPen(PURPLE_PRIMARY, 2))
        painter.drawRoundedRect(bar_x, bar_y, bar_width, bar_height, 12, 12)
        
        # Заполнение
        fill_width = int(bar_width * self.progress / 100)
        if fill_width > 0:
            gradient = QLinearGradient(bar_x, bar_y, bar_x + fill_width, bar_y + bar_height)
            gradient.setColorAt(0, PURPLE_PRIMARY)
            gradient.setColorAt(1, PURPLE_ACCENT)
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(bar_x, bar_y, fill_width, bar_height, 12, 12)
        
        # Процент
        painter.setPen(QPen(TEXT_SECONDARY))
        painter.setFont(QFont("Arial", 14))
        percent_text = f"{self.progress}%"
        painter.drawText(bar_x, bar_y + bar_height + 30, bar_width, 30, 
                        Qt.AlignmentFlag.AlignCenter, percent_text)

class NavigationPanel(QWidget):
    """Панель навигации"""
    
    navigationChanged = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        self.setStyleSheet(f"background-color: {PANEL_BG.name()}; border-radius: 10px;")
        
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 20, 10, 20)
        
        # Заголовок
        title = QLabel("Black Empire")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 18px; font-weight: bold; text-align: center;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Кнопки навигации
        nav_items = [
            ("🎮 Кликер", "clicker"),
            ("🏪 Магазины", "shops"),
            ("📈 Инвестиции", "investments"), 
            ("🏢 Бизнесы", "businesses"),
            ("👤 Профиль", "profile")
        ]
        
        self.buttons = {}
        
        for text, action in nav_items:
            btn = NavigationButton(text, action.split(':')[0] if ':' in text else text.lower())
            btn.setChecked(action == "clicker")
            btn.clicked.connect(lambda checked, a=action: self.navigationChanged.emit(a))
            self.button_group.addButton(btn)
            self.buttons[action] = btn
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Кнопка настроек
        settings_btn = NavigationButton("⚙️ Настройки", "settings")
        settings_btn.clicked.connect(lambda: self.navigationChanged.emit("settings"))
        self.button_group.addButton(settings_btn)
        self.buttons["settings"] = settings_btn
        layout.addWidget(settings_btn)
        
        # Версия игры
        version_label = QLabel(f"v{GAME_VERSION}")
        version_label.setStyleSheet(f"color: {TEXT_TERTIARY.name()}; font-size: 12px; text-align: center;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        self.setLayout(layout)
    
    def set_active_button(self, action):
        if action in self.buttons:
            self.buttons[action].setChecked(True)

class ClickerGame(QWidget):
    """Игровой кликер"""
    
    moneyChanged = pyqtSignal(int)
    exitToMenu = pyqtSignal()
    navigationRequested = pyqtSignal(str)  # Новый сигнал для навигации
    
    def __init__(self):
        super().__init__()
        self.money = 0
        self.per_click = 1
        self.total_clicks = 0
        self.config = GameConfig()
        
        # Список для хранения активных анимаций
        self.active_animations = []
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Левая панель - статистика
        left_panel = QFrame()
        left_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_BG.name()};
                border-radius: 15px;
                border: 2px solid {PURPLE_PRIMARY.name()};
            }}
        """)
        left_panel.setFixedWidth(300)
        
        left_layout = QVBoxLayout()
        
        # Статистика
        stats_group = QGroupBox("Статистика")
        stats_group.setStyleSheet(f"""
            QGroupBox {{
                color: {TEXT_PRIMARY.name()};
                font-size: 16px;
                font-weight: bold;
                border: 2px solid {PURPLE_ACCENT.name()};
                border-radius: 10px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        
        stats_layout = QVBoxLayout()
        
        self.money_label = QLabel("Капитал: $0")
        self.per_click_label = QLabel("Доход за клик: $1")
        self.clicks_label = QLabel("Всего кликов: 0")
        for label in [self.money_label, self.per_click_label, self.clicks_label]:
            OPENTYPE_MANAGER.apply_styles(label, 14, QFont.Weight.Normal)
            label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 14px; padding: 5px;")
            stats_layout.addWidget(label)
        
        stats_group.setLayout(stats_layout)
        left_layout.addWidget(stats_group)
        
        # Кнопки навигации в кликере
        nav_group = QGroupBox("Навигация")
        nav_group.setStyleSheet(stats_group.styleSheet())
        
        nav_layout = QVBoxLayout()
        
        nav_buttons = [
            ("🏪 Магазины", self.show_shops),
            ("📈 Инвестиции", self.show_investments),
            ("🏢 Бизнесы", self.show_businesses),
            ("👤 Профиль", self.show_profile),
            ("🚪 Выход в меню", self.exit_to_menu)
        ]
        
        for text, callback in nav_buttons:
            btn = AnimatedButton(text)
            btn.clicked.connect(callback)
            nav_layout.addWidget(btn)
        
        nav_group.setLayout(nav_layout)
        left_layout.addWidget(nav_group)
        
        left_layout.addStretch()
        left_panel.setLayout(left_layout)
        
        # Центральная панель - игра
        center_panel = QWidget()
        center_layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Корпоративный Кликер")
        OPENTYPE_MANAGER.apply_styles(title, 32, QFont.Weight.Bold)
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 32px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(title)
        
        center_layout.addSpacing(30)
        
        # НОВАЯ КНОПКА КЛИКА С ИМПОРТИРОВАННЫМ СТИЛЕМ
        self.click_button = AnimatedButton("𓀐𓂸ඞ НАЖМИ ЕСЛИ СОСАЛ")
        self.click_button.setFixedSize(600, 600)
        self.apply_imported_button_style()
        self.click_button.clicked.connect(self.handle_click)
        center_layout.addWidget(self.click_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        center_layout.addSpacing(20)
        
        # Инструкция
        instruction = QLabel("Нажимайте на кнопку или используйте ПРОБЕЛ для заработка\nESC - выход в меню")
        OPENTYPE_MANAGER.apply_styles(instruction, 14, QFont.Weight.Normal)
        instruction.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 14px;")
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(instruction)
        
        center_layout.addStretch()
        center_panel.setLayout(center_layout)
        
        # Правая панель - улучшения
        right_panel = QFrame()
        right_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_BG.name()};
                border-radius: 15px;
                border: 2px solid {PURPLE_PRIMARY.name()};
            }}
        """)
        right_panel.setFixedWidth(300)
        
        right_layout = QVBoxLayout()
        
        upgrades_group = QGroupBox("Улучшения")
        upgrades_group.setStyleSheet(stats_group.styleSheet())
        
        upgrades_layout = QVBoxLayout()
        
        upgrade_buttons = [
            ("💼 Увеличить доход", "increase_income", "Увеличивает доход за клик"),
            ("⚡ Ускорить клики", "speed_boost", "Уменьшает задержку между кликами"),
            ("🏢 Инвестировать", "invest", "Пассивный доход")
        ]
        
        for text, action, description in upgrade_buttons:
            btn = AnimatedButton(text)
            btn.setToolTip(description)
            btn.clicked.connect(lambda checked, a=action: self.handle_upgrade(a))
            upgrades_layout.addWidget(btn)
        
        upgrades_group.setLayout(upgrades_layout)
        right_layout.addWidget(upgrades_group)
        
        right_layout.addStretch()
        right_panel.setLayout(right_layout)
        
        # Собираем layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(center_panel, 1)
        main_layout.addWidget(right_panel)
        
        self.setLayout(main_layout)
        
        # Добавляем анимацию пульсации
        self.pulse_animation = QPropertyAnimation(self.click_button, b"windowOpacity")
        self.pulse_animation.setDuration(2000)
        self.pulse_animation.setLoopCount(-1)
        self.pulse_animation.setStartValue(0.9)
        self.pulse_animation.setEndValue(1.0)
        self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.pulse_animation.start()
        
    def apply_imported_button_style(self):
        """Применяет импортированный стиль к кнопке"""
        self.click_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                          stop:0 rgba(122, 47, 255, 0.18),
                                          stop:1 rgba(58, 14, 88, 0.12));
                border-radius: 40px;
                border: 1px solid rgba(255, 255, 255, 0.02);
                color: white;
                font-size: 32px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                          stop:0 rgba(122, 47, 255, 0.22),
                                          stop:1 rgba(58, 14, 88, 0.16));
                border: 1px solid rgba(255, 255, 255, 0.04);
            }
            QPushButton:pressed {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                          stop:0 rgba(122, 47, 255, 0.25),
                                          stop:1 rgba(58, 14, 88, 0.18));
                border: 1px solid rgba(255, 255, 255, 0.03);
            }
        """)
        
    def handle_click(self):
        self.money += self.per_click
        self.total_clicks += 1

        # Увеличения дохода за клик на 0.1%
        self.per_click *= 1.001

        self.update_display()
        self.moneyChanged.emit(self.money)
        
        # Анимация клика с новым стилем
        self.animate_click_imported()
        
    def animate_click_imported(self):
        """Анимация клика с импортированным стилем"""
        # Анимация нажатия кнопки
        self.click_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                          stop:0 rgba(122, 47, 255, 0.25),
                                          stop:1 rgba(58, 14, 88, 0.18));
                border-radius: 40px;
                border: 1px solid rgba(255, 255, 255, 0.03);
                color: white;
                font-size: 32px;
                font-weight: bold;
            }
        """)
        
        # Таймер для возврата обычного стиля
        QTimer.singleShot(150, self.apply_imported_button_style)
        
        # Показываем эффект клика
        self.show_click_effect()
        
    def handle_upgrade(self, action):
        cost = 0
        if action == "increase_income":
            cost = self.per_click * 10
            if self.money >= cost:
                self.money -= cost
                self.per_click += 1
                self.update_display()
        elif action == "speed_boost":
            cost = 500
            if self.money >= cost:
                self.money -= cost
                # Логика ускорения кликов
        elif action == "invest":
            cost = 1000
            if self.money >= cost:
                self.money -= cost
                # Логика инвестиций
        
        self.update_display()
        self.moneyChanged.emit(self.money)
        
    def update_display(self):
        self.money_label.setText(f"Капитал: ${self.money:.1f}")
        self.per_click_label.setText(f"Доход за клик: ${self.per_click:.1f}")
        self.clicks_label.setText(f"Всего кликов: {self.total_clicks}")
        
    # Остальные методы остаются без изменений
    def show_click_effect(self):
        """Визуальный эффект при клике с плавным исчезновением и движением вверх"""
        # Получаем позицию курсора относительно кнопки
        cursor_pos = self.click_button.mapFromGlobal(QCursor.pos())
        
        # Создаем эффектную метку
        effect_label = QLabel(f"+${self.per_click:.2f}", self)
        effect_label.setStyleSheet(f"""
            QLabel {{
                color: #bda8ff;
                font-size: 28px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 0px;
                min-width: 100px;
                max-width: 105px;
            }}
        """)
        effect_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Устанавливаем позицию в точке клика
        global_pos = self.click_button.mapTo(self, cursor_pos)
        effect_label.move(global_pos.x() - 40, global_pos.y() - 20)
        effect_label.resize(80, 40)
        effect_label.show()
        effect_label.raise_()
        
        # Создаем анимационную группу для плавного исчезновения
        animation_group = QParallelAnimationGroup()
        
        # Анимация движения вверх
        move_animation = QPropertyAnimation(effect_label, b"pos")
        move_animation.setDuration(1200)
        move_animation.setStartValue(effect_label.pos())
        move_animation.setEndValue(QPoint(
            effect_label.x(),
            effect_label.y() - 80  # Двигаемся выше
        ))
        move_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Анимация прозрачности (исчезновение)
        fade_animation = QPropertyAnimation(effect_label, b"windowOpacity")
        fade_animation.setDuration(1200)
        fade_animation.setStartValue(1.0)
        fade_animation.setEndValue(0.0)
        fade_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        
        # Добавляем анимации в группу
        animation_group.addAnimation(move_animation)
        animation_group.addAnimation(fade_animation)
        
        # Удаление лейбла после завершения анимации
        animation_group.finished.connect(lambda: effect_label.deleteLater())
        
        # Запускаем анимацию
        animation_group.start()
        
        # Сохраняем ссылку на анимацию
        self.active_animations.append(animation_group)
        
    def remove_effect_label(self, label):
        """Безопасное удаление лейбла эффекта"""
        if label:
            label.deleteLater()
        # Удаляем завершенные анимации из списка
        self.active_animations = [anim for anim in self.active_animations 
                                if anim.state() != QPropertyAnimation.State.Stopped]
        
    def keyPressEvent(self, a0):
        if a0 is not None and a0.key() == Qt.Key.Key_Space:
            self.handle_click()
        elif a0 is not None and a0.key() == Qt.Key.Key_Escape:
            self.exit_to_menu()
        else:
            super().keyPressEvent(a0)
    
    def show_shops(self):
        self.navigationRequested.emit("shops")
    
    def show_investments(self):
        self.navigationRequested.emit("investments")
    
    def show_businesses(self):
        self.navigationRequested.emit("businesses")
    
    def show_profile(self):
        self.navigationRequested.emit("profile")
    
    def exit_to_menu(self):
        self.navigationRequested.emit("main_menu")

@dataclass
class Product:
    id: int
    name: str
    price: int
    description: str
    category: str
    stats: str = ""

class ShopSystem:
    def __init__(self):
        self.export = coreLogic.ExportDB()
        
    def load_products(self, category):
        """Загрузка товаров по категории"""
        products = []
        
        if category == "islands":
            data = self.export.get_shop_islands()
            if data is not None:
                products.append(Product(data[0], data[1], data[2], data[3], "Острова"))
        elif category == "boosters":
            data = self.export.get_shop_boosters()
            if data is not None:
                products.append(Product(data[0], data[1], data[2], data[3], "Бустеры"))
        elif category == "cars":
            data = self.export.get_shop_cars()
            if data is not None:
                products.append(Product(data[0], data[1], data[2], data[3], "Машины", data[4]))
            
        return products

class InvestmentMenu(QWidget):
    """Меню инвестиций"""
    
    exitToClicker = pyqtSignal()
    exitToMenu = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.export = coreLogic.ExportDB()
        self.current_tab = "stocks"
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("Инвестиционный Портфель")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 32px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Кнопка возврата
        back_btn = AnimatedButton("🚪 Назад в меню")
        back_btn.clicked.connect(self.exitToClicker.emit)
        main_layout.addWidget(back_btn)
        
        # Виджет портфеля
        portfolio_widget = self.create_portfolio_widget()
        main_layout.addWidget(portfolio_widget)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {PURPLE_PRIMARY.name()};
                border-radius: 10px;
                background-color: {PANEL_BG.name()};
            }}
            QTabBar::tab {{
                background-color: {DEEP_PURPLE.name()};
                color: {TEXT_PRIMARY.name()};
                padding: 10px 20px;
                border: 1px solid {PURPLE_PRIMARY.name()};
                border-radius: 5px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {PURPLE_PRIMARY.name()};
            }}
            QTabBar::tab:hover {{
                background-color: {PURPLE_ACCENT.name()};
            }}
        """)
        
        # Вкладка акций
        stocks_tab = self.create_stocks_tab()
        self.tab_widget.addTab(stocks_tab, "📈 Акции")
        
        # Вкладка недвижимости
        real_estate_tab = self.create_real_estate_tab()
        self.tab_widget.addTab(real_estate_tab, "🏠 Недвижимость")
        
        # Вкладка криптовалюты
        crypto_tab = self.create_crypto_tab()
        self.tab_widget.addTab(crypto_tab, "₿ Криптовалюта")
        
        main_layout.addWidget(self.tab_widget)
        
        self.setLayout(main_layout)
        
    def create_portfolio_widget(self):
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_BG.name()};
                border: 2px solid {PURPLE_ACCENT.name()};
                border-radius: 15px;
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        portfolio_data = self.export.get_bag()
        if portfolio_data is None:
            portfolio_data = [0, 0, 0, 0, 0]
        stats = [
            f"💰 Стоимость портфеля: ${portfolio_data[0]:,}",
            f"📊 Дивидендная доходность: {portfolio_data[1]}%",
            f"💵 Стабильный доход: ${portfolio_data[2]:,}/час",
            f"🚀 Потенциал роста: {portfolio_data[3]}%"
            f"🏠 Арендная доходность: ${portfolio_data[4]}/час"
        ]
        
        for stat in stats:
            label = QLabel(stat)
            label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 14px; padding: 5px;")
            layout.addWidget(label)
        
        widget.setLayout(layout)
        return widget
        
    def create_stocks_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        stocks = self.export.get_actives()
        for stock in stocks:
            stock_widget = self.create_investment_item(stock, "Акция", "📈")
            layout.addWidget(stock_widget)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_real_estate_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        properties = self.export.get_homes()
        for prop in properties:
            prop_widget = self.create_investment_item(prop, "Недвижимость", "🏠")
            layout.addWidget(prop_widget)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_crypto_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        cryptos = self.export.get_crypto()
        for crypto in cryptos:
            crypto_widget = self.create_investment_item(crypto, "Криптовалюта", "₿")
            layout.addWidget(crypto_widget)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
        
    def create_investment_item(self, name, type, icon):
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG.name()};
                border: 1px solid {PURPLE_PRIMARY.name()};
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        # Информация
        info_layout = QVBoxLayout()
        
        name_label = QLabel(f"{icon} {name}")
        name_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 16px; font-weight: bold;")
        
        type_label = QLabel(type)
        type_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 14px;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(type_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Кнопка действия
        action_btn = AnimatedButton("Инвестировать")
        action_btn.setFixedSize(120, 35)
        layout.addWidget(action_btn)
        
        widget.setLayout(layout)
        return widget
        
    def keyPressEvent(self, a0):
        if a0 is not None and a0.key() == Qt.Key.Key_Escape:
            self.exitToMenu.emit()
        else:
            super().keyPressEvent(a0)

class ShopSelectionMenu(QWidget):
    """Выбор магазина"""
    
    shopSelected = pyqtSignal(str)
    navigationRequested = pyqtSignal(str)
    exitToClicker = pyqtSignal()
    exitToMenu = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Заголовок
        title = QLabel("Магазины")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 48px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Кнопка возврата
        back_btn = AnimatedButton("🚪 Назад в меню")
        back_btn.clicked.connect(self.exitToClicker)
        layout.addWidget(back_btn)
        
        subtitle = QLabel("Выберите магазин для покупок")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 24px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(50)
        
        # Кнопки магазинов
        shops_layout = QHBoxLayout()
        shops_layout.setSpacing(30)
        shops_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Светлый магазин
        light_shop_btn = self.create_shop_button(
            "🏪 Светлый рынок", 
            "Легальные товары и услуги", 
            "legal"
        )
        shops_layout.addWidget(light_shop_btn)
        
        # Черный рынок
        dark_shop_btn = self.create_shop_button(
            "🌑 Черный рынок", 
            "Эксклюзивные и редкие товары", 
            "black_market"
        )
        shops_layout.addWidget(dark_shop_btn)
        
        layout.addLayout(shops_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def create_shop_button(self, title, description, shop_type):
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {PANEL_BG.name()}, stop:1 {CARD_BG.name()});
                border: 3px solid {PURPLE_PRIMARY.name()};
                border-radius: 20px;
                padding: 30px;
            }}
            QFrame:hover {{
                border: 3px solid {PURPLE_ACCENT.name()};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {PURPLE_PRIMARY.name()}, stop:1 {DEEP_PURPLE.name()});
            }}
        """)
        widget.setFixedSize(400, 300)
        widget.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Заголовок
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 28px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        layout.addSpacing(20)
        
        # Описание
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 16px;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(30)
        
        # Кнопка выбора
        select_btn = AnimatedButton("Выбрать")
        select_btn.clicked.connect(lambda: self.shopSelected.emit(shop_type))
        layout.addWidget(select_btn)
        
        widget.setLayout(layout)
        return widget
        
    def keyPressEvent(self, a0):
        if a0 is not None and a0.key() == Qt.Key.Key_Escape:
            self.exitToMenu.emit()
        else:
            super().keyPressEvent(a0)

    def show_clicker_game(self):
        self.navigationRequested.emit("clicker")

class LightShopMenu(QWidget):
    """Светлый магазин"""
    
    exitToShopSelectionMenu = pyqtSignal()
    exitToMenu = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.shop_system = ShopSystem()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("🏪 Светлый рынок")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 32px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Кнопка возврата
        back_btn = AnimatedButton("🚪 Назад в меню")
        back_btn.clicked.connect(self.exitToShopSelectionMenu.emit)
        layout.addWidget(back_btn)
        
        # Категории товаров
        categories_layout = QGridLayout()
        categories_layout.setSpacing(15)
        
        categories = [
            ("🏝️ Острова", "islands"),
            ("🚀 Бустеры", "boosters"), 
            ("🖼️ NFT", "nft"),
            ("🚗 Машины", "cars"),
            ("💎 Уникальные предметы", "unique"),
            ("🛥️ Яхты", "yachts"),
            ("✈️ Самолёты", "planes"),
            ("🏛️ Резиденция", "residence"),
            ("💍 Ювелирные изделия", "jewelry")
        ]
        
        row, col = 0, 0
        for name, category in categories:
            btn = self.create_category_button(name, category)
            categories_layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        layout.addLayout(categories_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def create_category_button(self, name, category):
        btn = AnimatedButton(name)
        btn.setFixedHeight(80)
        btn.clicked.connect(lambda: self.open_category(category))
        return btn
        
    def open_category(self, category):
        print(f"Открыта категория: {category}")
        
    def keyPressEvent(self, a0):
        if a0 is not None and a0.key() == Qt.Key.Key_Escape:
            self.exitToMenu.emit()
        else:
            super().keyPressEvent(a0)

class BusinessManager:
    def __init__(self):
        self.my_businesses = []
        self.business_data = self.load_business_data()
        self.crypto_balance = 50000  # Начальный баланс крипты для трейдинга
        self.reputation = 100  # Репутация игрока
        self.risk_level = 0  # Уровень риска
        self.player_balance = 1000000  # Баланс игрока
        
    def load_business_data(self):
        """Загрузка данных о бизнесах из базы данных"""
        conn = sqlite3.connect("data/businesses.db")
        cursor = conn.cursor()
        
        businesses = []
        
        # Загружаем основные данные бизнесов
        cursor.execute('SELECT * FROM businesses')
        business_rows = cursor.fetchall()
        
        for row in business_rows:
            business = {
                'id': row[0],
                'name': row[1],
                'icon': row[2],
                'level': row[3],
                'income_per_hour': row[4],
                'workers': row[5],
                'workload': row[6],
                'primary_action': row[7],
                'type': row[8],
                'risk': row[9],
                'price': row[10],
                'can_go_dark': bool(row[11]),
                'ev_production': bool(row[12]),
                'bio_prosthetics': bool(row[13]),
                'neuro_chips': bool(row[14]),
                'servers': row[15],
                'data_center': bool(row[16]),
                'heat_recovery': bool(row[17]),
                'botnet_active': bool(row[18]),
                'trust_level': row[19],
                'max_launder_amount': row[20],
                'crypto_reserve_usage': row[21]
            }
            
            # Загружаем роли
            cursor.execute('SELECT name, cost, effect FROM business_roles WHERE business_id = ?', (business['id'],))
            business['available_roles'] = [{'name': r[0], 'cost': r[1], 'effect': r[2]} for r in cursor.fetchall()]
            
            # Загружаем специальные режимы
            cursor.execute('SELECT name, cooldown, cost, effect FROM special_modes WHERE business_id = ?', (business['id'],))
            business['special_modes'] = [{'name': r[0], 'cooldown': r[1], 'cost': r[2], 'effect': r[3]} for r in cursor.fetchall()]
            
            # Загружаем синергии
            cursor.execute('SELECT synergy_name FROM business_synergies WHERE business_id = ?', (business['id'],))
            business['synergies'] = [r[0] for r in cursor.fetchall()]
            
            # Загружаем темные действия
            cursor.execute('SELECT name, income_multiplier, risk_increase FROM dark_actions WHERE business_id = ?', (business['id'],))
            business['dark_actions'] = [{'name': r[0], 'income_multiplier': r[1], 'risk_increase': r[2]} for r in cursor.fetchall()]
            
            # Загружаем улучшения
            cursor.execute('SELECT upgrade_type, level FROM business_upgrades WHERE business_id = ?', (business['id'],))
            upgrades = cursor.fetchall()
            for upgrade_type, level in upgrades:
                business[f'upgrade_{upgrade_type}'] = level
            
            businesses.append(business)
        
        conn.close()
        return businesses
    
    def buy_business(self, business_data):
        """Покупка бизнеса с проверкой баланса"""
        cost = business_data.get('price', business_data.get('income_per_hour', 0) * 100)
        
        if self.player_balance >= cost:
            new_business = business_data.copy()
            new_business['is_owned'] = True
            new_business['level'] = 1  # Убедимся, что уровень установлен
            self.my_businesses.append(new_business)
            self.player_balance -= cost
            return True
        return False
    
    def create_business_from_db_row(self, row):
        """Создание объекта бизнеса из строки базы данных"""
        business = {
            'id': row[0],
            'name': row[1],
            'icon': row[2],
            'level': row[3],
            'income_per_hour': row[4],
            'workers': row[5],
            'workload': row[6],
            'primary_action': row[7],
            'type': row[8],
            'risk': row[9],
            'price': row[10],
            'can_go_dark': bool(row[11]),
            'ev_production': bool(row[12]),
            'bio_prosthetics': bool(row[13]),
            'neuro_chips': bool(row[14]),
            'servers': row[15],
            'data_center': bool(row[16]),
            'heat_recovery': bool(row[17]),
            'botnet_active': bool(row[18]),
            'trust_level': row[19],
            'max_launder_amount': row[20],
            'crypto_reserve_usage': row[21]
        }
        
        # Загружаем дополнительные данные для бизнеса
        conn = sqlite3.connect("data/businesses.db")
        cursor = conn.cursor()
        
        # Загружаем роли
        cursor.execute('SELECT name, cost, effect FROM business_roles WHERE business_id = ?', (business['id'],))
        business['available_roles'] = [{'name': r[0], 'cost': r[1], 'effect': r[2]} for r in cursor.fetchall()]
        
        # Загружаем специальные режимы
        cursor.execute('SELECT name, cooldown, cost, effect FROM special_modes WHERE business_id = ?', (business['id'],))
        business['special_modes'] = [{'name': r[0], 'cooldown': r[1], 'cost': r[2], 'effect': r[3]} for r in cursor.fetchall()]
        
        # Загружаем синергии
        cursor.execute('SELECT synergy_name FROM business_synergies WHERE business_id = ?', (business['id'],))
        business['synergies'] = [r[0] for r in cursor.fetchall()]
        
        # Загружаем темные действия
        cursor.execute('SELECT name, income_multiplier, risk_increase FROM dark_actions WHERE business_id = ?', (business['id'],))
        business['dark_actions'] = [{'name': r[0], 'income_multiplier': r[1], 'risk_increase': r[2]} for r in cursor.fetchall()]
        
        # Загружаем улучшения
        cursor.execute('SELECT upgrade_type, level FROM business_upgrades WHERE business_id = ?', (business['id'],))
        upgrades = cursor.fetchall()
        for upgrade_type, level in upgrades:
            business[f'upgrade_{upgrade_type}'] = level
        
        conn.close()
        return business
    
    def get_total_income(self):
        """Общий доход в час со всех бизнесов"""
        return sum(business.get('income_per_hour', 0) for business in self.my_businesses)
    
    def update_business_upgrade(self, business_id, upgrade_type, new_level):
        """Обновление уровня улучшения в базе данных"""
        conn = sqlite3.connect("data/businesses.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE business_upgrades 
            SET level = ? 
            WHERE business_id = ? AND upgrade_type = ?
        ''', (new_level, business_id, upgrade_type))
        
        conn.commit()
        conn.close()
        
    def upgrade_business(self, business_id, upgrade_type):
        """Улучшение бизнеса с эффектами"""
        for business in self.my_businesses:
            if business['id'] == business_id:
                current_level = business.get(f'upgrade_{upgrade_type}', 1)
                if current_level < 5:
                    business[f'upgrade_{upgrade_type}'] = current_level + 1
                    
                    # Применяем эффекты улучшения
                    self.apply_upgrade_effect(business, upgrade_type, current_level + 1)
                    return True
        return False
    
    def apply_upgrade_effect(self, business, upgrade_type, new_level):
        """Применение эффектов улучшения"""
        effects = {
            1: {  # Производительность
                2: 1.1, 3: 1.25, 4: 1.45, 5: 1.7  # Множители дохода
            },
            2: {  # Качество/Надежность
                2: 1.15, 3: 1.35, 4: 1.6, 5: 2.0  # Множители дохода
            },
            3: {  # Автоматизация
                2: 0.9, 3: 0.75, 4: 0.6, 5: 0.5  # Множители необходимых работников
            },
            4: {  # Инновация
                2: "Разблокировка фичи 1",
                3: "Разблокировка фичи 2", 
                4: "Разблокировка фичи 3",
                5: "Эксклюзивная технология"
            },
            5: {  # Доверие/Скрытность
                2: 0.8, 3: 0.6, 4: 0.4, 5: 0.2  # Множители риска/улучшение доверия
            }
        }
        
        effect = effects[upgrade_type].get(new_level)
        if effect:
            if upgrade_type in [1, 2]:
                business['income_per_hour'] = int(business['income_per_hour'] * effect)
            elif upgrade_type == 3:
                business['workers'] = max(1, int(business['workers'] * effect))
            elif upgrade_type == 4:
                self.unlock_feature(business, effect)
            elif upgrade_type == 5:
                if business['type'] == 'dark':
                    business['risk'] = max(5, int(business.get('risk', 20) * effect))
                else:
                    business['trust_bonus'] = effect  # Бонус к доверию
    
    def unlock_feature(self, business, feature):
        """Разблокировка специальных фич бизнеса"""
        if business['name'] == 'Автопром' and 'EV' in feature:
            business['ev_production'] = True
            business['income_per_hour'] = int(business['income_per_hour'] * 1.5)
        elif business['name'] == 'Робототехника' and 'био' in feature.lower():
            business['bio_prosthetics'] = True
        elif business['name'] == 'Робототехника' and 'нейро' in feature.lower():
            business['neuro_chips'] = True
        elif business['name'] == 'AI разработки' and 'сервер' in feature.lower():
            business['servers'] += 1
        elif business['name'] == 'AI разработки' and 'дата-центр' in feature.lower():
            business['data_center'] = True
            business['income_per_hour'] = int(business['income_per_hour'] * 1.3)
        elif business['name'] == 'Теневой майнинг' and 'рекуперация' in feature.lower():
            business['heat_recovery'] = True
            business['income_per_hour'] = int(business['income_per_hour'] * 1.2)
        elif business['name'] == 'Отмывание денег' and 'доверие' in feature.lower():
            business['trust_level'] += 1
            business['max_launder_amount'] *= 2
    
    def activate_special_mode(self, business, mode_name):
        """Активация специального режима бизнеса"""
        for mode in business.get('special_modes', []):
            if mode['name'] == mode_name:
                # В реальной реализации здесь была бы проверка кулдауна и стоимости
                # Пока просто применяем эффект
                if 'доход' in mode['effect'].lower():
                    # Временное увеличение дохода
                    pass
                elif 'риск' in mode['effect'].lower():
                    # Изменение уровня риска
                    pass
                return True
        return False
    
    def toggle_dark_side(self, business):
        """Перевод бизнеса на темную сторону"""
        if business.get('can_go_dark', False) and business['type'] == 'light':
            business['type'] = 'dark'
            business['income_per_hour'] = int(business['income_per_hour'] * 1.8)
            business['risk'] = 25  # Начальный уровень риска
            self.risk_level += 15
            self.reputation -= 20
            return True
        return False
    
    def calculate_synergy_bonus(self, business1, business2):
        """Расчет бонуса синергии между двумя бизнесами"""
        synergies = {
            ('Биотех Лаборатория', 'Робототехника'): 1.3,  # +30% доход
            ('AI разработки', 'IT-стартап'): 1.25,
            ('Автопром', 'УГМК'): 1.2,
            ('Трейдинг', 'Крипто-майнинг'): 1.35
        }
        
        pair = tuple(sorted([business1['name'], business2['name']]))
        return synergies.get(pair, 1.0)
    

class BusinessMenu(QWidget):
    """Меню бизнесов с полноценной системой карточек"""
    
    exitToClicker = pyqtSignal()
    exitToMenu = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.business_manager = BusinessManager()
        self.current_filter = "all"
        self.my_businesses_layout = None
        self.catalog_scroll = None
        self.my_businesses_scroll = None
        self.catalog_layout = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок с информацией о риске и репутации
        header_layout = QHBoxLayout()
        
        title = QLabel("🏢 Бизнес Империя")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 32px; font-weight: bold;")
        
        risk_label = QLabel(f"⚠️ Уровень риска: {self.business_manager.risk_level}%")
        risk_label.setStyleSheet(f"color: {'#ef4444' if self.business_manager.risk_level > 50 else '#f59e0b'}; font-size: 14px;")
        
        reputation_label = QLabel(f"⭐ Репутация: {self.business_manager.reputation}")
        reputation_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 14px;")
        
        crypto_label = QLabel(f"₿ Крипто: {self.business_manager.crypto_balance:,}")
        crypto_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 14px;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(risk_label)
        header_layout.addWidget(reputation_label)
        header_layout.addWidget(crypto_label)
        
        layout.addLayout(header_layout)
        
        # Кнопка возврата
        back_btn = AnimatedButton("🚪 Назад в меню")
        back_btn.clicked.connect(self.exitToClicker.emit)
        layout.addWidget(back_btn)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {PURPLE_PRIMARY.name()};
                border-radius: 10px;
                background-color: {PANEL_BG.name()};
            }}
            QTabBar::tab {{
                background-color: {DEEP_PURPLE.name()};
                color: {TEXT_PRIMARY.name()};
                padding: 10px 20px;
                border: 1px solid {PURPLE_PRIMARY.name()};
                border-radius: 5px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {PURPLE_PRIMARY.name()};
            }}
            QTabBar::tab:hover {{
                background-color: {PURPLE_ACCENT.name()};
            }}
        """)
        
        # Мои бизнесы
        my_businesses_tab = self.create_my_businesses_tab()
        self.tab_widget.addTab(my_businesses_tab, "💼 Мои бизнесы")
        
        # Каталог бизнесов
        catalog_tab = self.create_catalog_tab()
        self.tab_widget.addTab(catalog_tab, "📋 Каталог")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def refresh_interface(self):
        """Полное обновление интерфейса с сохранением позиции скролла"""
        # Сохраняем позиции скроллов с проверкой
        catalog_scroll_pos = 0
        my_businesses_scroll_pos = 0
        
        if hasattr(self, 'catalog_scroll') and self.catalog_scroll:
            scroll_bar = self.catalog_scroll.verticalScrollBar()
            if scroll_bar:
                catalog_scroll_pos = scroll_bar.value()
        
        if hasattr(self, 'my_businesses_scroll') and self.my_businesses_scroll:
            scroll_bar = self.my_businesses_scroll.verticalScrollBar()
            if scroll_bar:
                my_businesses_scroll_pos = scroll_bar.value()
        
        # Обновляем интерфейс
        if self.my_businesses_layout is not None:
            self.clear_layout(self.my_businesses_layout)
            self.load_my_businesses()
            # Восстанавливаем позицию скролла
            if hasattr(self, 'my_businesses_scroll') and self.my_businesses_scroll:
                scroll_bar = self.my_businesses_scroll.verticalScrollBar()
                if scroll_bar:
                    QTimer.singleShot(50, lambda: scroll_bar.setValue(my_businesses_scroll_pos))
        
        if self.catalog_layout is not None:
            self.clear_layout(self.catalog_layout)
            self.load_catalog()
            # Восстанавливаем позицию скролла
            if hasattr(self, 'catalog_scroll') and self.catalog_scroll:
                scroll_bar = self.catalog_scroll.verticalScrollBar()
                if scroll_bar:
                    QTimer.singleShot(50, lambda: scroll_bar.setValue(catalog_scroll_pos))
        
    def create_my_businesses_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Фильтры для моих бизнесов
        filter_layout = QHBoxLayout()
        
        filter_group = QButtonGroup()
        filters = [
            ("🔍 Все мои бизнесы", "all"),
            ("💡 Светлые", "light"),
            ("🌑 Темные", "dark")
        ]
        
        for text, filter_type in filters:
            btn = QRadioButton(text)
            btn.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 14px; padding: 5px;")
            btn.clicked.connect(lambda checked, ft=filter_type: self.filter_my_businesses(ft))
            filter_group.addButton(btn)
            filter_layout.addWidget(btn)
            if filter_type == "all":
                btn.setChecked(True)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Статистика
        stats_widget = self.create_stats_widget()
        layout.addWidget(stats_widget)
        
        # Сетка моих бизнесов
        self.my_businesses_scroll = QScrollArea()
        self.my_businesses_scroll.setWidgetResizable(True)
        self.my_businesses_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        if self.my_businesses_scroll.verticalScrollBar() is not None:
            my_business_scroll_bar = self.my_businesses_scroll.verticalScrollBar()
            my_business_scroll_bar.setSingleStep(20)
        
        self.my_businesses_container = QWidget()
        self.my_businesses_layout = QGridLayout(self.my_businesses_container)
        self.my_businesses_layout.setSpacing(15)
        self.my_businesses_scroll.setWidget(self.my_businesses_container)
        
        layout.addWidget(self.my_businesses_scroll)
        
        # Загружаем мои бизнесы
        self.load_my_businesses()
        
        return widget
        
    def create_catalog_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Фильтры для каталога
        filter_layout = QHBoxLayout()
        
        filter_group = QButtonGroup()
        filters = [
            ("🔍 Все бизнесы", "all"),
            ("💡 Светлые бизнесы", "light"),
            ("🌑 Темные бизнесы", "dark")
        ]
        
        for text, filter_type in filters:
            btn = QRadioButton(text)
            btn.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 14px; padding: 5px;")
            btn.clicked.connect(lambda checked, ft=filter_type: self.filter_catalog(ft))
            filter_group.addButton(btn)
            filter_layout.addWidget(btn)
            if filter_type == "all":
                btn.setChecked(True)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Сетка каталога
        self.catalog_scroll = QScrollArea()
        self.catalog_scroll.setWidgetResizable(True)
        self.catalog_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        if self.catalog_scroll.verticalScrollBar() is not None:
            scroll_bar = self.catalog_scroll.verticalScrollBar()
            scroll_bar.setSingleStep(20)
        
        self.catalog_container = QWidget()
        self.catalog_layout = QGridLayout(self.catalog_container)
        self.catalog_layout.setSpacing(15)
        self.catalog_scroll.setWidget(self.catalog_container)
        
        layout.addWidget(self.catalog_scroll)
        
        # Загружаем каталог
        self.load_catalog()
        
        return widget
        
    def create_stats_widget(self):
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_BG.name()};
                border: 2px solid {PURPLE_ACCENT.name()};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        total_income = sum(business.get('income_per_hour', 0) for business in self.business_manager.my_businesses)
        total_workers = sum(business.get('workers', 0) for business in self.business_manager.my_businesses)
        
        stats = [
            ("💰 Общий доход/час", f"${total_income:,}"),
            ("🏢 Активных бизнесов", str(len(self.business_manager.my_businesses))),
            ("👥 Всего работников", str(total_workers)),
            ("📈 Уровень империи", "3")
        ]
        
        for name, value in stats:
            stat_layout = QVBoxLayout()
            name_label = QLabel(name)
            name_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 12px;")
            value_label = QLabel(value)
            value_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 16px; font-weight: bold;")
            
            stat_layout.addWidget(name_label)
            stat_layout.addWidget(value_label)
            layout.addLayout(stat_layout)
            layout.addSpacing(20)
        
        widget.setLayout(layout)
        return widget
        
    def create_business_card(self, business_data, is_owned=False):
        """Создание карточки бизнеса"""
        card = QFrame()
        is_dark = business_data.get('type') == 'dark'
        
        card_style = f"""
            QFrame {{
                background-color: {CARD_BG.name()};
                border: 2px solid {'#ef4444' if is_dark else PURPLE_PRIMARY.name()};
                border-radius: 15px;
                padding: 20px;
            }}
        """
        card.setStyleSheet(card_style)
        
        if is_owned:
            card.setFixedSize(600, 750)  # Увеличили для новых функций
        else:
            card.setFixedSize(450, 400)

        layout = QVBoxLayout()
        card.setLayout(layout)  # Устанавливаем layout для карточки
        
        header_layout = QHBoxLayout()
        
        # Иконка и название
        title_layout = QHBoxLayout()
        icon_label = QLabel(business_data.get('icon', '🏢'))
        icon_label.setStyleSheet("font-size: 20px;")
        title_label = QLabel(business_data['name'])
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 18px; font-weight: bold;")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # Уровень и специальные флаги
        level_label = QLabel(f"Ур. {business_data.get('level', 1)}")
        level_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 14px; font-weight: bold;")
        
        header_layout.addLayout(title_layout)
        header_layout.addWidget(level_label)
        
        # Индикаторы специальных возможностей
        if business_data.get('ev_production'):
            ev_label = QLabel("⚡ EV")
            ev_label.setStyleSheet("color: #22c55e; font-size: 12px;")
            header_layout.addWidget(ev_label)
        
        if business_data.get('bio_prosthetics'):
            bio_label = QLabel("🦿 Био")
            bio_label.setStyleSheet("color: #3b82f6; font-size: 12px;")
            header_layout.addWidget(bio_label)
        
        # Индикатор риска для темных бизнесов
        if is_dark:
            risk_label = QLabel("⚠️ Риск")
            risk_label.setStyleSheet("color: #ef4444; font-size: 12px;")
            header_layout.addWidget(risk_label)
        
        # Добавляем header_layout в основной layout только ОДИН раз
        layout.addLayout(header_layout)
        
        # Панель состояния
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(5)
        
        income_label = QLabel(f"💰 Доход/час: ${business_data.get('income_per_hour', 0):,}")
        income_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 14px;")
        
        workers_label = QLabel(f"👥 Работники: {business_data.get('workers', 0)}")
        workers_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 14px;")
        
        if 'workload' in business_data:
            workload_label = QLabel(f"📊 Нагрузка: {business_data['workload']}%")
            workload_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 14px;")
            stats_layout.addWidget(workload_label)
        
        stats_layout.addWidget(income_label)
        stats_layout.addWidget(workers_label)
        layout.addLayout(stats_layout)
        layout.addSpacing(10)
        
        # Главная панель действий
        primary_action_layout = QHBoxLayout()
        
        if is_owned:
            primary_btn = AnimatedButton(business_data['primary_action'])
            primary_btn.setFixedHeight(40)
            primary_btn.clicked.connect(lambda: self.handle_primary_action(business_data))
            primary_action_layout.addWidget(primary_btn)
            
            # Вторичные действия
            secondary_layout = QVBoxLayout()
            
            hire_btn = AnimatedButton("👥 Найм")
            hire_btn.setFixedHeight(40)
            hire_btn.clicked.connect(lambda: self.show_hire_dialog(business_data))
            
            upgrade_btn = AnimatedButton("⚡ Улучшить")
            upgrade_btn.setFixedHeight(40)
            upgrade_btn.clicked.connect(lambda: self.show_upgrades(business_data))
            
            secondary_layout.addWidget(hire_btn)
            secondary_layout.addWidget(upgrade_btn)
            primary_action_layout.addLayout(secondary_layout)
        else:
            # Для каталога - кнопка покупки
            buy_btn = AnimatedButton(f"Купить за ${business_data.get('income_per_hour', 0) * 100:,}")
            buy_btn.setFixedHeight(40)
            buy_btn.clicked.connect(lambda: self.buy_business(business_data))
            primary_action_layout.addWidget(buy_btn)
        
        layout.addLayout(primary_action_layout)
        
        # Панель специальных режимов (только для owned)
        if is_owned and 'special_modes' in business_data:
            special_layout = QVBoxLayout()
            special_label = QLabel("Специальные режимы:")
            special_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 12px;")
            special_layout.addWidget(special_label)
            
            for mode in business_data['special_modes']:
                mode_btn = AnimatedButton(mode['name'])
                mode_btn.setFixedHeight(35)
                if 'cooldown' in mode:
                    mode_btn.setToolTip(f"Кулдаун: {mode['cooldown']}")
                mode_btn.clicked.connect(lambda checked, m=mode, b=business_data: self.activate_special_mode(m, b))
                special_layout.addWidget(mode_btn)
            
            layout.addLayout(special_layout)
        
        # Панель апгрейдов (только для owned)
        if is_owned:
            upgrades_label = QLabel("Улучшения:")
            upgrades_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 12px;")
            layout.addWidget(upgrades_label)
            
            upgrades_layout = QHBoxLayout()
            
            upgrade_types = [
                ("⚡", "Производительность"),
                ("🎯", "Качество"), 
                ("🤖", "Автоматизация"),
                ("💡", "Инновация"),
                ("🛡️", "Доверие" if not is_dark else "Скрытность")
            ]
            
            for i, (icon, name) in enumerate(upgrade_types, 1):
                upgrade_btn = QPushButton(f"{icon} {i}")
                upgrade_btn.setFixedSize(50, 50)
                upgrade_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {PANEL_BG.name()};
                        border: 2px solid {PURPLE_PRIMARY.name()};
                        border-radius: 8px;
                        color: {TEXT_PRIMARY.name()};
                        font-size: 10px;
                    }}
                    QPushButton:hover {{
                        background-color: {PURPLE_PRIMARY.name()};
                    }}
                """)
                current_level = business_data.get(f'upgrade_{i}', 1)
                upgrade_btn.setToolTip(f"{name}\nУровень: {current_level}")
                upgrade_btn.clicked.connect(lambda checked, idx=i, b=business_data: self.upgrade_business(b, idx))
                upgrades_layout.addWidget(upgrade_btn)
            
            layout.addLayout(upgrades_layout)
        
        # Кнопка перехода в темную сторону (для определенных бизнесов)
        if is_owned and business_data.get('can_go_dark', False) and not is_dark:
            dark_btn = AnimatedButton("🌑 Перейти в Тень")
            dark_btn.setStyleSheet("background-color: #7f1d1d; color: white;")
            dark_btn.clicked.connect(lambda: self.toggle_dark_side(business_data))
            layout.addWidget(dark_btn)
        
        layout.addStretch()
        return card
        
    def handle_ev_production(self, business_data):
        """Запуск производства электромобилей"""
        if business_data.get('ev_production', False):
            QMessageBox.information(self, "EV Производство", 
                                  "Запущено производство электромобилей!\nДоход увеличен на 50%")
        else:
            QMessageBox.warning(self, "Требуется улучшение", 
                              "Для производства EV необходимо улучшение 'Инновация' уровня 4")
            
    def load_my_businesses(self):
        """Загрузка купленных бизнесов"""
        if self.my_businesses_layout is None:
            return
            
        # Очищаем layout
        self.clear_layout(self.my_businesses_layout)
        
        # Добавляем бизнесы в сетку (2 колонки)
        row, col = 0, 0
        max_cols = 2
        
        for business_data in self.business_manager.my_businesses:
            # Применяем фильтр
            if self.current_filter == "light" and business_data.get('type') != 'light':
                continue
            elif self.current_filter == "dark" and business_data.get('type') != 'dark':
                continue
                
            card = self.create_business_card(business_data, is_owned=True)
            self.my_businesses_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Если нет бизнесов после фильтрации
        if self.my_businesses_layout.count() == 0:
            no_business_label = QLabel("Нет бизнесов, соответствующих фильтру")
            no_business_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 16px; text-align: center;")
            no_business_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.my_businesses_layout.addWidget(no_business_label, 0, 0, 1, max_cols)

    def clear_layout(self, layout):
        """Безопасная очистка layout"""
        if layout is None:
            return
            
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue
                
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
            else:
                nested_layout = item.layout()
                if nested_layout is not None:
                    self.clear_layout(nested_layout)
        
    def handle_crypto_trading(self, business_data):
        """Запуск крипто-трейдинга"""
        if business_data['name'] == 'Трейдинг':
            dialog = QDialog(self)
            dialog.setWindowTitle("Крипто Трейдинг")
            dialog.setFixedSize(300, 200)
            
            layout = QVBoxLayout(dialog)
            
            amount_label = QLabel("Использовать крипто-резерв:")
            amount_slider = QSlider(Qt.Orientation.Horizontal)
            amount_slider.setRange(10, 100)  # 10% - 100%
            amount_slider.setValue(int(business_data.get('crypto_reserve_usage', 0.1) * 100))
            
            layout.addWidget(amount_label)
            layout.addWidget(amount_slider)
            layout.addWidget(QLabel(f"Используется: {amount_slider.value()}%"))
            
            confirm_btn = AnimatedButton("Запустить стратегию")
            confirm_btn.clicked.connect(dialog.accept)
            layout.addWidget(confirm_btn)
            
            dialog.exec()

    def show_synergy_info(self, business_data):
        """Показать информацию о синергиях"""
        synergies = business_data.get('synergies', [])
        if synergies:
            synergy_text = "Синергии с:\n" + "\n".join(f"• {synergy}" for synergy in synergies)
            QMessageBox.information(self, "Синергии", synergy_text)

    def load_catalog(self):
        """Загрузка каталога бизнесов"""
        if self.catalog_layout is None:
            return
            
        # Очищаем layout
        self.clear_layout(self.catalog_layout)
        
        # Добавляем бизнесы в сетку (2 колонки)
        row, col = 0, 0
        max_cols = 2
        
        available_businesses = []
        
        for business_data in self.business_manager.business_data:
            # Пропускаем уже купленные бизнесы
            if any(b['id'] == business_data['id'] for b in self.business_manager.my_businesses):
                continue
                
            # Применяем фильтр
            if self.current_filter == "light" and business_data.get('type') != 'light':
                continue
            elif self.current_filter == "dark" and business_data.get('type') != 'dark':
                continue
                
            available_businesses.append(business_data)
        
        for business_data in available_businesses:
            card = self.create_business_card(business_data, is_owned=False)
            self.catalog_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Если нет доступных бизнесов
        if not available_businesses:
            no_business_label = QLabel("Нет доступных бизнесов для покупки")
            no_business_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 16px; text-align: center;")
            no_business_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.catalog_layout.addWidget(no_business_label, 0, 0, 1, max_cols)
        
    def filter_my_businesses(self, filter_type):
        """Фильтрация моих бизнесов"""
        self.current_filter = filter_type
        if self.my_businesses_layout is not None:
            # Сохраняем позицию скролла только если скролл существует
            scroll_pos = 0
            if hasattr(self, 'my_businesses_scroll') and self.my_businesses_scroll:
                scroll_bar = self.my_businesses_scroll.verticalScrollBar()
                if scroll_bar:
                    scroll_pos = scroll_bar.value()
            
            self.clear_layout(self.my_businesses_layout)
            self.load_my_businesses()
            
            # Восстанавливаем позицию скролла
            if hasattr(self, 'my_businesses_scroll') and self.my_businesses_scroll:
                scroll_bar = self.my_businesses_scroll.verticalScrollBar()
                if scroll_bar:
                    QTimer.singleShot(10, lambda: scroll_bar.setValue(scroll_pos))
        
    def filter_catalog(self, filter_type):
        """Фильтрация каталога"""
        self.current_filter = filter_type
        if self.catalog_layout is not None:
            # Сохраняем позицию скролла только если скролл существует
            scroll_pos = 0
            if hasattr(self, 'catalog_scroll') and self.catalog_scroll:
                scroll_bar = self.catalog_scroll.verticalScrollBar()
                if scroll_bar:
                    scroll_pos = scroll_bar.value()
            
            self.clear_layout(self.catalog_layout)
            self.load_catalog()
            
            # Восстанавливаем позицию скролла
            if hasattr(self, 'catalog_scroll') and self.catalog_scroll:
                scroll_bar = self.catalog_scroll.verticalScrollBar()
                if scroll_bar:
                    QTimer.singleShot(10, lambda: scroll_bar.setValue(scroll_pos))
        
    def handle_primary_action(self, business_data):
        """Обработка основного действия в зависимости от типа бизнеса"""
        business_name = business_data['name']
        
        if business_name == 'Трейдинг':
            self.handle_crypto_trading(business_data)
        elif business_name == 'Автопром':
            self.handle_ev_production(business_data)
        elif business_name in ['Биотех Лаборатория', 'Робототехника']:
            self.handle_research_development(business_data)
        else:
            # Стандартное действие для остальных бизнесов
            QMessageBox.information(self, "Действие", 
                                f"Выполнено: {business_data['primary_action']}\n"
                                f"Доход: ${business_data.get('income_per_hour', 0):,}")
            
    def handle_research_development(self, business_data):
        """Обработка исследований и разработок"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Исследования - {business_data['name']}")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        research_label = QLabel("Выберите направление исследований:")
        research_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 16px;")
        layout.addWidget(research_label)
        
        # Добавляем варианты исследований в зависимости от бизнеса
        if business_data['name'] == 'Биотех Лаборатория':
            options = ["Генная инженерия", "Фармацевтика", "Биопротезирование"]
        else:  # Робототехника
            options = ["AI интеграция", "Биомеханика", "Автономные системы"]
        
        for option in options:
            btn = AnimatedButton(option)
            btn.clicked.connect(lambda checked, o=option: self.start_research(business_data, o))
            layout.addWidget(btn)
        
        dialog.exec()

    def start_research(self, business_data, research_type):
        """Запуск исследования"""
        QMessageBox.information(self, "Исследование", 
                            f"Запущено исследование: {research_type}\n"
                            f"Бизнес: {business_data['name']}")
        
    def show_hire_dialog(self, business_data):
        """Диалог найма сотрудников"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Найм персонала - {business_data['name']}")
        dialog.setFixedSize(300, 400)
        dialog.setStyleSheet(f"background-color: {PANEL_BG.name()}; color: {TEXT_PRIMARY.name()};")
        
        layout = QVBoxLayout(dialog)
        
        roles_label = QLabel("Доступные роли:")
        roles_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 16px; font-weight: bold;")
        layout.addWidget(roles_label)
        
        roles = business_data.get('available_roles', [])
        for role in roles:
            role_frame = QFrame()
            role_frame.setStyleSheet(f"border: 1px solid {PURPLE_PRIMARY.name()}; border-radius: 5px; padding: 10px; margin: 5px;")
            role_layout = QHBoxLayout(role_frame)
            
            role_name = QLabel(f"{role['name']} - ${role['cost']:,}")
            role_name.setStyleSheet(f"color: {TEXT_PRIMARY.name()};")
            
            hire_btn = AnimatedButton("Нанять")
            hire_btn.setFixedSize(80, 30)
            hire_btn.clicked.connect(lambda checked, r=role: self.hire_employee(r, business_data))
            
            role_layout.addWidget(role_name)
            role_layout.addStretch()
            role_layout.addWidget(hire_btn)
            layout.addWidget(role_frame)
        
        # Чекбокс автонайма
        auto_hire = QCheckBox("Автонаём")
        auto_hire.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; padding: 10px;")
        layout.addWidget(auto_hire)
        
        dialog.exec()
        
    def hire_employee(self, role, business_data):
        """Нанять сотрудника"""
        QMessageBox.information(self, "Найм", f"Нанят: {role['name']}")
        
    def show_upgrades(self, business_data):
        """Показать улучшения"""
        QMessageBox.information(self, "Улучшения", f"Открыты улучшения для {business_data['name']}")
        
    def activate_special_mode(self, mode, business_data):
        """Активировать специальный режим"""
        QMessageBox.information(self, "Специальный режим", f"Активирован: {mode['name']}")
        
    def upgrade_business(self, business_data, upgrade_type):
        """Улучшить бизнес с проверкой стоимости"""
        upgrade_cost = self.calculate_upgrade_cost(business_data, upgrade_type)
        current_level = business_data.get(f'upgrade_{upgrade_type}', 1)
        
        if current_level >= 5:
            QMessageBox.information(self, "Максимальный уровень", 
                                "Достигнут максимальный уровень улучшения!")
            return
            
        # Проверяем баланс (в реальной реализации)
        if self.business_manager.player_balance >= upgrade_cost:
            if self.business_manager.upgrade_business(business_data['id'], upgrade_type):
                QMessageBox.information(self, "Улучшение", 
                                    f"Бизнес улучшен! Уровень {upgrade_type} повышен до {current_level + 1}.")
                self.load_my_businesses()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось улучшить бизнес")
        else:
            QMessageBox.warning(self, "Недостаточно средств", 
                            f"Для улучшения нужно ${upgrade_cost:,}")
            
    def calculate_upgrade_cost(self, business_data, upgrade_type):
        """Расчет стоимости улучшения"""
        base_cost = business_data.get('income_per_hour', 1000)
        current_level = business_data.get(f'upgrade_{upgrade_type}', 1)
        return base_cost * (2 ** current_level)  # Экспоненциальный рост стоимости
    
    def auto_update_businesses(self):
        """Автоматическое обновление состояния бизнесов"""
        for business in self.business_manager.my_businesses:
            # Автоматический доход
            self.add_passive_income(business)
            
            # Обновление состояния бизнеса
            self.update_business_state(business)

    def update_business_state(self, business):
        """Обновление состояния бизнеса (нагрузка, риск и т.д.)"""
        # Обновляем нагрузку
        if 'workload' in business:
            business['workload'] = min(100, business['workload'] + random.randint(1, 5))
            
        # Обновляем риск для темных бизнесов
        if business.get('type') == 'dark':
            business['risk'] = min(95, business.get('risk', 20) + random.randint(1, 3))

    def add_passive_income(self, business):
        """Добавление пассивного дохода от бизнеса"""
        income = business.get('income_per_hour', 0) / 3600  # Доход в секунду
        # В реальной реализации здесь должно добавляться к балансу игрока
        # self.business_manager.player_balance += income
            
    def toggle_dark_side(self, business_data):
        """Переключиться на темную сторону"""
        reply = QMessageBox.question(self, "Переход в Тень", 
                                   "Вы уверены, что хотите перевести бизнес на темную сторону?\n"
                                   "Это даст больше дохода, но увеличит риски.")
        if reply == QMessageBox.StandardButton.Yes:
            business_data['type'] = 'dark'
            business_data['income_per_hour'] = int(business_data['income_per_hour'] * 1.5)
            QMessageBox.information(self, "Успех", "Бизнес переведен на темную сторону! Доход увеличен.")
            self.load_my_businesses()
            
    def buy_business(self, business_data):
        """Купить бизнес с проверкой баланса"""
        cost = business_data.get('price', business_data.get('income_per_hour', 0) * 100)
        
        # Сохраняем позицию скролла перед покупкой с проверкой
        scroll_pos = 0
        if hasattr(self, 'catalog_scroll') and self.catalog_scroll:
            scroll_bar = self.catalog_scroll.verticalScrollBar()
            if scroll_bar:
                scroll_pos = scroll_bar.value()
        
        if self.business_manager.player_balance >= cost:
            if self.business_manager.buy_business(business_data):
                self.business_manager.player_balance -= cost
                
                QMessageBox.information(self, "Покупка", 
                                    f"Бизнес '{business_data['name']}' успешно куплен за ${cost:,}!")
                
                # Обновляем только каталог, сохраняя позицию скролла
                if self.catalog_layout is not None:
                    self.clear_layout(self.catalog_layout)
                    self.load_catalog()
                    # Восстанавливаем позицию скролла
                    if hasattr(self, 'catalog_scroll') and self.catalog_scroll:
                        scroll_bar = self.catalog_scroll.verticalScrollBar()
                        if scroll_bar:
                            QTimer.singleShot(10, lambda: scroll_bar.setValue(scroll_pos))
                
                # Обновляем мои бизнесы
                if self.my_businesses_layout is not None:
                    self.clear_layout(self.my_businesses_layout)
                    self.load_my_businesses()
                    
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось купить бизнес")
        else:
            QMessageBox.warning(self, "Недостаточно средств", 
                            f"Для покупки нужно ${cost:,}, а у вас только ${self.business_manager.player_balance:,}")
    
    def save_business_to_db(self, business):
        """Сохраняем бизнес в базу данных"""
        try:
            conn = sqlite3.connect("data/businesses.db")
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO player_businesses 
                (business_id, level, income_per_hour, workers, workload, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (business['id'], business['level'], business['income_per_hour'], 
                business['workers'], business.get('workload', 0), 1))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Ошибка сохранения бизнеса: {e}")
        
    def keyPressEvent(self, a0):
        if a0 is not None and a0.key() == Qt.Key.Key_Escape:
            self.exitToMenu.emit()
        else:
            super().keyPressEvent(a0)

class BusinessUpgradeSystem:
    """Универсальная система улучшений для всех бизнесов"""
    
    UPGRADE_TYPES = {
        1: {"name": "⚡ Производительность", "effect": "increase_speed", "icon": "⚡", "description": "Увеличивает скорость операций и доход"},
        2: {"name": "🎯 Качество", "effect": "increase_quality", "icon": "🎯", "description": "Повышает качество продукции и снижает риски"},
        3: {"name": "🤖 Автоматизация", "effect": "increase_automation", "icon": "🤖", "description": "Уменьшает потребность в работниках"},
        4: {"name": "💡 Инновация", "effect": "unlock_features", "icon": "💡", "description": "Открывает уникальные возможности"},
        5: {"name": "🛡️ Безопасность", "effect": "increase_security", "icon": "🛡️", "description": "Повышает защиту и снижает риски"}
    }
    
    def __init__(self, business):
        self.business = business
        self.levels = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1}
        self.max_level = 5
        
    def get_upgrade_cost(self, upgrade_type, current_level):
        """Расчет стоимости улучшения"""
        base_cost = self.business.get('base_upgrade_cost', 15000)
        return int(base_cost * (2.5 ** (current_level - 1)))
    
    def can_upgrade(self, upgrade_type):
        """Можно ли улучшить"""
        current_level = self.levels.get(upgrade_type, 1)
        return current_level < self.max_level
    
    def upgrade(self, upgrade_type, player_balance):
        """Улучшение с проверкой стоимости"""
        if not self.can_upgrade(upgrade_type):
            return False, "Максимальный уровень достигнут"
            
        current_level = self.levels[upgrade_type]
        cost = self.get_upgrade_cost(upgrade_type, current_level)
        
        if player_balance < cost:
            return False, f"Недостаточно средств. Нужно ${cost:,}"
        
        self.levels[upgrade_type] += 1
        self.apply_upgrade_effect(upgrade_type, self.levels[upgrade_type])
        return True, f"Улучшение {self.UPGRADE_TYPES[upgrade_type]['name']} повышено до уровня {self.levels[upgrade_type]}"
    
    def apply_upgrade_effect(self, upgrade_type, new_level):
        """Применение эффектов улучшения"""
        effects = {
            1: self._apply_productivity_effect,
            2: self._apply_quality_effect, 
            3: self._apply_automation_effect,
            4: self._apply_innovation_effect,
            5: self._apply_security_effect
        }
        
        if upgrade_type in effects:
            effects[upgrade_type](new_level)
    
    def _apply_productivity_effect(self, level):
        """Эффект производительности"""
        multiplier = 1.0 + (level - 1) * 0.3  # +30% за уровень
        if 'base_income' in self.business:
            self.business['income_per_hour'] = int(self.business['base_income'] * multiplier)
        self.business['efficiency'] = multiplier
    
    def _apply_quality_effect(self, level):
        """Эффект качества"""
        quality_bonus = (level - 1) * 0.2  # +20% за уровень
        self.business['quality_level'] = 1.0 + quality_bonus
        if 'risk' in self.business:
            self.business['risk'] = max(5, self.business['base_risk'] - (level - 1) * 5)
    
    def _apply_automation_effect(self, level):
        """Эффект автоматизации"""
        automation_rate = (level - 1) * 0.25  # +25% автоматизации за уровень
        self.business['automation_level'] = automation_rate
        if 'base_workers' in self.business:
            self.business['workers'] = max(1, int(self.business['base_workers'] * (1 - automation_rate)))
    
    def _apply_innovation_effect(self, level):
        """Эффект инноваций"""
        innovation_features = {
            2: "basic_innovation",
            3: "advanced_innovation", 
            4: "premium_innovation",
            5: "breakthrough_technology"
        }
        
        if level in innovation_features:
            feature = innovation_features[level]
            if 'unlocked_features' not in self.business:
                self.business['unlocked_features'] = []
            self.business['unlocked_features'].append(feature)
            self.unlock_business_specific_feature(feature, level)
    
    def _apply_security_effect(self, level):
        """Эффект безопасности"""
        security_bonus = (level - 1) * 0.15
        self.business['security_level'] = security_bonus
        if 'risk' in self.business:
            self.business['risk'] = max(5, self.business['risk'] - (level - 1) * 3)
    
    def unlock_business_specific_feature(self, feature, level):
        """Разблокировка уникальных фич для каждого бизнеса"""
        business_type = self.business['type']
        business_name = self.business['name']
        
        feature_map = {
            'Биотех Лаборатория': {
                'basic_innovation': {'research_speed': 1.2},
                'advanced_innovation': {'clinical_trials': True},
                'premium_innovation': {'gene_editing': True, 'income_multiplier': 1.4},
                'breakthrough_technology': {'neuro_implants': True, 'bio_prosthetics': True, 'income_multiplier': 1.8}
            },
            'Автопром': {
                'basic_innovation': {'production_speed': 1.3},
                'advanced_innovation': {'hybrid_tech': True},
                'premium_innovation': {'ev_platform': True, 'income_multiplier': 1.6},
                'breakthrough_technology': {'autonomous_driving': True, 'flying_cars': True, 'income_multiplier': 2.0}
            },
            'AI разработки': {
                'basic_innovation': {'training_speed': 1.25},
                'advanced_innovation': {'neural_networks': True},
                'premium_innovation': {'quantum_computing': True, 'income_multiplier': 1.7},
                'breakthrough_technology': {'agi_development': True, 'income_multiplier': 2.2}
            }
        }
        
        if business_name in feature_map and feature in feature_map[business_name]:
            feature_data = feature_map[business_name][feature]
            self.business.update(feature_data)
            
            # Применяем множитель дохода если есть
            if 'income_multiplier' in feature_data:
                multiplier = feature_data['income_multiplier']
                self.business['income_per_hour'] = int(self.business['base_income'] * multiplier)

class BusinessSpecialization:
    """Система специализации бизнесов"""
    
    SPECIALIZATIONS = {
        'tech': {
            'name': 'Технологическая специализация',
            'icon': '💻',
            'effects': {'research_bonus': 0.3, 'innovation_speed': 1.4}
        },
        'production': {
            'name': 'Производственная специализация', 
            'icon': '🏭',
            'effects': {'production_bonus': 0.4, 'cost_reduction': 0.2}
        },
        'service': {
            'name': 'Сервисная специализация',
            'icon': '🛎️',
            'effects': {'client_retention': 0.35, 'premium_pricing': 1.3}
        },
        'research': {
            'name': 'Исследовательская специализация',
            'icon': '🔬',
            'effects': {'breakthrough_chance': 0.25, 'patent_income': 1.5}
        }
    }
    
    def __init__(self, business):
        self.business = business
        self.current_specialization = None
        self.specialization_level = 0
    
    def set_specialization(self, specialization_type):
        """Установка специализации"""
        if specialization_type in self.SPECIALIZATIONS:
            self.current_specialization = specialization_type
            self.specialization_level = 1
            self.apply_specialization_effects()
            return True
        return False
    
    def apply_specialization_effects(self):
        """Применение эффектов специализации"""
        if self.current_specialization:
            effects = self.SPECIALIZATIONS[self.current_specialization]['effects']
            self.business.update(effects)

class BusinessResourceSystem:
    """Система управления ресурсами бизнеса"""
    
    def __init__(self, business):
        self.business = business
        self.resources = {}
        self.supply_chain = []
        self.init_resources()
    
    def init_resources(self):
        """Инициализация ресурсов в зависимости от типа бизнеса"""
        business_type = self.business['type']
        
        resource_templates = {
            'tech': {'servers': 0, 'bandwidth': 100, 'compute_power': 50},
            'manufacturing': {'raw_materials': 100, 'energy': 80, 'logistics': 70},
            'research': {'lab_equipment': 50, 'research_data': 30, 'talent': 80},
            'service': {'client_base': 100, 'service_capacity': 70, 'reputation': 60}
        }
        
        self.resources = resource_templates.get(business_type, {})
    
    def update_resources(self, delta_time):
        """Обновление ресурсов со временем"""
        for resource, value in self.resources.items():
            # Логика потребления/восстановления ресурсов
            if resource in ['energy', 'bandwidth']:
                self.resources[resource] = max(0, value - delta_time * 0.1)
            elif resource in ['client_base', 'reputation']:
                self.resources[resource] = min(100, value + delta_time * 0.05)

class AdvancedBusinessManager:
    """Продвинутый менеджер бизнесов с комплексной экономикой"""
    
    def __init__(self):
        self.my_businesses = []
        self.available_businesses = self.create_business_templates()
        self.synergies = {}
        self.global_events = []
        self.market_conditions = {'demand': 1.0, 'competition': 1.0, 'regulation': 1.0}
        
        # Игровые ресурсы
        self.player_balance = 1000000
        self.crypto_balance = 50000
        self.reputation = 100
        self.risk_level = 0
        self.innovation_points = 0
        
        # Таймеры
        self.economy_timer = QTimer()
        self.economy_timer.timeout.connect(self.update_economy)
        self.economy_timer.start(5000)  # Обновление каждые 5 секунд
        
        self.init_synergies()
        self.init_global_events()
    
    def create_business_templates(self):
        """Создание шаблонов всех бизнесов с глубокими механиками"""
        businesses = []
        
        # 1. БИОТЕХ ЛАБОРАТОРИЯ
        businesses.append({
            'id': 1, 'name': 'Биотех Лаборатория', 'icon': '🔬', 'type': 'research',
            'base_income': 12000, 'base_risk': 30, 'base_workers': 15,
            'price': 200000, 'base_upgrade_cost': 25000,
            'category': 'light', 'can_go_dark': True,
            'description': 'Передовые исследования в генной инженерии и биотехнологиях',
            'primary_action': 'Запустить исследование',
            'special_mechanics': {
                'research_projects': [
                    {'name': 'Генная терапия', 'cost': 80000, 'duration': 48, 'reward': 1.6},
                    {'name': 'Синтетическая биология', 'cost': 120000, 'duration': 72, 'reward': 2.2},
                    {'name': 'Нейроимпланты', 'cost': 200000, 'duration': 96, 'reward': 3.0}
                ],
                'clinical_trials': True,
                'patent_system': True
            },
            'unique_features': ['gene_sequencing', 'crispr_tech', 'bio_printing'],
            'upgrade_system': None,
            'specialization': None,
            'resource_system': None,
            'current_research': None,
            'research_progress': 0,
            'patents': [],
            'unlocked_features': []
        })
        
        # 2. АВТОПРОМ (EV ФОКУС)
        businesses.append({
            'id': 2, 'name': 'Автопром', 'icon': '🚗', 'type': 'manufacturing',
            'base_income': 15000, 'base_risk': 25, 'base_workers': 20,
            'price': 250000, 'base_upgrade_cost': 30000,
            'category': 'light', 'can_go_dark': False,
            'description': 'Производство электромобилей и автономного транспорта',
            'primary_action': 'Запустить производство', 
            'special_mechanics': {
                'production_lines': [
                    {'type': 'ICE', 'efficiency': 1.0, 'cost': 50000},
                    {'type': 'Hybrid', 'efficiency': 1.4, 'cost': 100000},
                    {'type': 'EV', 'efficiency': 2.0, 'cost': 200000},
                    {'type': 'Autonomous', 'efficiency': 3.0, 'cost': 500000}
                ],
                'battery_tech': True,
                'charging_network': True
            },
            'unique_features': ['ev_platform', 'battery_production', 'autonomous_ai'],
            'upgrade_system': None,
            'specialization': None,
            'resource_system': None,
            'current_production': 'ICE',
            'battery_level': 1,
            'charging_stations': 0,
            'unlocked_features': []
        })
        
        # 3. AI РАЗРАБОТКИ
        businesses.append({
            'id': 3, 'name': 'AI разработки', 'icon': '🤖', 'type': 'tech',
            'base_income': 18000, 'base_risk': 35, 'base_workers': 12,
            'price': 300000, 'base_upgrade_cost': 35000,
            'category': 'light', 'can_go_dark': True,
            'description': 'Разработка искусственного интеллекта и машинного обучения',
            'primary_action': 'Запустить обучение',
            'special_mechanics': {
                'ai_models': [
                    {'name': 'Компьютерное зрение', 'cost': 60000, 'training_time': 36},
                    {'name': 'Обработка языка', 'cost': 80000, 'training_time': 48},
                    {'name': 'Преобразующее обучение', 'cost': 150000, 'training_time': 72}
                ],
                'data_centers': True,
                'cloud_services': True
            },
            'unique_features': ['neural_networks', 'deep_learning', 'quantum_ai'],
            'upgrade_system': None,
            'specialization': None,
            'resource_system': None,
            'current_training': None,
            'training_progress': 0,
            'servers': 0,
            'data_centers': 0,
            'unlocked_features': []
        })
        
        # 4. КОСМИЧЕСКИЙ ТУРИЗМ
        businesses.append({
            'id': 4, 'name': 'Космический туризм', 'icon': '🚀', 'type': 'service',
            'base_income': 25000, 'base_risk': 40, 'base_workers': 8,
            'price': 500000, 'base_upgrade_cost': 50000,
            'category': 'light', 'can_go_dark': False,
            'description': 'Орбитальные полеты и космические отели',
            'primary_action': 'Запустить полет',
            'special_mechanics': {
                'spacecrafts': [
                    {'type': 'Суборбитальный', 'capacity': 6, 'cost': 300000},
                    {'type': 'Орбитальный', 'capacity': 4, 'cost': 800000},
                    {'type': 'Лунный', 'capacity': 2, 'cost': 2000000}
                ],
                'space_stations': True,
                'zeroG_experiences': True
            },
            'unique_features': ['reusable_rockets', 'space_hotels', 'mars_missions'],
            'upgrade_system': None,
            'specialization': None,
            'resource_system': None,
            'current_craft': None,
            'flights_completed': 0,
            'space_stations': 0,
            'unlocked_features': []
        })
        
        # 5. ВИРТУАЛЬНАЯ РЕАЛЬНОСТЬ
        businesses.append({
            'id': 5, 'name': 'Виртуальная реальность', 'icon': '🥽', 'type': 'tech',
            'base_income': 14000, 'base_risk': 20, 'base_workers': 10,
            'price': 180000, 'base_upgrade_cost': 22000,
            'category': 'light', 'can_go_dark': True,
            'description': 'Иммерсивные VR/AR решения и метавселенные',
            'primary_action': 'Запустить платформу',
            'special_mechanics': {
                'vr_platforms': [
                    {'name': 'Социальная VR', 'cost': 40000, 'users': 10000},
                    {'name': 'Образовательная VR', 'cost': 60000, 'users': 5000},
                    {'name': 'Корпоративная VR', 'cost': 80000, 'users': 2000}
                ],
                'metaverse': True,
                'haptic_tech': True
            },
            'unique_features': ['full_immersion', 'brain_computer', 'digital_twins'],
            'upgrade_system': None,
            'specialization': None,
            'resource_system': None,
            'active_platforms': [],
            'user_base': 0,
            'metaverse_development': 0,
            'unlocked_features': []
        })
        
        # 6. КРИПТО-МАЙНИНГ
        businesses.append({
            'id': 6, 'name': 'Крипто-майнинг', 'icon': '⛏️', 'type': 'tech',
            'base_income': 16000, 'base_risk': 45, 'base_workers': 5,
            'price': 150000, 'base_upgrade_cost': 20000,
            'category': 'dark', 'can_go_dark': False,
            'description': 'Добыча криптовалюты с передовыми фермами',
            'primary_action': 'Запустить майнинг',
            'special_mechanics': {
                'mining_rigs': [
                    {'type': 'GPU Ферма', 'hashrate': 500, 'cost': 50000},
                    {'type': 'ASIC Майнер', 'hashrate': 2000, 'cost': 100000},
                    {'type': 'Квантовый Майнер', 'hashrate': 10000, 'cost': 500000}
                ],
                'heat_recovery': True,
                'green_mining': True
            },
            'unique_features': ['quantum_mining', 'decentralized_finance', 'smart_contracts'],
            'upgrade_system': None,
            'specialization': None,
            'resource_system': None,
            'mining_rigs': [],
            'total_hashrate': 0,
            'energy_efficiency': 1.0,
            'unlocked_features': []
        })
        
        # 7. КИБЕРБЕЗОПАСНОСТЬ
        businesses.append({
            'id': 7, 'name': 'Кибербезопасность', 'icon': '🛡️', 'type': 'tech',
            'base_income': 17000, 'base_risk': 15, 'base_workers': 15,
            'price': 220000, 'base_upgrade_cost': 28000,
            'category': 'light', 'can_go_dark': True,
            'description': 'Защита от кибератак и консалтинг по безопасности',
            'primary_action': 'Запустить защиту', 
            'special_mechanics': {
                'security_services': [
                    {'name': 'Pentesting', 'cost': 30000, 'clients': 10},
                    {'name': 'SOC Мониторинг', 'cost': 50000, 'clients': 5},
                    {'name': 'Криптография', 'cost': 80000, 'clients': 3}
                ],
                'threat_intelligence': True,
                'zero_trust': True
            },
            'unique_features': ['quantum_encryption', 'ai_threat_detection', 'blockchain_security'],
            'upgrade_system': None,
            'specialization': None,
            'resource_system': None,
            'security_contracts': [],
            'threat_level': 0,
            'client_trust': 100,
            'unlocked_features': []
        })
        
        # Инициализация систем для каждого бизнеса
        for business in businesses:
            business['upgrade_system'] = BusinessUpgradeSystem(business)
            business['specialization'] = BusinessSpecialization(business)
            business['resource_system'] = BusinessResourceSystem(business)
            business['income_per_hour'] = business['base_income']
            business['risk'] = business['base_risk']
            business['workers'] = business['base_workers']
            business['level'] = 1
            business['experience'] = 0
            
        return businesses
    
    def init_synergies(self):
        """Инициализация синергий между бизнесами"""
        self.synergies = {
            ('Биотех Лаборатория', 'AI разработки'): {
                'name': 'Био-ИИ Синергия',
                'description': 'AI ускоряет генетические исследования',
                'bonus': 1.4,
                'requirements': {'biotech_level': 3, 'ai_level': 3},
                'effects': {'research_speed': 1.5, 'breakthrough_chance': 0.3}
            },
            ('Автопром', 'Крипто-майнинг'): {
                'name': 'Зеленая энергия',
                'description': 'Тепло от майнинга питает EV заводы',
                'bonus': 1.3,
                'requirements': {'auto_level': 2, 'mining_level': 4},
                'effects': {'energy_costs': 0.7, 'production_speed': 1.25}
            },
            ('Космический туризм', 'Виртуальная реальность'): {
                'name': 'Космическая VR',
                'description': 'VR симуляции космических полетов',
                'bonus': 1.6,
                'requirements': {'space_level': 3, 'vr_level': 4},
                'effects': {'customer_demand': 1.8, 'premium_pricing': 1.4}
            },
            ('Кибербезопасность', 'Крипто-майнинг'): {
                'name': 'Безопасный майнинг',
                'description': 'Повышенная защита крипто-операций',
                'bonus': 1.35,
                'requirements': {'security_level': 4, 'mining_level': 3},
                'effects': {'security_bonus': 0.5, 'risk_reduction': 0.4}
            }
        }
    
    def init_global_events(self):
        """Инициализация глобальных событий"""
        self.global_events = [
            {
                'name': 'Технологический прорыв',
                'description': 'Новые открытия ускоряют развитие',
                'duration': 24,
                'effects': {'research_speed': 1.3, 'innovation_chance': 0.2},
                'active': False
            },
            {
                'name': 'Экономический кризис',
                'description': 'Рынки нестабильны, риски повышены',
                'duration': 48,
                'effects': {'demand': 0.7, 'risk': 1.4},
                'active': False
            },
            {
                'name': 'Регуляторные изменения',
                'description': 'Новые законы влияют на бизнес',
                'duration': 36,
                'effects': {'compliance_costs': 1.3, 'innovation_speed': 0.8},
                'active': False
            }
        ]
    
    def start_research(self, business_id, research_project):
        """Запуск исследовательского проекта"""
        business = self.get_business_by_id(business_id)
        if not business or business['type'] != 'research':
            return False, "Бизнес не поддерживает исследования"
        
        project_data = next((p for p in business['special_mechanics']['research_projects'] 
                           if p['name'] == research_project), None)
        
        if not project_data:
            return False, "Проект не найден"
        
        if self.player_balance < project_data['cost']:
            return False, f"Недостаточно средств. Нужно ${project_data['cost']:,}"
        
        business['current_research'] = research_project
        business['research_progress'] = 0
        business['research_cost'] = project_data['cost']
        business['research_duration'] = project_data['duration']
        business['research_reward'] = project_data['reward']
        business['research_start_time'] = time.time()
        
        self.player_balance -= project_data['cost']
        return True, f"Исследование '{research_project}' начато"
    
    def start_ai_training(self, business_id, model_name):
        """Запуск обучения AI модели"""
        business = self.get_business_by_id(business_id)
        if not business or business['name'] != 'AI разработки':
            return False, "Только AI бизнес может обучать модели"
        
        model_data = next((m for m in business['special_mechanics']['ai_models'] 
                         if m['name'] == model_name), None)
        
        if not model_data:
            return False, "Модель не найдена"
        
        if self.player_balance < model_data['cost']:
            return False, f"Недостаточно средств. Нужно ${model_data['cost']:,}"
        
        business['current_training'] = model_name
        business['training_progress'] = 0
        business['training_cost'] = model_data['cost']
        business['training_duration'] = model_data['training_time']
        business['training_start_time'] = time.time()
        
        self.player_balance -= model_data['cost']
        return True, f"Обучение модели '{model_name}' начато"
    
    def upgrade_production_line(self, business_id, line_type):
        """Обновление производственной линии"""
        business = self.get_business_by_id(business_id)
        if not business or business['name'] != 'Автопром':
            return False, "Только автопром может обновлять линии"
        
        line_data = next((l for l in business['special_mechanics']['production_lines'] 
                        if l['type'] == line_type), None)
        
        if not line_data:
            return False, "Тип линии не найден"
        
        if self.player_balance < line_data['cost']:
            return False, f"Недостаточно средств. Нужно ${line_data['cost']:,}"
        
        business['current_production'] = line_type
        business['production_efficiency'] = line_data['efficiency']
        business['income_per_hour'] = int(business['base_income'] * line_data['efficiency'])
        
        self.player_balance -= line_data['cost']
        return True, f"Производственная линия обновлена до {line_type}"
    
    def buy_mining_rig(self, business_id, rig_type):
        """Покупка майнинг-рига"""
        business = self.get_business_by_id(business_id)
        if not business or business['name'] != 'Крипто-майнинг':
            return False, "Только майнинг бизнес может покупать риги"
        
        rig_data = next((r for r in business['special_mechanics']['mining_rigs'] 
                       if r['type'] == rig_type), None)
        
        if not rig_data:
            return False, "Тип рига не найден"
        
        if self.player_balance < rig_data['cost']:
            return False, f"Недостаточно средств. Нужно ${rig_data['cost']:,}"
        
        if 'mining_rigs' not in business:
            business['mining_rigs'] = []
        
        business['mining_rigs'].append(rig_data)
        business['total_hashrate'] += rig_data['hashrate']
        business['income_per_hour'] = int(business['base_income'] * (1 + business['total_hashrate'] / 1000))
        
        self.player_balance -= rig_data['cost']
        return True, f"Майнинг-риг {rig_type} приобретен"
    
    def update_economy(self):
        """Обновление экономической системы"""
        current_time = time.time()
        
        # Обновление прогресса исследований и тренировок
        for business in self.my_businesses:
            self.update_business_progress(business, current_time)
            
            # Обновление ресурсов
            if business['resource_system']:
                business['resource_system'].update_resources(5)  # 5 секунд прошло
        
        # Обновление глобальных событий
        self.update_global_events()
        
        # Расчет пассивного дохода
        self.calculate_passive_income()
        
        # Применение синергий
        self.apply_synergies()
    
    def update_business_progress(self, business, current_time):
        """Обновление прогресса бизнеса"""
        # Исследования
        if business.get('current_research') and business.get('research_start_time'):
            elapsed_hours = (current_time - business['research_start_time']) / 3600
            progress = min(100, (elapsed_hours / business['research_duration']) * 100)
            business['research_progress'] = progress
            
            if progress >= 100:
                self.complete_research(business)
        
        # AI тренировка
        if business.get('current_training') and business.get('training_start_time'):
            elapsed_hours = (current_time - business['training_start_time']) / 3600
            progress = min(100, (elapsed_hours / business['training_duration']) * 100)
            business['training_progress'] = progress
            
            if progress >= 100:
                self.complete_training(business)
    
    def complete_research(self, business):
        """Завершение исследования"""
        reward_multiplier = business['research_reward']
        business['income_per_hour'] = int(business['income_per_hour'] * reward_multiplier)
        
        # Начисление инновационных очков
        self.innovation_points += 50
        
        QMessageBox.information(None, "Исследование завершено", 
                              f"Исследование '{business['current_research']}' завершено!\n"
                              f"Доход увеличен в {reward_multiplier}x раза")
        
        business['current_research'] = None
        business['research_progress'] = 0
    
    def complete_training(self, business):
        """Завершение обучения AI модели"""
        model_name = business['current_training']
        
        # Увеличение дохода в зависимости от модели
        income_boost = 1.0
        if model_name == 'Компьютерное зрение':
            income_boost = 1.4
        elif model_name == 'Обработка языка':
            income_boost = 1.6
        elif model_name == 'Преобразующее обучение':
            income_boost = 2.0
        
        business['income_per_hour'] = int(business['income_per_hour'] * income_boost)
        self.innovation_points += 30
        
        QMessageBox.information(None, "Обучение завершено",
                              f"Модель '{model_name}' обучена!\n"
                              f"Доход увеличен в {income_boost}x раза")
        
        business['current_training'] = None
        business['training_progress'] = 0
    
    def calculate_passive_income(self):
        """Расчет пассивного дохода"""
        total_income = sum(business['income_per_hour'] for business in self.my_businesses)
        income_per_second = total_income / 3600
        self.player_balance += income_per_second * 5  # За 5 секунд
    
    def apply_synergies(self):
        """Применение синергий между бизнесами"""
        for (biz1_name, biz2_name), synergy in self.synergies.items():
            biz1 = self.get_business_by_name(biz1_name)
            biz2 = self.get_business_by_name(biz2_name)
            
            if biz1 and biz2:
                req = synergy['requirements']
                if (biz1['level'] >= req.get(f'{biz1_name.lower().split()[0]}_level', 1) and 
                    biz2['level'] >= req.get(f'{biz2_name.lower().split()[0]}_level', 1)):
                    
                    # Применяем эффекты синергии
                    for effect, value in synergy['effects'].items():
                        if effect in biz1:
                            biz1[effect] *= value
                        if effect in biz2:
                            biz2[effect] *= value
    
    def update_global_events(self):
        """Обновление глобальных событий"""
        # Упрощенная логика для демонстрации
        if random.random() < 0.01:  # 1% шанс каждые 5 секунд
            event = random.choice(self.global_events)
            event['active'] = True
            event['start_time'] = time.time()
            
            QMessageBox.information(None, "Глобальное событие", 
                                  f"{event['name']}\n\n{event['description']}")
    
    def get_business_by_id(self, business_id):
        """Поиск бизнеса по ID"""
        return next((b for b in self.my_businesses if b['id'] == business_id), None)
    
    def get_business_by_name(self, business_name):
        """Поиск бизнеса по имени"""
        return next((b for b in self.my_businesses if b['name'] == business_name), None)
    
    def buy_business(self, business_template):
        """Покупка бизнеса"""
        if self.player_balance >= business_template['price']:
            new_business = business_template.copy()
            new_business['is_owned'] = True
            new_business['level'] = 1
            new_business['experience'] = 0
            
            # Инициализация систем
            new_business['upgrade_system'] = BusinessUpgradeSystem(new_business)
            new_business['specialization'] = BusinessSpecialization(new_business)
            new_business['resource_system'] = BusinessResourceSystem(new_business)
            
            self.my_businesses.append(new_business)
            self.player_balance -= business_template['price']
            return True, f"Бизнес '{business_template['name']}' успешно приобретен!"
        else:
            return False, f"Недостаточно средств. Нужно ${business_template['price']:,}"

@dataclass
class Business:
    id: int
    name: str
    icon: str
    type: str
    category: str
    base_income: int
    base_risk: int
    base_workers: int
    price: int
    base_upgrade_cost: int
    description: str
    primary_action: str
    can_go_dark: bool = False
    width_percent: float = 45.0  # Ширина в % (меньше 50% чтобы было 2 в ряд)
    height_percent: float = 30.0 # Высота в %
    position_x: float = 0.0      # Позиция X в %
    position_y: float = 0.0      # Позиция Y в %

class RevolutionaryBusinessMenu(QWidget):
    """Совершенно новое меню бизнесов с революционным дизайном и правильным позиционированием"""
    
    exitToClicker = pyqtSignal()
    exitToMenu = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.business_manager = AdvancedBusinessManager()
        self.current_filter = "all"
        self.selected_specialization = None
        self.current_business_view = None
        
        # Инициализация stacked_widget и details_layout
        self.stacked_widget = QStackedWidget()
        self.details_layout = QVBoxLayout()
        
        # Создаем бизнесы с правильным позиционированием
        self.business_templates = self.create_business_templates_with_layout()
        
        self.init_ui()
        self.setup_business_timers()

    def create_business_templates_with_layout(self):
        """Создание бизнесов с правильным расположением в сетке"""
        businesses = []
        
        # Сетка 2x3 с правильными отступами
        grid_positions = [
            # Ряд 1 (сверху)
            (2.5, 10),   # Колонка 1
            (52.5, 10),  # Колонка 2
            
            # Ряд 2 (середина)  
            (2.5, 40),   # Колонка 1
            (52.5, 40),  # Колонка 2
            
            # Ряд 3 (снизу)
            (2.5, 70),   # Колонка 1
            (52.5, 70),  # Колонка 2
        ]
        
        business_data = [
            # 1. БИОТЕХ ЛАборатория
            {
                'id': 1, 'name': 'Биотех Лаборатория', 'icon': '🔬', 'type': 'research',
                'category': 'light', 'base_income': 12000, 'base_risk': 30, 'base_workers': 15,
                'price': 200000, 'base_upgrade_cost': 25000, 'can_go_dark': True,
                'description': 'Передовые исследования в генной инженерии и биотехнологиях',
                'primary_action': 'Запустить исследование'
            },
            # 2. АВТОПРОМ
            {
                'id': 2, 'name': 'Автопром', 'icon': '🚗', 'type': 'manufacturing', 
                'category': 'light', 'base_income': 15000, 'base_risk': 25, 'base_workers': 20,
                'price': 250000, 'base_upgrade_cost': 30000, 'can_go_dark': False,
                'description': 'Производство электромобилей и автономного транспорта',
                'primary_action': 'Запустить производство'
            },
            # 3. AI РАЗРАБОТКИ
            {
                'id': 3, 'name': 'AI разработки', 'icon': '🤖', 'type': 'tech',
                'category': 'light', 'base_income': 18000, 'base_risk': 35, 'base_workers': 12,
                'price': 300000, 'base_upgrade_cost': 35000, 'can_go_dark': True,
                'description': 'Разработка искусственного интеллекта и машинного обучения',
                'primary_action': 'Запустить обучение'
            },
            # 4. КОСМИЧЕСКИЙ ТУРИЗМ
            {
                'id': 4, 'name': 'Космический туризм', 'icon': '🚀', 'type': 'service',
                'category': 'light', 'base_income': 25000, 'base_risk': 40, 'base_workers': 8,
                'price': 500000, 'base_upgrade_cost': 50000, 'can_go_dark': False,
                'description': 'Орбитальные полеты и космические отели',
                'primary_action': 'Запустить полет'
            },
            # 5. ВИРТУАЛЬНАЯ РЕАЛЬНОСТЬ
            {
                'id': 5, 'name': 'Виртуальная реальность', 'icon': '🥽', 'type': 'tech',
                'category': 'light', 'base_income': 14000, 'base_risk': 20, 'base_workers': 10,
                'price': 180000, 'base_upgrade_cost': 22000, 'can_go_dark': True,
                'description': 'Иммерсивные VR/AR решения и метавселенные',
                'primary_action': 'Запустить платформу'
            },
            # 6. КРИПТО-МАЙНИНГ
            {
                'id': 6, 'name': 'Крипто-майнинг', 'icon': '⛏️', 'type': 'tech',
                'category': 'dark', 'base_income': 16000, 'base_risk': 45, 'base_workers': 5,
                'price': 150000, 'base_upgrade_cost': 20000, 'can_go_dark': False,
                'description': 'Добыча криптовалюты с передовыми фермами',
                'primary_action': 'Запустить майнинг'
            }
        ]
        
        for i, (pos_x, pos_y) in enumerate(grid_positions):
            if i < len(business_data):
                data = business_data[i]
                businesses.append(Business(
                    id=data['id'],
                    name=data['name'],
                    icon=data['icon'],
                    type=data['type'],
                    category=data['category'],
                    base_income=data['base_income'],
                    base_risk=data['base_risk'],
                    base_workers=data['base_workers'],
                    price=data['price'],
                    base_upgrade_cost=data['base_upgrade_cost'],
                    description=data['description'],
                    primary_action=data['primary_action'],
                    can_go_dark=data['can_go_dark'],
                    width_percent=45.0,  # 45% ширины экрана
                    height_percent=25.0, # 25% высоты экрана  
                    position_x=pos_x,    # Позиция X в %
                    position_y=pos_y     # Позиция Y в %
                ))
        
        return businesses

    def init_ui(self):
        """Инициализация революционного UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Заголовок с расширенной статистикой
        header_widget = self.create_enhanced_header()
        main_layout.addWidget(header_widget)
        
        # Кнопка возврата
        back_btn = AnimatedButton("🚪 Назад в меню")
        back_btn.clicked.connect(self.exitToClicker.emit)
        main_layout.addWidget(back_btn)
        
        # Панель быстрых действий
        quick_actions = self.create_quick_actions_panel()
        main_layout.addWidget(quick_actions)
        
        # Stacked widget для переключения между видами
        self.stacked_widget = QStackedWidget()
        
        # Главный вид с вкладками
        self.main_tabs_widget = self.create_enhanced_tabs()
        self.stacked_widget.addWidget(self.main_tabs_widget)
        
        # Виджет деталей бизнеса (изначально скрыт)
        details_widget = QWidget()
        self.details_layout = QVBoxLayout(details_widget)
        self.details_layout.setContentsMargins(10, 10, 10, 10)
        self.details_layout.setSpacing(10)
        
        # Добавляем скролл для деталей
        details_scroll = QScrollArea()
        details_scroll.setWidgetResizable(True)
        details_scroll.setWidget(details_widget)
        details_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.stacked_widget.addWidget(details_scroll)
        
        main_layout.addWidget(self.stacked_widget, 1)
        
        self.setLayout(main_layout)

    def create_enhanced_header(self):
        """Создание улучшенного заголовка"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {PANEL_BG.name()}, stop:1 {DEEP_PURPLE.name()});
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        # Основная информация
        info_layout = QVBoxLayout()
        
        title = QLabel("🏢 БИЗНЕС ИМПЕРИЯ 2.0")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 28px; font-weight: bold;")
        
        stats_layout = QHBoxLayout()
        
        stats = [
            (f"💰 ${self.business_manager.player_balance:,}", "Баланс"),
            (f"📈 {len(self.business_manager.my_businesses)}", "Бизнесов"),
            (f"⚡ {self.business_manager.innovation_points}", "Инновации"),
            (f"🛡️ {self.business_manager.reputation}", "Репутация"),
            (f"⚠️ {self.business_manager.risk_level}%", "Риск")
        ]
        
        for value, label in stats:
            stat_widget = self.create_stat_widget(value, label)
            stats_layout.addWidget(stat_widget)
        
        info_layout.addWidget(title)
        info_layout.addLayout(stats_layout)
        layout.addLayout(info_layout)
        
        # Кнопки глобальных действий
        action_layout = QVBoxLayout()
        
        global_actions = [
            ("🎯 Автооптимизация", self.auto_optimize),
            ("📊 Анализ рынка", self.market_analysis),
            ("🚀 Ускорение", self.global_boost)
        ]
        
        for text, callback in global_actions:
            btn = AnimatedButton(text)
            btn.setFixedHeight(35)
            btn.clicked.connect(callback)
            action_layout.addWidget(btn)
        
        layout.addLayout(action_layout)
        
        header.setLayout(layout)
        return header

    def create_stat_widget(self, value, label):
        """Создание виджета статистики"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 16px; font-weight: bold;")
        
        label_label = QLabel(label)
        label_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 12px;")
        
        layout.addWidget(value_label)
        layout.addWidget(label_label)
        widget.setLayout(layout)
        
        return widget

    def create_quick_actions_panel(self):
        """Панель быстрых действий"""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG.name()};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        actions = [
            ("🔍 Все бизнесы", "all"),
            ("💡 Светлые", "light"),
            ("🌑 Темные", "dark"),
            ("🚀 Технологии", "tech"),
            ("🏭 Производство", "manufacturing")
        ]
        
        for text, filter_type in actions:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setChecked(filter_type == "all")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {PANEL_BG.name()};
                    color: {TEXT_PRIMARY.name()};
                    border: 2px solid {PURPLE_PRIMARY.name()};
                    border-radius: 8px;
                    padding: 8px 12px;
                    margin: 2px;
                }}
                QPushButton:checked {{
                    background-color: {PURPLE_PRIMARY.name()};
                    color: white;
                }}
                QPushButton:hover {{
                    border-color: {PURPLE_ACCENT.name()};
                }}
            """)
            btn.clicked.connect(lambda checked, ft=filter_type: self.filter_businesses(ft))
            layout.addWidget(btn)
        
        panel.setLayout(layout)
        return panel

    def create_enhanced_tabs(self):
        """Создание улучшенных вкладок"""
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {PURPLE_PRIMARY.name()};
                border-radius: 10px;
                background-color: {PANEL_BG.name()};
            }}
            QTabBar::tab {{
                background-color: {DEEP_PURPLE.name()};
                color: {TEXT_PRIMARY.name()};
                padding: 12px 20px;
                border: 1px solid {PURPLE_PRIMARY.name()};
                border-radius: 5px;
                margin-right: 2px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: {PURPLE_PRIMARY.name()};
            }}
            QTabBar::tab:hover {{
                background-color: {PURPLE_ACCENT.name()};
            }}
        """)
        
        # Мои бизнесы
        my_businesses_tab = self.create_my_businesses_tab()
        tab_widget.addTab(my_businesses_tab, "💼 МОИ БИЗНЕСЫ")
        
        # Каталог
        catalog_tab = self.create_enhanced_catalog_tab()
        tab_widget.addTab(catalog_tab, "📋 КАТАЛОГ")
        
        # Синергии
        synergies_tab = self.create_synergies_tab()
        tab_widget.addTab(synergies_tab, "🔄 СИНЕРГИИ")
        
        # Аналитика
        analytics_tab = self.create_analytics_tab()
        tab_widget.addTab(analytics_tab, "📊 АНАЛИТИКА")
        
        return tab_widget

    def create_my_businesses_tab(self):
        """Создание вкладки моих бизнесов"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Заголовок раздела
        header_label = QLabel("💼 ВАШИ БИЗНЕСЫ")
        header_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY.name()};
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
            background-color: {PANEL_BG.name()};
            border-radius: 10px;
            border: 2px solid {PURPLE_PRIMARY.name()};
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Статистика империи
        empire_stats = self.create_empire_stats()
        layout.addWidget(empire_stats)
        
        # Контейнер для карточек бизнесов
        self.my_businesses_scroll = QScrollArea()
        self.my_businesses_scroll.setWidgetResizable(True)
        self.my_businesses_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255,255,255,0.1);
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(120, 20, 220, 0.6);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(160, 60, 255, 0.8);
            }
        """)
        
        self.my_businesses_container = QWidget()
        self.my_businesses_layout = QGridLayout(self.my_businesses_container)
        self.my_businesses_layout.setSpacing(20)
        self.my_businesses_layout.setContentsMargins(20, 20, 20, 20)
        self.my_businesses_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.my_businesses_scroll.setWidget(self.my_businesses_container)
        layout.addWidget(self.my_businesses_scroll, 1)
        
        # Загружаем бизнесы
        self.load_my_businesses()
        
        return widget

    def create_empire_stats(self):
        """Создание статистики империи"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {PANEL_BG.name()}, stop:1 {DEEP_PURPLE.name()});
                border: 2px solid {PURPLE_ACCENT.name()};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout(widget)
        
        total_income = sum(b['income_per_hour'] for b in self.business_manager.my_businesses)
        total_workers = sum(b['workers'] for b in self.business_manager.my_businesses)
        light_businesses = len([b for b in self.business_manager.my_businesses if b.get('category') == 'light'])
        dark_businesses = len([b for b in self.business_manager.my_businesses if b.get('category') == 'dark'])
        
        stats = [
            (f"💰 ${total_income:,}/час", "Общий доход"),
            (f"👥 {total_workers}", "Всего работников"),
            (f"💡 {light_businesses}", "Светлых бизнесов"),
            (f"🌑 {dark_businesses}", "Темных бизнесов"),
            (f"🏆 {len(self.business_manager.my_businesses)}", "Всего бизнесов")
        ]
        
        for value, title in stats:
            stat_layout = QVBoxLayout()
            value_label = QLabel(value)
            value_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 16px; font-weight: bold;")
            
            title_label = QLabel(title)
            title_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 12px;")
            
            stat_layout.addWidget(value_label)
            stat_layout.addWidget(title_label)
            layout.addLayout(stat_layout)
            layout.addSpacing(20)
        
        layout.addStretch()
        return widget

    def create_enhanced_catalog_tab(self):
        """Создание улучшенной вкладки каталога"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Заголовок раздела
        header_label = QLabel("📋 КАТАЛОГ БИЗНЕСОВ")
        header_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY.name()};
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
            background-color: {PANEL_BG.name()};
            border-radius: 10px;
            border: 2px solid {PURPLE_PRIMARY.name()};
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Панель фильтров
        filter_widget = self.create_filter_panel()
        layout.addWidget(filter_widget)
        
        # Статистика каталога
        stats_widget = self.create_catalog_stats()
        layout.addWidget(stats_widget)
        
        # Контейнер для карточек бизнесов
        self.catalog_scroll = QScrollArea()
        self.catalog_scroll.setWidgetResizable(True)
        self.catalog_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255,255,255,0.1);
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(120, 20, 220, 0.6);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(160, 60, 255, 0.8);
            }
        """)
        
        self.catalog_container = QWidget()
        self.catalog_layout = QGridLayout(self.catalog_container)
        self.catalog_layout.setSpacing(20)
        self.catalog_layout.setContentsMargins(20, 20, 20, 20)
        self.catalog_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.catalog_scroll.setWidget(self.catalog_container)
        layout.addWidget(self.catalog_scroll, 1)
        
        # Загружаем каталог
        self.load_catalog()
        
        return widget

    def create_filter_panel(self):
        """Создание панели фильтров"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_BG.name()};
                border: 2px solid {PURPLE_PRIMARY.name()};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout(widget)
        
        # Заголовок фильтров
        filter_label = QLabel("🔍 Фильтры:")
        filter_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 14px; font-weight: bold;")
        layout.addWidget(filter_label)
        
        # Кнопки фильтров
        filters = [
            ("🌐 Все", "all"),
            ("💡 Светлые", "light"),
            ("🌑 Темные", "dark"),
            ("🔬 Наука", "research"),
            ("🏭 Производство", "manufacturing"),
            ("💻 Технологии", "tech")
        ]
        
        self.filter_group = QButtonGroup()
        for text, filter_type in filters:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setChecked(filter_type == "all")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {DEEP_PURPLE.name()};
                    color: {TEXT_PRIMARY.name()};
                    border: 2px solid {PURPLE_PRIMARY.name()};
                    border-radius: 8px;
                    padding: 8px 12px;
                    margin: 2px;
                    font-size: 11px;
                }}
                QPushButton:checked {{
                    background-color: {PURPLE_PRIMARY.name()};
                    color: white;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border-color: {PURPLE_ACCENT.name()};
                }}
            """)
            btn.clicked.connect(lambda checked, ft=filter_type: self.filter_catalog(ft))
            self.filter_group.addButton(btn)
            layout.addWidget(btn)
        
        layout.addStretch()
        return widget

    def create_catalog_stats(self):
        """Создание статистики каталога"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {PANEL_BG.name()}, stop:1 {DEEP_PURPLE.name()});
                border: 2px solid {PURPLE_ACCENT.name()};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout(widget)
        
        # Статистика
        available_count = len([b for b in self.business_templates 
                             if not any(owned['id'] == b.id for owned in self.business_manager.my_businesses)])
        owned_count = len(self.business_manager.my_businesses)
        total_income = sum(b['income_per_hour'] for b in self.business_manager.my_businesses)
        
        stats = [
            (f"📊 Доступно: {available_count}", f"из {len(self.business_templates)}"),
            (f"💼 Ваши: {owned_count}", f"бизнеса"),
            (f"💰 Общий доход:", f"${total_income:,}/час")
        ]
        
        for title, value in stats:
            stat_layout = QVBoxLayout()
            title_label = QLabel(title)
            title_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 12px;")
            
            value_label = QLabel(value)
            value_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 14px; font-weight: bold;")
            
            stat_layout.addWidget(title_label)
            stat_layout.addWidget(value_label)
            layout.addLayout(stat_layout)
            layout.addSpacing(20)
        
        layout.addStretch()
        return widget

    def create_synergies_tab(self):
        """Создание вкладки синергий"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("🔄 СИНЕРГИИ БИЗНЕСОВ")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Заглушка для синергий
        synergy_info = QLabel("Система синергий будет доступна после покупки нескольких бизнесов\n\n"
                            "Комбинируйте бизнесы для получения бонусов к доходу!")
        synergy_info.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 16px;")
        synergy_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        synergy_info.setWordWrap(True)
        layout.addWidget(synergy_info)
        
        layout.addStretch()
        return widget

    def create_analytics_tab(self):
        """Создание вкладки аналитики"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("📊 АНАЛИТИКА ИМПЕРИИ")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Заглушка для аналитики
        analytics_info = QLabel("Детальная аналитика будет доступна при развитии бизнесов\n\n"
                              "Отслеживайте эффективность, риски и тенденции рынка!")
        analytics_info.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 16px;")
        analytics_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        analytics_info.setWordWrap(True)
        layout.addWidget(analytics_info)
        
        layout.addStretch()
        return widget

    def create_business_card(self, business, is_owned=False, container_width=0, container_height=0):
        """Создает карточку бизнеса с правильными размерами и позиционированием"""
        card = QFrame()
        
        # Рассчитываем реальные размеры на основе процентов
        if container_width > 0 and container_height > 0:
            width = int(container_width * business.width_percent / 100)
            height = int(container_height * business.height_percent / 100)
        else:
            # Значения по умолчанию
            width = 400
            height = 250
        
        card.setFixedSize(width, height)
        
        # Стиль в зависимости от типа бизнеса
        border_color = PURPLE_PRIMARY.name() if business.category == 'light' else "#dc2626"
        background_color = CARD_BG.name() if not is_owned else PANEL_BG.name()
        
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {background_color}, stop:1 {DEEP_PURPLE.name()});
                border: 3px solid {border_color};
                border-radius: 15px;
                padding: 15px;
            }}
            QFrame:hover {{
                border: 3px solid {PURPLE_ACCENT.name()};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {PURPLE_PRIMARY.name()}, stop:1 {DEEP_PURPLE.name()});
            }}
        """)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Заголовок с иконкой и названием
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(business.icon)
        icon_label.setStyleSheet("font-size: 20px;")
        
        name_label = QLabel(business.name)
        name_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY.name()}; 
            font-size: 16px; 
            font-weight: bold;
        """)
        name_label.setWordWrap(True)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        # Уровень для owned бизнесов
        if is_owned:
            level_label = QLabel(f"🎯 Ур.1")
            level_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 12px; font-weight: bold;")
            header_layout.addWidget(level_label)
        
        layout.addLayout(header_layout)
        
        # Описание
        desc_label = QLabel(business.description)
        desc_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 11px;")
        desc_label.setWordWrap(True)
        desc_label.setMaximumHeight(40)
        layout.addWidget(desc_label)
        
        # Основная информация
        info_layout = QGridLayout()
        info_layout.setHorizontalSpacing(10)
        info_layout.setVerticalSpacing(5)
        
        stats = [
            ("💰 Доход/час:", f"${business.base_income:,}"),
            ("👥 Работники:", str(business.base_workers)),
            ("🎯 Тип:", business.type),
            ("🏷️ Категория:", "💡 Светлый" if business.category == 'light' else "🌑 Темный")
        ]
        
        for i, (name, value) in enumerate(stats):
            name_label = QLabel(name)
            name_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 10px;")
            
            value_label = QLabel(value)
            value_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 10px; font-weight: bold;")
            
            info_layout.addWidget(name_label, i // 2, (i % 2) * 2)
            info_layout.addWidget(value_label, i // 2, (i % 2) * 2 + 1)
        
        layout.addLayout(info_layout)
        
        # Риск для темных бизнесов
        if business.category == 'dark':
            risk_frame = QFrame()
            risk_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(239, 68, 68, 0.2);
                    border: 1px solid #ef4444;
                    border-radius: 6px;
                    padding: 5px;
                }}
            """)
            risk_layout = QHBoxLayout(risk_frame)
            risk_label = QLabel(f"⚠️ Уровень риска: {business.base_risk}%")
            risk_label.setStyleSheet("color: #ef4444; font-size: 10px; font-weight: bold;")
            risk_layout.addWidget(risk_label)
            layout.addWidget(risk_frame)
        
        layout.addStretch()
        
        # Кнопка действия
        if is_owned:
            action_btn = AnimatedButton("⚡ Управлять")
            action_btn.setFixedHeight(30)
            action_btn.clicked.connect(lambda: self.show_business_details_tab(business))
        else:
            action_btn = AnimatedButton(f"💰 ${business.price:,}")
            action_btn.setFixedHeight(30)
            action_btn.clicked.connect(lambda: self.show_business_details(business))
            
            # Проверяем, хватает ли денег
            if self.business_manager.player_balance < business.price:
                action_btn.setEnabled(False)
                action_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {TEXT_TERTIARY.name()};
                        color: {TEXT_SECONDARY.name()};
                        border: 2px solid {TEXT_TERTIARY.name()};
                        border-radius: 8px;
                        font-size: 11px;
                        font-weight: bold;
                    }}
                """)
        
        layout.addWidget(action_btn)
        
        return card

    def load_my_businesses(self):
        """Загрузка собственных бизнесов с правильным позиционированием"""
        if hasattr(self, 'my_businesses_layout'):
            self.clear_layout(self.my_businesses_layout)
            
            if not self.business_manager.my_businesses:
                # Сообщение, если нет бизнесов
                empty_label = QLabel("🏪 У вас пока нет бизнесов\n\nПосетите вкладку 'Каталог' для покупки!")
                empty_label.setStyleSheet(f"""
                    color: {TEXT_SECONDARY.name()}; 
                    font-size: 18px; 
                    text-align: center;
                    padding: 60px;
                    background-color: {PANEL_BG.name()};
                    border-radius: 15px;
                    border: 2px dashed {PURPLE_PRIMARY.name()};
                """)
                empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                empty_label.setMinimumHeight(300)
                self.my_businesses_layout.addWidget(empty_label, 0, 0, 1, 2)
                return
            
            # Получаем размеры контейнера
            container_size = self.my_businesses_container.size()
            container_width = container_size.width()
            container_height = container_size.height()
            
            # Создаем карточки для каждого бизнеса
            for i, business_data in enumerate(self.business_manager.my_businesses):
                # Находим шаблон бизнеса
                business_template = next((b for b in self.business_templates if b.id == business_data['id']), None)
                if business_template:
                    card = self.create_business_card(
                        business_template, 
                        is_owned=True,
                        container_width=container_width,
                        container_height=container_height
                    )
                    
                    # Позиционируем в сетке 2x3
                    row = i // 2
                    col = i % 2
                    self.my_businesses_layout.addWidget(card, row, col)
            
            # Добавляем растягивающиеся элементы для правильного расположения
            rows_needed = (len(self.business_manager.my_businesses) + 1) // 2
            for row in range(rows_needed):
                self.my_businesses_layout.setRowStretch(row, 1)
            self.my_businesses_layout.setColumnStretch(0, 1)
            self.my_businesses_layout.setColumnStretch(1, 1)

    def load_catalog(self):
        """Загрузка каталога бизнесов с правильным позиционированием"""
        if hasattr(self, 'catalog_layout'):
            self.clear_layout(self.catalog_layout)
            
            # Фильтруем доступные бизнесы (еще не купленные)
            available_businesses = []
            for business in self.business_templates:
                if not any(owned['id'] == business.id for owned in self.business_manager.my_businesses):
                    if self.current_filter == "all" or business.category == self.current_filter:
                        available_businesses.append(business)
            
            if not available_businesses:
                # Сообщение, если все бизнесы куплены
                empty_label = QLabel("🎊 Все доступные бизнесы приобретены!\n\nРазвивайте текущие для увеличения дохода.")
                empty_label.setStyleSheet(f"""
                    color: {TEXT_SECONDARY.name()}; 
                    font-size: 18px; 
                    text-align: center;
                    padding: 60px;
                    background-color: {PANEL_BG.name()};
                    border-radius: 15px;
                    border: 2px dashed {ACCENT2.name()};
                """)
                empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                empty_label.setMinimumHeight(300)
                self.catalog_layout.addWidget(empty_label, 0, 0, 1, 2)
                return
            
            # Получаем размеры контейнера
            container_size = self.catalog_container.size()
            container_width = container_size.width()
            container_height = container_size.height()
            
            # Создаем карточки для каждого доступного бизнеса
            for i, business in enumerate(available_businesses):
                card = self.create_business_card(
                    business,
                    is_owned=False,
                    container_width=container_width,
                    container_height=container_height
                )
                
                # Позиционируем в сетке 2x3
                row = i // 2
                col = i % 2
                self.catalog_layout.addWidget(card, row, col)
            
            # Добавляем растягивающиеся элементы
            rows_needed = (len(available_businesses) + 1) // 2
            for row in range(rows_needed):
                self.catalog_layout.setRowStretch(row, 1)
            self.catalog_layout.setColumnStretch(0, 1)
            self.catalog_layout.setColumnStretch(1, 1)

    def show_business_details_tab(self, business_data):
        """Показывает детали бизнеса во вкладке вместо диалога"""
        self.current_business_view = business_data
        
        # Очищаем layout деталей
        self.clear_layout(self.details_layout)
        
        # Кнопка возврата к списку
        back_btn = AnimatedButton("← Назад к списку бизнесов")
        back_btn.clicked.connect(self.show_main_tabs)
        back_btn.setFixedHeight(40)
        self.details_layout.addWidget(back_btn)
        
        # Заголовок бизнеса
        header = self.create_business_management_header(business_data)
        self.details_layout.addWidget(header)
        
        # Основные показатели
        metrics = self.create_business_metrics(business_data)
        self.details_layout.addWidget(metrics)
        
        # Улучшения
        upgrades = self.create_business_upgrades_section(business_data)
        self.details_layout.addWidget(upgrades)
        
        # Действия бизнеса
        actions = self.create_business_actions_section(business_data)
        self.details_layout.addWidget(actions)
        
        # Добавляем растягивающийся элемент в конец
        self.details_layout.addStretch(1)
        
        # Переключаемся на вид деталей
        self.stacked_widget.setCurrentIndex(1)
    
    def show_main_tabs(self):
        """Возвращает к основным вкладкам"""
        self.stacked_widget.setCurrentIndex(0)
        # Обновляем интерфейс при возврате
        self.refresh_interface()

    def show_business_details(self, business):
        """Показ детальной информации о бизнесе"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"🏢 {business.name} - Детали")
        dialog.setFixedSize(500, 600)
        dialog.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {DARK_BG.name()}, stop:1 {PANEL_BG.name()});
                color: {TEXT_PRIMARY.name()};
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Заголовок
        header = self.create_business_detail_header(business)
        layout.addWidget(header)
        
        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {PURPLE_PRIMARY.name()}; margin: 10px 0;")
        layout.addWidget(line)
        
        # Детальная информация
        details = self.create_business_detail_info(business)
        layout.addWidget(details)
        
        # Улучшения (превью)
        upgrades = self.create_business_upgrades_preview(business)
        layout.addWidget(upgrades)
        
        layout.addStretch()
        
        # Кнопки действий
        button_layout = QHBoxLayout()
        
        buy_btn = AnimatedButton(f"💰 Купить за ${business.price:,}")
        buy_btn.setFixedHeight(45)
        buy_btn.clicked.connect(lambda: self.buy_business_from_details(business, dialog))
        
        # Проверяем баланс
        if self.business_manager.player_balance < business.price:
            buy_btn.setEnabled(False)
            buy_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {TEXT_TERTIARY.name()};
                    color: {TEXT_SECONDARY.name()};
                    border: 2px solid {TEXT_TERTIARY.name()};
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                }}
            """)
        
        cancel_btn = AnimatedButton("❌ Отмена")
        cancel_btn.setFixedHeight(45)
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(buy_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        dialog.exec()

    def create_business_detail_header(self, business):
        """Создание заголовка для детального просмотра"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {PANEL_BG.name()}, stop:1 {DEEP_PURPLE.name()});
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        
        layout = QHBoxLayout(widget)
        
        # Иконка и название
        title_layout = QVBoxLayout()
        icon_label = QLabel(business.icon)
        icon_label.setStyleSheet("font-size: 32px;")
        
        name_label = QLabel(business.name)
        name_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 24px; font-weight: bold;")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(name_label)
        layout.addLayout(title_layout)
        
        layout.addStretch()
        
        # Цена и категория
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        price_label = QLabel(f"${business.price:,}")
        price_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 20px; font-weight: bold;")
        
        category_label = QLabel("💡 Светлый бизнес" if business.category == 'light' else "🌑 Темный бизнес")
        category_label.setStyleSheet(f"color: {'#22c55e' if business.category == 'light' else '#ef4444'}; font-size: 14px;")
        
        info_layout.addWidget(price_label)
        info_layout.addWidget(category_label)
        layout.addLayout(info_layout)
        
        return widget

    def create_business_detail_info(self, business):
        """Создание детальной информации о бизнесе"""
        widget = QGroupBox("📊 Характеристики бизнеса")
        widget.setStyleSheet(f"""
            QGroupBox {{
                color: {TEXT_PRIMARY.name()};
                font-size: 16px;
                font-weight: bold;
                border: 2px solid {PURPLE_ACCENT.name()};
                border-radius: 10px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        
        layout = QGridLayout()
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(10)
        
        characteristics = [
            ("💰 Базовый доход/час:", f"${business.base_income:,}", "Доход без улучшений"),
            ("👥 Базовые работники:", str(business.base_workers), "Начальное количество"),
            ("⚡ Тип бизнеса:", business.type, "Основная специализация"),
            ("🔄 Основное действие:", business.primary_action, "Главная операция"),
            ("🎯 Категория:", "💡 Светлый" if business.category == 'light' else "🌑 Темный", "Тип деятельности")
        ]
        
        # Добавляем риск для темных бизнесов
        if business.category == 'dark':
            characteristics.append(
                ("⚠️ Уровень риска:", f"{business.base_risk}%", "Вероятность проблем")
            )
        
        # Добавляем возможность перехода в тень
        if business.can_go_dark:
            characteristics.append(
                ("🌑 Может в тень:", "Да", "Можно перевести в темный бизнес")
            )
        
        for i, (title, value, description) in enumerate(characteristics):
            # Заголовок
            title_label = QLabel(title)
            title_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 12px; font-weight: bold;")
            layout.addWidget(title_label, i, 0)
            
            # Значение
            value_label = QLabel(value)
            value_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 12px;")
            layout.addWidget(value_label, i, 1)
            
            # Описание
            desc_label = QLabel(description)
            desc_label.setStyleSheet(f"color: {TEXT_TERTIARY.name()}; font-size: 10px; font-style: italic;")
            layout.addWidget(desc_label, i, 2)
        
        widget.setLayout(layout)
        return widget

    def create_business_upgrades_preview(self, business):
        """Создание превью системы улучшений"""
        widget = QGroupBox("⚡ Система улучшений")
        widget.setStyleSheet(f"""
            QGroupBox {{
                color: {TEXT_PRIMARY.name()};
                font-size: 16px;
                font-weight: bold;
                border: 2px solid {PURPLE_ACCENT.name()};
                border-radius: 10px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        upgrade_types = [
            ("⚡", "Производительность", "Увеличивает доход и скорость операций"),
            ("🎯", "Качество", "Повышает качество и снижает риски"),
            ("🤖", "Автоматизация", "Уменьшает потребность в работниках"),
            ("💡", "Инновация", "Открывает уникальные возможности"),
            ("🛡️", "Безопасность", "Повышает защиту от рисков")
        ]
        
        for icon, name, description in upgrade_types:
            upgrade_frame = QFrame()
            upgrade_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {CARD_BG.name()};
                    border: 1px solid {PURPLE_PRIMARY.name()};
                    border-radius: 8px;
                    padding: 10px;
                    margin: 2px;
                }}
            """)
            
            upgrade_layout = QHBoxLayout(upgrade_frame)
            
            # Иконка
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 16px;")
            upgrade_layout.addWidget(icon_label)
            
            # Текст
            text_layout = QVBoxLayout()
            name_label = QLabel(name)
            name_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 12px; font-weight: bold;")
            
            desc_label = QLabel(description)
            desc_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 10px;")
            desc_label.setWordWrap(True)
            
            text_layout.addWidget(name_label)
            text_layout.addWidget(desc_label)
            upgrade_layout.addLayout(text_layout)
            upgrade_layout.addStretch()
            
            layout.addWidget(upgrade_frame)
        
        widget.setLayout(layout)
        return widget

    def buy_business_from_details(self, business, dialog):
        """Покупка бизнеса из детального просмотра"""
        # Создаем данные бизнеса для менеджера
        business_data = {
            'id': business.id,
            'name': business.name,
            'icon': business.icon,
            'type': business.type,
            'category': business.category,
            'base_income': business.base_income,
            'income_per_hour': business.base_income,
            'base_risk': business.base_risk,
            'risk': business.base_risk,
            'base_workers': business.base_workers,
            'workers': business.base_workers,
            'price': business.price,
            'base_upgrade_cost': business.base_upgrade_cost,
            'description': business.description,
            'primary_action': business.primary_action,
            'can_go_dark': business.can_go_dark,
            'level': 1,
            'experience': 0
        }
        
        success, message = self.business_manager.buy_business(business_data)
        
        if success:
            # Обновляем UI
            self.update_balance_display()
            self.load_my_businesses()
            self.load_catalog()
            
            # Показываем сообщение об успехе
            self.show_notification(f"🎉 Успешно!", f"Бизнес '{business.name}' куплен!")
            
            # Закрываем диалог
            dialog.accept()
        else:
            # Показываем ошибку
            self.show_notification("❌ Ошибка", message)

    def show_notification(self, title, message):
        """Показ уведомления"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {DARK_BG.name()};
                color: {TEXT_PRIMARY.name()};
            }}
            QMessageBox QPushButton {{
                background-color: {PURPLE_PRIMARY.name()};
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }}
        """)
        msg.exec()

    def update_balance_display(self):
        """Обновление отображения баланса"""
        if hasattr(self, 'balance_label'):
            self.balance_label.setText(f"💰 ${self.business_manager.player_balance:,}")

    def create_business_management_header(self, business_data):
        """Создает заголовок для управления бизнесом"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {PANEL_BG.name()}, stop:1 {DEEP_PURPLE.name()});
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Иконка и название
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        
        icon_label = QLabel(business_data.icon)
        icon_label.setStyleSheet("font-size: 24px;")
        
        name_label = QLabel(business_data.name)
        name_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 20px; font-weight: bold;")
        
        desc_label = QLabel(business_data.description)
        desc_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 12px;")
        desc_label.setWordWrap(True)
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(name_label)
        title_layout.addWidget(desc_label)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Уровень и доход
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(5)
        stats_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        level_label = QLabel(f"🎯 Уровень 1")
        level_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 16px; font-weight: bold;")
        
        income_label = QLabel(f"💰 ${business_data.base_income:,}/час")
        income_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 18px; font-weight: bold;")
        
        # Статус бизнеса
        status_text = "💡 Светлый бизнес" if business_data.category == 'light' else "🌑 Темный бизнес"
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"color: {'#22c55e' if business_data.category == 'light' else '#ef4444'}; font-size: 14px;")
        
        stats_layout.addWidget(level_label)
        stats_layout.addWidget(income_label)
        stats_layout.addWidget(status_label)
        
        layout.addLayout(stats_layout)
        
        return widget

    def create_business_metrics(self, business_data):
        """Создает виджет с основными метриками бизнеса"""
        widget = QGroupBox("📊 Основные показатели")
        widget.setStyleSheet(f"""
            QGroupBox {{
                color: {TEXT_PRIMARY.name()};
                font-size: 14px;
                font-weight: bold;
                border: 1px solid {PURPLE_ACCENT.name()};
                border-radius: 8px;
                margin-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px 0 3px;
            }}
        """)

        layout = QGridLayout()
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(10)

        # Основные метрики
        metrics = [
            ("💰 Текущий доход/час", f"${business_data.base_income:,}", 
             "Базовый доход + бонусы улучшений", ACCENT2.name()),
            
            ("📈 Базовый доход", f"${business_data.base_income:,}", 
             "Доход без учета улучшений", TEXT_PRIMARY.name()),
            
            ("👥 Занятость", f"{business_data.base_workers} работников", 
             f"Автоматизация: 0%", "#3b82f6"),
            
            ("⚡ Эффективность", "1.0x", 
             "Множитель от улучшений", "#f59e0b"),
        ]

        # Для темных бизнесов добавляем риск
        if business_data.category == 'dark':
            metrics.append(
                ("⚠️ Уровень риска", f"{business_data.base_risk}%", 
                 "Вероятность проблем", "#ef4444")
            )

        row, col = 0, 0
        for i, (title, value, description, color) in enumerate(metrics):
            metric_widget = self.create_compact_metric_card(title, value, description, color)
            layout.addWidget(metric_widget, row, col)
            
            col += 1
            if col >= 2:  # 2 колонки
                col = 0
                row += 1

        widget.setLayout(layout)
        return widget

    def create_compact_metric_card(self, title, value, description, color):
        """Создает компактную карточку метрики"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG.name()};
                border: 1px solid {PURPLE_PRIMARY.name()};
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        widget.setFixedHeight(70)  # Фиксированная высота

        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(5, 5, 5, 5)

        # Заголовок
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 10px;")

        # Значение
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")

        # Описание
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"color: {TEXT_TERTIARY.name()}; font-size: 8px;")
        desc_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(desc_label)

        return widget

    def create_business_upgrades_section(self, business_data):
        """Создает раздел улучшений бизнеса"""
        widget = QGroupBox("⚡ Система улучшений")
        widget.setStyleSheet(f"""
            QGroupBox {{
                color: {TEXT_PRIMARY.name()};
                font-size: 14px;
                font-weight: bold;
                border: 1px solid {PURPLE_ACCENT.name()};
                border-radius: 8px;
                margin-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px 0 3px;
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Прогресс уровня бизнеса
        level_progress = self.create_compact_level_progress(business_data)
        layout.addWidget(level_progress)

        # Сетка улучшений - 2 колонки
        upgrades_grid = QGridLayout()
        upgrades_grid.setHorizontalSpacing(10)
        upgrades_grid.setVerticalSpacing(8)

        upgrade_types = [
            (1, "⚡", "Производительность", "Увеличивает доход и скорость операций"),
            (2, "🎯", "Качество", "Повышает качество и снижает риски"),
            (3, "🤖", "Автоматизация", "Уменьшает потребность в работниках"),
            (4, "💡", "Инновация", "Открывает уникальные возможности"),
            (5, "🛡️", "Безопасность", "Повышает защиту от рисков")
        ]
        
        for upgrade_type, icon, name, description in upgrade_types:
            upgrade_widget = self.create_compact_upgrade_widget(
                upgrade_type, icon, name, description, business_data
            )
            
            row = (upgrade_type - 1) // 2  # 2 колонки
            col = (upgrade_type - 1) % 2
            upgrades_grid.addWidget(upgrade_widget, row, col)

        layout.addLayout(upgrades_grid)
        widget.setLayout(layout)
        return widget

    def create_compact_level_progress(self, business_data):
        """Создает компактный прогресс бар уровня бизнеса"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_BG.name()};
                border: 1px solid {PURPLE_PRIMARY.name()};
                border-radius: 6px;
                padding: 10px;
            }}
        """)

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Информация о уровне
        level_info = QVBoxLayout()
        level_info.setSpacing(2)
        
        level_label = QLabel(f"🎯 Уровень: 1")
        level_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 12px; font-weight: bold;")
        
        exp_label = QLabel(f"Опыт: 0/1000")
        exp_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 10px;")

        level_info.addWidget(level_label)
        level_info.addWidget(exp_label)

        # Прогресс бар
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(2)
        
        progress_bar = QProgressBar()
        progress_bar.setValue(0)
        progress_bar.setMaximum(100)
        progress_bar.setFixedHeight(12)
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {PURPLE_PRIMARY.name()};
                border-radius: 6px;
                text-align: center;
                background-color: {DARK_BG.name()};
                color: {TEXT_PRIMARY.name()};
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT1.name()}, stop:1 {ACCENT2.name()});
                border-radius: 5px;
            }}
        """)

        next_level_label = QLabel("След. уровень: +10% доход")
        next_level_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 9px;")

        progress_layout.addWidget(progress_bar)
        progress_layout.addWidget(next_level_label)

        layout.addLayout(level_info)
        layout.addStretch()
        layout.addLayout(progress_layout)

        return widget

    def create_compact_upgrade_widget(self, upgrade_type, icon, name, description, business_data):
        """Создает компактный виджет улучшения"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG.name()};
                border: 1px solid {PURPLE_PRIMARY.name()};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        widget.setFixedHeight(100)  # Фиксированная высота

        layout = QVBoxLayout(widget)
        layout.setSpacing(4)
        layout.setContentsMargins(5, 5, 5, 5)

        # Заголовок улучшения
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 14px;")
        
        name_label = QLabel(name[:10])  # Обрезаем длинные названия
        name_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 10px; font-weight: bold;")
        
        level_label = QLabel(f"1/5")
        level_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 9px; font-weight: bold;")

        header_layout.addWidget(icon_label)
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(level_label)

        layout.addLayout(header_layout)

        # Текущий эффект
        current_effect = self.get_upgrade_effect(upgrade_type, 1)
        effect_label = QLabel(current_effect[:20])  # Обрезаем длинный текст
        effect_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 9px;")
        effect_label.setWordWrap(True)
        layout.addWidget(effect_label)

        # Кнопка улучшения
        upgrade_cost = business_data.base_upgrade_cost
        upgrade_btn = AnimatedButton(f"${upgrade_cost:,}")
        upgrade_btn.setFixedHeight(20)
        upgrade_btn.setStyleSheet("font-size: 9px;")
        upgrade_btn.clicked.connect(
            lambda: self.upgrade_business_from_management(business_data, upgrade_type, upgrade_cost)
        )
        
        # Проверяем, хватает ли денег
        if self.business_manager.player_balance < upgrade_cost:
            upgrade_btn.setEnabled(False)
            upgrade_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {TEXT_TERTIARY.name()};
                    color: {TEXT_SECONDARY.name()};
                    border: 1px solid {TEXT_TERTIARY.name()};
                    border-radius: 4px;
                    font-size: 9px;
                }}
            """)
        
        layout.addWidget(upgrade_btn)

        return widget

    def get_upgrade_effect(self, upgrade_type, level):
        """Возвращает текстовое описание эффекта улучшения"""
        effects = {
            1: {1: "+0% доход", 2: "+30% доход", 3: "+60% доход", 4: "+100% доход", 5: "+150% доход"},
            2: {1: "+0% качество", 2: "+20% качество", 3: "+45% качество", 4: "+75% качество", 5: "+120% качество"},
            3: {1: "0% автоматизация", 2: "25% автоматизация", 3: "50% автоматизация", 4: "70% автоматизация", 5: "90% автоматизация"},
            4: {1: "Базовые возможности", 2: "Новые функции", 3: "Продвинутые технологии", 4: "Эксклюзивные разработки", 5: "Прорывные инновации"},
            5: {1: "Базовая защита", 2: "+20% безопасность", 3: "+45% безопасность", 4: "+75% безопасность", 5: "+120% безопасность"}
        }
        
        return effects.get(upgrade_type, {}).get(level, "Неизвестный эффект")

    def upgrade_business_from_management(self, business_data, upgrade_type, cost):
        """Улучшение бизнеса из меню управления"""
        if self.business_manager.player_balance >= cost:
            self.business_manager.player_balance -= cost
            self.show_notification("✅ Успех!", f"Улучшение '{self.get_upgrade_name(upgrade_type)}' применено!")
            self.update_balance_display()
        else:
            self.show_notification("❌ Ошибка", f"Недостаточно средств. Нужно ${cost:,}")

    def get_upgrade_name(self, upgrade_type):
        """Возвращает название улучшения"""
        names = {
            1: "Производительность",
            2: "Качество", 
            3: "Автоматизация",
            4: "Инновация",
            5: "Безопасность"
        }
        return names.get(upgrade_type, "Неизвестное улучшение")

    def create_business_actions_section(self, business_data):
        """Создает раздел действий для бизнеса"""
        widget = QGroupBox("🎮 Действия бизнеса")
        widget.setStyleSheet(f"""
            QGroupBox {{
                color: {TEXT_PRIMARY.name()};
                font-size: 14px;
                font-weight: bold;
                border: 1px solid {PURPLE_ACCENT.name()};
                border-radius: 8px;
                margin-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px 0 3px;
            }}
        """)

        layout = QVBoxLayout()

        # Основное действие бизнеса
        primary_action = self.create_primary_action_widget(business_data)
        layout.addWidget(primary_action)

        widget.setLayout(layout)
        return widget

    def create_primary_action_widget(self, business_data):
        """Создает виджет основного действия"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_BG.name()};
                border: 2px solid {ACCENT1.name()};
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }}
        """)

        layout = QVBoxLayout(widget)

        title_label = QLabel("🚀 Основное действие")
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 14px; font-weight: bold;")

        action_btn = AnimatedButton(business_data.primary_action)
        action_btn.setFixedHeight(45)
        action_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT1.name()}, stop:1 {ACCENT2.name()});
                border: 2px solid {LIGHT_PURPLE.name()};
                border-radius: 10px;
                color: {DARK_BG.name()};
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT2.name()}, stop:1 {ACCENT1.name()});
            }}
        """)
        
        action_btn.clicked.connect(lambda: self.handle_business_action(business_data))

        reward_label = QLabel(f"Награда: +${business_data.base_income:,} доход/час")
        reward_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 12px;")

        layout.addWidget(title_label)
        layout.addWidget(action_btn)
        layout.addWidget(reward_label)

        return widget

    def handle_business_action(self, business_data):
        """Обработчик действия бизнеса"""
        self.show_notification("✅ Действие выполнено!", 
                             f"Вы успешно выполнили: {business_data.primary_action}\n\n"
                             f"Доход бизнеса увеличен!")

    def filter_businesses(self, filter_type):
        """Фильтрация бизнесов"""
        self.current_filter = filter_type
        self.load_catalog()

    def auto_optimize(self):
        """Автооптимизация бизнесов"""
        self.show_notification("🎯 Автооптимизация", "Система автоматически оптимизировала ваши бизнесы!")

    def market_analysis(self):
        """Анализ рынка"""
        self.show_notification("📊 Анализ рынка", "Проведен анализ текущей рыночной ситуации!")

    def global_boost(self):
        """Глобальное ускорение"""
        self.show_notification("🚀 Ускорение", "Активировано глобальное ускорение на 1 час!")

    def setup_business_timers(self):
        """Настройка таймеров для бизнесов"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_businesses)
        self.update_timer.start(5000)  # Обновление каждые 5 секунд

    def update_businesses(self):
        """Обновление состояния бизнесов"""
        # Здесь будет логика обновления доходов и состояния бизнесов
        pass

    def resizeEvent(self, a0):
        """Обработчик изменения размера окна"""
        super().resizeEvent(a0)
        # Обновляем layout при изменении размера
        QTimer.singleShot(50, self.refresh_interface)

    def refresh_interface(self):
        """Полное обновление интерфейса"""
        if hasattr(self, 'my_businesses_layout'):
            self.load_my_businesses()
        if hasattr(self, 'catalog_layout'):
            self.load_catalog()

    def clear_layout(self, layout):
        """Очистка layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def keyPressEvent(self, a0):
        if a0 is not None and a0.key() == Qt.Key.Key_Escape:
            self.exitToMenu.emit()
        else:
            super().keyPressEvent(a0)

class ProfileMenu(QWidget):
    """Меню профиля"""
    
    exitToClicker = pyqtSignal()
    exitToMenu = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("👤 Профиль Игрока")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 32px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Кнопка возврата
        back_btn = AnimatedButton("🚪 Назад в меню")
        back_btn.clicked.connect(self.exitToClicker.emit)
        layout.addWidget(back_btn)
        
        # Основная информация
        info_widget = self.create_profile_info()
        layout.addWidget(info_widget)
        
        layout.addSpacing(20)
        
        # Статистика
        stats_widget = self.create_stats_widget()
        layout.addWidget(stats_widget)
        
        layout.addSpacing(20)
        
        # Достижения
        achievements_widget = self.create_achievements_widget()
        layout.addWidget(achievements_widget)
        
        layout.addStretch()
        
        self.setLayout(layout)
        
        
    def create_profile_info(self):
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_BG.name()};
                border: 2px solid {PURPLE_PRIMARY.name()};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        # Аватар
        avatar = QLabel("👑")
        avatar.setStyleSheet("font-size: 64px;")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(100, 100)
        layout.addWidget(avatar)
        
        # Информация
        info_layout = QVBoxLayout()
        
        name_label = QLabel("Игрок123")
        name_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 24px; font-weight: bold;")
        
        level_label = QLabel("Уровень: 15")
        level_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 16px;")
        
        balance_label = QLabel("Баланс: $1,250,000")
        balance_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 18px; font-weight: bold;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(level_label)
        info_layout.addWidget(balance_label)
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        # Кнопки действий
        action_layout = QVBoxLayout()
        
        daily_btn = AnimatedButton("🎁 Ежедневная награда")
        upgrade_btn = AnimatedButton("⚡ Улучшить профиль")
        
        action_layout.addWidget(daily_btn)
        action_layout.addWidget(upgrade_btn)
        layout.addLayout(action_layout)
        
        widget.setLayout(layout)
        return widget
        
    def create_stats_widget(self):
        widget = QGroupBox("📊 Статистика")
        widget.setStyleSheet(f"""
            QGroupBox {{
                color: {TEXT_PRIMARY.name()};
                font-size: 20px;
                font-weight: bold;
                border: 2px solid {PURPLE_ACCENT.name()};
                border-radius: 10px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        
        layout = QGridLayout()
        
        stats = [
            ("💰 Общий заработок:", "$5,250,000"),
            ("🎯 Всего кликов:", "125,430"),
            ("🏪 Бизнесов:", "8"),
            ("📈 Инвестиций:", "12"),
            ("🛒 Покупок:", "25"),
            ("⏱️ Время в игре:", "45ч 30м")
        ]
        
        row, col = 0, 0
        for name, value in stats:
            name_label = QLabel(name)
            name_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 14px;")
            
            value_label = QLabel(value)
            value_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 14px; font-weight: bold;")
            
            layout.addWidget(name_label, row, col * 2)
            layout.addWidget(value_label, row, col * 2 + 1)
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        widget.setLayout(layout)
        return widget
        
    def create_achievements_widget(self):
        widget = QGroupBox("🏆 Достижения")
        widget.setStyleSheet(f"""
            QGroupBox {{
                color: {TEXT_PRIMARY.name()};
                font-size: 20px;
                font-weight: bold;
                border: 2px solid {PURPLE_ACCENT.name()};
                border-radius: 10px;
                margin-top: 10px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Прогресс достижений
        progress_layout = QHBoxLayout()
        
        progress = QProgressBar()
        progress.setValue(65)
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {PURPLE_PRIMARY.name()};
                border-radius: 10px;
                text-align: center;
                background-color: {DARK_BG.name()};
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT1.name()}, stop:1 {ACCENT2.name()});
                border-radius: 8px;
            }}
        """)
        
        progress_text = QLabel("15/20 достижений (65%)")
        progress_text.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 14px;")
        
        progress_layout.addWidget(progress)
        progress_layout.addWidget(progress_text)
        layout.addLayout(progress_layout)
        
        # Список достижений
        achievements = [
            ("💰 Первые деньги", "Заработать $1,000", True),
            ("🏪 Бизнесмен", "Купить первый бизнес", True),
            ("📈 Инвестор", "Сделать первую инвестицию", True),
            ("🚀 Миллионер", "Заработать $1,000,000", True),
            ("👑 Империя", "Иметь 10 бизнесов", False)
        ]
        
        for name, desc, completed in achievements:
            achievement_widget = self.create_achievement_item(name, desc, completed)
            layout.addWidget(achievement_widget)
        
        widget.setLayout(layout)
        return widget
        
    def create_achievement_item(self, name, description, completed):
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG.name()};
                border: 1px solid {'#22c55e' if completed else PURPLE_PRIMARY.name()};
                border-radius: 8px;
                padding: 10px;
                margin: 2px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        # Статус
        status = QLabel("✅" if completed else "⏳")
        status.setStyleSheet("font-size: 16px;")
        layout.addWidget(status)
        
        # Информация
        info_layout = QVBoxLayout()
        
        name_label = QLabel(name)
        name_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 14px; font-weight: bold;")
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 12px;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(desc_label)
        layout.addLayout(info_layout)
        
        widget.setLayout(layout)
        return widget
        
    def keyPressEvent(self, a0):
        if a0 is not None and  a0.key() == Qt.Key.Key_Escape:
            self.exitToMenu.emit()
        else:
            super().keyPressEvent(a0)

class SettingsMenu(QWidget):
    """Меню настроек"""
    exitToMenu = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.settings_manager = coreLogic.Settings()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(600, 100, 600, 200)
        
        # Заголовок
        title = QLabel("⚙️ Настройки")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 32px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Кнопка возврата
        back_btn = AnimatedButton("🚪 Назад в меню")
        back_btn.clicked.connect(self.exitToMenu.emit)
        layout.addWidget(back_btn)
        
        # Сохраняем только виджет
        self.settings_widget = self.create_settings_widget()
        layout.addWidget(self.settings_widget)
        layout.addStretch()
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        apply_btn = AnimatedButton("Применить")
        apply_btn.clicked.connect(self.apply_settings)
        
        reset_btn = AnimatedButton("Сбросить")
        reset_btn.clicked.connect(self.reset_settings)
        
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(reset_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def create_settings_widget(self):
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {PANEL_BG.name()};
                border: 2px solid {PURPLE_PRIMARY.name()};
                border-radius: 15px;
                padding: 20px;
            }}
        """)

        layout = QFormLayout()
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setVerticalSpacing(20)
        layout.setContentsMargins(10, 10, 10, 10)
        
        combo_style = f"""
            QComboBox {{
                background-color: {DARK_BG.name()};
                color: {TEXT_PRIMARY.name()};
                border: 1px solid {PURPLE_PRIMARY.name()};
                border-radius: 8px;
                padding: 10px;
                margin-top: 9px;
                min-width: 400px;
                max-width: 450px;
            }}
            QComboBox:hover {{
                border: 1px solid {LIGHT_PURPLE.name()};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid {PURPLE_PRIMARY.name()};
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {LIGHT_PURPLE.name()};
                width: 0px;
                height: 0px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {DARK_BG.name()};
                border: 1px solid {PURPLE_ACCENT.name()};
                border-radius: 8px;
                padding: 5px;
                outline: none;
                min-width: 400px;
                max-width: 450px;
            }}
            QComboBox QAbstractItemView::item {{
                color: {TEXT_PRIMARY.name()};
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 4px;
                margin: 2px;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {PURPLE_PRIMARY.name()};
                color: white;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {PURPLE_ACCENT.name()};
                color: white;
            }}
        """
        
        # Сохраняем ссылки на комбобоксы для использования в apply_settings
        self.comboboxes = {}
        
        # Тема
        theme_combo = QComboBox()
        available_themes = self.settings_manager.show_themes()
        theme_combo.addItems(available_themes)
        theme_combo.setStyleSheet(combo_style)
        theme_combo.setFixedWidth(250)
        
        # Устанавливаем текущую тему
        current_theme = self.settings_manager.get_current_theme()
        if current_theme in available_themes:
            theme_combo.setCurrentText(current_theme)
        
        layout.addRow("🎨 Тема:", theme_combo)
        self.comboboxes['theme'] = theme_combo
        
        # Размер окна (окно/полный экран)
        state_combo = QComboBox()
        available_states = [f"{s}" for s in self.settings_manager.show_states()]
        state_combo.addItems(available_states)
        state_combo.setStyleSheet(combo_style)
        state_combo.setFixedWidth(250)
        
        # Устанавливаем текущий размер окна
        current_state = self.settings_manager.get_window_state()
        if current_state in available_states:
            state_combo.setCurrentText(current_state)
        
        layout.addRow("🖥️ Режим окна:", state_combo)
        self.comboboxes['state'] = state_combo

        # Разрешение
        resolution_combo = QComboBox()
        available_resolutions = [f"{w}x{h}" for w, h in self.settings_manager.show_window_sizes()]
        resolution_combo.addItems(available_resolutions)
        resolution_combo.setStyleSheet(combo_style)
        resolution_combo.setFixedWidth(250)
        
        # Устанавливаем текущее разрешение
        current_size = self.settings_manager.get_current_window_size()
        current_resolution = f"{current_size[0]}x{current_size[1]}"
        if current_resolution in available_resolutions:
            resolution_combo.setCurrentText(current_resolution)
        
        layout.addRow("📏 Разрешение:", resolution_combo)
        self.comboboxes['resolution'] = resolution_combo
        
        # FPS
        fps_combo = QComboBox()
        available_fps = [f"{fps} FPS" for fps in self.settings_manager.show_fps()]
        fps_combo.addItems(available_fps)
        fps_combo.setStyleSheet(combo_style)
        fps_combo.setFixedWidth(250)
        
        # Устанавливаем текущий FPS
        current_fps = self.settings_manager.get_current_fps()
        current_fps_text = f"{current_fps} FPS"
        if current_fps_text in available_fps:
            fps_combo.setCurrentText(current_fps_text)
        
        layout.addRow("🎯 FPS:", fps_combo)
        self.comboboxes['fps'] = fps_combo
        
        # Язык
        language_combo = QComboBox()
        available_langs = self.settings_manager.show_langs()
        language_combo.addItems(available_langs)
        language_combo.setStyleSheet(combo_style)
        language_combo.setFixedWidth(250)
        
        # Устанавливаем текущий язык
        current_lang = self.settings_manager.get_current_lang()
        if current_lang in available_langs:
            language_combo.setCurrentText(current_lang)
        
        layout.addRow("🌐 Язык:", language_combo)
        self.comboboxes['language'] = language_combo
        
        # Качество графики
        quality_combo = QComboBox()
        available_qualities = ["Низкое", "Среднее", "Высокое"]
        quality_combo.addItems(available_qualities)
        quality_combo.setStyleSheet(combo_style)
        quality_combo.setFixedWidth(250)
        
        # Устанавливаем текущее качество (если есть в системе)
        # Если нет системы хранения качества, устанавливаем "Высокое" по умолчанию
        quality_combo.setCurrentText("Высокое")
        
        layout.addRow("🎨 Качество графики:", quality_combo)
        self.comboboxes['quality'] = quality_combo
        
        # Громкость
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        
        # Устанавливаем текущую громкость
        current_volume = self.settings_manager.get_current_volume()  # Если есть такой метод
        volume_slider.setValue(current_volume if hasattr(self.settings_manager, 'get_current_volume') else 80)
        
        volume_slider.setFixedWidth(400)
        volume_slider.setMinimumHeight(40)
        
        volume_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 2px solid {PURPLE_PRIMARY.name()};
                height: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {DARK_BG.name()}, stop:0.3 {DEEP_PURPLE.name()}, stop:1 {PURPLE_PRIMARY.name()});
                border-radius: 7px;
            }}
            QSlider::handle:horizontal {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8,
                    stop:0 white, stop:0.6 {LIGHT_PURPLE.name()}, stop:1 {PURPLE_ACCENT.name()});
                border: 2px solid white;
                width: 28px;
                height: 28px;
                margin: -8px 0;
                border-radius: 14px;
            }}
            QSlider::sub-page:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT1.name()}, stop:0.5 {PURPLE_ACCENT.name()}, stop:1 {ACCENT2.name()});
                border-radius: 7px;
            }}
        """)
        
        # Контейнер для ползунка и значения
        slider_container = QWidget()
        slider_layout = QHBoxLayout(slider_container)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.setSpacing(15)
        
        slider_layout.addWidget(volume_slider)
        
        # Значение громкости
        volume_value = QLabel(f"{volume_slider.value()}%")
        volume_value.setStyleSheet(f"""
            QLabel {{
                color: {LIGHT_PURPLE.name()};
                font-size: 14px;
                font-weight: bold;
                background-color: {DARK_BG.name()};
                border: 1px solid {PURPLE_PRIMARY.name()};
                border-radius: 5px;
                padding: 8px 12px;
                min-width: 50px;
            }}
        """)
        volume_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        slider_layout.addWidget(volume_value)
        slider_layout.addStretch()
        
        # Обновление значения
        volume_slider.valueChanged.connect(lambda v: volume_value.setText(f"{v}%"))
        
        layout.addRow("🔊 Громкость:", slider_container)
        self.comboboxes['volume'] = volume_slider
        
        widget.setLayout(layout)
        return widget

    def apply_settings(self):
        # Получаем текущие значения ДО применения
        old_theme = self.settings_manager.get_current_theme()
        old_language = self.settings_manager.get_current_lang()
        old_size = self.settings_manager.get_current_window_size()
        old_resolution = f"{old_size[0]}x{old_size[1]}"
        old_state = self.settings_manager.get_window_state()
        old_fps = self.settings_manager.get_current_fps()
        old_quality = self.settings_manager.get_current_quality()
        old_volume = self.settings_manager.get_current_volume()
        
        # Получаем новые значения
        selected_theme = self.comboboxes['theme'].currentText()
        selected_state = self.comboboxes['state'].currentText()
        selected_resolution = self.comboboxes['resolution'].currentText()
        selected_fps = self.comboboxes['fps'].currentText().replace(' FPS', '')
        selected_language = self.comboboxes['language'].currentText()
        selected_quality = self.comboboxes['quality'].currentText()
        selected_volume = self.comboboxes['volume'].value()
        
        # Применяем настройки
        self.settings_manager.set_current_theme(selected_theme)
        self.settings_manager.set_current_window_state(selected_state)
        
        width, height = map(int, selected_resolution.split('x'))
        self.settings_manager.set_current_window_size(width, height)
        
        self.settings_manager.set_current_fps(int(selected_fps))
        self.settings_manager.set_current_lang(selected_language)
        
        # Проверяем изменения, требующие перезапуска
        restart_required = False
        changed_settings = []
        
        if selected_theme != old_theme:
            restart_required = True
            changed_settings.append(f"Тема: {old_theme} → {selected_theme}")
        
        if selected_language != old_language:
            restart_required = True
            changed_settings.append(f"Язык: {old_language} → {selected_language}")
        
        if selected_resolution != old_resolution:
            restart_required = True
            changed_settings.append(f"Разрешение: {old_resolution} → {selected_resolution}")

        if selected_state != old_state:
            restart_required = True
            changed_settings.append(f"Разрешение: {old_state} → {selected_state}")
            
        if selected_language != old_language:
            restart_required = True
            changed_settings.append(f"Язык: {old_language} → {selected_language}")

        if selected_fps != old_fps:
            restart_required = True
            changed_settings.append(f"FPS: {old_fps} → {selected_fps}")

        if selected_quality != old_quality:
            restart_required = True
            changed_settings.append(f"Качество: {old_quality} → {selected_quality}")

        if selected_volume != old_volume:
            restart_required = True
            changed_settings.append(f"Громкость: {old_volume} → {selected_volume}")
        
        if restart_required:
            self.show_restart_dialog(changed_settings)
        else:
            # Настройки, не требующие перезапуска
            print("Настройки применены без перезапуска")
            QMessageBox.information(self, "Настройки", "Настройки успешно применены!")

    def check_if_restart_required(self, theme, language, resolution , state, fps, quality, volume):
        """Проверяет, требуют ли изменения перезапуска"""
        # Настройки, требующие перезапуска
        restart_settings = ['theme', 'language', 'resolution', 'state', 'fps', 'quality', 'volume']
        
        # Сравниваем текущие значения с предыдущими
        old_theme = self.settings_manager.get_current_theme()
        old_language = self.settings_manager.get_current_lang()
        old_size = self.settings_manager.get_current_window_size()
        old_resolution = f"{old_size[0]}x{old_size[1]}"
        old_state = self.settings_manager.get_window_state()
        old_fps = self.settings_manager.get_current_fps()
        old_quality = self.settings_manager.get_current_quality()
        old_volume = self.settings_manager.get_current_volume()
        
        changes = []
        if theme != old_theme:
            changes.append("тема")
        if language != old_language:
            changes.append("язык")
        if resolution != old_resolution:
            changes.append("разрешение")
        if state != old_state:
            changes.append("состояние")
        if fps != old_fps:
            changes.append("fps")
        if quality != old_quality:
            changes.append("качество")
        if volume != old_volume:
            changes.append("громкость")
        
        if changes:
            return True
        return False

    def restart_application(self):
        """Перезапускает приложение"""
        reply = QMessageBox.question(
            self,
            "Перезапуск требуется",
            "Для применения некоторых настроек требуется перезапуск приложения.\n"
            "Перезапустить сейчас?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Перезапускаем приложение
            QApplication.quit()
            import subprocess
            import sys
            subprocess.Popen([sys.executable] + sys.argv)

    def show_restart_dialog(self, changed_settings):
        """Показывает диалог перезапуска"""
        settings_text = "\n".join(changed_settings)
        
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Требуется перезапуск")
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setText(
            "Для применения следующих настроек требуется перезапуск:\n\n"
            f"{settings_text}\n\n"
            "Вы хотите перезапустить приложение сейчас?"
        )
        
        # Добавляем кнопки
        restart_now = dialog.addButton("Перезапустить сейчас", QMessageBox.ButtonRole.YesRole)
        restart_later = dialog.addButton("Позже", QMessageBox.ButtonRole.NoRole)
        cancel = dialog.addButton("Отмена", QMessageBox.ButtonRole.RejectRole)
        
        dialog.exec()
        
        clicked_button = dialog.clickedButton()
        
        if clicked_button == restart_now:
            self.restart_application()
        elif clicked_button == restart_later:
            QMessageBox.information(
                self, 
                "Настройки сохранены", 
                "Настройки сохранены и будут применены после перезапуска."
            )
        else:  # Cancel - откатываем изменения
            self.reset_settings()
            QMessageBox.information(
                self, 
                "Изменения отменены", 
                "Изменения, требующие перезапуска, были отменены."
            )
        
    def reset_settings(self):
        reply = QMessageBox.question(self, "Сброс настроек", 
                                   "Вы уверены, что хотите сбросить все настройки?")
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Настройки", "Настройки сброшены!")
            
    def keyPressEvent(self, a0):
        if a0 is not None and a0.key() == Qt.Key.Key_Escape:
            self.exitToMenu.emit()
        else:
            super().keyPressEvent(a0)

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{AppLogic.name} v{GAME_VERSION}")
        self.setWindowIcon(QIcon("images/icon.ico"))
        
        # ФИКС: Правильная проверка полноэкранного режима
        window_state = Settings.get_window_state()
        # Если состояние в формате массива, берем первый элемент
        if isinstance(window_state, list) and len(window_state) > 0:
            window_state = window_state[0]
        
        if window_state == "MAXIMIZED":
            self.showMaximized()
        elif window_state == "FULLSCREEN":
            self.showFullScreen()
            self.is_fullscreen = True
        else:
            # Оконный режим с нормальным размером
            self.setMinimumSize(800, 600)
            screen = QGuiApplication.primaryScreen()
            if screen:
                screen_geometry = screen.availableGeometry()
                initial_width = int(screen_geometry.width() * 0.8)
                initial_height = int(screen_geometry.height() * 0.8)
                x = (screen_geometry.width() - initial_width) // 2
                y = (screen_geometry.height() - initial_height) // 2
                self.setGeometry(x, y, initial_width, initial_height)
        
        # ФИКС: создаем central_widget как атрибут
        self.central_widget = GradientWidget()
        self.setCentralWidget(self.central_widget)
        
        # Основной layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Стек виджетов для переключения между экранами
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"background: transparent;")
        
        # Создаем экраны
        self.loading_screen = LoadingScreen()
        self.main_menu = MainMenuScreen()
        self.clicker_game = ClickerGame()
        self.investment_menu = InvestmentMenu()
        self.shop_selection = ShopSelectionMenu()
        self.light_shop = LightShopMenu()
        #self.business_menu = BusinessMenu()
        self.business_menu = RevolutionaryBusinessMenu()
        self.profile_menu = ProfileMenu()
        self.settings_menu = SettingsMenu()
        
        # Добавляем экраны в стек
        self.content_stack.addWidget(self.loading_screen)        # 0
        self.content_stack.addWidget(self.main_menu)             # 1
        self.content_stack.addWidget(self.clicker_game)          # 2
        self.content_stack.addWidget(self.investment_menu)       # 3
        self.content_stack.addWidget(self.shop_selection)        # 4
        self.content_stack.addWidget(self.light_shop)            # 5
        self.content_stack.addWidget(self.business_menu)         # 6
        self.content_stack.addWidget(self.profile_menu)          # 7
        self.content_stack.addWidget(self.settings_menu)         # 8
        
        main_layout.addWidget(self.content_stack)
        self.central_widget.setLayout(main_layout)
        
        # Подключаем сигналы
        self.loading_screen.loadingFinished.connect(self.show_main_menu)
        self.main_menu.playClicked.connect(self.show_clicker_game)
        self.main_menu.settingsClicked.connect(self.show_settings)
        self.main_menu.exitClicked.connect(self.close)
        
        # Подключаем сигналы выхода в меню
        self.clicker_game.exitToMenu.connect(self.show_main_menu)
        self.investment_menu.exitToClicker.connect(self.show_clicker_game)
        self.shop_selection.exitToClicker.connect(self.show_clicker_game)
        self.light_shop.exitToShopSelectionMenu.connect(self.show_shop_selection)
        self.business_menu.exitToClicker.connect(self.show_clicker_game)
        self.profile_menu.exitToClicker.connect(self.show_clicker_game)
        self.settings_menu.exitToMenu.connect(self.show_main_menu)
        
        # Подключаем навигацию между разделами
        self.shop_selection.shopSelected.connect(self.handle_shop_selection)
        self.clicker_game.navigationRequested.connect(self.handle_navigation)
        
        # Показываем экран загрузки
        self.content_stack.setCurrentIndex(0)
        
        # Флаг для отслеживания полноэкранного режима
        self.is_fullscreen = False

    def toggle_fullscreen(self):
        """Переключение между полноэкранным и оконным режимом"""
        if self.is_fullscreen:
            self.showNormal()
            # Восстанавливаем разумный размер при выходе из полноэкранного режима
            screen = QGuiApplication.primaryScreen()
            if screen:
                screen_geometry = screen.availableGeometry()
                width = int(screen_geometry.width() * 0.8)
                height = int(screen_geometry.height() * 0.8)
                self.resize(width, height)
                self.center_window()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True

    def center_window(self):
        """Центрирование окна на экране"""
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        # ФИКС: используем centralWidget() вместо central_widget
        if self.centralWidget() and self.centralWidget().layout():
            self.centralWidget().layout().activate()
    
    def handle_navigation(self, destination):
        """Обрабатывает навигационные запросы из кликера"""
        if destination == "main_menu":
            self.show_main_menu()
        elif destination == "shops":
            self.show_shop_selection()
        elif destination == "investments":
            self.show_investments()
        elif destination == "businesses":
            self.show_businesses()
        elif destination == "profile":
            self.show_profile()
        
    def show_main_menu(self):
        """Показать главное меню"""
        self.content_stack.setCurrentIndex(1)
        self.apply_window_state()

    def apply_window_state(self):
        window_state = Settings.get_window_state()
        # ФИКС: правильно обрабатываем список
        if isinstance(window_state, list) and window_state:
            window_state = window_state[0]
        
        if window_state == "MAXIMIZED":
            self.showMaximized()
            self.is_fullscreen = False
        elif window_state == "FULLSCREEN":
            self.showFullScreen()
            self.is_fullscreen = True
        else:
            self.showNormal()
            self.is_fullscreen = False
        
    def show_clicker_game(self):
        """Показать игровой кликер"""
        self.content_stack.setCurrentIndex(2)
        
    def show_investments(self):
        """Показать инвестиции"""
        self.content_stack.setCurrentIndex(3)
        
    def show_shop_selection(self):
        """Показать выбор магазина"""
        self.content_stack.setCurrentIndex(4)
        
    def show_businesses(self):
        """Показать бизнесы"""
        self.content_stack.setCurrentIndex(6)
        
    def show_profile(self):
        """Показать профиль"""
        self.content_stack.setCurrentIndex(7)
        
    def show_settings(self):
        """Показать настройки"""
        self.content_stack.setCurrentIndex(8)
        
    def handle_shop_selection(self, shop_type):
        """Обработать выбор магазина"""
        if shop_type == "legal":
            self.content_stack.setCurrentIndex(5)  # Light shop
        elif shop_type == "black_market":
            QMessageBox.information(self, "Черный рынок", "Черный рынок в разработке!")
        
    def keyPressEvent(self, a0):
        """Глобальная обработка клавиш"""
        if a0 is not None and a0.key() == Qt.Key.Key_Escape:
            if self.is_fullscreen:
                # Выход из полноэкранного режима
                self.toggle_fullscreen()
            else:
                # Если мы не в главном меню, возвращаемся в него
                current_index = self.content_stack.currentIndex()
                if current_index != 1:  # Не главное меню
                    self.show_main_menu()
        elif a0 is not None and a0.key() == Qt.Key.Key_F11:
            # Переключение полноэкранного режима по F11
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(a0)

def main():
    # ОТКЛЮЧАЕМ НЕНУЖНЫЕ ПРЕДУПРЕЖДЕНИЯ QT
    os.environ["QT_LOGGING_RULES"] = "qt.text.font=false"
    
    def qt_debug_handler(msg_type, context, message):
        # Игнорируем сообщения про шрифты
        if "OpenType support missing" in message:
            return
        if "QLayout::addChildLayout" in message:
            import traceback
            print("⚠️ Ошибка QLayout:", message)
            traceback.print_stack(limit=6)
        else:
            print(message)

    qInstallMessageHandler(qt_debug_handler)
    app = QApplication(sys.argv)

    # ТЕПЕРЬ инициализируем шрифты ПОСЛЕ создания app
    global OPENTYPE_MANAGER, MAIN_FONT_FAMILY
    OPENTYPE_MANAGER = OpenType()
    OPENTYPE_MANAGER.init_fonts()
    MAIN_FONT_FAMILY = OPENTYPE_MANAGER.main_font_family
    
    # Устанавливаем стиль приложения
    app.setStyle("Fusion")

    # Настройка палитры
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, DARK_BG)
    palette.setColor(QPalette.ColorRole.WindowText, TEXT_PRIMARY)
    palette.setColor(QPalette.ColorRole.Base, PANEL_BG)
    palette.setColor(QPalette.ColorRole.AlternateBase, DEEP_PURPLE)
    palette.setColor(QPalette.ColorRole.ToolTipBase, WHITE)
    palette.setColor(QPalette.ColorRole.ToolTipText, WHITE)
    palette.setColor(QPalette.ColorRole.Text, TEXT_PRIMARY)
    palette.setColor(QPalette.ColorRole.Button, PURPLE_PRIMARY)
    palette.setColor(QPalette.ColorRole.ButtonText, TEXT_PRIMARY)
    palette.setColor(QPalette.ColorRole.BrightText, ACCENT2)
    palette.setColor(QPalette.ColorRole.Highlight, PURPLE_ACCENT)
    palette.setColor(QPalette.ColorRole.HighlightedText, BLACK)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()