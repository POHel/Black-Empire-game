import sqlite3
import json
import pygame
import sys
import math
import random
import time
from pygame import gfxdraw
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum
from coreLogic import Settings, ExportDB


pygame.init()

# Color palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BG = (5, 5, 20)
PANEL_BG = (15, 15, 40)
DEEP_PURPLE = (55, 0, 110)
PURPLE_PRIMARY = (120, 20, 220)
PURPLE_ACCENT = (160, 60, 255)
LIGHT_PURPLE = (180, 120, 240)
GLOW_OUTER = (140, 80, 220, 5)
BAR_BASE = (90, 30, 180)
BAR_HIGHLIGHT = (140, 80, 230)
TEXT_PRIMARY = (245, 245, 255)
TEXT_SECONDARY = (180, 180, 200)
TEXT_TERTIARY = (140, 140, 160)

# Новые константы для закруглений
PANEL_BORDER_RADIUS = 35
BUTTON_BORDER_RADIUS = 25
BAR_BORDER_RADIUS = 12
SETTINGS_PANEL_RADIUS = 25

class ScreenState(Enum):
    LOADING = 0
    MENU = 1
    SETTINGS = 2
    INVESTMENTS = 3
    CLICKER = 4
    SHOP_SELECTION = 5
    SHOP = 6
    SHOP_CATEGORY = 7
    BLACK_MARKET = 8
    BLACK_MARKET_CATEGORY = 9
    BUSINESSES = 10  # Новое состояние для бизнесов
    BUSINESS_CATEGORY = 11
    PROFILE = 12

class GameConfig:
    def __init__(self):
        self.screen_width = 900
        self.screen_height = 700
        self.button_height = 500
        self.font_sizes = {
            "small": 14,
            "medium": 18,
            "large": 24,
            "xlarge": 32,
            "title": 36
        }
        self.animations = {
            "click_effect_particles": 12,
            "click_effect_coins": 8,
            "float_text_duration": 1000,
            "particle_duration": 700
        }

class Particle:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], 
                 size: int, velocity: Tuple[float, float], lifetime: int):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alive = True
    
    def update(self, dt: float):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        self.alive = self.lifetime > 0
    
    def draw(self, surface: pygame.Surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        # Создаем поверхность для частицы с альфа-каналом
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, (self.color, alpha), (self.size, self.size), self.size)
        
        # Рисуем частицу на основной поверхности
        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))

# Всплывающий текст
class FloatingText:
    def __init__(self, x: float, y: float, text: str, color: Tuple[int, int, int], 
                 size: int, duration: int = 1000):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.size = size
        self.duration = duration
        self.max_duration = duration
        self.alive = True
    
    def update(self, dt: float):
        self.y -= 0.1 * dt  # Медленно поднимаемся вверх
        self.duration -= dt
        self.alive = self.duration > 0
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        alpha = int(255 * (self.duration / self.max_duration))
        
        # Создаем текст с альфа-каналом
        text_surface = font.render(self.text, True, self.color)
        text_surface.set_alpha(alpha)
        
        # Рисуем текст
        surface.blit(text_surface, (int(self.x - text_surface.get_width() / 2), 
                                   int(self.y - text_surface.get_height() / 2)))

