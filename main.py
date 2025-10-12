import sys
import math
import random
import time
import json
import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Tuple
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame, QScrollArea, 
    QGridLayout, QLineEdit, QSlider, QComboBox, QProgressBar,
    QGroupBox, QTabWidget, QTextEdit, QListWidget, QListWidgetItem,
    QDialog, QMessageBox, QSplitter, QToolBar, QStatusBar,
    QSizePolicy, QSpacerItem, QButtonGroup, QRadioButton,
    QCheckBox, QDoubleSpinBox, QSpinBox, QFormLayout
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, 
    QRect, QPoint, QSize, QDateTime, QSequentialAnimationGroup,
    QParallelAnimationGroup
)
from PyQt6.QtGui import (
    QFont, QPalette, QColor, QPainter, QLinearGradient, 
    QRadialGradient, QPen, QBrush, QFontDatabase, QPixmap,
    QIcon, QMovie, QKeyEvent
)

# Константы игры
GAME_VERSION = "0.0.1"
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

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
        self.screen_width = 1920
        self.screen_height = 1080
        self.button_height = 70
        self.font_sizes = {
            "small": 14,
            "medium": 18,
            "large": 24,
            "xlarge": 32,
            "title": 36
        }

# Базовые классы для логики
class Settings:
    def __init__(self):
        pass
    
    def show_themes(self):
        return ["Темная", "Светлая", "Фиолетовая"]
    
    def show_window_sizes(self):
        return [(1280, 720), (1450, 830), (1920, 1080)]
    
    def show_fps(self):
        return [30, 60, 120]
    
    def show_langs(self):
        return ["Русский", "English", "Deutsch"]
    
    def get_current_theme(self):
        return "Темная"
    
    def get_current_window_size(self):
        return (1450, 830)
    
    def get_current_fps(self):
        return 60
    
    def get_current_lang(self):
        return "Русский"
    
    def set_current_theme(self, theme):
        pass
    
    def set_current_fps(self, fps):
        pass
    
    def set_current_lang(self, lang):
        pass

class ExportDB:
    def __init__(self):
        pass
    
    def get_bag(self):
        return (1000000, 5, 5000, 15, 2000, 30000)
    
    def get_actives(self):
        return ["Акция A", "Акция B", "Акция C"]
    
    def get_homes(self):
        return ["Квартира", "Дом", "Вилла"]
    
    def get_crypto(self):
        return ["Bitcoin", "Ethereum", "Dogecoin"]
    
    def balance(self):
        return 1500000
    
    def get_shop_islands(self):
        return (1, "Тропический остров", 5000000, "Райский остров в океане")
    
    def get_shop_boosters(self):
        return (1, "Бустер дохода", 5000, "Увеличивает доход на 24 часа")
    
    def get_shop_nft(self):
        return (1, "Редкое NFT", 25000, "Уникальный цифровой актив")
    
    def get_shop_cars(self):
        return (1, "Спортивный автомобиль", 120000, "Быстрая и стильная машина", "Спортивный", 320)
    
    def get_shop_u_items(self):
        return (1, "Золотой слиток", 50000, "Ценный инвестиционный актив")
    
    def get_shop_yachts(self):
        return (1, "Роскошная яхта", 2000000, "Яхта класса люкс")
    
    def get_shop_planes(self):
        return (1, "Частный самолет", 5000000, "Собственный авиатранспорт")
    
    def get_shop_jewelry(self):
        return (1, "Бриллиантовое колье", 150000, "Эксклюзивное украшение")

