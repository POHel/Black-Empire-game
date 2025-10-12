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
    QParallelAnimationGroup, qInstallMessageHandler
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
            
        """)
        #text-shadow: 0 0 20px var{PURPLE_ACCENT.name()};
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
        loading_texts = ["Загрузка", "Загрузка.", "Загрузка..", "Загрузка...", "Загрузка..."]
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
        self.click_button = AnimatedButton("💰КЛИК! ")
        self.click_button.setFixedSize(500, 500)
        self.click_button.setStyleSheet("""
            QPushButton {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8,
                    stop:0 #7828c8, stop:1 #371e72);
                border: 4px solid #8b5cf6;
                border-radius: 250px;
                color: white;
                font-size: 70px;
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
        
    def keyPressEvent(self, a0: QKeyEvent | None):
        if a0 is not None and a0.key() == Qt.Key.Key_Space:
            self.handle_click()
        elif a0 is not None and a0.key() == Qt.Key.Key_Escape:
            self.exit_to_menu()
        else:
            super().keyPressEvent(a0)
    """
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
    """
    
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
    
    exitToClicker = pyqtSignal()
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
        
    def keyPressEvent(self, a0: QKeyEvent | None):
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
        
    def keyPressEvent(self, a0: QKeyEvent | None):
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
        
    def keyPressEvent(self, a0: QKeyEvent | None):
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
        """Загрузка данных о бизнесах с улучшенными механиками"""
        return [
            # Светлые бизнесы
            {
                'id': 1,
                'name': 'Продажа (Retail)',
                'icon': '🏪',
                'level': 1,
                'income_per_hour': 5000,
                'workers': 5,
                'workload': 75,
                'primary_action': 'Открыть ассортимент',
                'available_roles': [
                    {'name': 'Продавец', 'cost': 1000, 'effect': '+10% доход'},
                    {'name': 'Менеджер', 'cost': 3000, 'effect': '+25% эффективность'},
                    {'name': 'Merchandiser', 'cost': 2000, 'effect': '+15% оборачиваемость'}
                ],
                'special_modes': [
                    {'name': 'Маркет-кампания', 'cooldown': '6ч', 'cost': 15000, 'effect': '+200% спрос на 1ч'},
                    {'name': 'Сезонные коллаборации', 'cooldown': '24ч', 'cost': 25000, 'effect': '+10% маржа'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['IT-стартап', 'Логистика'],
                'price': 50000
            },
            {
                'id': 2,
                'name': 'Строительство',
                'icon': '🏗️',
                'level': 1,
                'income_per_hour': 12000,
                'workers': 12,
                'workload': 80,
                'primary_action': 'Запустить проект',
                'available_roles': [
                    {'name': 'Бригадир', 'cost': 8000, 'effect': '+20% скорость строительства'},
                    {'name': 'Инженер', 'cost': 12000, 'effect': '+25% качество'},
                    {'name': 'Менеджер проектов', 'cost': 15000, 'effect': '+30% эффективность'}
                ],
                'special_modes': [
                    {'name': 'Экспресс-лаг', 'cooldown': '24ч', 'cost': 40000, 'effect': 'Ускорение проекта 50%'},
                    {'name': 'Лоббирование', 'cooldown': '48ч', 'cost': 30000, 'effect': 'Ускорение разрешений'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['УГМК', 'Электросетевая компания'],
                'price': 150000
            },
            {
                'id': 3,
                'name': 'IT-стартап',
                'icon': '💻',
                'level': 1,
                'income_per_hour': 8000,
                'workers': 3,
                'workload': 60,
                'primary_action': 'Разработать фичу',
                'available_roles': [
                    {'name': 'Junior Dev', 'cost': 2000, 'effect': '+5% скорость разработки'},
                    {'name': 'Senior Dev', 'cost': 5000, 'effect': '+20% качество кода'},
                    {'name': 'PM', 'cost': 4000, 'effect': '+15% эффективность команды'},
                    {'name': 'Growth Hacker', 'cost': 4500, 'effect': '+25% прирост пользователей'}
                ],
                'special_modes': [
                    {'name': 'Инвест-раунд', 'cooldown': '12ч', 'cost': 30000, 'effect': '+50000 капитала'},
                    {'name': 'Бета-тест', 'cooldown': '8ч', 'cost': 10000, 'effect': 'Шанс вирусного роста'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['AI разработки', 'Кибербезопасность'],
                'price': 75000
            },
            {
                'id': 4,
                'name': 'Электросетевая компания',
                'icon': '⚡',
                'level': 1,
                'income_per_hour': 18000,
                'workers': 8,
                'workload': 70,
                'primary_action': 'План генерации',
                'available_roles': [
                    {'name': 'Диспетчер', 'cost': 7000, 'effect': '+15% эффективность сети'},
                    {'name': 'Инженер линии', 'cost': 9000, 'effect': '+20% надежность'},
                    {'name': 'Аналитик спроса', 'cost': 6000, 'effect': '+25% прогнозирование'}
                ],
                'special_modes': [
                    {'name': 'Smart Grid', 'cooldown': '36ч', 'cost': 60000, 'effect': 'P2P торговля энергией'},
                    {'name': 'Экстренный тариф', 'cooldown': '12ч', 'cost': 20000, 'effect': '+300% доход на 2ч'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['Строительство', 'Теневой майнинг'],
                'price': 200000,
                'smart_grid': False
            },
            {
                'id': 5,
                'name': 'Сеть кофеен',
                'icon': '☕',
                'level': 1,
                'income_per_hour': 6000,
                'workers': 6,
                'workload': 65,
                'primary_action': 'Открыть новую точку',
                'available_roles': [
                    {'name': 'Бариста', 'cost': 2000, 'effect': '+10% качество'},
                    {'name': 'Менеджер', 'cost': 5000, 'effect': '+20% эффективность'},
                    {'name': 'Маркетолог', 'cost': 4000, 'effect': '+15% посещаемость'}
                ],
                'special_modes': [
                    {'name': 'Франшизирование', 'cooldown': '48ч', 'cost': 35000, 'effect': 'Пассивный доход +50%'},
                    {'name': 'Сезонная акция', 'cooldown': '24ч', 'cost': 15000, 'effect': '+100% клиентов на 4ч'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['Продажа (Retail)', 'Биотех Лаборатория'],
                'price': 60000
            },
            {
                'id': 6,
                'name': 'Биотех Лаборатория',
                'icon': '🧬',
                'level': 1,
                'income_per_hour': 12000,
                'workers': 8,
                'workload': 45,
                'primary_action': 'Запустить исследование',
                'available_roles': [
                    {'name': 'Исследователь', 'cost': 6000, 'effect': '+15% скорость исследований'},
                    {'name': 'Клинический специалист', 'cost': 7000, 'effect': '+20% успех испытаний'},
                    {'name': 'Регуляторный менеджер', 'cost': 5500, 'effect': '-30% время одобрения'}
                ],
                'special_modes': [
                    {'name': 'Клинические испытания', 'cooldown': '24ч', 'cost': 50000, 'effect': 'Патент + доход'},
                    {'name': 'Подать на патент', 'cooldown': '48ч', 'cost': 25000, 'effect': 'Монополия 6 месяцев'}
                ],
                'can_go_dark': True,
                'dark_actions': [
                    {'name': 'Несанкционированные испытания', 'income_multiplier': 2.0, 'risk_increase': 25},
                    {'name': 'Продажа запрещенных имплантов', 'income_multiplier': 3.0, 'risk_increase': 40}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['Робототехника', 'Медицинский центр'],
                'price': 150000
            },
            {
                'id': 7,
                'name': 'Образовательная платформа',
                'icon': '🎓',
                'level': 1,
                'income_per_hour': 9000,
                'workers': 5,
                'workload': 55,
                'primary_action': 'Создать курс',
                'available_roles': [
                    {'name': 'Методолог', 'cost': 5000, 'effect': '+20% качество курсов'},
                    {'name': 'Куратор', 'cost': 4000, 'effect': '+15% завершаемость'},
                    {'name': 'Маркетолог', 'cost': 4500, 'effect': '+25% привлечение'}
                ],
                'special_modes': [
                    {'name': 'B2B Контракт', 'cooldown': '36ч', 'cost': 40000, 'effect': 'Корпоративные клиенты'},
                    {'name': 'Автор-премия', 'cooldown': '24ч', 'cost': 20000, 'effect': 'Привлечение звезд'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['IT-стартап', 'AI разработки'],
                'price': 100000
            },
            {
                'id': 8,
                'name': 'Технопарк',
                'icon': '🏭',
                'level': 1,
                'income_per_hour': 15000,
                'workers': 7,
                'workload': 60,
                'primary_action': 'Принять стартап',
                'available_roles': [
                    {'name': 'Менеджер парка', 'cost': 8000, 'effect': '+20% привлечение'},
                    {'name': 'Акселератор', 'cost': 12000, 'effect': '+30% успешность'},
                    {'name': 'Резидент-менеджер', 'cost': 10000, 'effect': '+25% доход с резидентов'}
                ],
                'special_modes': [
                    {'name': 'Инфраструктурный пакет', 'cooldown': '48ч', 'cost': 50000, 'effect': 'Премиум услуги'},
                    {'name': 'Экзит-стратегия', 'cooldown': '72ч', 'cost': 80000, 'effect': 'Крупный доход от продажи'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['IT-стартап', 'AI разработки'],
                'price': 180000
            },
            {
                'id': 9,
                'name': 'Автопром',
                'icon': '🚗',
                'level': 1,
                'income_per_hour': 20000,
                'workers': 15,
                'workload': 80,
                'primary_action': 'Запустить производство модели',
                'available_roles': [
                    {'name': 'Инженер', 'cost': 8000, 'effect': '+10% качество'},
                    {'name': 'Конструктор', 'cost': 10000, 'effect': '+15% инновации'},
                    {'name': 'Менеджер производства', 'cost': 12000, 'effect': '+20% эффективность'}
                ],
                'special_modes': [
                    {'name': 'EV Платформа', 'cooldown': '72ч', 'cost': 100000, 'effect': 'Производство электромобилей'},
                    {'name': 'Автоматизация', 'cooldown': '48ч', 'cost': 75000, 'effect': '-40% себестоимость'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['УГМК', 'Робототехника'],
                'price': 300000,
                'ev_production': False
            },
            {
                'id': 10,
                'name': 'Кибербезопасность',
                'icon': '🛡️',
                'level': 1,
                'income_per_hour': 16000,
                'workers': 6,
                'workload': 70,
                'primary_action': 'Предложить контракт',
                'available_roles': [
                    {'name': 'Pentester', 'cost': 9000, 'effect': '+20% обнаружение уязвимостей'},
                    {'name': 'Analyst', 'cost': 8000, 'effect': '+15% анализ угроз'},
                    {'name': 'SOC Operator', 'cost': 7000, 'effect': '+25% скорость реакции'}
                ],
                'special_modes': [
                    {'name': 'Incident Response', 'cooldown': '12ч', 'cost': 30000, 'effect': 'Экстренный доход'},
                    {'name': 'Threat Intelligence', 'cooldown': '24ч', 'cost': 25000, 'effect': 'Проактивная защита'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['IT-стартап', 'Банк'],
                'price': 140000
            },
            {
                'id': 11,
                'name': 'Медицинский центр',
                'icon': '🏥',
                'level': 1,
                'income_per_hour': 14000,
                'workers': 10,
                'workload': 75,
                'primary_action': 'Открыть отдел',
                'available_roles': [
                    {'name': 'Врач', 'cost': 10000, 'effect': '+20% качество услуг'},
                    {'name': 'Медсестра', 'cost': 5000, 'effect': '+15% уход'},
                    {'name': 'Администратор', 'cost': 4000, 'effect': '+25% эффективность'}
                ],
                'special_modes': [
                    {'name': 'Телемедицина', 'cooldown': '24ч', 'cost': 30000, 'effect': 'Удаленные консультации'},
                    {'name': 'Эксклюзивные процедуры', 'cooldown': '48ч', 'cost': 50000, 'effect': 'Премиум услуги'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['Биотех Лаборатория', 'Робототехника'],
                'price': 160000
            },
            {
                'id': 12,
                'name': 'Робототехника',
                'icon': '🤖',
                'level': 1,
                'income_per_hour': 18000,
                'workers': 10,
                'workload': 70,
                'primary_action': 'Запустить проект робота',
                'available_roles': [
                    {'name': 'Мехатроник', 'cost': 9000, 'effect': '+15% точность'},
                    {'name': 'AI-инженер', 'cost': 12000, 'effect': '+25% интеллект систем'},
                    {'name': 'Техлид', 'cost': 15000, 'effect': '+30% скорость разработки'}
                ],
                'special_modes': [
                    {'name': 'Биопротезы', 'cooldown': '36ч', 'cost': 80000, 'effect': 'Медицинская робототехника'},
                    {'name': 'Нейрочипы', 'cooldown': '48ч', 'cost': 120000, 'effect': 'Нейроинтерфейсы'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['Биотех Лаборатория', 'AI разработки'],
                'price': 250000,
                'bio_prosthetics': False,
                'neuro_chips': False
            },
            {
                'id': 13,
                'name': 'Космический туризм',
                'icon': '🚀',
                'level': 1,
                'income_per_hour': 35000,
                'workers': 5,
                'workload': 40,
                'primary_action': 'Строить корабль',
                'available_roles': [
                    {'name': 'Астроинженер', 'cost': 20000, 'effect': '+25% надежность'},
                    {'name': 'Капитан', 'cost': 25000, 'effect': '+30% безопасность'},
                    {'name': 'PR-менеджер', 'cost': 15000, 'effect': '+40% привлечение'}
                ],
                'special_modes': [
                    {'name': 'Звёздный рейс', 'cooldown': '96ч', 'cost': 200000, 'effect': 'PR бонус +100%'},
                    {'name': 'Научная миссия', 'cooldown': '72ч', 'cost': 150000, 'effect': 'Гранты + репутация'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['AI разработки', 'Оборонное предприятие'],
                'price': 500000
            },
            {
                'id': 14,
                'name': 'AI разработки',
                'icon': '🧠',
                'level': 1,
                'income_per_hour': 15000,
                'workers': 6,
                'workload': 65,
                'primary_action': 'Запустить обучение модели',
                'available_roles': [
                    {'name': 'ML-инженер', 'cost': 10000, 'effect': '+20% качество моделей'},
                    {'name': 'Дата-инженер', 'cost': 8000, 'effect': '+15% эффективность данных'},
                    {'name': 'DevOps', 'cost': 7000, 'effect': '+25% скорость развертывания'}
                ],
                'special_modes': [
                    {'name': 'Train Big', 'cooldown': '24ч', 'cost': 50000, 'effect': 'Крупная модель +50% доход'},
                    {'name': 'API Лицензирование', 'cooldown': '48ч', 'cost': 30000, 'effect': 'Пассивный доход'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['IT-стартап', 'Кибербезопасность'],
                'price': 200000,
                'servers': 0,
                'data_center': False
            },
            {
                'id': 15,
                'name': 'Банк',
                'icon': '🏦',
                'level': 1,
                'income_per_hour': 22000,
                'workers': 8,
                'workload': 85,
                'primary_action': 'Открыть продукт',
                'available_roles': [
                    {'name': 'Риск-офицер', 'cost': 15000, 'effect': '+20% безопасность'},
                    {'name': 'Клерк', 'cost': 6000, 'effect': '+15% обслуживание'},
                    {'name': 'Трейдер', 'cost': 18000, 'effect': '+25% инвестиционный доход'}
                ],
                'special_modes': [
                    {'name': 'Кредитная программа', 'cooldown': '24ч', 'cost': 40000, 'effect': 'Массовое кредитование'},
                    {'name': 'Аудит', 'cooldown': '48ч', 'cost': 30000, 'effect': 'Снижение риска проверок'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['Трейдинг', 'Отмывание денег'],
                'price': 280000
            },
            {
                'id': 16,
                'name': 'Нефтегазовая компания',
                'icon': '🛢️',
                'level': 1,
                'income_per_hour': 25000,
                'workers': 12,
                'workload': 80,
                'primary_action': 'Начать бурение',
                'available_roles': [
                    {'name': 'Геолог', 'cost': 12000, 'effect': '+25% успех разведки'},
                    {'name': 'Инженер', 'cost': 10000, 'effect': '+20% эффективность'},
                    {'name': 'Трейдер', 'cost': 15000, 'effect': '+30% торговая прибыль'}
                ],
                'special_modes': [
                    {'name': 'Хеджирование', 'cooldown': '24ч', 'cost': 50000, 'effect': 'Фиксация цен'},
                    {'name': 'НИОКР', 'cooldown': '48ч', 'cost': 60000, 'effect': 'Экологичные технологии'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['УГМК', 'Электросетевая компания'],
                'price': 350000
            },
            {
                'id': 17,
                'name': 'Трейдинг',
                'icon': '📊',
                'level': 1,
                'income_per_hour': 25000,
                'workers': 4,
                'workload': 90,
                'primary_action': 'Запустить стратегию',
                'available_roles': [
                    {'name': 'Quant', 'cost': 20000, 'effect': '+30% эффективность алгоритмов'},
                    {'name': 'Trader', 'cost': 15000, 'effect': '+25% доходность сделок'},
                    {'name': 'Ops', 'cost': 10000, 'effect': '+20% скорость исполнения'}
                ],
                'special_modes': [
                    {'name': 'Арбитраж', 'cooldown': '12ч', 'cost': 0, 'effect': 'Использование крипто-резерва'},
                    {'name': 'Маркет-мейкинг', 'cooldown': '24ч', 'cost': 0, 'effect': 'Комиссионный доход'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['Банк', 'Крипто-майнинг'],
                'price': 180000,
                'crypto_reserve_usage': 0.1
            },
            {
                'id': 18,
                'name': 'Оборонное предприятие',
                'icon': '🪖',
                'level': 1,
                'income_per_hour': 30000,
                'workers': 10,
                'workload': 70,
                'primary_action': 'Подать на тендер',
                'available_roles': [
                    {'name': 'Инженер-конструктор', 'cost': 18000, 'effect': '+25% инновации'},
                    {'name': 'PM', 'cost': 15000, 'effect': '+20% управление'},
                    {'name': 'Compliance', 'cost': 12000, 'effect': '+30% соответствие'}
                ],
                'special_modes': [
                    {'name': 'Госзаказ', 'cooldown': '48ч', 'cost': 80000, 'effect': 'Крупный контракт'},
                    {'name': 'Секретный проект', 'cooldown': '72ч', 'cost': 120000, 'effect': 'Эксклюзивные технологии'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['УГМК', 'AI разработки'],
                'price': 400000
            },
            {
                'id': 19,
                'name': 'УГМК',
                'icon': '⛏️',
                'level': 1,
                'income_per_hour': 30000,
                'workers': 25,
                'workload': 85,
                'primary_action': 'Открыть рудник',
                'available_roles': [
                    {'name': 'Горняк', 'cost': 5000, 'effect': '+10% добыча'},
                    {'name': 'Металлург', 'cost': 12000, 'effect': '+20% переработка'},
                    {'name': 'Логист', 'cost': 8000, 'effect': '+15% эффективность поставок'}
                ],
                'special_modes': [
                    {'name': 'Вертикальная интеграция', 'cooldown': '96ч', 'cost': 200000, 'effect': 'Контроль над рынком'},
                    {'name': 'Санкционный обход', 'cooldown': '48ч', 'cost': 50000, 'effect': 'Темный доход +100%'}
                ],
                'can_go_dark': True,
                'dark_actions': [
                    {'name': 'Нелегальный экспорт', 'income_multiplier': 2.5, 'risk_increase': 30},
                    {'name': 'Схемы уклонения', 'income_multiplier': 1.8, 'risk_increase': 20}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'light',
                'synergies': ['Автопром', 'Строительство'],
                'price': 400000
            },

            # Темные бизнесы
            {
                'id': 101,
                'name': 'Кибер-мошенничество',
                'icon': '🌐',
                'level': 1,
                'income_per_hour': 15000,
                'workers': 4,
                'workload': 85,
                'primary_action': 'Запустить кампанию',
                'available_roles': [
                    {'name': 'Оператор', 'cost': 3000, 'effect': '+15% успех операций'},
                    {'name': 'Crypto Launder', 'cost': 8000, 'effect': '-20% риск обнаружения'},
                    {'name': 'Packer', 'cost': 5000, 'effect': '+25% скрытность'}
                ],
                'special_modes': [
                    {'name': 'Exploit Market', 'cooldown': '12ч', 'cost': 20000, 'effect': 'Продажа эксплойтов'},
                    {'name': 'Cover-up', 'cooldown': '6ч', 'cost': 10000, 'effect': 'Снижение риска на 50%'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'dark',
                'risk': 25,
                'price': 100000
            },
            {
                'id': 102,
                'name': 'Теневой банкинг',
                'icon': '💳',
                'level': 1,
                'income_per_hour': 18000,
                'workers': 5,
                'workload': 75,
                'primary_action': 'Открыть пул',
                'available_roles': [
                    {'name': 'Бухгалтер', 'cost': 8000, 'effect': '+20% эффективность'},
                    {'name': 'Юрист', 'cost': 12000, 'effect': '-25% риск'},
                    {'name': 'Брокер', 'cost': 10000, 'effect': '+30% доходность'}
                ],
                'special_modes': [
                    {'name': 'Офшор-сеть', 'cooldown': '48ч', 'cost': 50000, 'effect': 'Глобальная сеть счетов'},
                    {'name': 'Слияние фондов', 'cooldown': '72ч', 'cost': 80000, 'effect': 'Объединение капиталов'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'dark',
                'risk': 30,
                'price': 150000
            },
            {
                'id': 103,
                'name': 'Контрабанда',
                'icon': '📦',
                'level': 1,
                'income_per_hour': 14000,
                'workers': 6,
                'workload': 80,
                'primary_action': 'Отправить партию',
                'available_roles': [
                    {'name': 'Курьер', 'cost': 4000, 'effect': '+20% скорость'},
                    {'name': 'Логист', 'cost': 7000, 'effect': '+25% безопасность'},
                    {'name': 'Заправщик', 'cost': 3000, 'effect': '+15% дальность'}
                ],
                'special_modes': [
                    {'name': 'Большой рейд', 'cooldown': '96ч', 'cost': 60000, 'effect': 'Крупная партия +200% доход'},
                    {'name': 'Взятка', 'cooldown': '24ч', 'cost': 15000, 'effect': 'Снижение риска на 70%'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'dark',
                'risk': 35,
                'price': 120000
            },
            {
                'id': 104,
                'name': 'Пиратское ПО',
                'icon': '🏴‍☠️',
                'level': 1,
                'income_per_hour': 11000,
                'workers': 3,
                'workload': 70,
                'primary_action': 'Выпустить релиз',
                'available_roles': [
                    {'name': 'Dev', 'cost': 6000, 'effect': '+20% качество'},
                    {'name': 'Креакер', 'cost': 8000, 'effect': '+25% обход защиты'},
                    {'name': 'Sysadmin', 'cost': 5000, 'effect': '+30% стабильность'}
                ],
                'special_modes': [
                    {'name': 'Обновление защиты', 'cooldown': '24ч', 'cost': 20000, 'effect': 'Снижение риска'},
                    {'name': 'Подпольный рынок', 'cooldown': '48ч', 'cost': 30000, 'effect': 'Массовое распространение'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'dark',
                'risk': 20,
                'price': 90000
            },
            {
                'id': 105,
                'name': 'Нелегальные ставки',
                'icon': '🎲',
                'level': 1,
                'income_per_hour': 16000,
                'workers': 4,
                'workload': 85,
                'primary_action': 'Открыть ставку',
                'available_roles': [
                    {'name': 'Кассир', 'cost': 5000, 'effect': '+15% обслуживание'},
                    {'name': 'Аналитик', 'cost': 9000, 'effect': '+25% точность'},
                    {'name': 'Охрана', 'cost': 4000, 'effect': '+20% безопасность'}
                ],
                'special_modes': [
                    {'name': 'Инсайдерская информация', 'cooldown': '24ч', 'cost': 40000, 'effect': 'Гарантированный выигрыш'},
                    {'name': 'Зеленая книга', 'cooldown': '48ч', 'cost': 25000, 'effect': 'VIP клиенты +100% доход'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'dark',
                'risk': 28,
                'price': 130000
            },
            {
                'id': 106,
                'name': 'Фальшивые документы',
                'icon': '📄',
                'level': 1,
                'income_per_hour': 9000,
                'workers': 4,
                'workload': 65,
                'primary_action': 'Сделать партию',
                'available_roles': [
                    {'name': 'График', 'cost': 6000, 'effect': '+25% качество'},
                    {'name': 'Офис-оператор', 'cost': 4000, 'effect': '+20% скорость'},
                    {'name': 'Курьер', 'cost': 3000, 'effect': '+15% доставка'}
                ],
                'special_modes': [
                    {'name': 'Визовые схемы', 'cooldown': '48ч', 'cost': 35000, 'effect': 'Премиум документы'},
                    {'name': 'Контроль качества', 'cooldown': '24ч', 'cost': 15000, 'effect': 'Снижение риска'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'dark',
                'risk': 22,
                'price': 80000
            },
            {
                'id': 107,
                'name': 'Нелегальный импорт/экспорт',
                'icon': '🚢',
                'level': 1,
                'income_per_hour': 17000,
                'workers': 7,
                'workload': 75,
                'primary_action': 'Запустить рейс',
                'available_roles': [
                    {'name': 'Брокер', 'cost': 8000, 'effect': '+20% эффективность'},
                    {'name': 'Капитан', 'cost': 12000, 'effect': '+25% безопасность'},
                    {'name': 'Складской', 'cost': 5000, 'effect': '+15% логистика'}
                ],
                'special_modes': [
                    {'name': 'Экспортные сделки', 'cooldown': '72ч', 'cost': 70000, 'effect': 'Крупные контракты'},
                    {'name': 'Фальсификация деклараций', 'cooldown': '24ч', 'cost': 20000, 'effect': 'Снижение риска'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'dark',
                'risk': 32,
                'price': 160000
            },
            {
                'id': 108,
                'name': 'Теневой майнинг',
                'icon': '⛏️',
                'level': 1,
                'income_per_hour': 12000,
                'workers': 3,
                'workload': 75,
                'primary_action': 'Построить ферму',
                'available_roles': [
                    {'name': 'Rigger', 'cost': 4000, 'effect': '+20% хешрейт'},
                    {'name': 'Sysadmin', 'cost': 6000, 'effect': '+15% стабильность'},
                    {'name': 'Электрик', 'cost': 3000, 'effect': '-25% энергопотребление'}
                ],
                'special_modes': [
                    {'name': 'Рекуперация тепла', 'cooldown': '24ч', 'cost': 15000, 'effect': 'Экономия энергии + доход'},
                    {'name': 'Ботнет', 'cooldown': '8ч', 'cost': 0, 'effect': 'Временный +100% хешрейт'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'dark',
                'risk': 20,
                'price': 80000,
                'heat_recovery': False,
                'botnet_active': False
            },
            {
                'id': 109,
                'name': 'Наркокартель',
                'icon': '💊',
                'level': 1,
                'income_per_hour': 25000,
                'workers': 8,
                'workload': 90,
                'primary_action': 'Запустить производство',
                'available_roles': [
                    {'name': 'Химик', 'cost': 10000, 'effect': '+25% качество'},
                    {'name': 'Охрана', 'cost': 6000, 'effect': '+30% безопасность'},
                    {'name': 'Курьер', 'cost': 5000, 'effect': '+20% доставка'}
                ],
                'special_modes': [
                    {'name': 'Захват территории', 'cooldown': '48ч', 'cost': 50000, 'effect': 'Расширение влияния'},
                    {'name': 'Коррупция', 'cooldown': '24ч', 'cost': 30000, 'effect': 'Снижение риска рейдов'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'dark',
                'risk': 45,
                'price': 200000
            },
            {
                'id': 110,
                'name': 'Отмывание денег',
                'icon': '💸',
                'level': 1,
                'income_per_hour': 20000,
                'workers': 5,
                'workload': 60,
                'primary_action': 'Отмыть сумму',
                'available_roles': [
                    {'name': 'Бухгалтер', 'cost': 10000, 'effect': '+20% эффективность'},
                    {'name': 'Юрист', 'cost': 15000, 'effect': '-30% риск'},
                    {'name': 'Front Manager', 'cost': 12000, 'effect': '+25% доверие компаний'}
                ],
                'special_modes': [
                    {'name': 'Корпоративные цепочки', 'cooldown': '48ч', 'cost': 50000, 'effect': 'Большие суммы + доверие'},
                    {'name': 'Паник-режим', 'cooldown': '24ч', 'cost': 0, 'effect': 'Экстренное снижение риска'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'dark',
                'risk': 35,
                'price': 150000,
                'trust_level': 1,
                'max_launder_amount': 50000
            },
            {
                'id': 111,
                'name': 'Подпольный хостинг',
                'icon': '🖥️',
                'level': 1,
                'income_per_hour': 13000,
                'workers': 4,
                'workload': 70,
                'primary_action': 'Запустить ноду',
                'available_roles': [
                    {'name': 'Sysadmin', 'cost': 7000, 'effect': '+25% стабильность'},
                    {'name': 'Network', 'cost': 8000, 'effect': '+30% скорость'},
                    {'name': 'Support', 'cost': 5000, 'effect': '+20% обслуживание'}
                ],
                'special_modes': [
                    {'name': 'DDOS-защита', 'cooldown': '24ч', 'cost': 25000, 'effect': 'Повышение безопасности'},
                    {'name': 'Шифрование', 'cooldown': '48ч', 'cost': 30000, 'effect': 'Анонимность +50%'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'dark',
                'risk': 18,
                'price': 110000
            },
            {
                'id': 112,
                'name': 'Нелегальный аутсорсинг',
                'icon': '👥',
                'level': 1,
                'income_per_hour': 10000,
                'workers': 6,
                'workload': 80,
                'primary_action': 'Взять заказ',
                'available_roles': [
                    {'name': 'Фриланс-исполнитель', 'cost': 4000, 'effect': '+15% качество'},
                    {'name': 'Контролер качества', 'cost': 6000, 'effect': '+20% надежность'}
                ],
                'special_modes': [
                    {'name': 'Ускорение выполнения', 'cooldown': '12ч', 'cost': 15000, 'effect': 'Быстрые деньги + риск'},
                    {'name': 'Крупный контракт', 'cooldown': '48ч', 'cost': 40000, 'effect': 'Большой доход'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'dark',
                'risk': 15,
                'price': 70000
            },
            {
                'id': 113,
                'name': 'Тёмный арбитраж',
                'icon': '🔄',
                'level': 1,
                'income_per_hour': 19000,
                'workers': 3,
                'workload': 85,
                'primary_action': 'Запустить арбитраж',
                'available_roles': [
                    {'name': 'Arb-bot', 'cost': 15000, 'effect': '+35% эффективность'},
                    {'name': 'Ops', 'cost': 10000, 'effect': '+25% скорость'}
                ],
                'special_modes': [
                    {'name': 'Инсайдерский поток', 'cooldown': '24ч', 'cost': 45000, 'effect': 'Гарантированная прибыль'},
                    {'name': 'Ускорение шлюза', 'cooldown': '12ч', 'cost': 20000, 'effect': 'Мгновенные переводы'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'dark',
                'risk': 25,
                'price': 170000
            },
            {
                'id': 114,
                'name': 'Частная военная компания',
                'icon': '⚔️',
                'level': 1,
                'income_per_hour': 28000,
                'workers': 12,
                'workload': 90,
                'primary_action': 'Взять контракт',
                'available_roles': [
                    {'name': 'Солдат', 'cost': 8000, 'effect': '+20% боеспособность'},
                    {'name': 'Снайпер', 'cost': 12000, 'effect': '+25% точность'},
                    {'name': 'Спецназ', 'cost': 15000, 'effect': '+30% эффективность'}
                ],
                'special_modes': [
                    {'name': 'Covert Операция', 'cooldown': '72ч', 'cost': 100000, 'effect': 'Высокий риск/вознаграждение'},
                    {'name': 'Апгрейд техники', 'cooldown': '48ч', 'cost': 60000, 'effect': 'Улучшение вооружения'}
                ],
                'upgrade_1': 1, 'upgrade_2': 1, 'upgrade_3': 1, 'upgrade_4': 1, 'upgrade_5': 1,
                'type': 'dark',
                'risk': 40,
                'price': 300000
            }
        ]
    
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
    
    def get_total_income(self):
        """Общий доход в час со всех бизнесов"""
        return sum(business.get('income_per_hour', 0) for business in self.my_businesses)
        
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
        
    def create_my_businesses_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)  # Устанавливаем layout непосредственно для widget
        
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
            btn.toggled.connect(lambda checked, ft=filter_type: self.filter_my_businesses(ft))
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
        layout = QVBoxLayout(widget)  # Устанавливаем layout непосредственно для widget
        
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
            btn.toggled.connect(lambda checked, ft=filter_type: self.filter_catalog(ft))
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
        
        self.catalog_container = QWidget()
        self.catalog_layout = QGridLayout(self.catalog_container)  # Устанавливаем layout
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
        """Загрузка моих бизнесов"""
        # Проверяем, инициализирован ли layout
        if self.my_businesses_layout is None:
            print("Ошибка: my_businesses_layout не инициализирован")
            return
            
        # Безопасная очистка layout
        self.clear_layout(self.my_businesses_layout)
        
        # Добавляем бизнесы
        row, col = 0, 0
        max_cols = 2
        
        for business_data in self.business_manager.my_businesses:
            card = self.create_business_card(business_data, is_owned=True)
            self.my_businesses_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
        # Если бизнесов нет, показываем сообщение
        if not self.business_manager.my_businesses:
            no_business_label = QLabel("У вас пока нет бизнесов. Посетите каталог для покупки!")
            no_business_label.setStyleSheet(f"color: {TEXT_SECONDARY.name()}; font-size: 16px; text-align: center;")
            no_business_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.my_businesses_layout.addWidget(no_business_label, 0, 0, 1, max_cols)

    def clear_layout(self, layout):
        """Безопасная рекурсивная очистка layout"""
        if layout is None:
            return
            
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue
                
            widget = item.widget()
            if widget is not None:
                # Если это виджет - удаляем его
                widget.deleteLater()
            else:
                # Если это вложенный layout - очищаем его рекурсивно
                nested_layout = item.layout()
                if nested_layout is not None:
                    self.clear_layout(nested_layout)
                    # Удаляем сам layout
                    nested_layout.deleteLater()
        
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
        # Проверяем, инициализирован ли layout
        if self.catalog_layout is None:
            return
            
        # Очищаем layout - безопасно удаляем все элементы
        self.clear_layout(self.catalog_layout)
        
        # Добавляем бизнесы
        row, col = 0, 0
        max_cols = 2
        
        for business_data in self.business_manager.business_data:
            # Пропускаем уже купленные бизнесы
            if any(b['id'] == business_data['id'] for b in self.business_manager.my_businesses):
                continue
                
            card = self.create_business_card(business_data, is_owned=False)
            self.catalog_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
    def filter_my_businesses(self, filter_type):
        """Фильтрация моих бизнесов"""
        self.current_filter = filter_type
        # В реальной реализации здесь была бы фильтрация
        # Пока просто перезагружаем, если layout инициализирован
        if self.my_businesses_layout is not None:
            self.load_my_businesses()
        
    def filter_catalog(self, filter_type):
        """Фильтрация каталога"""
        self.current_filter = filter_type
        # В реальной реализации здесь была бы фильтрация
        # Пока просто перезагружаем, если layout инициализирован
        if self.catalog_layout is not None:
            self.load_catalog()
        
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
        # Расчет стоимости (используем базовую стоимость из данных)
        cost = business_data.get('price', business_data.get('income_per_hour', 0) * 100)
        
        # Проверяем, есть ли у игрока достаточно денег
        # В реальной реализации здесь должна быть проверка баланса игрока
        player_balance = 1000000000000  # Заглушка - должен браться из игровой экономики
        
        if player_balance >= cost:
            if self.business_manager.buy_business(business_data):
                # В реальной реализации здесь должно списываться с баланса
                QMessageBox.information(self, "Покупка", 
                                    f"Бизнес '{business_data['name']}' успешно куплен за ${cost:,}!")
                self.load_catalog()
                self.load_my_businesses()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось купить бизнес")
        else:
            QMessageBox.warning(self, "Недостаточно средств", 
                            f"Для покупки нужно ${cost:,}, а у вас только ${player_balance:,}")
        
    def keyPressEvent(self, a0: QKeyEvent | None):
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
        
    def keyPressEvent(self, a0: QKeyEvent | None):
        if a0 is not None and  a0.key() == Qt.Key.Key_Escape:
            self.exitToMenu.emit()
        else:
            super().keyPressEvent(a0)

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
        layout.setVerticalSpacing(20)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Общий стиль для всех ComboBox с настройкой ширины
        combo_style = f"""
            QComboBox {{
                background-color: {DARK_BG.name()};
                color: {TEXT_PRIMARY.name()};
                border: 1px solid {PURPLE_PRIMARY.name()};
                border-radius: 8px;
                padding: 10px;
                margin-top: 9px;
                min-width: 400px;           /* Минимальная ширина в неактивном состоянии */
                max-width: 450px;           /* Максимальная ширина в неактивном состоянии */
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
                min-width: 400px;           /* Минимальная ширина выпадающего списка */
                max-width: 450px;           /* Максимальная ширина выпадающего списка */
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
        
        # Тема
        theme_combo = QComboBox()
        theme_combo.addItems(self.settings_manager.show_themes())
        theme_combo.setStyleSheet(combo_style)
        # Можно также установить фиксированную ширину для конкретного комбобокса
        theme_combo.setFixedWidth(250)  # Ширина в неактивном состоянии
        layout.addRow("🎨 Тема:", theme_combo)
        
        # Разрешение
        resolution_combo = QComboBox()
        resolutions = [f"{w}x{h}" for w, h in self.settings_manager.show_window_sizes()]
        resolution_combo.addItems(resolutions)
        resolution_combo.setStyleSheet(combo_style)
        resolution_combo.setFixedWidth(250)
        layout.addRow("🖥️ Разрешение:", resolution_combo)
        
        # FPS
        fps_combo = QComboBox()
        fps_combo.addItems([f"{fps} FPS" for fps in self.settings_manager.show_fps()])
        fps_combo.setStyleSheet(combo_style)
        fps_combo.setFixedWidth(250)
        layout.addRow("🎯 FPS:", fps_combo)
        
        # Язык
        language_combo = QComboBox()
        language_combo.addItems(self.settings_manager.show_langs())
        language_combo.setStyleSheet(combo_style)
        language_combo.setFixedWidth(250)
        layout.addRow("🌐 Язык:", language_combo)
        
        # Качество графики
        quality_combo = QComboBox()
        quality_combo.addItems(["Низкое", "Среднее", "Высокое", "Ультра"])
        quality_combo.setStyleSheet(combo_style)
        quality_combo.setFixedWidth(250)
        layout.addRow("🎨 Качество графики:", quality_combo)
        
        # Громкость - используем обычную строку формы
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(80)
        
        # НАСТРОЙКИ РАЗМЕРА
        volume_slider.setFixedWidth(400)  # Ширина ползунка
        volume_slider.setMinimumHeight(40)  # Минимальная высота
        
        # Стиль ползунка
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
        volume_value = QLabel("80%")
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
        slider_layout.addStretch()  # Чтобы прижалось к левому краю
        
        # Обновление значения
        volume_slider.valueChanged.connect(lambda v: volume_value.setText(f"{v}%"))
        
        # Добавляем в форму - ползунок будет выровнен с другими элементами
        layout.addRow("🔊 Громкость:", slider_container)
        
        widget.setLayout(layout)
        return widget
        
    def apply_settings(self):
        QMessageBox.information(self, "Настройки", "Настройки успешно применены!")
        
    def reset_settings(self):
        reply = QMessageBox.question(self, "Сброс настроек", 
                                   "Вы уверены, что хотите сбросить все настройки?")
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Настройки", "Настройки сброшены!")
            
    def keyPressEvent(self, a0: QKeyEvent | None):
        if a0 is not None and a0.key() == Qt.Key.Key_Escape:
            self.exitToMenu.emit()
        else:
            super().keyPressEvent(a0)

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
        
    def keyPressEvent(self, a0: QKeyEvent | None):
        """Глобальная обработка клавиш"""
        if a0 is not None and a0.key() == Qt.Key.Key_Escape:
            # Если мы не в главном меню, возвращаемся в него
            current_index = self.content_stack.currentIndex()
            if current_index != 1:  # Не главное меню
                self.show_main_menu()
        else:
            super().keyPressEvent(a0)

def main():
    def qt_debug_handler(msg_type, context, message):
        if "QLayout::addChildLayout" in message:
            import traceback
            print("⚠️ Ошибка QLayout:", message)
            traceback.print_stack(limit=6)
        else:
            print(message)

    qInstallMessageHandler(qt_debug_handler)
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