class ClickerMenu:
    """Исправленная версия кликера с использованием общей палитры цветов."""

    def __init__(self):
        self.config = GameConfig()
        self.screen = pygame.display.set_mode((self.config.screen_width, self.config.screen_height), 
                                             pygame.RESIZABLE)
        pygame.display.set_caption("Корпоративный Кликер")
        
        # Загрузка шрифтов
        self.fonts = self.load_fonts()
        
        # Состояние игры
        self.money = 0
        self.per_click = 1
        self.total_clicks = 0
        self.running = True
        
        # Визуальные эффекты
        self.particles: List[Particle] = []
        self.floating_texts: List[FloatingText] = []
        
        # Кэшированные поверхности для оптимизации
        self.cached_surfaces: Dict[str, pygame.Surface] = {}
        
        # Время для плавной анимации
        self.clock = pygame.time.Clock()
        self.last_time = pygame.time.get_ticks()

    def load_fonts(self) -> Dict[str, pygame.font.Font]:
        fonts = {}
        try:
            # Попытка загрузить системный шрифт
            font_name = pygame.font.get_default_font()
            for size_name, size in self.config.font_sizes.items():
                fonts[size_name] = pygame.font.SysFont(font_name, size)
        except:
            # Fallback на стандартный шрифт
            for size_name, size in self.config.font_sizes.items():
                fonts[size_name] = pygame.font.Font(None, size)
            
        return fonts

    def format_money(self, amount: int) -> str:
        """Форматирует денежную сумму для отображения"""
        if amount >= 1000000:
            return f"${amount/1000000:.1f}M"
        elif amount >= 1000:
            return f"${amount/1000:.1f}K"
        return f"${amount}"

    def create_gradient_background(self, width: int, height: int) -> pygame.Surface:
        """Создает градиентный фон с эффектами как в оригинале"""
        surface = pygame.Surface((width, height))
        surface.fill(COLORS[DARK_BG])
        
        # Рисуем радиальные градиенты (упрощенная версия)
        for i in range(2):
            center_x = width * 0.1 if i == 0 else width * 0.9
            center_y = height * 0.2 if i == 0 else height * 0.8
            radius = min(width, height) * 0.3
            
            # Упрощенный градиент - рисуем полупрозрачные круги
            for r in range(int(radius), 0, -10):
                alpha = max(0, 10 - int(r / (radius / 10)))
                if alpha > 0:
                    color = (*COLORS[BLACK], alpha) if i == 0 else (*COLORS[BLACK], alpha)
                    gradient_surface = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                    pygame.draw.circle(gradient_surface, color, (r, r), r)
                    surface.blit(gradient_surface, (int(center_x - r), int(center_y - r)))
        
        return surface



    def initialize_ui(self):
        """Инициализация UI кликера."""
        self.nav_buttons = []
        nav_options = [
            ("Кликер", lambda: self.game.play_game(), True),  # Активная кнопка
            ("Магазины", lambda: self.game.open_shop_selection(), False),
            ("Инвестиции", lambda: self.game.open_investments(), False),
            ("Бизнесы", lambda: self.game.open_businesses(), False),
            ("Профиль", lambda: self.game.open_profile(), False)
        ]


        button_width, button_height = 200, 60
        button_x, button_y_start = 50, 150

        for i, (text, action, is_active) in enumerate(nav_options):
            rect = pygame.Rect(button_x, button_y_start + i * 70, button_width, button_height)
            self.nav_buttons.append(NavButton(rect, text, action, is_active))

        # Кнопка клика
        self.click_button_rect = pygame.Rect(700, 400, 300, 100)

    def draw_button(self, surface: pygame.Surface, rect: pygame.Rect, text: str, 
                   subtitle: str, is_pressed: bool = False, is_hovered: bool = False):
        """Рисует кнопку инвестирования"""
        button_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        
        # Основной цвет кнопки
        if is_pressed:
            base_color = (*COLORS[BLACK], 180)
        elif is_hovered:
            base_color = (*COLORS[BLACK], 200)
        else:
            base_color = (*COLORS[BLACK], 150)
        
        pygame.draw.rect(button_surface, base_color, (0, 0, rect.width, rect.height), border_radius=40)
        
        # Внутренняя тень
        inner_shadow = pygame.Surface((rect.width - 20, rect.height - 20), pygame.SRCALPHA)
        pygame.draw.rect(inner_shadow, (0, 0, 0, 100), 
                        (0, 0, inner_shadow.get_width(), inner_shadow.get_height()), 
                        border_radius=30)
        button_surface.blit(inner_shadow, (10, 10))
        
        # Иконка воспроизведения
        icon_size = 80
        icon_x = rect.width // 2 - icon_size // 2
        icon_y = rect.height // 3 - icon_size // 2
        
        pygame.draw.rect(button_surface, (*COLORS[BLACK], 220), 
                        (icon_x, icon_y, icon_size, icon_size), border_radius=20)
        
        # Треугольник воспроизведения
        triangle_points = [
            (icon_x + icon_size // 3, icon_y + icon_size // 4),
            (icon_x + icon_size // 3, icon_y + 3 * icon_size // 4),
            (icon_x + 2 * icon_size // 3, icon_y + icon_size // 2)
        ]
        pygame.draw.polygon(button_surface, COLORS[WHITE], triangle_points)
        
        # Текст кнопки
        title_font = self.fonts["xlarge"]
        subtitle_font = self.fonts["medium"]
        
        title_text = title_font.render(text, True, COLORS[WHITE])
        subtitle_text = subtitle_font.render(subtitle, True, COLORS[DEEP_PURPLE])
        
        button_surface.blit(title_text, 
                          (rect.width // 2 - title_text.get_width() // 2, 
                           rect.height // 2 + 30))
        button_surface.blit(subtitle_text, 
                          (rect.width // 2 - subtitle_text.get_width() // 2, 
                           rect.height // 2 + 80))
        
        # Эффект пульсации (если не нажата)
        if not is_pressed and not is_hovered:
            pulse_alpha = int(100 + 50 * math.sin(pygame.time.get_ticks() / 500))
            pulse_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(pulse_surface, (*COLORS[BLACK], pulse_alpha), 
                            (0, 0, rect.width, rect.height), border_radius=40, width=3)
            button_surface.blit(pulse_surface, (0, 0))
        
        surface.blit(button_surface, rect)

    def draw_panel(self, surface: pygame.Surface, rect: pygame.Rect):
        """Рисует панель с закругленными углами и эффектом стекла"""
        # Эффект тени
        shadow_surface = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 100), 
                        (10, 10, rect.width, rect.height), 
                        border_radius=24)
        surface.blit(shadow_surface, (rect.x - 10, rect.y - 10))
        
        # Основная панель
        panel_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (*COLORS[PANEL_BG], 200), 
                        (0, 0, rect.width, rect.height), 
                        border_radius=24)
        
        # Эффект звездного поля (упрощенный)
        for _ in range(50):
            x = random.randint(0, rect.width)
            y = random.randint(0, rect.height)
            size = random.randint(1, 2)
            brightness = random.randint(5, 15)
            pygame.draw.circle(panel_surface, (255, 255, 255, brightness), (x, y), size)
        
        surface.blit(panel_surface, rect)

    def create_click_effects(self, x: float, y: float):
        """Создает визуальные эффекты при клике"""
        # Частицы
        for _ in range(self.config.animations["click_effect_particles"]):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            color = random.choice([COLORS[BLACK], COLORS[BLACK], (203, 168, 255)])
            particle = Particle(x, y, color, random.randint(3, 6), velocity, 
                              self.config.animations["particle_duration"])
            self.particles.append(particle)
        
        # "Монеты"
        for _ in range(self.config.animations["click_effect_coins"]):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 6)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            particle = Particle(x, y, COLORS[DEEP_PURPLE], random.randint(4, 8), velocity, 
                              self.config.animations["particle_duration"])
            self.particles.append(particle)
        
        # Всплывающий текст
        text = f"+{self.format_money(self.per_click)}"
        floating_text = FloatingText(x, y - 50, text, (189, 168, 255), 
                                   self.config.font_sizes["large"])
        self.floating_texts.append(floating_text)

        def draw(self):
        # Фон
        bg_key = f"{DARK_BG}_{self.config.screen_width}_{self.config.screen_height}"
        if bg_key not in self.cached_surfaces:
            self.cached_surfaces[bg_key] = self.create_gradient_background(
                self.config.screen_width, self.config.screen_height
            )
        self.screen.blit(self.cached_surfaces[bg_key], (0, 0))
        
        # Основная панель
        panel_rect = pygame.Rect(50, 50, self.config.screen_width - 100, self.config.screen_height - 100)
        self.draw_panel(self.screen, panel_rect)
        
        # Заголовок
        title_font = self.fonts["title"]
        brand_font = self.fonts["medium"]
        
        title_text = title_font.render("Корпоративный Кликер", True, COLORS[WHITE])
        brand_text = brand_font.render("Black Empire", True, COLORS[BLACK])
        
        self.screen.blit(brand_text, (self.config.screen_width // 2 - brand_text.get_width() // 2, 80))
        self.screen.blit(title_text, (self.config.screen_width // 2 - title_text.get_width() // 2, 110))
        
        # Статистика
        stats_y = 180
        stat_font = self.fonts["large"]
        label_font = self.fonts["small"]
        
        stats = [
            (self.format_money(self.money), "Капитал"),
            (self.format_money(self.per_click), "Доход за клик"),
            (str(self.total_clicks), "Всего кликов")
        ]
        
        stat_width = (self.config.screen_width - 200) // 3
        for i, (value, label) in enumerate(stats):
            x = 100 + i * stat_width
            
            value_text = stat_font.render(value, True, COLORS[WHITE])
            label_text = label_font.render(label, True, COLORS[DEEP_PURPLE])
            
            self.screen.blit(value_text, (x + stat_width // 2 - value_text.get_width() // 2, stats_y))
            self.screen.blit(label_text, (x + stat_width // 2 - label_text.get_width() // 2, stats_y + 40))
        
        # Разделительная линия
        pygame.draw.line(self.screen, COLORS[PANEL_BG], 
                        (100, stats_y + 80), 
                        (self.config.screen_width - 100, stats_y + 80), 2)
        
        # Кнопка инвестирования
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(
            self.config.screen_width // 2 - 200,
            self.config.screen_height // 2 - self.config.button_height // 2 + 100,
            400, self.config.button_height
        )
        is_button_hovered = button_rect.collidepoint(mouse_pos)
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        self.draw_button(self.screen, button_rect, "Инвестировать", 
                        f"+{self.format_money(self.per_click)} за клик",
                        is_pressed=mouse_pressed and is_button_hovered,
                        is_hovered=is_button_hovered)
        
        # Инструкция
        instruction_font = self.fonts["small"]
        instruction_text = instruction_font.render(
            "Нажимайте на кнопку или используйте пробел для инвестирования", 
            True, COLORS[DEEP_PURPLE]
        )
        self.screen.blit(instruction_text, 
                        (self.config.screen_width // 2 - instruction_text.get_width() // 2, 
                         self.config.screen_height - 80))
        
        
        # Отрисовываем всплывающий текст
        for text in self.floating_texts:
            text.draw(self.screen, self.fonts["large"])
        
        pygame.display.flip()

    def handle_event(self):
        """Обрабатывает события игры"""
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(
            self.config.screen_width // 2 - 200,
            self.config.screen_height // 2 - self.config.button_height // 2 + 100,
            400, self.config.button_height
        )
        is_button_hovered = button_rect.collidepoint(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.VIDEORESIZE:
                # Обработка изменения размера окна
                self.config.screen_width, self.config.screen_height = event.size
                self.screen = pygame.display.set_mode((self.config.screen_width, self.config.screen_height), 
                                                     pygame.RESIZABLE)
                # Очищаем кэш поверхностей при изменении размера
                self.cached_surfaces.clear()
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if is_button_hovered:
                    self.handle_click()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.handle_click()

    def handle_click(self):
        """Обрабатывает клик по кнопке"""
        self.money += self.per_click
        self.total_clicks += 1
        
        # Создаем эффекты в центре кнопки
        center_x = self.config.screen_width // 2
        center_y = self.config.screen_height // 2 + 100
        self.create_click_effects(center_x, center_y)
        
        # Периодическое увеличение дохода
        if self.total_clicks % 50 == 0:
            self.per_click += 1
            # Эффект улучшения
            upgrade_text = FloatingText(center_x, center_y - 100, "Доход увеличен!", 
                                      (122, 255, 122), self.config.font_sizes["medium"])
            self.floating_texts.append(upgrade_text)

    def update(self, dt: float):
        """Обновляет состояние игры"""
        # Обновляем частицы
        self.particles = [p for p in self.particles if p.alive]
        for particle in self.particles:
            particle.update(dt)
        
        # Обновляем всплывающий текст
        self.floating_texts = [t for t in self.floating_texts if t.alive]
        for text in self.floating_texts:
            text.update(dt)

class Game:
    """Основной класс игры."""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Black Empire')
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = ScreenState.LOADING
        self.settings_manager = Settings()

        self.shop_system = ShopSystem(self)
        self.shop_selection_menu = ShopSelectionMenu(self)
        self.light_shop_menu = LightShopMenu(self)
        self.light_category_products_menu = LightCategoryProductsMenu(self)
        self.black_market_category_products_menu = BlackMarketCategoryProductsMenu(self)
        self.black_market_menu = BlackMarketMenu(self)
        self.business_menu = BusinessMenu(self)
        self.profile_menu = ProfileMenu(self)
        
        
        # Получаем доступные опции из config.json
        self.theme_options = self.settings_manager.show_themes()
        self.resolution_options = [f"{size[0]}x{size[1]}" for size in self.settings_manager.show_window_sizes()]
        self.fps_options = [f"{fps} fps" for fps in self.settings_manager.show_fps()]
        self.language_options = self.settings_manager.show_langs()
        self.quality_options = ["Низкое", "Среднее", "Высокое"]
        
        # Получаем текущие настройки из config.json и преобразуем в нужный формат
        current_resolution = self.settings_manager.get_current_window_size()
        resolution_str = f"{current_resolution[0]}x{current_resolution[1]}"
        fps_str = f"{self.settings_manager.get_current_fps()} fps"
        
        self.current_settings = {
            "theme": self.settings_manager.get_current_theme(),
            "resolution": resolution_str,  # Строка "widthxheight"
            "fps": fps_str,  # Строка "fps fps"
            "language": self.settings_manager.get_current_lang(),
            "quality": "Среднее"
        }
        
        self.font_manager = FontManager()
        self.icon_renderer = IconRenderer()
        self.clicker_menu = ClickerMenu(self)
        self.investment_menu = InvestmentMenu(self)
        self.loading_screen = LoadingScreen(self.screen, self.font_manager)
        
        self.stars = []
        self.background_cache = None
        self.panel_cache = {}
        self.last_time = time.time()
        
        # Инициализируем UI
        self.initialize_ui()

        # Создаем звезды
        for _ in range(100):
            self.stars.append(Star(
                x=random.uniform(0, SCREEN_WIDTH),
                y=random.uniform(0, SCREEN_HEIGHT),
                z=random.uniform(0, 1),
                size=random.uniform(0.5, 2.5),
                speed=random.uniform(20, 100),
                pulse_speed=random.uniform(0.001, 0.005),
                pulse_offset=random.uniform(0, math.pi * 2),
                alpha=random.randint(50, 255),
                alpha_change=random.uniform(-20, 20)
            ))
    def apply_settings(self):
        try:
            # ДОБАВЛЯЕМ проверку существования dropdown атрибутов:
            if not hasattr(self, 'theme_dropdown') or not hasattr(self, 'resolution_dropdown'):
                print("Dropdown элементы еще не инициализированы")
                return
                
            # Получаем выбранные значения из dropdown
            selected_theme = self.theme_dropdown.options[self.theme_dropdown.selected_index]
            selected_resolution = self.resolution_dropdown.options[self.resolution_dropdown.selected_index]
            selected_fps = self.fps_dropdown.options[self.fps_dropdown.selected_index]
            selected_language = self.language_dropdown.options[self.language_dropdown.selected_index]
            selected_quality = self.quality_dropdown.options[self.quality_dropdown.selected_index]
                
            # Применяем настройки через Settings класс
            self.settings_manager.set_current_theme(selected_theme)
            
            # Парсим разрешение (формат "1280x720" -> [1280, 720])
            width, height = map(int, selected_resolution.split('x'))
            self.current_settings["resolution"] = (width, height)  # кортеж
            
            # Парсим FPS (формат "60 fps" -> 60)
            fps_value = int(selected_fps.split(' ')[0])
            self.settings_manager.set_current_fps(fps_value)
            
            self.settings_manager.set_current_lang(selected_language)
            
            # Обновляем текущие настройки
            self.current_settings = {
                "theme": selected_theme,
                "resolution": selected_resolution,  # ← Сохраняем как строку
                "fps": selected_fps,
                "language": selected_language,
                "quality": selected_quality
            }
            
            print("Настройки успешно применены и сохранены:")
            for key, value in self.current_settings.items():
                print(f"  {key}: {value}")
                
            # Применяем настройки в реальном времени
            self.apply_settings_in_realtime()
            
        except Exception as e:
            print(f"Ошибка при применении настроек: {e}")
    
    def apply_settings_in_realtime(self):
        """Применяет настройки в реальном времени."""
        # Применяем FPS
        fps_value = int(self.current_settings["fps"].split(' ')[0])
        pygame.display.set_caption(f'Black Empire - {fps_value} FPS')
        
        # Здесь можно добавить смену разрешения (требует пересоздания окна)
        # width, height = map(int, self.current_settings["resolution"].split('x'))
        # self.screen = pygame.display.set_mode((width, height))
        
        print("Настройки применены в реальном времени")

    
    def update_navigation_state(self, active_button_text):
        """Обновляет состояние кнопок навигации во всех меню"""
        menus = [
            getattr(self, 'clicker_menu', None),
            getattr(self, 'investment_menu', None),
            getattr(self, 'shop_selection_menu', None),
            getattr(self, 'light_shop_menu', None),
            getattr(self, 'black_market_menu', None),
            getattr(self, 'business_menu', None)  # ДОБАВИТЬ бизнес-меню
        ]
        
        for menu in menus:
            if menu is not None:
                # Пытаемся получить кнопки из разных возможных атрибутов
                buttons = None
                for attr_name in ['nav_buttons', 'buttons', 'navigation_buttons']:
                    if hasattr(menu, attr_name):
                        buttons = getattr(menu, attr_name)
                        break
                
                if buttons:
                    for button in buttons:
                        if (hasattr(button, 'text') and hasattr(button, 'is_active')):
                            button.is_active = (button.text == active_button_text)

    def play_game(self):
            """Переход в игровой режим (кликер)."""
            self.state = ScreenState.CLICKER
            self.update_navigation_state("Кликер")
            print("Запуск игры...")

    def open_investments(self):
            """Открывает меню инвестиций."""
            self.state = ScreenState.INVESTMENTS
            self.update_navigation_state("Инвестиции")
            print("Открытие инвестиций...")

    def open_shop_selection(self):
            """Открывает выбор магазина"""
            self.state = ScreenState.SHOP_SELECTION
            self.update_navigation_state("Магазины")
            print("Открытие выбора магазина...")

    def open_light_shop(self):
            """Открывает светлый магазин"""
            self.state = ScreenState.SHOP
            self.update_navigation_state("Магазины")
            print("Открытие светлого магазина...")

    def open_black_market(self):
            """Открывает черный рынок"""
            self.state = ScreenState.BLACK_MARKET
            self.update_navigation_state("Магазины")
            print("Открытие черного рынка...")

    def open_businesses(self):
        """Открывает меню бизнесов."""
        self.state = ScreenState.BUSINESSES
        self.update_navigation_state("Бизнесы")
        print("Открытие бизнесов...")

    def open_profile(self):
        """Открывает меню профиля."""
        self.state = ScreenState.PROFILE
        self.update_navigation_state("Профиль")
        print("Открытие профиля...")

    def open_settings(self):
        """Открывает меню настроек."""
        self.state = ScreenState.SETTINGS
        print("Открытие настроек...")

    def exit_game(self):
        """Выход из игры."""
        self.running = False
        print("Выход из игры...")

    def back_to_menu(self):
        """Возврат в главное меню."""
        self.state = ScreenState.MENU
        print("Возврат в главное меню...")
        
    def initialize_ui(self):
        self.texts = {
            'bus': "SKATT", 'title': "Black Empire",
            'subtitle1': "Построй империю от старта до", 'subtitle2': "корпорации",
            'desc': [
                "Стартуй маленьким бизнесом: закупи сырье,",
                "управляй активами, инвестируй в улучшения",
                "своего бизнеса. Пройди — это вызов —",
                "старте."
            ],
            'version': "v" + GAME_VERSION
        }
        
        # Панели главного меню
        self.left_panel_rect = pygame.Rect(80, 120, 580, 680)
        self.right_panel_rect = pygame.Rect(740, 120, 580, 680)
        
        button_width, button_height = 460, 65
        button_y_start = self.right_panel_rect.y + 200
        
        # ОБНОВЛЕННЫЕ кнопки с изображениями
        self.buttons = [
            Button(
                pygame.Rect(self.right_panel_rect.x + 60, button_y_start, button_width, button_height),
                "Играть", 
                lambda surface, icon_x, icon_y, size=30: self.icon_renderer.draw_play_image_icon(surface, icon_x, icon_y, size), 
                self.play_game
            ),
            Button(
                pygame.Rect(self.right_panel_rect.x + 60, button_y_start + 100, button_width, button_height),
                "Настройки", 
                lambda surface, icon_x, icon_y, size=30: self.icon_renderer.draw_settings_image_icon(surface, icon_x, icon_y, size), 
                self.open_settings
            ),
            Button(
                pygame.Rect(self.right_panel_rect.x + 60, button_y_start + 200, button_width, button_height),
                "Выход", 
                lambda surface, icon_x, icon_y, size=30: self.icon_renderer.draw_exit_icon(surface, icon_x, icon_y, size), 
                self.exit_game
            )
        ]
        
        # Панель настроек
        self.settings_panel_rect = pygame.Rect(200, 120, 1000, 600)
        
        # Кнопка "Назад" в настройках
        self.back_button = Button(
            pygame.Rect(50, 50, 200, 60),
            "Назад",
            lambda surface, icon_x, icon_y, size=25: self.icon_renderer.draw_back_icon(surface, icon_x, icon_y, size),
            self.back_to_menu,
            icon_size=25
        )

        # Новая кнопка "Применить"
        self.apply_button = Button(
            pygame.Rect(270, 50, 250, 60),  # Справа от кнопки "Назад"
            "Применить",
            lambda surface, icon_x, icon_y, size=25: self.icon_renderer.draw_apply_icon(surface, icon_x, icon_y, size),
            self.apply_settings,
            icon_size=25
        )
        
        # Dropdown для настроек - создаем здесь, после инициализации options
        dropdown_theme_x = SCREEN_WIDTH//2 - 350 + 70
        dropdown_resolution_x = SCREEN_WIDTH//2 + 30 + 135
        dropdown_fps_x = SCREEN_WIDTH//2 - 350 + 60
        dropdown_language_x = SCREEN_WIDTH//2 + 30 + 70
        dropdown_quality_x = SCREEN_WIDTH//2 - 350 + 107


        dropdown_width, dropdown_height = 200, 50

        self.theme_dropdown = Dropdown(
            pygame.Rect(dropdown_theme_x, 230, dropdown_width, dropdown_height),
            self.theme_options,
            self.theme_options.index(self.current_settings["theme"])
        )

        self.resolution_dropdown = Dropdown(
            pygame.Rect(dropdown_resolution_x, 230, dropdown_width, dropdown_height),
            self.resolution_options,
            self.resolution_options.index(self.current_settings["resolution"])
        )

        self.fps_dropdown = Dropdown(
            pygame.Rect(dropdown_fps_x, 410, dropdown_width, dropdown_height),
            self.fps_options,
            self.fps_options.index(self.current_settings["fps"])
        )

        self.language_dropdown = Dropdown(
            pygame.Rect(dropdown_language_x, 410, dropdown_width, dropdown_height),
            self.language_options,
            self.language_options.index(self.current_settings["language"])
        )
        self.quality_dropdown = Dropdown(
            pygame.Rect(dropdown_quality_x, 590, dropdown_width, dropdown_height),
            self.quality_options,
            self.quality_options.index(self.current_settings["quality"])
        )
        
        self.dropdowns = [
            self.theme_dropdown,
            self.resolution_dropdown,
            self.fps_dropdown,
            self.language_dropdown,
            self.quality_dropdown
        ]

    def handle_shop_events(self, event, mouse_pos):
        """Обработка событий магазинов с обработкой исключений"""
        try:
            if self.state == ScreenState.SHOP_SELECTION:
                if self.shop_selection_menu.handle_event(event):
                    return True
            
            elif self.state == ScreenState.SHOP:
                if self.light_shop_menu.handle_event(event):
                    return True
            
            elif self.state == ScreenState.SHOP_CATEGORY:
                if self.light_category_products_menu.handle_event(event):
                    return True
            
            elif self.state == ScreenState.BLACK_MARKET:
                if self.black_market_menu.handle_event(event):
                    return True
                    
            elif self.state == ScreenState.BLACK_MARKET_CATEGORY:
                if self.black_market_category_products_menu.handle_event(event):
                    return True
                    
        except Exception as e:
            print(f"Ошибка в обработке событий магазина: {e}")
            # При ошибке возвращаемся в главное меню
            self.state = ScreenState.CLICKER
            return True
            
        return False
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == ScreenState.MENU:
                        self.running = False
                    elif self.state in [ScreenState.SETTINGS, ScreenState.CLICKER, ScreenState.INVESTMENTS, 
                                    ScreenState.SHOP_SELECTION, ScreenState.SHOP, ScreenState.SHOP_CATEGORY,
                                    ScreenState.BLACK_MARKET, ScreenState.BLACK_MARKET_CATEGORY,
                                    ScreenState.BUSINESSES]:  # ДОБАВИТЬ BUSINESSES
                        self.back_to_menu()
                    else:
                        self.running = False
            
            # Флаг для отслеживания обработки dropdown событий
            dropdown_handled = False
            
            # Сначала обрабатываем специфичные для состояния события
            if self.state == ScreenState.CLICKER:
                if self.clicker_menu.handle_event(event):
                    continue
                    
            elif self.state == ScreenState.INVESTMENTS:
                if self.investment_menu.handle_event(event):
                    continue
                    
            elif self.state in [ScreenState.SHOP_SELECTION, ScreenState.SHOP, ScreenState.SHOP_CATEGORY, 
                            ScreenState.BLACK_MARKET, ScreenState.BLACK_MARKET_CATEGORY]:
                if self.handle_shop_events(event, mouse_pos):
                    continue
            
            # ДОБАВИТЬ обработку для BUSINESSES
            elif self.state == ScreenState.BUSINESSES:
                if self.business_menu.handle_event(event):
                    continue
            elif self.state == ScreenState.PROFILE:
                if self.profile_menu.handle_event(event):
                    continue
            
            # Затем обрабатываем dropdown события (только для настроек)
            if self.state == ScreenState.SETTINGS:
                # Обрабатываем dropdown события
                for dropdown in self.dropdowns:
                    if dropdown.handle_event(event):
                        dropdown_handled = True
                        break
                
                if dropdown_handled:
                    continue
            
            # Обработка главного меню
            if self.state == ScreenState.MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in self.buttons:
                        if button.is_hovered(mouse_pos):
                            button.click()
                elif event.type == pygame.MOUSEMOTION:
                    for button in self.buttons:
                        button.hovered = button.is_hovered(mouse_pos)
            
            # Обработка настроек
            elif self.state == ScreenState.SETTINGS:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_button.is_hovered(mouse_pos):
                        self.back_button.click()
                    elif self.apply_button.is_hovered(mouse_pos):
                        self.apply_button.click()
                    else:
                        # Логика закрытия dropdown
                        click_on_dropdown = False
                        for dropdown in self.dropdowns:
                            if dropdown.rect.collidepoint(mouse_pos):
                                click_on_dropdown = True
                                break
                        
                        if not click_on_dropdown:
                            Dropdown.close_all_dropdowns()
                
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    self.back_button.hovered = self.back_button.is_hovered(mouse_pos)
                    self.apply_button.hovered = self.apply_button.is_hovered(mouse_pos)
        
    def run(self):
        while self.running:
            current_time = pygame.time.get_ticks()
            dt = current_time - self.last_time
            self.last_time = current_time
            
            self.ClickerMenu.handle_events()
            self.ClickerMenu.update(dt)
            self.ClickerMenu.draw()
            
        """Основной игровой цикл."""
        while self.running:
            current_time = time.time()
            dt = current_time - self.last_time
            self.last_time = current_time
            
            self.handle_events()
            
            # Обновление состояния
            if self.state == ScreenState.LOADING:
                if self.loading_screen.update():
                    self.state = ScreenState.MENU
            else:
                # Обновление звезд
                for star in self.stars:
                    star.update(dt)
                
                # Обновление кнопок
                for button in self.buttons:
                    button.update(dt)
                self.back_button.update(dt)
                self.apply_button.update(dt)
            
            # Отрисовка
            self.screen.fill(DARK_BG)
            
            # Рисуем звезды
            for star in self.stars:
                x, y = star.get_screen_pos()
                size = star.get_current_size()
                alpha_color = (*LIGHT_PURPLE[:3], star.alpha)
                pygame.draw.circle(self.screen, alpha_color, (int(x), int(y)), int(size))
            
            if self.state == ScreenState.LOADING:
                self.loading_screen.draw()
            elif self.state == ScreenState.MENU:
                self.draw_main_menu()
            elif self.state == ScreenState.SETTINGS:
                self.draw_settings()
            elif self.state == ScreenState.INVESTMENTS:
                self.draw_investments()
            elif self.state == ScreenState.CLICKER:
                self.draw_clicker()
            elif self.state == ScreenState.SHOP_SELECTION:
                self.shop_selection_menu.draw(self.screen)
            elif self.state == ScreenState.SHOP:
                self.light_shop_menu.draw(self.screen)
            elif self.state == ScreenState.SHOP_CATEGORY:
                self.light_category_products_menu.draw(self.screen)
            elif self.state == ScreenState.BLACK_MARKET:
                self.black_market_menu.draw(self.screen)
            elif self.state == ScreenState.BLACK_MARKET_CATEGORY:
                self.black_market_category_products_menu.draw(self.screen)
            elif self.state == ScreenState.BUSINESSES:
                self.business_menu.draw(self.screen)
            elif self.state == ScreenState.PROFILE:
                self.profile_menu.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)

    def draw_main_menu(self):
        """Отрисовывает главное меню."""
        # Рисуем левую панель
        self.draw_panel(self.left_panel_rect)
        
        # Рисуем правую панель
        self.draw_panel(self.right_panel_rect)
        
        # Текст на левой панели
        self.draw_left_panel_text()
        
        # Кнопки на правой панели
        for button in self.buttons:
            icon_x = button.rect.x + 20
            icon_y = button.rect.centery - 15
            button.draw(self.screen, self.font_manager.get_font('button'), icon_x, icon_y)

    def draw_settings(self):
        """Отрисовывает экран настроек."""
        # Рисуем панель настроек
        self.draw_panel(self.settings_panel_rect)
        
        # Кнопка "Назад"
        back_icon_x = self.back_button.rect.x + 20
        back_icon_y = self.back_button.rect.centery - 12
        self.back_button.draw(self.screen, self.font_manager.get_font('button'), back_icon_x, back_icon_y)
        
        # Кнопка "Применить"
        apply_icon_x = self.apply_button.rect.x + 15
        apply_icon_y = self.apply_button.rect.centery - 12
        self.apply_button.draw(self.screen, self.font_manager.get_font('button'), apply_icon_x, apply_icon_y)
        
        # Заголовок настроек
        title = self.font_manager.get_rendered_text("Настройки", 'settings_title', TEXT_PRIMARY, True)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        # Опции настроек
        self.draw_settings_options()

    def draw_investments(self):
        """Отрисовывает меню инвестиций."""
        self.investment_menu.draw(self.screen)

    def draw_clicker(self):
        """Отрисовывает кликер."""
        self.clicker_menu.draw(self.screen)

    def draw_panel(self, rect):
        """Рисует закругленную панель."""
        # Используем кортеж с координатами и размерами как ключ для кэша
        cache_key = (rect.x, rect.y, rect.width, rect.height)
        
        if cache_key not in self.panel_cache:
            colors = [(30, 30, 50, 200), (20, 20, 40, 200), (10, 10, 30, 200)]
            self.panel_cache[cache_key] = GradientGenerator.create_rounded_rect(
                (rect.width, rect.height), colors, PANEL_BORDER_RADIUS
            )
        self.screen.blit(self.panel_cache[cache_key], rect.topleft)

    def draw_left_panel_text(self):
        """Рисует текст на левой панели."""
        # BUS текст
        bus_text = self.font_manager.get_rendered_text(self.texts['bus'], 'title', PURPLE_ACCENT, True)
        self.screen.blit(bus_text, (self.left_panel_rect.x + 50, self.left_panel_rect.y + 50))
        
        # Заголовок
        title_text = self.font_manager.get_rendered_text(self.texts['title'], 'title_large', TEXT_PRIMARY, True)
        self.screen.blit(title_text, (self.left_panel_rect.x + 50, self.left_panel_rect.y + 120))
        
        # Подзаголовок
        subtitle1 = self.font_manager.get_rendered_text(self.texts['subtitle1'], 'subtitle', TEXT_SECONDARY)
        subtitle2 = self.font_manager.get_rendered_text(self.texts['subtitle2'], 'subtitle', PURPLE_ACCENT, True)
        self.screen.blit(subtitle1, (self.left_panel_rect.x + 50, self.left_panel_rect.y + 220))
        self.screen.blit(subtitle2, (self.left_panel_rect.x + 50, self.left_panel_rect.y + 260))
        
        # Описание
        for i, line in enumerate(self.texts['desc']):
            desc_text = self.font_manager.get_rendered_text(line, 'desc', TEXT_TERTIARY)
            self.screen.blit(desc_text, (self.left_panel_rect.x + 50, self.left_panel_rect.y + 320 + i * 30))
        
        # Версия
        version_text = self.font_manager.get_rendered_text(self.texts['version'], 'version', TEXT_SECONDARY)
        self.screen.blit(version_text, (self.left_panel_rect.x + 50, self.left_panel_rect.y + self.left_panel_rect.height - 50))

    def draw_settings_options(self):
    #"""Рисует опции настроек с индивидуальным позиционированием."""
    # Индивидуальные позиции для каждой надписи
        theme_x = SCREEN_WIDTH//2 - 350
        resolution_x = SCREEN_WIDTH//2 + 30
        fps_x = SCREEN_WIDTH//2 - 350
        language_x = SCREEN_WIDTH//2 + 30
        quality_x = SCREEN_WIDTH//2 - 350
    
        options = [
            ("Тема:", self.theme_dropdown, theme_x, 240),
            ("Разрешение:", self.resolution_dropdown, resolution_x, 240),
            ("FPS:", self.fps_dropdown, fps_x, 420),
            ("Язык:", self.language_dropdown, language_x, 420),
            ("Качество:", self.quality_dropdown, quality_x, 600)
        ]
        
        for label, dropdown, x_pos, y_pos in options:
            # Метка
            label_text = self.font_manager.get_rendered_text(label, 'settings_option', TEXT_PRIMARY)
            self.screen.blit(label_text, (x_pos, y_pos))
            
            # Dropdown
            dropdown.draw(self.screen, self.font_manager.get_font('settings_value'))

    def change_resolution(self, width, height):
        """Изменяет разрешение экрана."""
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH, SCREEN_HEIGHT = width, height
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        print(f"Разрешение изменено на {width}x{height}")
        
        # Пересоздаем UI элементы для нового разрешения
        self.initialize_ui()