class UpdateDB:
    def __init__(self):
        pass

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
    
    def enterEvent(self, a0):
        self.animate_hover()
        super().enterEvent(a0)
    
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
                transform: scale(1.05);
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
    """Виджет с градиентным фоном"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Градиентный фон
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, DARK_BG)
        gradient.setColorAt(0.5, PANEL_BG)
        gradient.setColorAt(1, DARK_BG)
        
        painter.fillRect(self.rect(), gradient)
        
        # Звезды на фоне
        painter.setPen(QPen(WHITE, 1))
        for _ in range(50):
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            size = random.randint(1, 3)
            alpha = random.randint(50, 200)
            star_color = QColor(255, 255, 255, alpha)
            painter.setPen(QPen(star_color, size))
            painter.drawPoint(x, y)

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
        logo_label.setStyleSheet(f"""
            color: {ACCENT2.name()};
            font-size: 36px;
            font-weight: bold;
            font-family: 'Arial';
            letter-spacing: 3px;
        """)
        header_layout.addWidget(logo_label)
        
        # Название игры
        title_label = QLabel("Black Empire")
        title_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY.name()};
            font-size: 72px;
            font-weight: bold;
            font-family: 'Arial';
            margin: 20px 0;
            text-shadow: 0 0 20px {PURPLE_ACCENT.name()};
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
    """Экран загрузки"""
    
    loadingFinished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.progress = 0
        self.dots = 0
        self.rotation_angle = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_loading)
        self.timer.start(100)  # Увеличил интервал для замедления загрузки
        
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.update_rotation)
        self.rotation_timer.start(100)
        
        self.dots_timer = QTimer()
        self.dots_timer.timeout.connect(self.update_dots)
        self.dots_timer.start(300)
        
    def update_loading(self):
        self.progress += 1
        if self.progress >= 100:
            self.timer.stop()
            self.rotation_timer.stop()
            self.dots_timer.stop()
            self.loadingFinished.emit()
        self.update()
        
    def update_rotation(self):
        self.rotation_angle = (self.rotation_angle + 5) % 360
        self.update()
        
    def update_dots(self):
        self.dots = (self.dots + 1) % 4
        self.update()
        
    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Фон
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, DARK_BG)
        gradient.setColorAt(1, PANEL_BG)
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
        
        # Текст загрузки
        painter.setPen(QPen(TEXT_PRIMARY))
        painter.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        loading_text = f"Загрузка{'.' * self.dots}"
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, loading_text)
        
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
    
    def __init__(self):
        super().__init__()
        self.money = 0
        self.per_click = 1
        self.total_clicks = 0
        self.config = GameConfig()
        
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
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 32px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(title)
        
        center_layout.addSpacing(30)
        
        # Кнопка клика
        self.click_button = AnimatedButton("💰 КЛИК!")
        self.click_button.setFixedSize(200, 200)
        self.click_button.setStyleSheet("""
            QPushButton {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8,
                    stop:0 #7828c8, stop:1 #371e72);
                border: 4px solid #8b5cf6;
                border-radius: 100px;
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8,
                    stop:0 #9333ea, stop:1 #482880);
                border: 4px solid #a78bfa;
            }
        """)
        self.click_button.clicked.connect(self.handle_click)
        center_layout.addWidget(self.click_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        center_layout.addSpacing(20)
        
        # Инструкция
        instruction = QLabel("Нажимайте на кнопку или используйте ПРОБЕЛ для заработка\nESC - выход в меню")
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
        
    def handle_click(self):
        self.money += self.per_click
        self.total_clicks += 1
        self.update_display()
        self.moneyChanged.emit(self.money)
        
        # Анимация клика
        self.animate_click()
        
    def handle_upgrade(self, action):
        cost = 0
        if action == "increase_income":
            cost = self.per_click * 10
            if self.money >= cost:
                self.money -= cost
                self.per_click += 1
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
        self.money_label.setText(f"Капитал: ${self.money:,}")
        self.per_click_label.setText(f"Доход за клик: ${self.per_click}")
        self.clicks_label.setText(f"Всего кликов: {self.total_clicks}")
        
    def animate_click(self):
        # Анимация увеличения кнопки
        anim = QPropertyAnimation(self.click_button, b"geometry")
        anim.setDuration(100)
        anim.setStartValue(self.click_button.geometry())
        anim.setEndValue(QRect(
            self.click_button.x() - 5, 
            self.click_button.y() - 5,
            self.click_button.width() + 10,
            self.click_button.height() + 10
        ))
        
        anim2 = QPropertyAnimation(self.click_button, b"geometry")
        anim2.setDuration(100)
        anim2.setStartValue(QRect(
            self.click_button.x() - 5, 
            self.click_button.y() - 5,
            self.click_button.width() + 10,
            self.click_button.height() + 10
        ))
        anim2.setEndValue(self.click_button.geometry())
        
        sequence = QSequentialAnimationGroup()
        sequence.addAnimation(anim)
        sequence.addAnimation(anim2)
        sequence.start()
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            self.handle_click()
        elif event.key() == Qt.Key.Key_Escape:
            self.exit_to_menu()
        else:
            super().keyPressEvent(event)
    
    def show_shops(self):
        self.exitToMenu.emit()
        # Сигнал будет обработан в MainWindow для перехода к магазинам
    
    def show_investments(self):
        self.exitToMenu.emit()
        # Сигнал будет обработан в MainWindow для перехода к инвестициям
    
    def show_businesses(self):
        self.exitToMenu.emit()
        # Сигнал будет обработан в MainWindow для перехода к бизнесам
    
    def show_profile(self):
        self.exitToMenu.emit()
        # Сигнал будет обработан в MainWindow для перехода к профилю
    
    def exit_to_menu(self):
        self.exitToMenu.emit()

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
        self.export = ExportDB()
        
    def load_products(self, category):
        """Загрузка товаров по категории"""
        products = []
        
        if category == "islands":
            data = self.export.get_shop_islands()
            products.append(Product(data[0], data[1], data[2], data[3], "Острова"))
        elif category == "boosters":
            data = self.export.get_shop_boosters()
            products.append(Product(data[0], data[1], data[2], data[3], "Бустеры"))
        elif category == "cars":
            data = self.export.get_shop_cars()
            products.append(Product(data[0], data[1], data[2], data[3], "Машины", data[4]))
            
        return products

class InvestmentMenu(QWidget):
    """Меню инвестиций"""
    
    exitToMenu = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.export = ExportDB()
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
        back_btn.clicked.connect(self.exitToMenu.emit)
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
        stats = [
            f"💰 Стоимость портфеля: ${portfolio_data[0]:,}",
            f"📊 Дивидендная доходность: {portfolio_data[1]}%",
            f"💵 Стабильный доход: ${portfolio_data[2]:,}/мес",
            f"🚀 Потенциал роста: {portfolio_data[3]}%"
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
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.exitToMenu.emit()
        else:
            super().keyPressEvent(event)

class ShopSelectionMenu(QWidget):
    """Выбор магазина"""
    
    shopSelected = pyqtSignal(str)
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
        back_btn.clicked.connect(self.exitToMenu.emit)
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
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.exitToMenu.emit()
        else:
            super().keyPressEvent(event)

class LightShopMenu(QWidget):
    """Светлый магазин"""
    
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
        back_btn.clicked.connect(self.exitToMenu.emit)
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
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.exitToMenu.emit()
        else:
            super().keyPressEvent(event)

class BusinessManager:
    def __init__(self):
        self.my_businesses = []
        
    def buy_business(self, business_data):
        # Логика покупки бизнеса
        pass
        
    def upgrade_business(self, business_id):
        # Логика улучшения бизнеса
        pass

class BusinessMenu(QWidget):
    """Меню бизнесов"""
    
    exitToMenu = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.business_manager = BusinessManager()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("🏢 Бизнес Империя")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 32px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Кнопка возврата
        back_btn = AnimatedButton("🚪 Назад в меню")
        back_btn.clicked.connect(self.exitToMenu.emit)
        layout.addWidget(back_btn)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #7828c8;
                border-radius: 10px;
                background-color: #0f0f28;
            }
            QTabBar::tab {
                background-color: #371e72;
                color: white;
                padding: 10px 20px;
                border: 1px solid #7828c8;
                border-radius: 5px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #7828c8;
            }
        """)
        
        # Мои бизнесы
        my_businesses_tab = self.create_my_businesses_tab()
        self.tab_widget.addTab(my_businesses_tab, "💼 Мои бизнесы")
        
        # Каталог бизнесов
        catalog_tab = self.create_catalog_tab()
        self.tab_widget.addTab(catalog_tab, "📋 Каталог")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
    def create_my_businesses_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок
        header = QLabel("Ваши бизнесы")
        header.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 24px; font-weight: bold;")
        layout.addWidget(header)
        
        # Сетка бизнесов
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        container = QWidget()
        container_layout = QGridLayout()
        container_layout.setSpacing(15)
        
        # Пример бизнесов
        businesses = [
            ("🏪 Магазин", "Розничная торговля", 5000, 50),
            ("🏢 Офис", "Бизнес-центр", 15000, 120),
            ("🏭 Завод", "Производство", 50000, 350)
        ]
        
        row, col = 0, 0
        for name, desc, income, level in businesses:
            business_card = self.create_business_card(name, desc, income, level)
            container_layout.addWidget(business_card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        container.setLayout(container_layout)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        widget.setLayout(layout)
        return widget
        
    def create_catalog_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Заголовок
        header = QLabel("Доступные бизнесы")
        header.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 24px; font-weight: bold;")
        layout.addWidget(header)
        
        # Фильтры
        filter_layout = QHBoxLayout()
        
        light_filter = QRadioButton("💡 Светлые бизнесы")
        dark_filter = QRadioButton("🌑 Темные бизнесы")
        all_filter = QRadioButton("🔍 Все бизнесы")
        all_filter.setChecked(True)
        
        for rb in [light_filter, dark_filter, all_filter]:
            rb.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 14px;")
            filter_layout.addWidget(rb)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Сетка бизнесов
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        container_layout = QGridLayout()
        container_layout.setSpacing(15)
        
        # Пример бизнесов из каталога
        catalog_businesses = [
            ("🏪 Продажа", "Розничная торговля", 5000, 50, "light"),
            ("🏗️ Строительство", "Строительные работы", 25000, 350, "light"),
            ("💻 IT-стартап", "Разработка ПО", 40000, 500, "light"),
            ("🌐 Кибер-мошенничество", "Темная ниша", 12000, 300, "dark"),
            ("💰 Теневой банкинг", "Подпольные финансы", 40000, 900, "dark")
        ]
        
        row, col = 0, 0
        for name, desc, price, income, type in catalog_businesses:
            catalog_card = self.create_catalog_card(name, desc, price, income, type)
            container_layout.addWidget(catalog_card, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        container.setLayout(container_layout)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        widget.setLayout(layout)
        return widget
        
    def create_business_card(self, name, description, income, level):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG.name()};
                border: 2px solid {PURPLE_PRIMARY.name()};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        card.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        # Заголовок
        name_label = QLabel(name)
        name_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 20px; font-weight: bold;")
        layout.addWidget(name_label)
        
        # Описание
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 14px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # Статистика
        stats_layout = QHBoxLayout()
        
        income_label = QLabel(f"💰 ${income}/час")
        income_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 14px;")
        
        level_label = QLabel(f"📊 Ур. {level}")
        level_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 14px;")
        
        stats_layout.addWidget(income_label)
        stats_layout.addWidget(level_label)
        layout.addLayout(stats_layout)
        
        layout.addSpacing(10)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        upgrade_btn = AnimatedButton("Улучшить")
        upgrade_btn.setFixedHeight(30)
        
        manage_btn = AnimatedButton("Управлять")
        manage_btn.setFixedHeight(30)
        
        btn_layout.addWidget(upgrade_btn)
        btn_layout.addWidget(manage_btn)
        layout.addLayout(btn_layout)
        
        card.setLayout(layout)
        return card
        
    def create_catalog_card(self, name, description, price, income, business_type):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG.name()};
                border: 2px solid {'#ef4444' if business_type == 'dark' else PURPLE_PRIMARY.name()};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        card.setFixedSize(400, 180)
        
        layout = QVBoxLayout()
        
        # Заголовок и тип
        header_layout = QHBoxLayout()
        
        name_label = QLabel(name)
        name_label.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 18px; font-weight: bold;")
        
        type_label = QLabel("🌑" if business_type == 'dark' else "💡")
        type_label.setStyleSheet("font-size: 16px;")
        
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(type_label)
        layout.addLayout(header_layout)
        
        # Описание
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 14px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addSpacing(10)
        
        # Цена и доход
        info_layout = QHBoxLayout()
        
        price_label = QLabel(f"💰 Цена: ${price:,}")
        price_label.setStyleSheet(f"color: {ACCENT2.name()}; font-size: 14px;")
        
        income_label = QLabel(f"📈 Доход: ${income}/час")
        income_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 14px;")
        
        info_layout.addWidget(price_label)
        info_layout.addWidget(income_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        layout.addSpacing(10)
        
        # Кнопка покупки
        buy_btn = AnimatedButton("Купить бизнес")
        buy_btn.setFixedHeight(35)
        layout.addWidget(buy_btn)
        
        card.setLayout(layout)
        return card
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.exitToMenu.emit()
        else:
            super().keyPressEvent(event)

class ProfileMenu(QWidget):
    """Меню профиля"""
    
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
        back_btn.clicked.connect(self.exitToMenu.emit)
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
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.exitToMenu.emit()
        else:
            super().keyPressEvent(event)

class SettingsMenu(QWidget):
    """Меню настроек"""
    
    exitToMenu = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.settings_manager = Settings()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("⚙️ Настройки")
        title.setStyleSheet(f"color: {TEXT_PRIMARY.name()}; font-size: 32px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Кнопка возврата
        back_btn = AnimatedButton("🚪 Назад в меню")
        back_btn.clicked.connect(self.exitToMenu.emit)
        layout.addWidget(back_btn)
        
        # Настройки
        settings_widget = self.create_settings_widget()
        layout.addWidget(settings_widget)
        
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
        
        # Тема
        theme_combo = QComboBox()
        theme_combo.addItems(self.settings_manager.show_themes())
        theme_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {DARK_BG.name()};
                color: {TEXT_PRIMARY.name()};
                border: 1px solid {PURPLE_PRIMARY.name()};
                border-radius: 5px;
                padding: 5px;
            }}
        """)
        layout.addRow("🎨 Тема:", theme_combo)
        
        # Разрешение
        resolution_combo = QComboBox()
        resolutions = [f"{w}x{h}" for w, h in self.settings_manager.show_window_sizes()]
        resolution_combo.addItems(resolutions)
        resolution_combo.setStyleSheet(theme_combo.styleSheet())
        layout.addRow("🖥️ Разрешение:", resolution_combo)
        
        # FPS
        fps_combo = QComboBox()
        fps_combo.addItems([f"{fps} FPS" for fps in self.settings_manager.show_fps()])
        fps_combo.setStyleSheet(theme_combo.styleSheet())
        layout.addRow("🎯 FPS:", fps_combo)
        
        # Язык
        language_combo = QComboBox()
        language_combo.addItems(self.settings_manager.show_langs())
        language_combo.setStyleSheet(theme_combo.styleSheet())
        layout.addRow("🌐 Язык:", language_combo)
        
        # Качество графики
        quality_combo = QComboBox()
        quality_combo.addItems(["Низкое", "Среднее", "Высокое", "Ультра"])
        quality_combo.setStyleSheet(theme_combo.styleSheet())
        layout.addRow("🎨 Качество графики:", quality_combo)
        
        # Громкость
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(80)
        volume_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {PURPLE_PRIMARY.name()};
                height: 8px;
                background: {DARK_BG.name()};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {PURPLE_ACCENT.name()};
                border: 1px solid {LIGHT_PURPLE.name()};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QSlider::sub-page:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT1.name()}, stop:1 {ACCENT2.name()});
                border-radius: 4px;
            }}
        """)
        layout.addRow("🔊 Громкость:", volume_slider)
        
        widget.setLayout(layout)
        return widget
        
    def apply_settings(self):
        QMessageBox.information(self, "Настройки", "Настройки успешно применены!")
        
    def reset_settings(self):
        reply = QMessageBox.question(self, "Сброс настроек", 
                                   "Вы уверены, что хотите сбросить все настройки?")
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Настройки", "Настройки сброшены!")
            
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.exitToMenu.emit()
        else:
            super().keyPressEvent(event)

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Black Empire v{GAME_VERSION}")
        self.setGeometry(100, 100, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Центральный виджет с градиентным фоном
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
        self.business_menu = BusinessMenu()
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
        self.investment_menu.exitToMenu.connect(self.show_main_menu)
        self.shop_selection.exitToMenu.connect(self.show_main_menu)
        self.light_shop.exitToMenu.connect(self.show_main_menu)
        self.business_menu.exitToMenu.connect(self.show_main_menu)
        self.profile_menu.exitToMenu.connect(self.show_main_menu)
        self.settings_menu.exitToMenu.connect(self.show_main_menu)
        
        # Подключаем навигацию между разделами
        self.shop_selection.shopSelected.connect(self.handle_shop_selection)
        
        # Показываем экран загрузки
        self.content_stack.setCurrentIndex(0)
        
    def show_main_menu(self):
        """Показать главное меню"""
        self.content_stack.setCurrentIndex(1)
        
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
            # Здесь можно добавить черный рынок
            QMessageBox.information(self, "Черный рынок", "Черный рынок в разработке!")
        
    def keyPressEvent(self, event: QKeyEvent):
        """Глобальная обработка клавиш"""
        if event.key() == Qt.Key.Key_Escape:
            # Если мы не в главном меню, возвращаемся в него
            current_index = self.content_stack.currentIndex()
            if current_index != 1:  # Не главное меню
                self.show_main_menu()
        else:
            super().keyPressEvent(event)

def main():
    app = QApplication(sys.argv)
    
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