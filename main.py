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

class RevolutionaryBusinessMenu(QWidget):
    """Совершенно новое меню бизнесов с революционным дизайном"""
    
    exitToClicker = pyqtSignal()
    exitToMenu = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.business_manager = AdvancedBusinessManager()
        self.current_filter = "all"
        self.selected_specialization = None
        
        self.init_ui()
        self.setup_business_timers()
    
    def init_ui(self):
        """Инициализация революционного UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
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
        
        # Вкладки с улучшенной навигацией
        self.tab_widget = self.create_enhanced_tabs()
        main_layout.addWidget(self.tab_widget)
        
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
        """Вкладка моих бизнесов"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Статистика империи
        empire_stats = self.create_empire_stats()
        layout.addWidget(empire_stats)
        
        # Сетка бизнесов
        self.my_businesses_scroll = QScrollArea()
        self.my_businesses_scroll.setWidgetResizable(True)
        self.my_businesses_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.my_businesses_container = QWidget()
        self.my_businesses_layout = QGridLayout(self.my_businesses_container)
        self.my_businesses_layout.setSpacing(15)
        self.my_businesses_scroll.setWidget(self.my_businesses_container)
        
        layout.addWidget(self.my_businesses_scroll)
        
        self.load_my_businesses()
        return widget
    
    def create_enhanced_catalog_tab(self):
        """Улучшенная вкладка каталога"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Фильтры каталога
        filter_layout = QHBoxLayout()
        
        categories = [
            ("🔬 Наука", "research"),
            ("🏭 Производство", "manufacturing"), 
            ("💻 Технологии", "tech"),
            ("🛎️ Сервисы", "service"),
            ("🌑 Теневые", "dark")
        ]
        
        for icon, category in categories:
            btn = QPushButton(icon)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {PANEL_BG.name()};
                    color: {TEXT_PRIMARY.name()};
                    border: 2px solid {PURPLE_PRIMARY.name()};
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 16px;
                    margin: 2px;
                }}
                QPushButton:checked {{
                    background-color: {PURPLE_PRIMARY.name()};
                }}
                QPushButton:hover {{
                    border-color: {PURPLE_ACCENT.name()};
                }}
            """)
            btn.clicked.connect(lambda checked, c=category: self.filter_catalog_by_category(c))
            filter_layout.addWidget(btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Сетка каталога
        self.catalog_scroll = QScrollArea()
        self.catalog_scroll.setWidgetResizable(True)
        self.catalog_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.catalog_container = QWidget()
        self.catalog_layout = QGridLayout(self.catalog_container)
        self.catalog_layout.setSpacing(15)
        self.catalog_scroll.setWidget(self.catalog_container)
        
        layout.addWidget(self.catalog_scroll)
        
        self.load_catalog()
        return widget
    
    def create_synergies_tab(self):
        """Вкладка синергий"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        synergies_label = QLabel("🔄 СИСТЕМА СИНЕРГИЙ")
        synergies_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 20px; font-weight: bold;")
        layout.addWidget(synergies_label)
        
        # Отображение доступных синергий
        for (biz1, biz2), synergy in self.business_manager.synergies.items():
            synergy_widget = self.create_synergy_widget(biz1, biz2, synergy)
            layout.addWidget(synergy_widget)
        
        layout.addStretch()
        return widget
    
    def create_analytics_tab(self):
        """Вкладка аналитики"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        analytics_label = QLabel("📊 АНАЛИТИКА ИМПЕРИИ")
        analytics_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 20px; font-weight: bold;")
        layout.addWidget(analytics_label)
        
        # Статистика доходов
        income_analysis = self.create_income_analysis()
        layout.addWidget(income_analysis)
        
        # Рекомендации
        recommendations = self.create_recommendations()
        layout.addWidget(recommendations)
        
        layout.addStretch()
        return widget
    
    def create_empire_stats(self):
        """Статистика империи"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG.name()};
                border: 2px solid {PURPLE_ACCENT.name()};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        total_income = sum(business['income_per_hour'] for business in self.business_manager.my_businesses)
        total_workers = sum(business['workers'] for business in self.business_manager.my_businesses)
        avg_risk = sum(business['risk'] for business in self.business_manager.my_businesses) / max(1, len(self.business_manager.my_businesses))
        
        stats = [
            (f"${total_income:,}/час", "Общий доход"),
            (str(len(self.business_manager.my_businesses)), "Активных бизнесов"),
            (str(total_workers), "Всего работников"),
            (f"{avg_risk:.1f}%", "Средний риск"),
            (f"{self.business_manager.innovation_points}", "Инновационные очки")
        ]
        
        for value, label in stats:
            stat_widget = self.create_stat_widget(value, label)
            layout.addWidget(stat_widget)
        
        widget.setLayout(layout)
        return widget
    
    def create_revolutionary_business_card(self, business_data, is_owned=False):
        """Создание революционной карточки бизнеса"""
        card = QFrame()
        
        # Динамический стиль в зависимости от типа бизнеса
        border_color = PURPLE_PRIMARY.name() if business_data['category'] == 'light' else "#dc2626"
        bg_gradient = f"""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {CARD_BG.name()}, stop:1 {DEEP_PURPLE.name()});
        """ if business_data['category'] == 'light' else f"""
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {CARD_BG.name()}, stop:1 #7f1d1d);
        """
        
        card.setStyleSheet(f"""
            QFrame {{
                {bg_gradient}
                border: 3px solid {border_color};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        
        if is_owned:
            card.setFixedSize(600, 700)
        else:
            card.setFixedSize(450, 400)
        
        layout = QVBoxLayout()
        card.setLayout(layout)
        
        # Верхняя панель с основной информацией
        header_layout = QHBoxLayout()
        
        # Иконка и название
        title_layout = QVBoxLayout()
        icon_label = QLabel(business_data['icon'])
        icon_label.setStyleSheet("font-size: 24px;")
        name_label = QLabel(business_data['name'])
        name_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 20px; font-weight: bold;")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(name_label)
        header_layout.addLayout(title_layout)
        
        # Статус и уровень
        status_layout = QVBoxLayout()
        level_label = QLabel(f"Ур. {business_data['level']}")
        level_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 16px; font-weight: bold;")
        
        risk_label = QLabel(f"⚠️ Риск: {business_data['risk']}%")
        risk_label.setStyleSheet(f"color: {'#ef4444' if business_data['risk'] > 50 else '#f59e0b'}; font-size: 12px;")
        
        status_layout.addWidget(level_label)
        status_layout.addWidget(risk_label)
        header_layout.addLayout(status_layout)
        
        layout.addLayout(header_layout)
        
        # Описание
        desc_label = QLabel(business_data['description'])
        desc_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 12px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Основные показатели
        stats_layout = QHBoxLayout()
        
        indicators = [
            (f"💰 ${business_data['income_per_hour']:,}", "Доход/час"),
            (f"👥 {business_data['workers']}", "Работники"),
            (f"⚡ {business_data.get('efficiency', 1.0):.1f}x", "Эффективность")
        ]
        
        for value, label in indicators:
            indicator = QLabel(value)
            indicator.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 12px; font-weight: bold;")
            stats_layout.addWidget(indicator)
        
        layout.addLayout(stats_layout)
        
        # Основное действие
        primary_action_layout = QHBoxLayout()
        
        if is_owned:
            primary_btn = AnimatedButton(business_data['primary_action'])
            primary_btn.setFixedHeight(40)
            primary_btn.clicked.connect(lambda: self.handle_primary_action(business_data))
            primary_action_layout.addWidget(primary_btn)
            
            # Дополнительные действия
            if business_data['name'] == 'Биотех Лаборатория':
                research_btn = AnimatedButton("🔬 Исследования")
                research_btn.clicked.connect(lambda: self.show_research_dialog(business_data))
                primary_action_layout.addWidget(research_btn)
            elif business_data['name'] == 'AI разработки':
                training_btn = AnimatedButton("🤖 Обучение AI")
                training_btn.clicked.connect(lambda: self.show_training_dialog(business_data))
                primary_action_layout.addWidget(training_btn)
        else:
            # Для каталога - кнопка покупки
            buy_btn = AnimatedButton(f"Купить за ${business_data['price']:,}")
            buy_btn.setFixedHeight(40)
            buy_btn.clicked.connect(lambda: self.buy_business(business_data))
            primary_action_layout.addWidget(buy_btn)
        
        layout.addLayout(primary_action_layout)
        
        # Система улучшений (только для owned)
        if is_owned:
            upgrades_label = QLabel("⚡ УЛУЧШЕНИЯ")
            upgrades_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 14px; font-weight: bold;")
            layout.addWidget(upgrades_label)
            
            upgrades_layout = QGridLayout()
            
            for upgrade_type in range(1, 6):
                upgrade_info = BusinessUpgradeSystem.UPGRADE_TYPES[upgrade_type]
                current_level = business_data['upgrade_system'].levels[upgrade_type]
                
                upgrade_btn = QPushButton(f"{upgrade_info['icon']} {upgrade_type}")
                upgrade_btn.setFixedSize(50, 50)
                upgrade_btn.setToolTip(f"{upgrade_info['name']}\nУровень: {current_level}\n{upgrade_info['description']}")
                upgrade_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {PANEL_BG.name()};
                        border: 2px solid {PURPLE_PRIMARY.name()};
                        border-radius: 8px;
                        color: {TEXT_PRIMARY.name()};
                        font-size: 14px;
                    }}
                    QPushButton:hover {{
                        background-color: {PURPLE_PRIMARY.name()};
                    }}
                """)
                upgrade_btn.clicked.connect(lambda checked, idx=upgrade_type, biz=business_data: 
                                          self.upgrade_business(biz, idx))
                
                row = (upgrade_type - 1) // 3
                col = (upgrade_type - 1) % 3
                upgrades_layout.addWidget(upgrade_btn, row, col)
            
            layout.addLayout(upgrades_layout)
            
            # Специализированные панели
            if business_data.get('current_research'):
                self.add_research_progress_panel(layout, business_data)
            elif business_data.get('current_training'):
                self.add_training_progress_panel(layout, business_data)
            
            # Кнопка перехода в темную сторону
            if business_data.get('can_go_dark', False) and business_data['category'] == 'light':
                dark_btn = AnimatedButton("🌑 Перейти в Тень")
                dark_btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #7f1d1d, stop:1 #991b1b);
                        border: 2px solid #dc2626;
                        border-radius: 10px;
                        color: white;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 8px 16px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #991b1b, stop:1 #b91c1c);
                        border: 2px solid #ef4444;
                    }
                """)
                dark_btn.clicked.connect(lambda: self.show_dark_side_dialog(business_data))
                layout.addWidget(dark_btn)
        
        layout.addStretch()
        return card
    
    def add_research_progress_panel(self, layout, business_data):
        """Добавление панели прогресса исследования"""
        research_frame = QFrame()
        research_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(6, 246, 230, 0.1);
                border: 1px solid {ACCENT2.name()};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        research_layout = QVBoxLayout(research_frame)
        
        research_label = QLabel(f"🔬 {business_data['current_research']}")
        research_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 14px; font-weight: bold;")
        
        progress_bar = QProgressBar()
        progress_bar.setValue(int(business_data['research_progress']))
        progress_bar.setMaximum(100)
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {ACCENT2.name()};
                border-radius: 5px;
                text-align: center;
                background-color: {DARK_BG.name()};
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT1.name()}, stop:1 {ACCENT2.name()});
                border-radius: 3px;
            }}
        """)
        
        research_layout.addWidget(research_label)
        research_layout.addWidget(progress_bar)
        layout.addWidget(research_frame)
    
    def add_training_progress_panel(self, layout, business_data):
        """Добавление панели прогресса обучения"""
        training_frame = QFrame()
        training_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 59, 111, 0.1);
                border: 1px solid #ff3b6f;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        training_layout = QVBoxLayout(training_frame)
        
        training_label = QLabel(f"🤖 {business_data['current_training']}")
        training_label.setStyleSheet("color: #ff3b6f; font-size: 14px; font-weight: bold;")
        
        progress_bar = QProgressBar()
        progress_bar.setValue(int(business_data['training_progress']))
        progress_bar.setMaximum(100)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ff3b6f;
                border-radius: 5px;
                text-align: center;
                background-color: #0b0f12;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff3b6f, stop:1 #ff2a4a);
                border-radius: 3px;
            }
        """)
        
        training_layout.addWidget(training_label)
        training_layout.addWidget(progress_bar)
        layout.addWidget(training_frame)
    
    def handle_primary_action(self, business_data):
        """Обработка основного действия"""
        business_name = business_data['name']
        
        if business_name == 'Биотех Лаборатория':
            self.show_research_dialog(business_data)
        elif business_name == 'AI разработки':
            self.show_training_dialog(business_data)
        elif business_name == 'Автопром':
            self.show_production_dialog(business_data)
        elif business_name == 'Крипто-майнинг':
            self.show_mining_dialog(business_data)
        else:
            QMessageBox.information(self, "Действие", 
                                  f"Выполнено: {business_data['primary_action']}")
    
    def show_research_dialog(self, business_data):
        """Диалог исследований для биотеха"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🔬 Исследовательские проекты")
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        title = QLabel("Выберите исследовательский проект:")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        for project in business_data['special_mechanics']['research_projects']:
            project_frame = QFrame()
            project_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {CARD_BG.name()};
                    border: 1px solid {PURPLE_PRIMARY.name()};
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px;
                }}
            """)
            
            project_layout = QHBoxLayout(project_frame)
            
            info_layout = QVBoxLayout()
            name_label = QLabel(project['name'])
            name_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 14px; font-weight: bold;")
            
            details_label = QLabel(f"Стоимость: ${project['cost']:,} | Длительность: {project['duration']}ч")
            details_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 12px;")
            
            reward_label = QLabel(f"Награда: Увеличение дохода в {project['reward']}x")
            reward_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 12px;")
            
            info_layout.addWidget(name_label)
            info_layout.addWidget(details_label)
            info_layout.addWidget(reward_label)
            
            start_btn = AnimatedButton("Начать")
            start_btn.setFixedSize(80, 30)
            start_btn.clicked.connect(lambda checked, p=project['name']: 
                                    self.start_research(business_data, p))
            
            project_layout.addLayout(info_layout)
            project_layout.addWidget(start_btn)
            
            layout.addWidget(project_frame)
        
        dialog.exec()
    
    def show_training_dialog(self, business_data):
        """Диалог обучения AI моделей"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🤖 Обучение AI моделей")
        dialog.setFixedSize(450, 350)
        
        layout = QVBoxLayout(dialog)
        
        title = QLabel("Выберите модель для обучения:")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        for model in business_data['special_mechanics']['ai_models']:
            model_btn = AnimatedButton(f"{model['name']}\n"
                                     f"Стоимость: ${model['cost']:,} | Время: {model['training_time']}ч")
            model_btn.clicked.connect(lambda checked, m=model['name']: 
                                    self.start_training(business_data, m))
            layout.addWidget(model_btn)
        
        dialog.exec()
    
    def show_production_dialog(self, business_data):
        """Диалог обновления производственных линий"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🏭 Обновление производства")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        title = QLabel("Выберите тип производственной линии:")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        for line in business_data['special_mechanics']['production_lines']:
            line_btn = AnimatedButton(f"{line['type']}\n"
                                    f"Эффективность: {line['efficiency']}x | Стоимость: ${line['cost']:,}")
            line_btn.clicked.connect(lambda checked, l=line['type']: 
                                   self.upgrade_production(business_data, l))
            layout.addWidget(line_btn)
        
        dialog.exec()
    
    def show_mining_dialog(self, business_data):
        """Диалог покупки майнинг-оборудования"""
        dialog = QDialog(self)
        dialog.setWindowTitle("⛏️ Майнинг оборудование")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        title = QLabel("Выберите майнинг-риг:")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        for rig in business_data['special_mechanics']['mining_rigs']:
            rig_btn = AnimatedButton(f"{rig['type']}\n"
                                   f"Хэшрейт: {rig['hashrate']} | Стоимость: ${rig['cost']:,}")
            rig_btn.clicked.connect(lambda checked, r=rig['type']: 
                                  self.buy_mining_rig(business_data, r))
            layout.addWidget(rig_btn)
        
        dialog.exec()
    
    def start_research(self, business_data, project_name):
        """Запуск исследования"""
        success, message = self.business_manager.start_research(business_data['id'], project_name)
        if success:
            QMessageBox.information(self, "Исследование начато", message)
            self.refresh_interface()
        else:
            QMessageBox.warning(self, "Ошибка", message)
    
    def start_training(self, business_data, model_name):
        """Запуск обучения AI"""
        success, message = self.business_manager.start_ai_training(business_data['id'], model_name)
        if success:
            QMessageBox.information(self, "Обучение начато", message)
            self.refresh_interface()
        else:
            QMessageBox.warning(self, "Ошибка", message)
    
    def upgrade_production(self, business_data, line_type):
        """Обновление производственной линии"""
        success, message = self.business_manager.upgrade_production_line(business_data['id'], line_type)
        if success:
            QMessageBox.information(self, "Производство обновлено", message)
            self.refresh_interface()
        else:
            QMessageBox.warning(self, "Ошибка", message)
    
    def buy_mining_rig(self, business_data, rig_type):
        """Покупка майнинг-рига"""
        success, message = self.business_manager.buy_mining_rig(business_data['id'], rig_type)
        if success:
            QMessageBox.information(self, "Оборудование приобретено", message)
            self.refresh_interface()
        else:
            QMessageBox.warning(self, "Ошибка", message)
    
    def upgrade_business(self, business_data, upgrade_type):
        """Улучшение бизнеса"""
        success, message = business_data['upgrade_system'].upgrade(upgrade_type, self.business_manager.player_balance)
        if success:
            self.business_manager.player_balance -= business_data['upgrade_system'].get_upgrade_cost(
                upgrade_type, business_data['upgrade_system'].levels[upgrade_type] - 1)
            QMessageBox.information(self, "Улучшение применено", message)
            self.refresh_interface()
        else:
            QMessageBox.warning(self, "Ошибка", message)
    
    def buy_business(self, business_template):
        """Покупка бизнеса"""
        success, message = self.business_manager.buy_business(business_template)
        if success:
            QMessageBox.information(self, "Покупка успешна", message)
            self.refresh_interface()
        else:
            QMessageBox.warning(self, "Ошибка", message)
    
    def show_dark_side_dialog(self, business_data):
        """Диалог перехода в темную сторону"""
        reply = QMessageBox.question(
            self,
            "Переход в Тень",
            f"Вы уверены, что хотите перевести {business_data['name']} на темную сторону?\n\n"
            "✨ ПРЕИМУЩЕСТВА:\n"
            "• Доход увеличится на 80%\n"
            "• Откроются эксклюзивные операции\n"
            "• Доступ к черным рынкам\n\n"
            "⚠️ РИСКИ:\n"
            "• Риск возрастет до 70%\n" 
            "• Репутация уменьшится на 25\n"
            "• Возможны рейды и санкции\n\n"
            "Это действие НЕОБРАТИМО!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Здесь будет логика перехода в темную сторону
            QMessageBox.information(self, "Переход завершен", 
                                  f"{business_data['name']} теперь работает в тени!")
    
    def load_my_businesses(self):
        """Загрузка моих бизнесов"""
        if hasattr(self, 'my_businesses_layout'):
            self.clear_layout(self.my_businesses_layout)
            
            row, col = 0, 0
            max_cols = 2
            
            for business in self.business_manager.my_businesses:
                card = self.create_revolutionary_business_card(business, is_owned=True)
                self.my_businesses_layout.addWidget(card, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            if len(self.business_manager.my_businesses) == 0:
                empty_label = QLabel("У вас пока нет бизнесов. Посетите каталог для покупки!")
                empty_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 16px; text-align: center;")
                empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.my_businesses_layout.addWidget(empty_label, 0, 0, 1, max_cols)
    
    def load_catalog(self):
        """Загрузка каталога"""
        if hasattr(self, 'catalog_layout'):
            self.clear_layout(self.catalog_layout)
            
            row, col = 0, 0
            max_cols = 2
            
            available_businesses = [b for b in self.business_manager.available_businesses 
                                  if not any(owned['id'] == b['id'] for owned in self.business_manager.my_businesses)]
            
            for business in available_businesses:
                card = self.create_revolutionary_business_card(business, is_owned=False)
                self.catalog_layout.addWidget(card, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            if len(available_businesses) == 0:
                empty_label = QLabel("Все доступные бизнесы уже приобретены!")
                empty_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 16px; text-align: center;")
                empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.catalog_layout.addWidget(empty_label, 0, 0, 1, max_cols)
    
    def filter_businesses(self, filter_type):
        """Фильтрация бизнесов"""
        self.current_filter = filter_type
        self.load_my_businesses()
    
    def filter_catalog_by_category(self, category):
        """Фильтрация каталога по категории"""
        # Здесь будет логика фильтрации по категориям
        pass
    
    def create_synergy_widget(self, biz1, biz2, synergy):
        """Создание виджета синергии"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG.name()};
                border: 2px solid {PURPLE_ACCENT.name()};
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        
        # Заголовок
        title = QLabel(f"🔄 {synergy['name']}")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Описание
        desc = QLabel(synergy['description'])
        desc.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Бизнесы
        businesses_label = QLabel(f"💼 {biz1} + {biz2}")
        businesses_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 14px;")
        layout.addWidget(businesses_label)
        
        # Бонус
        bonus_label = QLabel(f"📈 Бонус: +{int((synergy['bonus'] - 1) * 100)}%")
        bonus_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 12px;")
        layout.addWidget(bonus_label)
        
        # Требования
        req_text = "Требования: "
        reqs = []
        for req, level in synergy['requirements'].items():
            reqs.append(f"{req}: ур. {level}")
        
        req_label = QLabel(req_text + ", ".join(reqs))
        req_label.setStyleSheet(f"color: {TEXT_TERTIARY.name()}; font-size: 10px;")
        layout.addWidget(req_label)
        
        return widget
    
    def create_income_analysis(self):
        """Анализ доходов"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG.name()};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        
        title = QLabel("📊 Анализ доходов")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Здесь будет детальный анализ доходов по бизнесам
        analysis_text = "• Биотех Лаборатория: $12,000/час\n"
        analysis_text += "• Автопром: $15,000/час\n"
        analysis_text += "• AI разработки: $18,000/час\n"
        analysis_text += "• Общий доход: $45,000/час"
        
        analysis_label = QLabel(analysis_text)
        analysis_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 12px;")
        layout.addWidget(analysis_label)
        
        return widget
    
    def create_recommendations(self):
        """Рекомендации по развитию"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG.name()};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        
        title = QLabel("💡 Рекомендации")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        recommendations = [
            "• Улучшите производительность Биотех до уровня 3",
            "• Запустите исследование генной терапии",
            "• Купите майнинг-риг для увеличения дохода",
            "• Рассмотрите переход AI разработок в тень"
        ]
        
        for rec in recommendations:
            rec_label = QLabel(rec)
            rec_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 12px;")
            layout.addWidget(rec_label)
        
        return widget
    
    def auto_optimize(self):
        """Автооптимизация бизнесов"""
        QMessageBox.information(self, "Автооптимизация", "Система оптимизировала ваши бизнесы!")
    
    def market_analysis(self):
        """Анализ рынка"""
        QMessageBox.information(self, "Анализ рынка", "Текущие рыночные условия анализированы!")
    
    def global_boost(self):
        """Глобальное ускорение"""
        QMessageBox.information(self, "Ускорение", "Все процессы ускорены на 24 часа!")
    
    def setup_business_timers(self):
        """Настройка таймеров для бизнесов"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_interface)
        self.update_timer.start(1000)  # Обновление каждую секунду
    
    def refresh_interface(self):
        """Обновление интерфейса"""
        self.load_my_businesses()
        self.load_catalog()
    
    def clear_layout(self, layout):
        """Очистка layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def keyPressEvent(self, a0):
        """Обработка клавиш"""
        if a0.key() == Qt.Key.Key_Escape:
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