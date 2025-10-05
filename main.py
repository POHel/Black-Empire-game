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
from coreLogic import Settings, ExportDB, UpdateDB

GAME_VERSION = "0.0.1"

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1450
SCREEN_HEIGHT = 830

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
    BUSINESSES = 10
    BUSINESS_CATEGORY = 11
    PROFILE = 12


# Добавить перед классом Business
@dataclass
class BusinessStats:
    """Статистика бизнеса"""
    income: float = 0
    expenses: float = 0
    risk: float = 0  # 0-100%
    legal_status: float = 100  # 0-100%
    employee_count: int = 0
    customer_satisfaction: float = 100  # 0-100%
    market_share: float = 0  # 0-100%
    

class BusinessTier(Enum):
    """Уровни бизнеса"""
    STARTUP = "Стартап"
    SMALL = "Малый"
    MEDIUM = "Средний"
    LARGE = "Крупный"
    CORPORATE = "Корпорация"
    MEGA = "Мега-корпорация"

class BusinessCategory(Enum):
    LIGHT = "light"
    DARK = "dark"

# Добавить в начало файла после других импортов
class NavButton:
    """Кнопка навигации в левой панели."""
    
    def __init__(self, rect, text, action, is_active=False):
        self.rect = rect
        self.text = text
        self.action = action
        self.is_active = is_active
    
    def draw(self, surface, font):
        """Рисует кнопку навигации."""
        if self.is_active:
            color = (80, 80, 140, 255)  # Активный цвет
            text_color = (255, 255, 255, 255)
        else:
            color = (50, 50, 90, 255)  # Неактивный цвет
            text_color = (200, 200, 200, 255)
        
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (100, 100, 150, 255), self.rect, width=1, border_radius=10)
        
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def click(self):
        """Выполняет действие при клике."""
        if self.action:
            self.action()

@dataclass
class Star:
    """Класс для анимированных звезд."""
    x: float
    y: float
    z: float
    size: float
    speed: float
    pulse_speed: float
    pulse_offset: float
    alpha: float
    alpha_change: float
    
    def update(self, dt: float):
        """Обновляет состояние звезды."""
        # Параллакс-движение
        self.y += self.speed * dt * (1 + self.z * 0.5)
        
        # Возврат звезды наверх при выходе за экран
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.uniform(0, SCREEN_WIDTH)
            self.z = random.uniform(0, 1)
            
        # Пульсация альфа-канала
        self.alpha += self.alpha_change
        if self.alpha > 255:
            self.alpha = 255
            self.alpha_change *= -1
        elif self.alpha < 50:
            self.alpha = 50
            self.alpha_change *= -1
    
    def get_current_size(self):
        """Возвращает текущий размер с пульсацией."""
        pulse = math.sin(pygame.time.get_ticks() * self.pulse_speed + self.pulse_offset) * 0.3
        return max(0.5, self.size + pulse)
    
    def get_screen_pos(self):
        """Возвращает экранные координаты с учетом параллакса."""
        parallax_x = self.x + (SCREEN_WIDTH/2 - self.x) * self.z * 0.1
        return parallax_x, self.y

class ParticleSystem:
    """Система частиц для фоновых эффектов."""
    
    def __init__(self, max_particles=1000):
        self.particles = []
        self.max_particles = max_particles
        
    def add_particle(self, x, y, color, size, lifetime, velocity):
        """Добавляет новую частицу."""
        if len(self.particles) < self.max_particles:
            self.particles.append({
                'x': x, 'y': y,
                'color': color,
                'size': size,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'velocity': velocity,
                'alpha': 255
            })
    
    def update(self, dt):
        """Обновляет все частицы."""
        for particle in self.particles[:]:
            particle['x'] += particle['velocity'][0] * dt
            particle['y'] += particle['velocity'][1] * dt
            particle['lifetime'] -= dt * 1000
            particle['alpha'] = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        """Отрисовывает все частицы."""
        for particle in self.particles:
            alpha_color = (*particle['color'][:3], particle['alpha'])
            pygame.draw.circle(
                surface, alpha_color,
                (int(particle['x']), int(particle['y'])),
                int(particle['size'])
            )

class FontManager:
    """Управление шрифтами с кэшированием."""
    
    def __init__(self):
        self.fonts = {}
        self.text_cache = {}
        self.initialize_fonts()
    
    def initialize_fonts(self):
        """Инициализирует все шрифты."""
        font_specs = {
            'title_large': ('segoeui.ttf', 80, True),
            'title': ('segoeui.ttf', 36, True),
            'subtitle': ('segoeui.ttf', 22, False),
            'desc': ('segoeui.ttf', 17, False),
            'button': ('segoeui.ttf', 26, True),
            'version': ('segoeui.ttf', 15, False),
            'loading': ('segoeui.ttf', 32, True),
            'settings_title': ('segoeui.ttf', 32, True),
            'settings_option': ('segoeui.ttf', 24, False),
            'settings_value': ('segoeui.ttf', 22, True),
        }
        
        for name, (font_name, size, bold) in font_specs.items():
            try:
                self.fonts[name] = pygame.font.Font(font_name, size)
                if bold:
                    self.fonts[name].set_bold(True)
            except:
                self.fonts[name] = pygame.font.SysFont('arial', size, bold)
    
    def get_font(self, name):
        return self.fonts.get(name, pygame.font.SysFont('arial', 17))
    
    def get_rendered_text(self, text, font_name, color, shadow=False):
        cache_key = (text, font_name, color, shadow)
        if cache_key in self.text_cache:
            return self.text_cache[cache_key]
        
        font = self.get_font(font_name)
        text_surf = font.render(text, True, color)
        
        if shadow:
            shadow_surf = pygame.Surface((text_surf.get_width() + 2, text_surf.get_height() + 2), pygame.SRCALPHA)
            shadow_text = font.render(text, True, (*BLACK, 150))
            shadow_surf.blit(shadow_text, (1, 1))
            shadow_surf.blit(text_surf, (0, 0))
            self.text_cache[cache_key] = shadow_surf
            return shadow_surf
        
        self.text_cache[cache_key] = text_surf
        return text_surf

class GradientGenerator:
    """Генератор градиентов."""
    
    @staticmethod
    def create_vertical_gradient(size, colors):
        width, height = size
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if len(colors) == 1:
            surface.fill(colors[0])
            return surface
        
        for y in range(int(height)):
            pos = y / max(height - 1, 1)
            color_index = pos * (len(colors) - 1)
            idx1 = min(int(color_index), len(colors) - 2)
            idx2 = idx1 + 1
            blend = color_index - idx1
            
            r = int(colors[idx1][0] + (colors[idx2][0] - colors[idx1][0]) * blend)
            g = int(colors[idx1][1] + (colors[idx2][1] - colors[idx1][1]) * blend)
            b = int(colors[idx1][2] + (colors[idx2][2] - colors[idx1][2]) * blend)
            a = int(colors[idx1][3] + (colors[idx2][3] - colors[idx1][3]) * blend)
            
            pygame.draw.line(surface, (r, g, b, a), (0, y), (width, y))
        
        return surface

    @staticmethod
    def create_horizontal_gradient(size, colors):
        """Создает горизонтальный градиент."""
        width, height = size
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if len(colors) == 1:
            surface.fill(colors[0])
            return surface
        
        for x in range(int(width)):
            pos = x / max(width - 1, 1)
            color_index = pos * (len(colors) - 1)
            idx1 = min(int(color_index), len(colors) - 2)
            idx2 = idx1 + 1
            blend = color_index - idx1
            
            r = int(colors[idx1][0] + (colors[idx2][0] - colors[idx1][0]) * blend)
            g = int(colors[idx1][1] + (colors[idx2][1] - colors[idx1][1]) * blend)
            b = int(colors[idx1][2] + (colors[idx2][2] - colors[idx1][2]) * blend)
            a = int(colors[idx1][3] + (colors[idx2][3] - colors[idx1][3]) * blend)
            
            pygame.draw.line(surface, (r, g, b, a), (x, 0), (x, height))
        
        return surface

    @staticmethod
    def create_radial_gradient(size, center_color, edge_color, center=None):
        """Создает радиальный градиент."""
        width, height = size
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if center is None:
            center = (width // 2, height // 2)
        
        max_distance = max(math.sqrt((center[0])**2 + (center[1])**2),
                          math.sqrt((width - center[0])**2 + (center[1])**2),
                          math.sqrt((center[0])**2 + (height - center[1])**2),
                          math.sqrt((width - center[0])**2 + (height - center[1])**2))
        
        for y in range(height):
            for x in range(width):
                distance = math.sqrt((x - center[0])**2 + (y - center[1])**2)
                ratio = min(distance / max_distance, 1.0)
                
                r = int(center_color[0] + (edge_color[0] - center_color[0]) * ratio)
                g = int(center_color[1] + (edge_color[1] - center_color[1]) * ratio)
                b = int(center_color[2] + (edge_color[2] - center_color[2]) * ratio)
                a = int(center_color[3] + (edge_color[3] - center_color[3]) * ratio)
                
                surface.set_at((x, y), (r, g, b, a))
        
        return surface

    @staticmethod
    def create_rounded_rect(size, colors, radius):
        """Создает закругленный прямоугольник с градиентом."""
        width, height = size
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Создаем маску для закругленных углов
        mask = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, width, height), border_radius=radius)
        
        # Создаем градиент
        gradient = GradientGenerator.create_vertical_gradient((width, height), colors)
        
        # Применяем маску к градиенту
        surface.blit(gradient, (0, 0))
        surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        return surface

class IconRenderer:
    """Рендерер иконок."""
    
    def __init__(self):
        self.icon_cache = {}
        self.play_icon_img = None
        self.settings_icon_img = None
        self.load_image_icons()

    def load_image_icons(self):
        """Загружает иконки из файлов с правильной обработкой ошибок."""
        try:
            import os
            if os.path.exists('images/play_icon.png'):
                self.play_icon_img = pygame.image.load('images/play_icon.png').convert_alpha()
                self.play_icon_img = pygame.transform.scale(self.play_icon_img, (30, 30))
            else:
                print("Файл images/play_icon.png не найден, используем векторные иконки")
                self.play_icon_img = None
                
            if os.path.exists('images/settings_icon.png'):
                self.settings_icon_img = pygame.image.load('images/settings_icon.png').convert_alpha()
                self.settings_icon_img = pygame.transform.scale(self.settings_icon_img, (30, 30))
            else:
                print("Файл images/settings_icon.png не найден, используем векторные иконки")
                self.settings_icon_img = None
                
        except pygame.error as e:
            print(f"Ошибка загрузки иконок: {e}")
            self.play_icon_img = None
            self.settings_icon_img = None
        except Exception as e:
            print(f"Общая ошибка при загрузке иконок: {e}")
            self.play_icon_img = None
            self.settings_icon_img = None
    
    def draw_play_image_icon(self, surface, x, y, size=30):
        """Рисует иконку игры из изображения."""
        if self.play_icon_img is not None:
            try:
                if size != 30:
                    scaled_icon = pygame.transform.scale(self.play_icon_img, (size, size))
                    surface.blit(scaled_icon, (x, y))
                else:
                    surface.blit(self.play_icon_img, (x, y))
                return True
            except Exception as e:
                print(f"Ошибка отрисовки изображения play: {e}")
        
        # Fallback на векторную иконку
        self.draw_play_icon(surface, x, y, size)
        return False
    
    def draw_settings_image_icon(self, surface, x, y, size=30):
        """Рисует иконку настроек из изображения."""
        if self.settings_icon_img is not None:
            try:
                if size != 30:
                    scaled_icon = pygame.transform.scale(self.settings_icon_img, (size, size))
                    surface.blit(scaled_icon, (x, y))
                else:
                    surface.blit(self.settings_icon_img, (x, y))
                return True
            except Exception as e:
                print(f"Ошибка отрисовки изображения settings: {e}")
        
        # Fallback на векторную иконку
        self.draw_settings_icon(surface, x, y, size)
        return False
    
    def draw_play_icon(self, surface, x, y, size=30):
        cache_key = ("play", size)
        if cache_key not in self.icon_cache:
            icon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            points = [(size*0.3, size*0.2), (size*0.8, size*0.5), (size*0.3, size*0.8)]
            gfxdraw.filled_polygon(icon_surf, points, PURPLE_PRIMARY)
            gfxdraw.aapolygon(icon_surf, points, TEXT_PRIMARY)
            self.icon_cache[cache_key] = icon_surf
        
        surface.blit(self.icon_cache[cache_key], (x, y))
    
    def draw_settings_icon(self, surface, x, y, size=40):
        cache_key = ("settings", size)
        if cache_key not in self.icon_cache:
            icon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            center = size // 2
            pygame.draw.circle(icon_surf, TEXT_PRIMARY, (center, center), size//3, 2)
            for i in range(8):
                angle = math.radians(i * 45)
                x1 = center + (size//3) * math.cos(angle)
                y1 = center + (size//3) * math.sin(angle)
                x2 = center + (size//2) * math.cos(angle)
                y2 = center + (size//2) * math.sin(angle)
                pygame.draw.line(icon_surf, TEXT_PRIMARY, (x1, y1), (x2, y2), 2)
            self.icon_cache[cache_key] = icon_surf
        
        surface.blit(self.icon_cache[cache_key], (x, y))
    
    def draw_exit_icon(self, surface, x, y, size=30):
        cache_key = ("exit", size)
        if cache_key not in self.icon_cache:
            icon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            margin = size // 4
            pygame.draw.line(icon_surf, TEXT_PRIMARY, (margin, margin), (size-margin, size-margin), 3)
            pygame.draw.line(icon_surf, TEXT_PRIMARY, (size-margin, margin), (margin, size-margin), 3)
            self.icon_cache[cache_key] = icon_surf
        
        surface.blit(self.icon_cache[cache_key], (x, y))
    
    def draw_back_icon(self, surface, x, y, size=30):
        cache_key = ("back", size)
        if cache_key not in self.icon_cache:
            icon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.line(icon_surf, TEXT_PRIMARY, (size*0.7, size*0.2), (size*0.3, size*0.5), 3)
            pygame.draw.line(icon_surf, TEXT_PRIMARY, (size*0.3, size*0.5), (size*0.7, size*0.8), 3)
            self.icon_cache[cache_key] = icon_surf
        
        surface.blit(self.icon_cache[cache_key], (x, y))

    def draw_apply_icon(self, surface, x, y, size=25):
        """Рисует иконку применения (галочку)."""
        cache_key = ("apply", size)
        if cache_key not in self.icon_cache:
            icon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            # Рисуем галочку
            margin = size // 4
            points = [
                (margin, size // 2),
                (size // 2 - 2, size - margin),
                (size - margin, margin)
            ]
            pygame.draw.lines(icon_surf, TEXT_PRIMARY, False, points, 3)
            self.icon_cache[cache_key] = icon_surf
        
        surface.blit(self.icon_cache[cache_key], (x, y))

class Button:
    """Интерактивная кнопка с увеличенным закруглением."""
    
    def __init__(self, rect, text, icon_renderer=None, action=None, icon_size=30, is_active=False):
        self.rect = rect
        self.text = text
        self.icon_renderer = icon_renderer
        self.action = action
        self.hovered = False
        self.cache = {}
        self.click_animation = 0
        self.icon_size = icon_size
        self.is_active = is_active  # Добавляем атрибут активности
    
    def draw(self, surface, font, icon_x, icon_y):
        state_key = (self.rect.width, self.rect.height, self.hovered, int(self.click_animation * 10))
        if state_key not in self.cache:
            # Создаем закругленную кнопку с градиентом
            if self.hovered:
                colors = [(180, 60, 255, 150), (120, 20, 220, 150), (55, 0, 110, 150)]
            else:
                colors = [(55, 0, 110, 100), (120, 20, 220, 100), (55, 0, 110, 100)]
            
            btn_surf = GradientGenerator.create_rounded_rect(
                (self.rect.width, self.rect.height), colors, BUTTON_BORDER_RADIUS
            )
            
            # Мягкая тень
            shadow_surf = pygame.Surface((self.rect.width + 6, self.rect.height + 6), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, 40), (3, 3, self.rect.width, self.rect.height), 
                        border_radius=BUTTON_BORDER_RADIUS)
            
            # Эффект клика
            if self.click_animation > 0:
                glow = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow, (255, 255, 255, int(100 * self.click_animation)), 
                            glow.get_rect(), border_radius=BUTTON_BORDER_RADIUS)
                btn_surf.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)
            
            # Собираем финальную кнопку с тенью
            final_surf = pygame.Surface((self.rect.width + 6, self.rect.height + 6), pygame.SRCALPHA)
            final_surf.blit(shadow_surf, (0, 0))
            final_surf.blit(btn_surf, (3, 3))
            
            self.cache[state_key] = final_surf
        
        surface.blit(self.cache[state_key], (self.rect.x - 3, self.rect.y - 3))
        
        if self.icon_renderer:
            # Передаем правильное количество аргументов (surface, x, y, size)
            self.icon_renderer(surface, icon_x, icon_y, self.icon_size)
        
        text_surf = font.render(self.text, True, TEXT_PRIMARY)
        text_rect = text_surf.get_rect(midleft=(icon_x + 60, self.rect.centery))
        surface.blit(text_surf, text_rect)
    
    def update(self, dt):
        if self.click_animation > 0:
            self.click_animation -= dt * 5
    
    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
    def click(self):
        if self.action:
            self.click_animation = 1.0
            self.action()

class Dropdown:
    """Выпадающий список для настроек."""
    
    # Статический список всех созданных dropdown элементов
    all_dropdowns = []
    active_dropdown = None  # Текущий активный dropdown
    
    def __init__(self, rect, options, default_index=0):
        self.rect = rect
        self.options = options
        self.selected_index = default_index
        self.is_open = False
        self.hovered_index = -1
        self.cache = {}
        
        # Добавляем себя в общий список
        Dropdown.all_dropdowns.append(self)
    
    def close_all_other_dropdowns(self):
        """Закрывает все другие выпадающие списки кроме текущего."""
        for dropdown in Dropdown.all_dropdowns:
            if dropdown != self and dropdown.is_open:
                dropdown.is_open = False
                dropdown.hovered_index = -1
    
    def draw(self, surface, font):
        # Рисуем основную кнопку
        state_key = (self.rect.width, self.rect.height, self.is_open)
        if state_key not in self.cache:
            # Создаем закругленный прямоугольник - УБИРАЕМ ПРОЗРАЧНОСТЬ
            btn_surf = GradientGenerator.create_rounded_rect(
                (self.rect.width, self.rect.height), 
                [(55, 0, 110, 100), (120, 20, 220, 100), (55, 0, 110, 100)],
                SETTINGS_PANEL_RADIUS
            )
            
            # Стрелка вниз/вверх
            arrow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            if self.is_open:
                # Стрелка вверх
                pygame.draw.polygon(arrow_surf, TEXT_PRIMARY, [(5, 15), (10, 5), (15, 15)])
            else:
                # Стрелка вниз
                pygame.draw.polygon(arrow_surf, TEXT_PRIMARY, [(5, 5), (10, 15), (15, 5)])
            
            btn_surf.blit(arrow_surf, (self.rect.width - 30, (self.rect.height - 20) // 2))
            self.cache[state_key] = btn_surf
        
        surface.blit(self.cache[state_key], self.rect.topleft)
        
        # Текст выбранной опции
        text = self.options[self.selected_index]
        text_surf = font.render(text, True, TEXT_PRIMARY)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 15, self.rect.centery))
        surface.blit(text_surf, text_rect)
        
        # Если открыт, рисуем опции (только если это активный dropdown)
        if self.is_open and Dropdown.active_dropdown == self:
            option_height = 40
            dropdown_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, option_height * len(self.options))
            
            # Фон dropdown - УБИРАЕМ ПРОЗРАЧНОСТЬ
            dropdown_surf = GradientGenerator.create_rounded_rect(
                (dropdown_rect.width, dropdown_rect.height), 
                [(55, 0, 110, 100), (120, 20, 220, 100), (55, 0, 110, 100)],
                SETTINGS_PANEL_RADIUS
            )
            surface.blit(dropdown_surf, dropdown_rect.topleft)
            
            # Опции
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * option_height, self.rect.width, option_height)
                color = PURPLE_ACCENT if i == self.hovered_index else TEXT_PRIMARY
                
                option_surf = font.render(option, True, color)
                option_text_rect = option_surf.get_rect(midleft=(option_rect.x + 15, option_rect.centery))
                surface.blit(option_surf, option_text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                # При открытии закрываем все другие dropdown
                if not self.is_open:
                    self.close_all_other_dropdowns()
                    Dropdown.active_dropdown = self
                self.is_open = not self.is_open
                return True
            elif self.is_open:
                option_height = 40
                for i in range(len(self.options)):
                    option_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * option_height, self.rect.width, option_height)
                    if option_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.is_open = False
                        Dropdown.active_dropdown = None
                        return True
                
                # Клик вне dropdown - закрываем все dropdown
                Dropdown.close_all_dropdowns()
                return True
        
        elif event.type == pygame.MOUSEMOTION and self.is_open and Dropdown.active_dropdown == self:
            self.hovered_index = -1
            option_height = 40
            for i in range(len(self.options)):
                option_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * option_height, self.rect.width, option_height)
                if option_rect.collidepoint(event.pos):
                    self.hovered_index = i
                    break
        
        return False
    
    @classmethod
    def close_all_dropdowns(cls):
        """Закрывает все выпадающие списки."""
        for dropdown in cls.all_dropdowns:
            dropdown.is_open = False
            dropdown.hovered_index = -1
        cls.active_dropdown = None

    # Также добавьте эту функцию в основной цикл обработки событий:
    # def handle_global_events(self, event, dropdowns):
    #     """Обрабатывает глобальные события для dropdown."""
    #     if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
    #         # Проверяем, был ли клик по любому dropdown
    #         clicked_on_dropdown = False
    #         for dropdown in dropdowns:
    #             if dropdown.handle_event(event):
    #                 clicked_on_dropdown = True
    #                 break
            
    #         # Если клик был не по dropdown, закрываем все
    #         if not clicked_on_dropdown:
    #             # Проверяем, был ли клик по области любого открытого dropdown
    #             for dropdown in dropdowns:
    #                 if dropdown.is_open:
    #                     option_height = 40
    #                     dropdown_rect = pygame.Rect(
    #                         dropdown.rect.x, 
    #                         dropdown.rect.bottom, 
    #                         dropdown.rect.width, 
    #                         option_height * len(dropdown.options)
    #                     )
    #                     if dropdown_rect.collidepoint(event.pos):
    #                         clicked_on_dropdown = True
    #                         break
                
    #             if not clicked_on_dropdown:
    #                 Dropdown.close_all_dropdowns()
        
    #     elif event.type == pygame.MOUSEMOTION:
    #         # Обрабатываем движение мыши только для активного dropdown
    #         if Dropdown.active_dropdown:
    #             Dropdown.active_dropdown.handle_event(event)
    #         else:
    #             for dropdown in dropdowns:
    #                 dropdown.handle_event(event)

class Slider:
    """Ползунок для настроек."""
    
    def __init__(self, rect, min_value, max_value, current_value):
        self.rect = rect
        self.min_value = min_value
        self.max_value = max_value
        self.value = current_value
        self.dragging = False
        self.cache = {}
    
    def draw(self, surface):
        # Фон слайдера
        bg_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height//2 - 3, self.rect.width, 6)
        pygame.draw.rect(surface, DEEP_PURPLE, bg_rect, border_radius=3)
        
        # Заполненная часть
        fill_width = int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height//2 - 3, fill_width, 6)
            pygame.draw.rect(surface, PURPLE_PRIMARY, fill_rect, border_radius=3)
        
        # Ползунок
        slider_x = self.rect.x + fill_width
        slider_rect = pygame.Rect(slider_x - 10, self.rect.y, 20, self.rect.height)
        pygame.draw.rect(surface, LIGHT_PURPLE, slider_rect, border_radius=10)
        pygame.draw.rect(surface, TEXT_PRIMARY, slider_rect, 2, border_radius=10)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            slider_rect = pygame.Rect(
                self.rect.x + int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width) - 10,
                self.rect.y,
                20,
                self.rect.height
            )
            if slider_rect.collidepoint(event.pos):
                self.dragging = True
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            return True
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = max(0, min(event.pos[0] - self.rect.x, self.rect.width))
            self.value = self.min_value + (rel_x / self.rect.width) * (self.max_value - self.min_value)
            return True
        
        return False

class LoadingScreen:
    """Экран загрузки с анимацией."""
    
    def __init__(self, screen, font_manager):
        self.screen = screen
        self.font_manager = font_manager
        self.progress = 0.0
        self.start_time = time.time()
        self.loading_duration = 1.0  # 5 секунд загрузки
        self.dots = 0
        self.last_dot_time = 0
        self.rotation_angle = 0
        self.particles = ParticleSystem(200)
        
    def update(self):
        current_time = time.time()
        elapsed = current_time - self.start_time
        self.progress = min(elapsed / self.loading_duration, 1.0)
        
        # Анимация точек
        if current_time - self.last_dot_time > 0.3:
            self.dots = (self.dots + 1) % 4
            self.last_dot_time = current_time
        
        # Вращение
        self.rotation_angle = (self.rotation_angle + 2) % 360
        
        # Добавляем частицы
        if random.random() < 0.1:
            x = random.randint(0, SCREEN_WIDTH)
            self.particles.add_particle(
                x, SCREEN_HEIGHT + 20,
                (160, 60, 255), random.uniform(1, 3),
                random.uniform(1, 3), (0, random.uniform(-100, -200))
            )
        
        self.particles.update(1/60)
        
        return self.progress >= 1.0
    
    def draw(self):
        # Темный фон
        self.screen.fill(DARK_BG)
        
        # Частицы
        self.particles.draw(self.screen)
        
        # Вращающийся логотип
        logo_size = 120
        logo_surf = pygame.Surface((logo_size, logo_size), pygame.SRCALPHA)
        pygame.draw.circle(logo_surf, PURPLE_PRIMARY, (logo_size//2, logo_size//2), logo_size//3)
        pygame.draw.circle(logo_surf, LIGHT_PURPLE, (logo_size//2, logo_size//2), logo_size//4)
        
        rotated_logo = pygame.transform.rotate(logo_surf, self.rotation_angle)
        logo_rect = rotated_logo.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        self.screen.blit(rotated_logo, logo_rect)
        
        # Текст загрузки
        loading_text = "Загрузка" + "." * self.dots
        text_surf = self.font_manager.get_rendered_text(loading_text, 'loading', TEXT_PRIMARY, True)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(text_surf, text_rect)
        
        # Закругленный прогресс-бар
        bar_width, bar_height = 500, 25
        bar_x, bar_y = SCREEN_WIDTH//2 - bar_width//2, SCREEN_HEIGHT//2 + 50
        
        # Фон прогресс-бара
        pygame.draw.rect(self.screen, DEEP_PURPLE, (bar_x, bar_y, bar_width, bar_height), 
                       border_radius=BAR_BORDER_RADIUS)
        
        # Заполнение - ИСПРАВЛЕННАЯ СТРОКА
        fill_width = int(bar_width * self.progress)
        if fill_width > 0:
            # Используем простой прямоугольник вместо градиента для прогресс-бара
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(self.screen, PURPLE_PRIMARY, fill_rect, border_radius=BAR_BORDER_RADIUS)
        
        # Процент
        percent_text = f"{int(self.progress * 100)}%"
        percent_surf = self.font_manager.get_rendered_text(percent_text, 'subtitle', TEXT_SECONDARY)
        percent_rect = percent_surf.get_rect(center=(SCREEN_WIDTH//2, bar_y + 40))
        self.screen.blit(percent_surf, percent_rect)
        
        # Анимированные звезды на фоне загрузки
        for _ in range(3):
            x, y = random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)
            size = random.uniform(1, 3)
            pygame.draw.circle(self.screen, (255, 255, 255, 100), (x, y), int(size))

class GameConfig:
    def __init__(self):
        self.screen_width = 1450
        self.screen_height = 830
        self.button_height = 70
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
     """Класс для частиц (упрощенная версия)"""
     def __init__(self, x, y, color, size, velocity, duration=1.0):
         self.x = x
         self.y = y
         self.color = color
         self.size = size
         self.velocity = velocity
         self.duration = duration
         self.lifetime = 0
         self.alive = True
    
     def update(self, dt):
         self.lifetime += dt
         if self.lifetime >= self.duration:
             self.alive = False
         else:
             self.x += self.velocity[0] * dt
             self.y += self.velocity[1] * dt
    
     def draw(self, surface):
         alpha = 255 * (1 - self.lifetime / self.duration)
         color_with_alpha = (*self.color, int(alpha))
         particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
         pygame.draw.circle(particle_surface, color_with_alpha, (self.size, self.size), self.size)
         surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))

# Всплывающий текст
class FloatingText:
    """Класс для всплывающего текста"""
    def __init__(self, x, y, text, color, font_size):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font_size = font_size
        self.lifetime = 0
        self.duration = 1.5
        self.alive = True
    
    def update(self, dt):
        self.lifetime += dt
        self.y -= 50 * dt  # Движение вверх
        if self.lifetime >= self.duration:
            self.alive = False
    
    def draw(self, surface, font):
        alpha = int(255 * (1 - self.lifetime / self.duration))
        # Ограничиваем alpha в диапазоне 0-255
        alpha = max(0, min(255, alpha))
        text_color = (*self.color, alpha)
        text_surface = font.render(self.text, True, text_color)
        surface.blit(text_surface, (int(self.x - text_surface.get_width() // 2), int(self.y)))

class ClickerMenu:
    """Исправленная версия кликера с использованием общей палитры цветов."""

    def __init__(self, game):  # Добавляем параметр game
        self.game = game  # Сохраняем ссылку на основной игровой объект
        self.config = GameConfig()
        # Используем экран из game вместо создания нового
        self.screen = game.screen
        
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
        
        # Инициализация UI
        self.initialize_ui()

    def load_fonts(self) -> Dict[str, pygame.font.Font]:
        fonts = {}
        try:
            font_name = pygame.font.get_default_font()
            for size_name, size in self.config.font_sizes.items():
                fonts[size_name] = pygame.font.SysFont(font_name, size)
        except:
            for size_name, size in self.config.font_sizes.items():
                fonts[size_name] = pygame.font.Font(None, size)
        return fonts

    def format_money(self, amount: int) -> str:
        if amount >= 1000000:
            return f"${amount/1000000:.1f}M"
        elif amount >= 1000:
            return f"${amount/1000:.1f}K"
        return f"${amount}"

    def create_gradient_background(self, width: int, height: int) -> pygame.Surface:
        surface = pygame.Surface((width, height))
        surface.fill(DARK_BG)
        
        # Упрощенный градиент
        for i in range(2):
            center_x = width * 0.1 if i == 0 else width * 0.9
            center_y = height * 0.2 if i == 0 else height * 0.8
            radius = min(width, height) * 0.3
            
            for r in range(int(radius), 0, -10):
                alpha = max(0, 10 - int(r / (radius / 10)))
                if alpha > 0:
                    color = (*PANEL_BG, alpha) if i == 0 else (*PANEL_BG, alpha)
                    gradient_surface = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                    pygame.draw.circle(gradient_surface, color, (r, r), r)
                    surface.blit(gradient_surface, (int(center_x - r), int(center_y - r)))
        
        return surface

    def initialize_ui(self):
        """Инициализация UI кликера с индивидуальным расположением кнопок."""
        self.nav_buttons = []
        self.invest_button = None
        
        # Индивидуальные позиции для навигационных кнопок
        nav_positions = [
            ("Кликер", 10, 20, 80, 150),      # x, y, width, height
            ("Магазины", 10, 180, 80, 150),
            ("Инвестиции", 10, 340, 80, 150),
            ("Бизнесы", 10, 500, 80, 150),
            ("Профиль", 10, 660, 80, 150)
        ]
        
        nav_actions = {
            "Кликер": lambda: self.game.play_game(),
            "Магазины": lambda: self.game.open_shop_selection(),
            "Инвестиции": lambda: self.game.open_investments(),
            "Бизнесы": lambda: self.game.open_businesses(),
            "Профиль": lambda: self.game.open_profile()
        }

        for text, x, y, width, height in nav_positions:
            rect = pygame.Rect(x, y, width, height)
            action = nav_actions[text]
            is_active = (text == "Кликер")  # Первая кнопка активна по умолчанию
            self.nav_buttons.append(NavButton(rect, text, action, is_active))
        
        # Индивидуальная позиция для кнопки инвестирования
        invest_rect = pygame.Rect(
            self.config.screen_width - 250,  # индивидуальный X
            self.config.screen_height // 2 - 100,  # индивидуальный Y
            1000,  # индивидуальная ширина
            300   # индивидуальная высота
        )
        self.invest_button = InvestButton(invest_rect, "Инвестировать")

    def draw_button(self, surface: pygame.Surface, rect: pygame.Rect, text: str, 
                   subtitle: str, is_pressed: bool = False, is_hovered: bool = False):
        """Рисует кнопку инвестирования с индивидуальными настройками"""
        button_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        
        # Основной цвет кнопки
        if is_pressed:
            base_color = (*DEEP_PURPLE, 180)
        elif is_hovered:
            base_color = (*DEEP_PURPLE, 200)
        else:
            base_color = (*DEEP_PURPLE, 150)
        
        pygame.draw.rect(button_surface, base_color, (0, 0, rect.width, rect.height), border_radius=40)
        
        # Внутренняя тень
        inner_shadow = pygame.Surface((rect.width - 20, rect.height - 20), pygame.SRCALPHA)
        pygame.draw.rect(inner_shadow, (0, 0, 0, 100), 
                        (0, 0, inner_shadow.get_width(), inner_shadow.get_height()), 
                        border_radius=30)
        button_surface.blit(inner_shadow, (10, 10))
        
        # Иконка воспроизведения (размер адаптируется под кнопку)
        icon_size = min(80, rect.height // 2)
        icon_x = rect.width // 2 - icon_size // 2
        icon_y = rect.height // 3 - icon_size // 2
        
        pygame.draw.rect(button_surface, (*DEEP_PURPLE, 220), 
                        (icon_x, icon_y, icon_size, icon_size), border_radius=20)
        
        # Треугольник воспроизведения
        triangle_points = [
            (icon_x + icon_size // 3, icon_y + icon_size // 4),
            (icon_x + icon_size // 3, icon_y + 3 * icon_size // 4),
            (icon_x + 2 * icon_size // 3, icon_y + icon_size // 2)
        ]
        pygame.draw.polygon(button_surface, WHITE, triangle_points)
        
        # Текст кнопки (размер шрифта адаптируется)
        title_font_size = min(self.config.font_sizes["xlarge"], rect.height // 4)
        subtitle_font_size = min(self.config.font_sizes["medium"], rect.height // 6)
        
        title_font = pygame.font.Font(None, title_font_size)
        subtitle_font = pygame.font.Font(None, subtitle_font_size)
        
        title_text = title_font.render(text, True, WHITE)
        subtitle_text = subtitle_font.render(subtitle, True, DEEP_PURPLE)
        
        button_surface.blit(title_text, 
                          (rect.width // 2 - title_text.get_width() // 2, 
                           rect.height // 2 + 20))
        button_surface.blit(subtitle_text, 
                          (rect.width // 2 - subtitle_text.get_width() // 2, 
                           rect.height // 2 + 50))
        
        # Эффект пульсации
        if not is_pressed and not is_hovered:
            pulse_alpha = int(100 + 50 * math.sin(pygame.time.get_ticks() / 500))
            pulse_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(pulse_surface, (*PANEL_BG, pulse_alpha), 
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
        pygame.draw.rect(panel_surface, (*PANEL_BG, 200), 
                        (0, 0, rect.width, rect.height), 
                        border_radius=24)
        
        # Эффект звездного поля
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
            color = random.choice([DEEP_PURPLE, DARK_BG, (203, 168, 255)])
            # particle = Particle(x, y, color, random.randint(3, 6), velocity, 
            #                   self.config.animations["particle_duration"])
            # self.particles.append(particle)
        
        # "Монеты"
        for _ in range(self.config.animations["click_effect_coins"]):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 6)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            # particle = Particle(x, y, DEEP_PURPLE, random.randint(4, 8), velocity, 
            #                   self.config.animations["particle_duration"])
            # self.particles.append(particle)
        
        # Всплывающий текст
        text = f"+{self.format_money(self.per_click)}"
        floating_text = FloatingText(x, y - 50, text, (189, 168, 255), 
                                   self.config.font_sizes["large"])
        self.floating_texts.append(floating_text)

    def draw(self):
        """Отрисовка кликера"""
        # Фон
        bg_key = f"bg_{self.config.screen_width}_{self.config.screen_height}"
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
        
        title_text = title_font.render("Корпоративный Кликер", True, WHITE)
        brand_text = brand_font.render("Black Empire", True, BLACK)
        
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
            
            value_text = stat_font.render(value, True, WHITE)
            label_text = label_font.render(label, True, DEEP_PURPLE)
            
            self.screen.blit(value_text, (x + stat_width // 2 - value_text.get_width() // 2, stats_y))
            self.screen.blit(label_text, (x + stat_width // 2 - label_text.get_width() // 2, stats_y + 40))
        
        # Кнопки навигации
        for button in self.nav_buttons:
            button.draw(self.screen, self.fonts["medium"])

        # Разделительная линия
        pygame.draw.line(self.screen, PANEL_BG, 
                        (100, stats_y + 80), 
                        (self.config.screen_width - 100, stats_y + 80), 2)
        
        # Кнопка инвестирования
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(
            self.config.screen_width - 700,
            self.config.screen_height // 2 - 140,  # Исправлена высота
            400, 450  # Исправлены размеры кнопки
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
            True, DEEP_PURPLE
        )
        self.screen.blit(instruction_text, 
                        (self.config.screen_width // 2 - instruction_text.get_width() // 2, 
                         self.config.screen_height - 80))
        
        # Отрисовываем частицы
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Отрисовываем всплывающий текст
        for text in self.floating_texts:
            text.draw(self.screen, self.fonts["large"])

    def handle_event(self, event):
        """Обработка кликов по кнопке и навигации."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            # Проверяем навигационные кнопки
            for button in self.nav_buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    # Обновляем активное состояние
                    for btn in self.nav_buttons:
                        btn.is_active = (btn.text == button.text)
                    return True

        """Обрабатывает события игры"""
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(
            self.config.screen_width - 700,
            self.config.screen_height // 2 - 140,
            400, 450
        )
        is_button_hovered = button_rect.collidepoint(mouse_pos)
        
        if event.type == pygame.QUIT:
            self.running = False
            self.game.running = False
        
        elif event.type == pygame.VIDEORESIZE:
            # Обработка изменения размера окна
            self.config.screen_width, self.config.screen_height = event.size
            self.screen = pygame.display.set_mode((self.config.screen_width, self.config.screen_height), 
                                                 pygame.RESIZABLE)
            self.cached_surfaces.clear()
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if is_button_hovered:
                self.handle_click()
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.handle_click()
            elif event.key == pygame.K_ESCAPE:
                self.game.back_to_menu()

    def handle_click(self):
        """Обрабатывает клик по кнопке"""
        self.money += self.per_click
        self.total_clicks += 1
        
        # Создаем эффекты в центре кнопки
        center_x = self.config.screen_width - 500
        center_y = self.config.screen_height // 2
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

class InvestButton:
    """Класс для кнопки инвестирования с индивидуальными свойствами"""
    def __init__(self, rect: pygame.Rect, text: str):
        self.rect = rect
        self.text = text
        self.is_hovered = False
        self.is_pressed = False

#вкладка Инвестиции
class InvestmentMenu:
    """Класс для меню инвестиций."""
    
    def __init__(self, game):
        self.game = game
        self.export = ExportDB()
        self.current_tab = "акции"  # Текущая активная вкладка
        self.buttons = []
        self.tab_buttons = []
        self.initialize_ui()
    
    def initialize_ui(self):
        """Инициализация UI элементов меню инвестиций."""
        # Кнопки левой панели навигации
        nav_buttons = [
            ("Кликер", lambda: self.game.play_game()),
            ("Магазины", lambda: self.game.open_shop_selection()),
            ("Инвестиции", lambda: None),
            ("Бизнесы", lambda: self.game.open_businesses()),
            ("Профиль", lambda: self.game.open_profile())
        ]
        
        # Создаем кнопки навигации
        button_width, button_height = 200, 60
        button_x = 50
        button_y_start = 150
        
        for i, (text, action) in enumerate(nav_buttons):
            rect = pygame.Rect(button_x, button_y_start + i * 70, button_width, button_height)
            is_active = text == "Инвестиции"
            self.buttons.append(NavButton(rect, text, action, is_active))
        
        # Кнопки вкладок (акции, недвижимость, криптовалюта)
        tab_button_width, tab_button_height = 150, 50
        tab_button_x = 300
        tab_button_y = 100
        
        tab_buttons = [
            ("Акции", lambda: self.set_current_tab("акции")),
            ("Недвижимость", lambda: self.set_current_tab("недвижимость")),
            ("Криптовалюта", lambda: self.set_current_tab("криптовалюта"))
        ]
        
        for i, (text, action) in enumerate(tab_buttons):
            rect = pygame.Rect(tab_button_x + i * 160, tab_button_y, tab_button_width, tab_button_height)
            is_active = text.lower() == self.current_tab
            self.tab_buttons.append(TabButton(rect, text, action, is_active))
    
    def set_current_tab(self, tab_name):
        """Устанавливает текущую активную вкладку."""
        self.current_tab = tab_name
        # Обновляем состояние кнопок вкладок
        for button in self.tab_buttons:
            button.is_active = button.text.lower() == tab_name
    
    def draw(self, surface):
        """Отрисовывает меню инвестиций."""
        # Рисуем левую панель навигации
        nav_panel_rect = pygame.Rect(30, 120, 240, 500)
        self.draw_panel(surface, nav_panel_rect, (30, 30, 50, 200))
        
        # Рисуем правую панель с контентом
        content_panel_rect = pygame.Rect(300, 120, 1100, 600)
        self.draw_panel(surface, content_panel_rect, (30, 30, 50, 200))
        
        # Рисуем кнопки навигации
        for button in self.buttons:
            button.draw(surface, self.game.font_manager.get_font('button'))
        
        # Рисуем кнопки вкладок
        for button in self.tab_buttons:
            button.draw(surface, self.game.font_manager.get_font('button'))
        
        # Рисуем виджет с данными портфеля
        self.draw_portfolio_widget(surface, 320, 170)
        
        # Рисуем контент в зависимости от активной вкладка
        if self.current_tab == "акции":
            self.draw_stocks_content(surface, 320, 250)
        elif self.current_tab == "недвижимость":
            self.draw_real_estate_content(surface, 320, 250)
        elif self.current_tab == "криптовалюта":
            self.draw_crypto_content(surface, 320, 250)
    
    def draw_panel(self, surface, rect, color):
        """Рисует панель с закругленными углами."""
        pygame.draw.rect(surface, color, rect, border_radius=15)
        pygame.draw.rect(surface, (100, 100, 150, 255), rect, width=2, border_radius=15)
    
    def draw_portfolio_widget(self, surface, x, y):
        """Рисует виджет с данными портфеля."""
        widget_rect = pygame.Rect(x, y, 1060, 60)
        self.draw_panel(surface, widget_rect, (40, 40, 70, 200))
        
        # Получаем данные портфеля
        portfolio_data = self.export.get_bag()
        if not portfolio_data:
            portfolio_data = (0,0,0,0,0,0)
        
        if len(portfolio_data) < 6:
            portfolio_data = list(portfolio_data) + [0] * (6 - len(portfolio_data))
        
        labels = [
            f"Стоимость всего портфеля: {portfolio_data[0]}$",
            f"Дивидендная доходность: {portfolio_data[1]}%",
            f"Стабильный доход: {portfolio_data[2]}$",
            f"Потенциал роста: {portfolio_data[3]}%",
            f"Доход от аренды: {portfolio_data[4]}$",
            #f"Общая стоимость криптовалюты: {portfolio_data[5]}$"
        ]
        
        font = self.game.font_manager.get_font('desc')
        label_width = 1060 // len(labels)
        
        for i, label in enumerate(labels):
            text_surf = font.render(label, True, TEXT_PRIMARY)
            text_x = x + i * label_width + (label_width - text_surf.get_width()) // 2
            surface.blit(text_surf, (text_x, y + 20))
    
    def draw_stocks_content(self, surface, x, y):
        """Рисует контент для вкладки акций."""
        # Заголовок
        title_font = self.game.font_manager.get_font('subtitle')
        title_surf = title_font.render("Доступные акции", True, TEXT_PRIMARY)
        surface.blit(title_surf, (x, y))
        
        # Получаем список акций
        actives = self.export.get_actives()
        if actives:
            stocks = actives
        else:
            stocks = ["Все акции куплены"]
        
        # Отображаем акции в виде сетки
        stock_width, stock_height = 200, 40
        columns = 4
        spacing = 20
        
        for i, stock in enumerate(stocks):
            row = i // columns
            col = i % columns
            
            stock_x = x + col * (stock_width + spacing)
            stock_y = y + 50 + row * (stock_height + spacing)
            
            # Рисуем кнопку акции
            stock_rect = pygame.Rect(stock_x, stock_y, stock_width, stock_height)
            self.draw_stock_button(surface, stock_rect, stock)
    
    def draw_real_estate_content(self, surface, x, y):
        """Рисует контент для вкладки недвижимость."""
        # Заголовок
        title_font = self.game.font_manager.get_font('subtitle')
        title_surf = title_font.render("Доступная недвижимость", True, TEXT_PRIMARY)
        surface.blit(title_surf, (x, y))
        
        actives = self.export.get_homes()
        if actives:
            stocks = actives
        else:
            stocks = ["Вся недвижимость куплена"]
        
        # Отображаем акции в виде сетки
        stock_width, stock_height = 200, 40
        columns = 4
        spacing = 20
        
        for i, stock in enumerate(stocks):
            row = i // columns
            col = i % columns
            
            stock_x = x + col * (stock_width + spacing)
            stock_y = y + 50 + row * (stock_height + spacing)
            
            # Рисуем кнопку акции
            stock_rect = pygame.Rect(stock_x, stock_y, stock_width, stock_height)
            self.draw_stock_button(surface, stock_rect, stock)
    
    def draw_crypto_content(self, surface, x, y):
        """Рисует контент для вкладки криптовалюта."""
        # Заголовок
        title_font = self.game.font_manager.get_font('subtitle')
        title_surf = title_font.render("Доступная криптовалюта", True, TEXT_PRIMARY)
        surface.blit(title_surf, (x, y))
        
        actives = self.export.get_crypto()
        if actives:
            stocks = actives
        else:
            stocks = ["Вся криптовалюта куплена"]
        
        # Отображаем акции в виде сетки
        stock_width, stock_height = 200, 40
        columns = 4
        spacing = 20
        
        for i, stock in enumerate(stocks):
            row = i // columns
            col = i % columns
            
            stock_x = x + col * (stock_width + spacing)
            stock_y = y + 50 + row * (stock_height + spacing)
            
            # Рисуем кнопку акции
            stock_rect = pygame.Rect(stock_x, stock_y, stock_width, stock_height)
            self.draw_stock_button(surface, stock_rect, stock)
    
    def draw_stock_button(self, surface, rect, stock_name):
        """Рисует кнопку акции."""
        pygame.draw.rect(surface, (60, 60, 100, 255), rect, border_radius=10)
        pygame.draw.rect(surface, (100, 100, 150, 255), rect, width=1, border_radius=10)
        
        font = self.game.font_manager.get_font('desc')
        text_surf = font.render(stock_name, True, TEXT_PRIMARY)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            for button in self.buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    self.game.update_navigation_state(button.text)
                    return True
            
            for button in self.tab_buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    for btn in self.tab_buttons:
                        btn.is_active = (btn.text.lower() == self.current_tab)
                    return True
        return False

class TabButton:
    """Кнопка вкладки (акции, недвижимость, криптовалюта)."""
    
    def __init__(self, rect, text, action, is_active=False):
        self.rect = rect
        self.text = text
        self.action = action
        self.is_active = is_active
    
    def draw(self, surface, font):
        """Рисует кнопку вкладки."""
        if self.is_active:
            color = (70, 70, 120, 255)  # Активный цвет
            text_color = (255, 255, 255, 255)
        else:
            color = (50, 50, 90, 255)  # Неактивный цвет
            text_color = (180, 180, 180, 255)
        
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (100, 100, 150, 255), self.rect, width=1, border_radius=10)
        
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def click(self):
        """Выполняет действие при клике."""
        if self.action:
            self.action()


# Магазины
class ShopCategory(Enum):
    ISLANDS = "Острова"  
    BOOSTERS = "Бустеры"
    NFT = "NFT"
    CARS = "Машины"
    UNIQUE_ITEMS = "Уникальные предметы"
    YACHTS = "Яхты"
    PLANES = "Самолёты"
    RESIDENCE = "Резиденция"
    JEWELRY = "Ювелирные изделия"

class BlackMarketCategory(Enum):
    WEAPONS = "Оружия"
    SUBSTANCES = "Вещества"
    PREPARATIONS = "Препараты"
    CONTRABAND = "Контрабанда"
    DANGEROUS_SERVICES = "Опасные услуги"
    CYBERIMPLANTS = "Кибермипланты"
    GAMBLING = "Азарт"
    EXOTICS = "Экзотика"
    RARITIES = "Редкости"
    LEGENDARIES = "Легендарки"

class Product:
    def __init__(self, id, name, price, description, category, stats=None):
        self.id = id
        self.name = name
        self.price = price
        self.description = description
        self.category = category
        self.stats = stats or {}

class ShopSystem:
    def __init__(self, game):
        self.game = game
        self.current_shop = None
        self.current_category = None
        self.products = []
        self.search_query = ""
        self.export = ExportDB()
        
    def load_products(self, category):
        """Загрузка продуктов из существующих таблиц базы данных"""
        try:
            # Очищаем предыдущие продукты
            self.products = []

            if self.current_shop == "light":
                if category == ShopCategory.ISLANDS:
                    islands = self.export.get_shop_islands()
                    if islands is not None:
                        self.products.append(Product(islands[0], islands[1], islands[2], islands[3], category.value))
                    else:
                        print("Таблица островов пуста или не найдена, используем демо-данные")
                        self.load_demo_products(category)

                elif category == ShopCategory.BOOSTERS:
                    boosters = self.export.get_shop_boosters()
                    if boosters is not None:
                        self.products.append(Product(boosters[0], boosters[1], boosters[2], boosters[3], category.value))
                        # Если boosters содержит несколько бустеров, добавьте их все
                        # Например: for booster in boosters: self.products.append(Product(...))
                    else:
                        print("Таблица бустеров пуста или не найдена, используем демо-данные")
                        self.load_demo_products(category)

                elif category == ShopCategory.NFT:
                    NFT = self.export.get_shop_nft()
                    if NFT is not None:
                        self.products.append(Product(NFT[0], NFT[1], NFT[2], NFT[3], category.value))
                    else:
                        print("Таблица NFT пуста или не найдена, используем демо-данные")
                        self.load_demo_products(category)

                elif category == ShopCategory.CARS:
                    cars = self.export.get_shop_cars()
                    if cars is not None:
                        stats = {"type": cars[4], "max_speed": cars[5]}
                        self.products.append(Product(cars[0], cars[1], cars[2], cars[3], category.value, cars[4]))
                    else:
                        print("Таблица машин пуста или не найдена, используем демо-данные")
                        self.load_demo_products(category)

                elif category == ShopCategory.UNIQUE_ITEMS:
                    items = self.export.get_shop_u_items()
                    if items is not None:
                        self.products.append(Product(items[0], items[1], items[2], items[3], category.value))
                    else:
                        print("Таблица уникальных предметов пуста или не найдена, используем демо-данные")
                        self.load_demo_products(category)

                elif category == ShopCategory.YACHTS:
                    yachts = self.export.get_shop_yachts()
                    if yachts is not None:
                        self.products.append(Product(yachts[0], yachts[1], yachts[2], yachts[3], category.value))
                    else:
                        print("Таблица яхт пуста или не найдена, используем демо-данные")
                        self.load_demo_products(category)

                elif category == ShopCategory.PLANES:
                    planes = self.export.get_shop_planes()
                    if planes is not None:
                        self.products.append(Product(planes[0], planes[1], planes[2], planes[3], category.value))
                    else:
                        print("Таблица самолетов пуста или не найдена, используем демо-данные")
                        self.load_demo_products(category)

                elif category == ShopCategory.JEWELRY:
                    jewelry = self.export.get_shop_jewelry()
                    if jewelry is not None:
                        self.products.append(Product(jewelry[0], jewelry[1], jewelry[2], jewelry[3], category.value))
                    else:
                        print("Таблица ювелирных изделий пуста или не найдена, используем демо-данные")
                        self.load_demo_products(category)   
                
                # Добавьте другие категории по аналогии
                else:
                    # Если таблицы не существует, используем демо-данные
                    print(f"Таблица для категории {category.value} не найдена, используем демо-данные")
                    self.load_demo_products(category)
                        
            else:  # Черный рынок
                pass
                        
            print(f"Загружено {len(self.products)} товаров для категории {category.value}")
            
        except Exception as e:
            print(f"Error loading products: {e}")
            # В случае ошибки загружаем демо-данные
            self.load_demo_products(category)
    
    def load_demo_products(self, category):
        """Демо-данные если база недоступна"""
        self.products = []
        
        if self.current_shop == "light":
            if category == ShopCategory.CARS:
                demo_cars = [
                    (1, "Sprint ZX", 12000, "Спортивный седан", {"type": "Седан", "max_speed": 220}),
                    (2, "Titan V8", 28000, "Мощный внедорожник", {"type": "Внедорожник", "max_speed": 260}),
                    (3, "Mercury Van", 18000, "Вместительный фургон", {"type": "Фургон", "max_speed": 180}),
                ]
                for car in demo_cars:
                    self.products.append(Product(car[0], car[1], car[2], car[3], category.value, car[4]))
        
        else:  # Черный рынок
            if category == BlackMarketCategory.WEAPONS:
                demo_weapons = [
                    (1, "Пистолет 'Тишина'", 5000, "Бесшумное оружие", {"danger": "Высокий", "type": "Огнестрел"}),
                    (2, "Боевой нож", 2000, "Острое лезвие", {"danger": "Средний", "type": "Холодное"}),
                ]
                for weapon in demo_weapons:
                    self.products.append(Product(weapon[0], weapon[1], weapon[2], weapon[3], category.value, weapon[4]))

    def buy_product(self, product_id):
        """Покупка товара с проверкой баланса"""
        product = next((p for p in self.products if p.id == product_id), None)
        if not product:
            return False
            
        # Проверяем баланс через ExportDB
        try:
            from coreLogic import ExportDB
            export_db = ExportDB()
            balance = export_db.balance()
            
            if balance >= product.price:
                # Логика покупки - обновляем баланс
                # В реальной реализации здесь будет вызов UpdateDB
                print(f"Покупка {product.name} за {product.price}$")
                return True
            else:
                print("Недостаточно средств")
                return False
                
        except Exception as e:
            print(f"Ошибка при покупке: {e}")
            return False

class ShopSelectionMenu:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.nav_buttons = []  # Добавляем навигационные кнопки
        self.initialize_ui()
    
    def initialize_ui(self):
        # Кнопки левой панели навигации
        nav_buttons = [
            ("Кликер", lambda: self.game.play_game(), False),
            ("Магазины", lambda: None, True),  # Активная кнопка
            ("Инвестиции", lambda: self.game.open_investments(), False),
            ("Бизнесы", lambda: self.game.open_businesses(), False),
            ("Профиль", lambda: self.game.open_profile(), False)
        ]
        
        # Создаем кнопки навигации
        button_width, button_height = 200, 60
        button_x = 50
        button_y_start = 150
        
        for i, (text, action, is_active) in enumerate(nav_buttons):
            rect = pygame.Rect(button_x, button_y_start + i * 70, button_width, button_height)
            self.nav_buttons.append(NavButton(rect, text, action, is_active))
        
        # Основные кнопки выбора магазина
        button_width, button_height = 300, 80
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # ПРАВИЛЬНО:
        self.buttons = [
            Button(
                pygame.Rect(center_x - 350, center_y - 50, button_width, button_height),
                "Светлый рынок",
                None,
                lambda: self.game.open_light_shop()  # Используем self.game
            ),
            Button(
                pygame.Rect(center_x + 50, center_y - 50, button_width, button_height),
                "Тёмный рынок", 
                None,
                lambda: self.game.open_black_market()  # Используем self.game
            )
        ]

    def open_light_shop(self):
        self.game.state = ScreenState.SHOP
    
    def open_black_market(self):
        self.game.state = ScreenState.BLACK_MARKET
    
    def draw(self, surface):
        # Рисуем левую панель навигации
        nav_panel_rect = pygame.Rect(30, 120, 240, 500)
        self.draw_panel(surface, nav_panel_rect, (30, 30, 50, 200))
        
        # Рисуем правую панель с контентом
        content_panel_rect = pygame.Rect(300, 120, 1100, 600)
        self.draw_panel(surface, content_panel_rect, (30, 30, 50, 200))
        
        # Рисуем кнопки навигации
        for button in self.nav_buttons:
            button.draw(surface, self.game.font_manager.get_font('button'))
        
        # Заголовок
        title = self.game.font_manager.get_rendered_text("Магазины", 'title', TEXT_PRIMARY, True)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 180))
        
        # Кнопки выбора магазина
        for button in self.buttons:
            icon_x = button.rect.x + 30
            icon_y = button.rect.centery - 25
            button.draw(surface, self.game.font_manager.get_font('button'), icon_x, icon_y)
        
        # Описание
        desc_text = "Выберите магазин для покупок"
        desc = self.game.font_manager.get_rendered_text(desc_text, 'subtitle', TEXT_SECONDARY)
        surface.blit(desc, (SCREEN_WIDTH//2 - desc.get_width()//2, 350))
    
    def draw_panel(self, surface, rect, color):
        """Рисует панель с закругленными углами."""
        pygame.draw.rect(surface, color, rect, border_radius=15)
        pygame.draw.rect(surface, (100, 100, 150, 255), rect, width=2, border_radius=15)

    def handle_event(self, event):
        """Обрабатывает события меню выбора магазина."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Проверяем клики по кнопкам навигации
            for button in self.nav_buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    # Обновляем состояние кнопок
                    for btn in self.nav_buttons:
                        btn.is_active = (btn.text == button.text)
                    return True
            
            # Проверяем клики по основным кнопкам
            for button in self.buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    return True
        
        return False

class LightShopMenu:
    def __init__(self, game):
        self.game = game
        self.category_buttons = []
        self.nav_buttons = []
        self.initialize_ui() 
    
    def initialize_ui(self):
        # Кнопки левой панели навигации
        nav_buttons = [
            ("Кликер", lambda: self.game.play_game(), False),
            ("Магазины", lambda: self.game.open_shop_selection(), True),  # Активная кнопка
            ("Инвестиции", lambda: self.game.open_investments(), False),
            ("Бизнесы", lambda: self.game.open_businesses(), False),
            ("Профиль", lambda: self.game.open_profile(), False)
        ]
        
        # Создаем кнопки навигации
        button_width, button_height = 200, 60
        button_x = 50
        button_y_start = 150
        
        for i, (text, action, is_active) in enumerate(nav_buttons):
            rect = pygame.Rect(button_x, button_y_start + i * 70, button_width, button_height)
            self.nav_buttons.append(NavButton(rect, text, action, is_active))
        
        # Кнопка назад
        self.back_button = Button(pygame.Rect(300, 50, 200, 60),"Назад в магазины",None, lambda: setattr(self.game, 'state', ScreenState.SHOP_SELECTION))
        
        # Кнопки категорий
        categories = list(ShopCategory)
        button_width, button_height = 250, 80
        start_x = 300
        start_y = 200
        spacing = 30
        
        for i, category in enumerate(categories):
            row = i // 3
            col = i % 3
            x = start_x + col * (button_width + spacing)
            y = start_y + row * (button_height + spacing)
            
            self.category_buttons.append(
                Button(
                    pygame.Rect(x, y, button_width, button_height),
                    category.value,
                    None,
                    lambda cat=category: self.open_category(cat)
                )
            )
    
    def open_category(self, category):
        self.game.shop_system.current_shop = "light"  # Устанавливаем магазин
        self.game.shop_system.current_category = category
        self.game.shop_system.load_products(category)
        self.game.state = ScreenState.SHOP_CATEGORY
    
    def draw(self, surface):
        # Рисуем левую панель навигации
        nav_panel_rect = pygame.Rect(30, 120, 240, 500)
        self.draw_panel(surface, nav_panel_rect, (30, 30, 50, 200))
        
        # Рисуем правую панель с контентом
        content_panel_rect = pygame.Rect(300, 120, 1100, 600)
        self.draw_panel(surface, content_panel_rect, (30, 30, 50, 200))
        
        # Рисуем кнопки навигации
        for button in self.nav_buttons:
            button.draw(surface, self.game.font_manager.get_font('button'))
        
        # Кнопка назад
        if self.back_button:
            icon_x = self.back_button.rect.x + 20
            icon_y = self.back_button.rect.centery - 12
            # Используем icon_renderer из game для отрисовки иконки
            self.game.icon_renderer.draw_back_icon(surface, icon_x, icon_y, 25)
            self.back_button.draw(surface, self.game.font_manager.get_font('button'), icon_x, icon_y)
        
        # Заголовок
        title = self.game.font_manager.get_rendered_text("Светлый рынок", 'title', (200, 200, 255), True)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        # Кнопки категорий
        for button in self.category_buttons:
            button.draw(surface, self.game.font_manager.get_font('button'), button.rect.x + 20, button.rect.centery - 15)
        
        # Инструкция
        instruction = self.game.font_manager.get_rendered_text("Выберите категорию товаров", 'subtitle', TEXT_SECONDARY)
        surface.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, 550))
    
    def draw_panel(self, surface, rect, color):
        """Рисует панель с закругленными углами."""
        pygame.draw.rect(surface, color, rect, border_radius=15)
        pygame.draw.rect(surface, (100, 100, 150, 255), rect, width=2, border_radius=15)

    def handle_event(self, event):
        """Обрабатывает события светлого магазина."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Проверяем клики по кнопкам навигации
            for button in self.nav_buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    return True
            
            # Проверяем клики по кнопке назад (только если она существует)
            if self.back_button and self.back_button.rect.collidepoint(mouse_pos):
                self.back_button.click()
                return True
            
            # Проверяем клики по кнопкам категорий
            for button in self.category_buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    return True
        
        return False

class LightCategoryProductsMenu:
    def __init__(self, game):
        self.game = game
        self.nav_buttons = []
        self.product_buttons = []
        self.search_box = pygame.Rect(300, 180, 400, 40)
        self.search_active = False
        self.search_text = ""
        self.initialize_ui()
    
    def initialize_ui(self):
        # Кнопки левой панели навигации
        nav_buttons = [
            ("Кликер", lambda: self.game.play_game(), False),
            ("Магазины", lambda: self.game.open_shop_selection(), True),
            ("Инвестиции", lambda: self.game.open_investments(), False),
            ("Бизнесы", lambda: self.game.open_businesses(), False),
            ("Профиль", lambda: self.game.open_profile(), False)
        ]
        
        # Создаем кнопки навигации
        button_width, button_height = 200, 60
        button_x = 50
        button_y_start = 150
        
        for i, (text, action, is_active) in enumerate(nav_buttons):
            rect = pygame.Rect(button_x, button_y_start + i * 70, button_width, button_height)
            self.nav_buttons.append(NavButton(rect, text, action, is_active))

        # Кнопка назад - возврат в СВЕТЛЫЙ магазин
        self.back_button = Button(
            pygame.Rect(300, 50, 200, 60),
            "Назад",
            None,
            lambda: setattr(self.game, 'state', ScreenState.SHOP)
        )
    
    def update_products(self):
        """Обновляет кнопки товаров на основе загруженных продуктов"""
        self.product_buttons = []
        
        if not self.game.shop_system.products:
            # Если товаров нет, создаем сообщение
            return
        
        # Создаем кнопки для каждого товара
        product_width, product_height = 300, 80
        start_x = 320
        start_y = 250
        spacing = 20
        
        for i, product in enumerate(self.game.shop_system.products):
            # Фильтрация по поисковому запросу
            if self.search_text and self.search_text.lower() not in product.name.lower():
                continue
                
            row = i // 3
            col = i % 3
            x = start_x + col * (product_width + spacing)
            y = start_y + row * (product_height + spacing)
            
            # Если товаров слишком много, добавляем прокрутку
            if y > 600:  # Максимальная высота
                continue
                
            self.product_buttons.append(
                ProductButton(
                    pygame.Rect(x, y, product_width, product_height),
                    product,
                    lambda p=product: self.buy_product(p.id)
                )
            )
    
    def buy_product(self, product_id):
        """Покупка товара"""
        if self.game.shop_system.buy_product(product_id):
            print("Товар куплен!")
            # Обновляем отображение
            self.update_products()
    
    def draw(self, surface):
        # Рисуем левую панель навигации
        nav_panel_rect = pygame.Rect(30, 120, 240, 500)
        self.draw_panel(surface, nav_panel_rect, (30, 30, 50, 200))
        
        # Рисуем правую панель с контентом
        content_panel_rect = pygame.Rect(300, 120, 1100, 600)
        self.draw_panel(surface, content_panel_rect, (30, 30, 50, 200))
        
        # Рисуем кнопки навигации
        for button in self.nav_buttons:
            button.draw(surface, self.game.font_manager.get_font('button'))
        
        # Кнопка назад
        if self.back_button:
            icon_x = self.back_button.rect.x + 20
            icon_y = self.back_button.rect.centery - 12
            self.game.icon_renderer.draw_back_icon(surface, icon_x, icon_y, 25)
            self.back_button.draw(surface, self.game.font_manager.get_font('button'), icon_x, icon_y)
        
        # Заголовок категории
        category_name = self.game.shop_system.current_category.value if self.game.shop_system.current_category else "Категория"
        title = self.game.font_manager.get_rendered_text(category_name, 'title', TEXT_PRIMARY, True)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        # Поле поиска
        self.draw_search_box(surface)
        
        # Обновляем и рисуем товары
        self.update_products()
        for button in self.product_buttons:
            button.draw(surface, self.game.font_manager.get_font('desc'))
        
        # Сообщение если товаров нет
        if not self.product_buttons and not self.search_text:
            no_products_text = "Товары не найдены"
            text_surf = self.game.font_manager.get_rendered_text(no_products_text, 'subtitle', TEXT_SECONDARY)
            surface.blit(text_surf, (SCREEN_WIDTH//2 - text_surf.get_width()//2, 300))
    
    def draw_search_box(self, surface):
        """Рисует поле поиска"""
        # Фон поля поиска
        pygame.draw.rect(surface, (40, 40, 70, 255), self.search_box, border_radius=10)
        pygame.draw.rect(surface, (100, 100, 150, 255), self.search_box, width=1, border_radius=10)
        
        # Текст поиска
        search_font = self.game.font_manager.get_font('desc')
        search_surf = search_font.render(self.search_text + ("|" if self.search_active else ""), True, TEXT_PRIMARY)
        surface.blit(search_surf, (self.search_box.x + 10, self.search_box.y + 10))
        
        # Подсказка
        if not self.search_text and not self.search_active:
            hint_surf = search_font.render("Поиск...", True, TEXT_TERTIARY)
            surface.blit(hint_surf, (self.search_box.x + 10, self.search_box.y + 10))
    
    def draw_panel(self, surface, rect, color):
        """Рисует панель с закругленными углами"""
        pygame.draw.rect(surface, color, rect, border_radius=15)
        pygame.draw.rect(surface, (100, 100, 150, 255), rect, width=2, border_radius=15)

    def handle_event(self, event):
        """Обрабатывает события категории товаров СВЕТЛОГО магазина"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Проверяем клики по кнопкам навигации
            for button in self.nav_buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    return True
            
            # Проверяем клики по кнопке назад
            if self.back_button.rect.collidepoint(mouse_pos):
                self.back_button.click()
                return True
            
            # Проверяем клики по товарам
            for button in self.product_buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    return True
            
            # Активация поля поиска
            if self.search_box.collidepoint(mouse_pos):
                self.search_active = True
            else:
                self.search_active = False
                
        elif event.type == pygame.KEYDOWN and self.search_active:
            if event.key == pygame.K_BACKSPACE:
                self.search_text = self.search_text[:-1]
            elif event.key == pygame.K_RETURN:
                self.search_active = False
            else:
                # Добавляем символ (ограничиваем длину)
                if len(self.search_text) < 30:
                    self.search_text += event.unicode
        
        return False

class ProductButton:
    """Кнопка товара"""
    
    def __init__(self, rect, product, action):
        self.rect = rect
        self.product = product
        self.action = action
        self.hovered = False
    
    def draw(self, surface, font):
        """Рисует кнопку товара"""
        # Фон товара
        color = (60, 60, 100, 255) if self.hovered else (40, 40, 70, 255)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (100, 100, 150, 255), self.rect, width=1, border_radius=10)
        
        # Название товара
        name_surf = font.render(self.product.name, True, TEXT_PRIMARY)
        surface.blit(name_surf, (self.rect.x + 10, self.rect.y + 10))
        
        # Цена
        price_surf = font.render(f"{self.product.price}$", True, PURPLE_ACCENT)
        surface.blit(price_surf, (self.rect.x + 10, self.rect.y + 40))
        
        # Описание (если помещается)
        if len(self.product.description) < 50:
            desc_surf = font.render(self.product.description, True, TEXT_SECONDARY)
            surface.blit(desc_surf, (self.rect.x + 150, self.rect.y + 25))
    
    def click(self):
        """Обрабатывает клик по товару"""
        if self.action:
            self.action()

class BlackMarketCategoryProductsMenu(LightCategoryProductsMenu):
    """Категория товаров черного рынка (наследуется от светлой версии)"""
    
    def __init__(self, game):
        super().__init__(game)
        # Переопределяем кнопку назад для черного рынка
        self.back_button = Button(
            pygame.Rect(300, 50, 200, 60),
            "Назад",
            None,
            lambda: setattr(self.game, 'state', ScreenState.BLACK_MARKET)
        )
    
    def draw(self, surface):
        # Темный стиль для черного рынка
        nav_panel_rect = pygame.Rect(30, 120, 240, 500)
        self.draw_panel(surface, nav_panel_rect, (30, 30, 50, 200))
        
        # Темная панель для контента
        content_panel_rect = pygame.Rect(300, 120, 1100, 600)
        dark_panel = GradientGenerator.create_rounded_rect(
            (content_panel_rect.width, content_panel_rect.height), 
            [(20, 5, 10, 200), (15, 2, 8, 200), (10, 1, 5, 200)], 
            PANEL_BORDER_RADIUS
        )
        surface.blit(dark_panel, content_panel_rect.topleft)
        pygame.draw.rect(surface, (100, 20, 20, 255), content_panel_rect, width=2, border_radius=15)
        
        # Остальная отрисовка как в родительском классе
        for button in self.nav_buttons:
            button.draw(surface, self.game.font_manager.get_font('button'))
        
        if self.back_button:
            icon_x = self.back_button.rect.x + 20
            icon_y = self.back_button.rect.centery - 12
            self.game.icon_renderer.draw_back_icon(surface, icon_x, icon_y, 25)
            self.back_button.draw(surface, self.game.font_manager.get_font('button'), icon_x, icon_y)
        
        # Красный заголовок для черного рынка
        category_name = self.game.shop_system.current_category.value if self.game.shop_system.current_category else "Категория"
        title = self.game.font_manager.get_rendered_text(category_name, 'title', (220, 20, 20), True)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        self.draw_search_box(surface)
        self.update_products()
        
        for button in self.product_buttons:
            # Темный стиль для кнопок товаров
            self.draw_dark_product_button(surface, button)
        
        if not self.product_buttons and not self.search_text:
            no_products_text = "Товары не найдены"
            text_surf = self.game.font_manager.get_rendered_text(no_products_text, 'subtitle', (200, 100, 100))
            surface.blit(text_surf, (SCREEN_WIDTH//2 - text_surf.get_width()//2, 300))
    
    def draw_dark_product_button(self, surface, button):
        """Рисует кнопку товара в темном стиле"""
        color = (80, 20, 20, 255) if button.hovered else (50, 10, 10, 255)
        pygame.draw.rect(surface, color, button.rect, border_radius=10)
        pygame.draw.rect(surface, (150, 50, 50, 255), button.rect, width=1, border_radius=10)
        
        font = self.game.font_manager.get_font('desc')
        name_surf = font.render(button.product.name, True, (255, 200, 200))
        surface.blit(name_surf, (button.rect.x + 10, button.rect.y + 10))
        
        price_surf = font.render(f"{button.product.price}$", True, (255, 100, 100))
        surface.blit(price_surf, (button.rect.x + 10, button.rect.y + 40))
        
        if len(button.product.description) < 30:
            desc_surf = font.render(button.product.description, True, (200, 150, 150))
            surface.blit(desc_surf, (button.rect.x + 150, button.rect.y + 25))

# Аналогичный класс для черного рынка с темным стилем
class BlackMarketMenu:
    def __init__(self, game):
        self.game = game
        self.category_buttons = []
        self.nav_buttons = []
        self.initialize_ui()
    
    def initialize_ui(self):
        # Кнопки левой панели навигации
        nav_buttons = [
            ("Кликер", lambda: self.game.play_game(), False),
            ("Магазины", lambda: self.game.open_shop_selection(), True),  # Активная кнопка
            ("Инвестиции", lambda: self.game.open_investments(), False),
            ("Бизнесы", lambda: self.game.open_businesses(), False),
            ("Профиль", lambda: self.game.open_profile(), False)
        ]
        
        # Создаем кнопки навигации
        button_width, button_height = 200, 60
        button_x = 50
        button_y_start = 150
        
        for i, (text, action, is_active) in enumerate(nav_buttons):
            rect = pygame.Rect(button_x, button_y_start + i * 70, button_width, button_height)
            self.nav_buttons.append(NavButton(rect, text, action, is_active))
        
        # Кнопка назад
        self.back_button = Button(pygame.Rect(300, 50, 200, 60),"Назад в магазины",None, lambda: setattr(self.game, 'state', ScreenState.SHOP_SELECTION))
        
        # Кнопки категорий черного рынка
        categories = list(BlackMarketCategory)
        button_width, button_height = 280, 70
        start_x = 250
        start_y = 180
        spacing = 20
        
        for i, category in enumerate(categories):
            row = i // 3
            col = i % 3
            x = start_x + col * (button_width + spacing)
            y = start_y + row * (button_height + spacing)
            
            self.category_buttons.append(
                Button(
                    pygame.Rect(x, y, button_width, button_height),
                    category.value,
                    None,
                    lambda cat=category: self.open_category(cat)
                )
            )

    def open_category(self, category):
        self.game.shop_system.current_shop = "black"  # Устанавливаем рынок
        self.game.shop_system.current_category = category
        self.game.shop_system.load_products(category)
        self.game.state = ScreenState.BLACK_MARKET_CATEGORY
    
    def draw(self, surface):
        # Рисуем левую панель навигации
        nav_panel_rect = pygame.Rect(30, 120, 240, 500)
        self.draw_panel(surface, nav_panel_rect, (30, 30, 50, 200))
        
        # Темная панель для черного рынка
        dark_panel_rect = pygame.Rect(300, 120, 1100, 600)
        dark_panel = GradientGenerator.create_rounded_rect(
            (dark_panel_rect.width, dark_panel_rect.height), 
            [(20, 5, 10, 200), (15, 2, 8, 200), (10, 1, 5, 200)], 
            PANEL_BORDER_RADIUS
        )
        surface.blit(dark_panel, dark_panel_rect.topleft)
        pygame.draw.rect(surface, (100, 20, 20, 255), dark_panel_rect, width=2, border_radius=15)
        
        # Рисуем кнопки навигации
        for button in self.nav_buttons:
            button.draw(surface, self.game.font_manager.get_font('button'))
        
        # Кнопка назад
        icon_x = self.back_button.rect.x + 20
        icon_y = self.back_button.rect.centery - 12
        self.back_button.draw(surface, self.game.font_manager.get_font('button'), icon_x, icon_y)
        
        # Заголовок с красным акцентом
        title = self.game.font_manager.get_rendered_text("Чёрный рынок", 'title', (220, 20, 20), True)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        # Кнопки категорий
        for button in self.category_buttons:
            button.draw(surface, self.game.font_manager.get_font('button'), button.rect.x + 20, button.rect.centery - 15)
    
    def draw_panel(self, surface, rect, color):
        """Рисует панель с закругленными углами."""
        pygame.draw.rect(surface, color, rect, border_radius=15)
        pygame.draw.rect(surface, (100, 100, 150, 255), rect, width=2, border_radius=15)

    def handle_event(self, event):
        """Обрабатывает события черного рынка."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Проверяем клики по кнопкам навигации
            for button in self.nav_buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    return True
            
            # Проверяем клики по кнопке назад (с обработкой исключений)
            if self.back_button.rect.collidepoint(mouse_pos):
                try:
                    self.back_button.click()
                    return True
                except Exception as e:
                    print(f"Ошибка при возврате из черного рынка: {e}")
                    # Принудительно возвращаемся в меню выбора магазина
                    self.game.state = ScreenState.SHOP_SELECTION
                    return True
            
            # Проверяем клики по кнопкам категорий (с обработкой исключений)
            for button in self.category_buttons:
                if button.rect.collidepoint(mouse_pos):
                    try:
                        button.click()
                        return True
                    except Exception as e:
                        print(f"Ошибка при открытии категории черного рынка: {e}")
                        # Загружаем демо-данные при ошибке
                        self.game.shop_system.load_demo_products(button.text)
                        self.game.state = ScreenState.BLACK_MARKET_CATEGORY
                        return True
        return False
    
# Класс для бизнеса

class Business:
    def __init__(self, id, name, base_price, base_income, description, category, 
                 tier=BusinessTier.STARTUP, max_level=20):
        self.id = id
        self.name = name
        self.base_price = base_price
        self.base_income = base_income
        self.description = description
        self.category = category
        self.tier = tier
        self.level = 1
        self.max_level = max_level
        self.is_owned = False
        self.is_active = True
        self.employees = []
        self.upgrades = []
        self.stats = BusinessStats()
        
        # Визуальные свойства
        self.icon = None
        self.color: Optional[tuple] = None  # Явно указываем тип
        self.particles = []
        
        self.calculate_current_stats()
    
    def calculate_current_stats(self):
        """Пересчитывает текущую статистику на основе уровня и улучшений"""
        level_multiplier = 1 + (self.level - 1) * 0.15
        upgrade_multiplier = 1 + len([u for u in self.upgrades if u.active]) * 0.1
        
        self.stats.income = self.base_income * level_multiplier * upgrade_multiplier
        self.stats.expenses = self.base_income * 0.3 * level_multiplier
        self.stats.employee_count = max(1, int(self.level * 2))
        
        # Специфичные для категории расчеты
        if self.category == BusinessCategory.LIGHT:
            self.stats.risk = max(5, 20 - self.level)
            self.stats.legal_status = min(100, 80 + self.level)
        else:  # DARK
            self.stats.risk = min(95, 30 + self.level * 3)
            self.stats.legal_status = max(5, 100 - self.level * 4)
    
    def get_upgrade_cost(self):
        """Стоимость улучшения"""
        return int(self.base_price * (1.5 ** (self.level - 1)))
    
    def get_sell_price(self):
        """Цена продажи (70% от вложений)"""
        total_investment = self.base_price
        for level in range(2, self.level + 1):
            total_investment += int(self.base_price * (1.5 ** (level - 2)))
        return int(total_investment * 0.7)
    
    def upgrade(self):
        """Улучшение бизнеса"""
        if self.level < self.max_level and self.is_owned:
            self.level += 1
            self.calculate_current_stats()
            return True
        return False
    
    def add_employee(self, employee):
        """Добавление сотрудника"""
        if len(self.employees) < self.stats.employee_count * 2:  # Максимум в 2 раза больше базового
            self.employees.append(employee)
            self.calculate_current_stats()
            return True
        return False
    
    def add_upgrade(self, upgrade):
        """Добавление улучшения"""
        if upgrade not in self.upgrades:
            self.upgrades.append(upgrade)
            self.calculate_current_stats()
            return True
        return False
    
    def get_net_income(self):
        """Чистый доход"""
        employee_cost = len(self.employees) * 500  # Базовая зарплата
        return self.stats.income - self.stats.expenses - employee_cost
    
    def update_particles(self, dt):
        """Обновление частиц для анимации"""
        for particle in self.particles[:]:
            particle['lifetime'] -= dt
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['alpha'] = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
        
        # Добавляем новые частицы
        if random.random() < 0.3 and self.is_active:
            self.particles.append({
                'x': random.uniform(0, 100),
                'y': random.uniform(0, 100),
                'vx': random.uniform(-10, 10),
                'vy': random.uniform(-10, 10),
                'lifetime': random.uniform(1, 3),
                'max_lifetime': 3,
                'alpha': 255,
                'color': self.color or (100, 200, 255)
            })

class Employee:
    def __init__(self, name, specialization, skill_level, salary):
        self.name = name
        self.specialization = specialization
        self.skill_level = skill_level  # 1-10
        self.salary = salary
        self.productivity = skill_level * 10  # 10-100%
        self.morale = 100  # 0-100%

class BusinessUpgrade:
    def __init__(self, name, description, cost, effect_type, effect_value):
        self.name = name
        self.description = description
        self.cost = cost
        self.effect_type = effect_type  # 'income', 'efficiency', 'risk', etc.
        self.effect_value = effect_value
        self.active = False
    
    def activate(self, business):
        """Активация улучшения"""
        if not self.active:
            self.active = True
            business.calculate_current_stats()
            return True
        return False

class BusinessManager:
    """Менеджер для управления всеми бизнесами"""
    
    def __init__(self, game):
        self.game = game
        self.businesses = []
        self.owned_businesses = []
        self.total_income = 0
        self.total_expenses = 0
        self.last_income_time = pygame.time.get_ticks()
        
        self.load_businesses()
        self.load_owned_businesses()

    def load_owned_businesses(self):
        """Загружает купленные бизнесы"""
        self.owned_businesses = [b for b in self.businesses if b.is_owned]
        print(f"Загружено {len(self.owned_businesses)} купленных бизнесов")
    
    def load_businesses(self):
        """Загрузка бизнесов из базы данных или создание по умолчанию"""
        try:
            # Сначала пытаемся загрузить из базы
            self.load_from_database()
            
            # Если в базе нет бизнесов, создаем по умолчанию
            if not self.businesses:
                print("База данных пуста, создаем бизнесы по умолчанию")
                self.create_default_businesses()
                self.save_to_database()
                
        except Exception as e:
            print(f"Ошибка загрузки бизнесов: {e}")
            print("Создаем бизнесы по умолчанию")
            self.create_default_businesses()
            self.save_to_database()
    
    def create_default_businesses(self):
        """Создание бизнесов по умолчанию"""
        print("Создание бизнесов по умолчанию...")
        
        # Очищаем существующие бизнесы
        self.businesses = []
        self.owned_businesses = []
        # Светлые бизнесы
        light_businesses = [
            ("Продажа", 10000, 100, "Розничная торговля", BusinessCategory.LIGHT),
            ("Строительство", 50000, 500, "Строительная компания", BusinessCategory.LIGHT),
            ("IT-стартап", 100000, 1000, "Технологический стартап", BusinessCategory.LIGHT),
            ("Электросетевая компания", 500000, 5000, "Энергетика", BusinessCategory.LIGHT),
            ("Сеть кофеен", 1000000, 10000, "Франшиза общепита", BusinessCategory.LIGHT),
            ("Биотех Лаборатория", 5000000, 50000, "Научные исследования", BusinessCategory.LIGHT),
            ("Образовательная платформа", 10000000, 100000, "Онлайн образование", BusinessCategory.LIGHT),
            ("Технопарк", 50000000, 500000, "Технологический парк", BusinessCategory.LIGHT),
            ("Автопром", 100000000, 1000000, "Автомобилестроение", BusinessCategory.LIGHT),
            ("Кибербезопасность", 500000000, 5000000, "Защита информации", BusinessCategory.LIGHT),
            ("Медицинский центр", 1000000000, 10000000, "Медицинские услуги", BusinessCategory.LIGHT),
            ("Робототехника", 5000000000, 50000000, "Роботостроение", BusinessCategory.LIGHT),
            ("Космический туризм", 10000000000, 100000000, "Космические полеты", BusinessCategory.LIGHT),
            ("AI разработки", 50000000000, 500000000, "Искусственный интеллект", BusinessCategory.LIGHT),
            ("Банк", 100000000000, 1000000000, "Финансовый институт", BusinessCategory.LIGHT),
            ("Нефтегазовая компания", 500000000000, 5000000000, "Добыча ресурсов", BusinessCategory.LIGHT),
            ("Трейдинг", 1000000000000, 10000000000, "Финансовые операции", BusinessCategory.LIGHT),
            ("Оборонное предприятие", 5000000000000, 50000000000, "Военная промышленность", BusinessCategory.LIGHT),
            ("УГМК", 10000000000000, 100000000000, "Горнодобывающая компания", BusinessCategory.LIGHT)
        ]
        
        # Темные бизнесы
        dark_businesses = [
            ("Кибер-мошенничество", 15000, 150, "Нелегальные онлайн схемы", BusinessCategory.DARK),
            ("Теневой банкинг", 75000, 750, "Незаконные финансовые операции", BusinessCategory.DARK),
            ("Контрабанда", 150000, 1500, "Нелегальная перевозка товаров", BusinessCategory.DARK),
            ("Пиратское ПО", 750000, 7500, "Распространение пиратского софта", BusinessCategory.DARK),
            ("Нелегальные ставки", 1500000, 15000, "Подпольные тотализаторы", BusinessCategory.DARK),
            ("Фальшивые документы", 7500000, 75000, "Подделка документов", BusinessCategory.DARK),
            ("Нелегальный импорт/экспорт", 15000000, 150000, "Контрабанда товаров", BusinessCategory.DARK),
            ("Теневой майнинг", 75000000, 750000, "Незаконная добыча криптовалюты", BusinessCategory.DARK),
            ("Нарко-картель", 150000000, 1500000, "Нелегальные вещества", BusinessCategory.DARK),
            ("Отмывание денег", 750000000, 7500000, "Легализация незаконных доходов", BusinessCategory.DARK),
            ("Подпольный хостинг", 1500000000, 15000000, "Нелегальные серверы", BusinessCategory.DARK),
            ("Нелегальный аутсорсинг", 7500000000, 75000000, "Теневой найм", BusinessCategory.DARK),
            ("Темный арбитраж", 15000000000, 150000000, "Незаконные посреднические услуги", BusinessCategory.DARK),
            ("Частная военная компания", 75000000000, 750000000, "Нелегальные военные операции", BusinessCategory.DARK)
        ]
        
        # Создаем бизнесы
        business_id = 1
        for name, price, income, desc, category in light_businesses:
            business = Business(business_id, name, price, income, desc, category)
            business.color = (100, 200, 255)  # Голубой для светлых
            self.businesses.append(business)
            business_id += 1
        
        for name, price, income, desc, category in dark_businesses:
            business = Business(business_id, name, price, income, desc, category)
            business.color = (255, 100, 100)  # Красный для темных
            self.businesses.append(business)
            business_id += 1
        
        print(f"Создано {len(self.businesses)} бизнесов: {len(light_businesses)} светлых, {len(dark_businesses)} темных")
    
    def load_from_database(self):
        """Загрузка из базы данных"""
        try:
            import os
            # Создаем папку data если не существует
            if not os.path.exists('data'):
                os.makedirs('data')
                
            connect = sqlite3.connect('data/business.db')
            cursor = connect.cursor()
            
            # Создаем таблицу если не существует
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS businesses (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    base_price INTEGER,
                    base_income INTEGER,
                    description TEXT,
                    category TEXT,
                    level INTEGER DEFAULT 1,
                    is_owned BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            cursor.execute("SELECT * FROM businesses")
            rows = cursor.fetchall()
            print(f"Загружено {len(rows)} бизнесов из базы данных")
            
            for row in rows:
                try:
                    business = Business(row[0], row[1], row[2], row[3], row[4], 
                                    BusinessCategory(row[5]))
                    business.level = row[6]
                    business.is_owned = bool(row[7])
                    business.is_active = bool(row[8])
                    
                    if business.is_owned:
                        self.owned_businesses.append(business)
                    
                    self.businesses.append(business)
                except Exception as e:
                    print(f"Ошибка загрузки бизнеса {row[0]}: {e}")
            
            connect.close()
        except Exception as e:
            print(f"Ошибка загрузки бизнесов из базы: {e}")
            raise  # Пробрасываем исключение дальше
    
    def save_to_database(self):
        """Сохранение в базу данных"""
        try:
            connect = sqlite3.connect('data/business.db')
            cursor = connect.cursor()
            
            cursor.execute('DELETE FROM businesses')
            
            for business in self.businesses:
                cursor.execute('''
                    INSERT INTO businesses 
                    (id, name, base_price, base_income, description, category, level, is_owned, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (business.id, business.name, business.base_price, business.base_income,
                     business.description, business.category.value, business.level,
                     business.is_owned, business.is_active))
            
            connect.commit()
            connect.close()
        except Exception as e:
            print(f"Ошибка сохранения бизнесов: {e}")
    
    def buy_business(self, business_id):
        """Покупка бизнеса с улучшенной обработкой"""
        business = next((b for b in self.businesses if b.id == business_id), None)
        if not business or business.is_owned:
            return False
        
        # Проверяем баланс
        from coreLogic import ExportDB
        export_db = ExportDB()
        balance = export_db.balance()
        
        if balance >= business.base_price:
            try:
                # Логика покупки
                business.is_owned = True
                business.is_active = True
                self.owned_businesses.append(business)
                
                # Обновляем баланс
                self.update_balance(-business.base_price)
                
                # Сохраняем в БД
                self.save_to_database()
                
                print(f"Бизнес '{business.name}' успешно куплен!")
                return True
                
            except Exception as e:
                print(f"Ошибка при покупке бизнеса: {e}")
                return False
        
        print("Недостаточно средств для покупки бизнеса")
        return False
    
    def sell_business(self, business_id):
        """Продажа бизнеса"""
        business = next((b for b in self.owned_businesses if b.id == business_id), None)
        if not business:
            return False
        
        sell_price = business.get_sell_price()
        
        # Логика продажи
        business.is_owned = False
        business.is_active = False
        self.owned_businesses.remove(business)
        
        # Обновляем баланс
        self.update_balance(sell_price)
        
        self.save_to_database()
        return True
    
    def upgrade_business(self, business_id):
        """Улучшение бизнеса"""
        business = next((b for b in self.owned_businesses if b.id == business_id), None)
        if not business:
            return False
        
        upgrade_cost = business.get_upgrade_cost()
        
        # Проверяем баланс
        from coreLogic import ExportDB
        export_db = ExportDB()
        balance = export_db.balance()
        
        if balance >= upgrade_cost and business.upgrade():
            # Обновляем баланс
            self.update_balance(-upgrade_cost)
            
            self.save_to_database()
            return True
        
        return False
    
    def update_balance(self, amount):
        """Обновление баланса через UpdateDB"""
        try:
            from coreLogic import UpdateDB
            # Здесь должна быть логика обновления баланса
            # Временно просто выводим в консоль
            print(f"Обновление баланса на: {amount}$")
        except:
            print("Ошибка обновления баланса")
    
    def update(self, dt):
        """Обновление всех бизнесов"""
        current_time = pygame.time.get_ticks()
        
        # Начисляем доход каждые 10 секунд
        if current_time - self.last_income_time > 10000:  # 10 секунд
            self.collect_income()
            self.last_income_time = current_time
        
        # Обновляем анимации
        for business in self.owned_businesses:
            if business.is_active:
                business.update_particles(dt)
    
    def collect_income(self):
        """Сбор дохода со всех активных бизнесов"""
        total_income = 0
        
        for business in self.owned_businesses:
            if business.is_active:
                net_income = business.get_net_income()
                total_income += net_income
        
        if total_income > 0:
            self.update_balance(total_income)
            print(f"Собран доход с бизнесов: {total_income}$")
    
    def get_business_by_category(self, category):
        """Получение бизнесов по категории"""
        filtered_businesses = [b for b in self.businesses if b.category == category]
        print(f"Бизнесы категории {category}: {len(filtered_businesses)} шт.")
        for business in filtered_businesses:
            print(f"  - {business.name} (ID: {business.id})")
        return filtered_businesses
    
    def get_total_net_income(self):
        """Общий чистый доход в секунду"""
        total = 0
        for business in self.owned_businesses:
            if business.is_active:
                total += business.get_net_income()
        return total / 10  # Приводим к доходу в секунду

class BusinessActionButton:
    """Специальная кнопка для действий с бизнесом"""
    
    def __init__(self, rect, text, action, button_type):
        self.rect = rect
        self.text = text
        self.action = action
        self.button_type = button_type  # "buy", "upgrade", "sell", "toggle", "back"
        self.hovered = False
    
    def draw(self, surface, font):
        """Отрисовка кнопки"""
        # Цвет в зависимости от типа кнопки
        if self.button_type == "buy":
            base_colors = [(0, 150, 0), (0, 120, 0), (0, 100, 0)]
        elif self.button_type == "upgrade":
            base_colors = [(0, 100, 200), (0, 80, 180), (0, 60, 160)]
        elif self.button_type == "sell":
            base_colors = [(200, 100, 0), (180, 80, 0), (160, 60, 0)]
        elif self.button_type == "toggle":
            base_colors = [(150, 150, 0), (120, 120, 0), (100, 100, 0)]
        else:  # back
            base_colors = [(100, 100, 100), (80, 80, 80), (60, 60, 60)]
        
        # Добавляем альфа-канал
        colors = [(c[0], c[1], c[2], 200) for c in base_colors]
        
        if self.hovered:
            # Увеличиваем яркость при наведении
            colors = [(min(c[0] + 30, 255), min(c[1] + 30, 255), min(c[2] + 30, 255), c[3]) for c in colors]
        
        # Создаем поверхность для кнопки
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Рисуем градиентный фон
        gradient = GradientGenerator.create_vertical_gradient(
            (self.rect.width, self.rect.height),
            colors
        )
        button_surface.blit(gradient, (0, 0))
        
        # Рисуем закругленные углы
        mask = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, self.rect.width, self.rect.height), 
                        border_radius=10)
        button_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        # Рамка
        pygame.draw.rect(button_surface, (255, 255, 255, 150), 
                        (0, 0, self.rect.width, self.rect.height), 
                        width=2, border_radius=10)
        
        # Текст
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        button_surface.blit(text_surf, text_rect)
        
        # Отображаем кнопку на основной поверхности
        surface.blit(button_surface, self.rect.topleft)
    
    def is_hovered(self, mouse_pos):
        """Проверяет, наведена ли мышь на кнопку"""
        return self.rect.collidepoint(mouse_pos)
    
    def click(self):
        """Обработка клика"""
        if self.action:
            self.action()

# Обновленный BusinessMenu с улучшенной графикой
class AdvancedBusinessMenu:
    def __init__(self, game):
        self.game = game
        self.business_manager = BusinessManager(game)
        self.current_category = BusinessCategory.LIGHT
        self.selected_business = None
        self.business_buttons = []
        self.category_buttons = []
        self.nav_buttons = []
        self.action_buttons = []
        self.scroll_offset = 0
        self.max_scroll = 0
        self.view_mode = "owned"
        
        self.initialize_ui()
        self.update_business_buttons()
    
    def initialize_ui(self):
        """Инициализация UI"""
        # Навигационные кнопки
        nav_buttons = [
            ("Кликер", lambda: self.game.play_game(), False),
            ("Магазины", lambda: self.game.open_shop_selection(), False),
            ("Инвестиции", lambda: self.game.open_investments(), False),
            ("Бизнесы", lambda: None, True),
            ("Профиль", lambda: self.game.open_profile(), False)
        ]
        
        button_width, button_height = 200, 60
        button_x = 50
        button_y_start = 150
        
        for i, (text, action, is_active) in enumerate(nav_buttons):
            rect = pygame.Rect(button_x, button_y_start + i * 70, button_width, button_height)
            self.nav_buttons.append(NavButton(rect, text, action, is_active))
        
        # Кнопки категорий
        categories = [
            (BusinessCategory.LIGHT, "💡 Светлые"),
            (BusinessCategory.DARK, "🌙 Тёмные"),
        ]

        category_width, category_height = 250, 60
        start_x = 320
        start_y = 100

        for i, (category, text) in enumerate(categories):
            rect = pygame.Rect(start_x + i * (category_width + 20), start_y, 
                            category_width, category_height)
            is_active = (category == self.current_category)
            button = Button(rect, text, None, lambda cat=category: self.set_category(cat))
            button.is_active = is_active
            self.category_buttons.append(button)
        
        # Кнопки режима просмотра
        self.view_owned_button = Button(
            pygame.Rect(320, 170, 200, 40),
            "Мои бизнесы",
            None,
            lambda: self.set_view_mode("owned")
        )
        self.view_available_button = Button(
            pygame.Rect(530, 170, 200, 40),
            "Доступные",
            None,
            lambda: self.set_view_mode("available")
        )
        
        # Кнопка назад
        self.back_button = Button(
            pygame.Rect(300, 50, 200, 60),
            "Назад",
            None,
            lambda: self.game.back_to_menu()
        )

    def update_action_buttons(self):
        """Обновляет кнопки действий для выбранного бизнеса"""
        self.action_buttons = []
        
        if not self.selected_business:
            return
            
        business = self.selected_business
        action_y = 280  # Начальная позиция для кнопок
        
        if not business.is_owned:
            # Кнопка покупки
            buy_button = BusinessActionButton(
                pygame.Rect(860, action_y, 300, 50),
                f"Купить за {business.base_price}$",
                lambda: self.buy_business(business),
                "buy"
            )
            self.action_buttons.append(buy_button)
            action_y += 70
        else:
            # Кнопка улучшения (если не достигнут максимальный уровень)
            if business.level < business.max_level:
                upgrade_cost = business.get_upgrade_cost()
                upgrade_button = BusinessActionButton(
                    pygame.Rect(860, action_y, 300, 50),
                    f"Улучшить за {upgrade_cost}$",
                    lambda: self.upgrade_business(business),
                    "upgrade"
                )
                self.action_buttons.append(upgrade_button)
                action_y += 70
            
            # Кнопка продажи
            sell_price = business.get_sell_price()
            sell_button = BusinessActionButton(
                pygame.Rect(860, action_y, 300, 50),
                f"Продать за {sell_price}$",
                lambda: self.sell_business(business),
                "sell"
            )
            self.action_buttons.append(sell_button)
            action_y += 70
            
            # Кнопка активности
            status_text = "Деактивировать" if business.is_active else "Активировать"
            status_button = BusinessActionButton(
                pygame.Rect(860, action_y, 300, 50),
                status_text,
                lambda: self.toggle_business_activity(business),
                "toggle"
            )
            self.action_buttons.append(status_button)
            action_y += 70
        
        # Кнопка назад к списку
        back_button = BusinessActionButton(
            pygame.Rect(860, action_y, 300, 50),
            "Назад к списку",
            lambda: self.go_back_to_list(),
            "back"
        )
        self.action_buttons.append(back_button)
    
    def go_back_to_list(self):
        """Возврат к списку бизнесов"""
        self.selected_business = None
        self.action_buttons = []

    def set_view_mode(self, mode):
        """Устанавливает режим просмотра"""
        self.view_mode = mode
        self.update_business_buttons()
        
        # Обновляем активность кнопок режима
        self.view_owned_button.is_active = (mode == "owned")
        self.view_available_button.is_active = (mode == "available")
    
    def set_category(self, category):
        """Установка категории"""
        self.current_category = category
        self.selected_business = None
        self.scroll_offset = 0
        self.update_business_buttons()
        
        # Обновляем состояние кнопок категорий
        for button in self.category_buttons:
            is_light_active = (category == BusinessCategory.LIGHT and "Светлые" in button.text)
            is_dark_active = (category == BusinessCategory.DARK and "Тёмные" in button.text)
            button.is_active = (is_light_active or is_dark_active)
    
    def update_business_buttons(self):
        """Обновление кнопок бизнесов"""
        self.business_buttons = []
        
        # Фильтруем бизнесы по категории и режиму просмотра
        if self.view_mode == "owned":
            businesses = [b for b in self.business_manager.owned_businesses 
                         if b.category == self.current_category]
        else:
            businesses = [b for b in self.business_manager.businesses 
                         if b.category == self.current_category and not b.is_owned]
        
        business_width, business_height = 340, 120
        start_x = 320
        start_y = 220
        spacing = 20
        columns = 3
        
        for i, business in enumerate(businesses):
            row = i // columns
            col = i % columns
            
            x = start_x + col * (business_width + spacing)
            y = start_y + row * (business_height + spacing) - self.scroll_offset
            
            rect = pygame.Rect(x, y, business_width, business_height)
            self.business_buttons.append(
                BusinessCard(rect, business, self.select_business)
            )
        
        # Расчет максимальной прокрутки
        total_rows = (len(businesses) + columns - 1) // columns
        content_height = total_rows * (business_height + spacing)
        self.max_scroll = max(0, content_height - 400)
    
    def select_business(self, business):
        """Выбор бизнеса для детального просмотра"""
        self.selected_business = business
    
    def draw(self, surface):
        """Отрисовка меню"""
        # Фон
        nav_panel_rect = pygame.Rect(30, 120, 240, 500)
        self.draw_panel(surface, nav_panel_rect, (20, 25, 35, 255))
        
        content_panel_rect = pygame.Rect(300, 120, 1100, 600)
        self.draw_panel(surface, content_panel_rect, (26, 34, 48, 255))
        
        # Навигация
        for button in self.nav_buttons:
            button.draw(surface, self.game.font_manager.get_font('button'))
        
        # Кнопка назад
        icon_x = self.back_button.rect.x + 20
        icon_y = self.back_button.rect.centery - 12
        self.game.icon_renderer.draw_back_icon(surface, icon_x, icon_y, 25)
        self.back_button.draw(surface, self.game.font_manager.get_font('button'), icon_x, icon_y)
        
        # Заголовок
        title = self.game.font_manager.get_rendered_text("Бизнес Империя", 'title', (255, 255, 255), True)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 140))
        
        # Статистика
        self.draw_business_stats(surface, 320, 160)
        
        # Категории
        for button in self.category_buttons:
            icon_x = button.rect.x + 20
            icon_y = button.rect.centery - 15
            button.draw(surface, self.game.font_manager.get_font('button'), icon_x, icon_y)
        
        # Кнопки режима просмотра
        self.view_owned_button.draw(surface, self.game.font_manager.get_font('button'), 
                                  self.view_owned_button.rect.x + 20, self.view_owned_button.rect.centery - 10)
        self.view_available_button.draw(surface, self.game.font_manager.get_font('button'), 
                                      self.view_available_button.rect.x + 20, self.view_available_button.rect.centery - 10)
        
        # Контент
        if self.selected_business:
            self.draw_business_details(surface)
        else:
            self.draw_business_list(surface)
    
    def draw_business_stats(self, surface, x, y):
        """Отрисовка статистики бизнесов"""
        stats_rect = pygame.Rect(x, y, 1060, 50)
        
        # Фон
        stats_bg = GradientGenerator.create_vertical_gradient(
            (stats_rect.width, stats_rect.height),
            [(0, 100, 200, 150), (0, 80, 180, 150), (0, 60, 160, 150)]
        )
        surface.blit(stats_bg, stats_rect.topleft)
        pygame.draw.rect(surface, (0, 150, 255, 255), stats_rect, width=2, border_radius=8)
        
        # Данные
        owned_count = len(self.business_manager.owned_businesses)
        total_income = self.business_manager.get_total_net_income()
        active_count = len([b for b in self.business_manager.owned_businesses if b.is_active])
        
        stats_font = self.game.font_manager.get_font('desc')
        texts = [
            f"Владеете: {owned_count} бизнесов",
            f"Активных: {active_count}",
            f"Доход: {total_income:.0f}$/сек"
        ]
        
        for i, text in enumerate(texts):
            text_surf = stats_font.render(text, True, (255, 255, 255))
            text_x = x + 20 + i * (1060 // len(texts))
            surface.blit(text_surf, (text_x, y + 15))
    
    def draw_business_list(self, surface):
        """Отрисовка списка бизнесов"""
        if not self.business_buttons:
            # Сообщение если бизнесов нет
            no_business_text = "Нет бизнесов для отображения" if self.view_mode == "owned" else "Все бизнесы куплены!"
            text_surf = self.game.font_manager.get_rendered_text(no_business_text, 'subtitle', TEXT_SECONDARY)
            surface.blit(text_surf, (SCREEN_WIDTH//2 - text_surf.get_width()//2, 300))
        
        for card in self.business_buttons:
            if card.rect.y + card.rect.height > 220 and card.rect.y < 700:
                card.draw(surface, self.game.font_manager.get_font('desc'))
    
    def draw_business_details(self, surface):
        """Отрисовка детальной информации о бизнесе"""
        if not self.selected_business:
            return
        
        business = self.selected_business
        
        # Основная информация
        info_rect = pygame.Rect(320, 220, 500, 400)
        self.draw_panel(surface, info_rect, (40, 45, 60, 255))
        
        # Заголовок
        title_font = self.game.font_manager.get_font('subtitle')
        title_surf = title_font.render(business.name, True, (255, 255, 255))
        surface.blit(title_surf, (340, 240))
        
        # Описание
        desc_font = self.game.font_manager.get_font('desc')
        desc_surf = desc_font.render(business.description, True, (200, 200, 200))
        surface.blit(desc_surf, (340, 280))
        
        # Статистика
        stats_y = 320
        stats = [
            f"Уровень: {business.level}/{business.max_level}",
            f"Доход: {business.stats.income:.0f}$/10сек",
            f"Расходы: {business.stats.expenses:.0f}$/10сек",
            f"Чистый доход: {business.get_net_income():.0f}$/10сек",
            f"Риск: {business.stats.risk:.0f}%",
            f"Легальность: {business.stats.legal_status:.0f}%",
            f"Сотрудники: {len(business.employees)}/{business.stats.employee_count}"
        ]
        
        for i, stat in enumerate(stats):
            stat_surf = desc_font.render(stat, True, (200, 200, 200))
            surface.blit(stat_surf, (340, stats_y + i * 25))
        
        # Кнопки действий
        actions_rect = pygame.Rect(840, 220, 340, 400)
        self.draw_panel(surface, actions_rect, (40, 45, 60, 255))
        
        action_y = 240
        action_buttons = []
        
        if not business.is_owned:
            # Кнопка покупки
            buy_button = BusinessActionButton(
                pygame.Rect(860, action_y, 300, 50),
                f"Купить за {business.base_price}$",
                lambda: self.buy_business(business),
                "buy"
            )
            action_buttons.append(buy_button)
            action_y += 70
        else:
            # Кнопка улучшения
            upgrade_cost = business.get_upgrade_cost()
            upgrade_button = BusinessActionButton(
                pygame.Rect(860, action_y, 300, 50),
                f"Улучшить за {upgrade_cost}$",
                lambda: self.upgrade_business(business),
                "upgrade"
            )
            action_buttons.append(upgrade_button)
            action_y += 70
            
            # Кнопка продажи
            sell_price = business.get_sell_price()
            sell_button = BusinessActionButton(
                pygame.Rect(860, action_y, 300, 50),
                f"Продать за {sell_price}$",
                lambda: self.sell_business(business),
                "sell"
            )
            action_buttons.append(sell_button)
            action_y += 70
            
            # Кнопка активности
            status_text = "Деактивировать" if business.is_active else "Активировать"
            status_button = BusinessActionButton(
                pygame.Rect(860, action_y, 300, 50),
                status_text,
                lambda: self.toggle_business_activity(business),
                "toggle"
            )
            action_buttons.append(status_button)
            action_y += 70
        
        # Кнопка назад к списку
        back_button = BusinessActionButton(
            pygame.Rect(860, action_y, 300, 50),
            "Назад к списку",
            lambda: setattr(self, 'selected_business', None),
            "back"
        )
        action_buttons.append(back_button)
        
        # Рисуем кнопки действий
        for button in action_buttons:
            button.draw(surface, self.game.font_manager.get_font('button'))
        
        # Анимация частиц
        for particle in business.particles:
            if particle['lifetime'] > 0:
                particle_x = 340 + particle['x']
                particle_y = 340 + particle['y']
                color = (*particle['color'], particle['alpha'])
                pygame.draw.circle(surface, color, (int(particle_x), int(particle_y)), 2)
    
    def buy_business(self, business):
        """Покупка бизнеса"""
        if self.business_manager.buy_business(business.id):
            self.selected_business = None
            self.update_business_buttons()
    
    def upgrade_business(self, business):
        """Улучшение бизнеса"""
        if self.business_manager.upgrade_business(business.id):
            self.update_business_buttons()
    
    def sell_business(self, business):
        """Продажа бизнеса"""
        if self.business_manager.sell_business(business.id):
            self.selected_business = None
            self.update_business_buttons()
    
    def toggle_business_activity(self, business):
        """Переключение активности бизнеса"""
        business.is_active = not business.is_active
        self.business_manager.save_to_database()
    
    def draw_panel(self, surface, rect, color):
        """Рисует панель"""
        pygame.draw.rect(surface, color, rect, border_radius=15)
        pygame.draw.rect(surface, (100, 100, 150, 255), rect, width=2, border_radius=15)
    
    def handle_event(self, event):
        """Обработка событий"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Навигация
            for button in self.nav_buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    self.game.update_navigation_state(button.text)
                    return True
            
            # Кнопка назад
            if self.back_button.rect.collidepoint(mouse_pos):
                self.back_button.click()
                return True
            
            # Кнопки категорий
            for button in self.category_buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    return True
            
            # Кнопки режима просмотра
            if self.view_owned_button.rect.collidepoint(mouse_pos):
                self.view_owned_button.click()
                return True
            if self.view_available_button.rect.collidepoint(mouse_pos):
                self.view_available_button.click()
                return True
            
            # Карточки бизнесов
            for card in self.business_buttons:
                if card.rect.collidepoint(mouse_pos):
                    card.click()
                    return True
            
            # Обработка действий в детальном просмотре
            if self.selected_business:
                # Здесь будет обработка кнопок действий
                pass
        
        elif event.type == pygame.MOUSEWHEEL:
            # Прокрутка
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - event.y * 30))
            self.update_business_buttons()
            return True
        
        return False

class BusinessCard:
    """Улучшенная карточка бизнеса"""
    
    def __init__(self, rect, business, action):
        self.rect = rect
        self.business = business
        self.action = action
        self.hovered = False
    
    def draw(self, surface, font):
        """Отрисовка карточки"""
        # Фон с градиентом
        if self.business.is_owned:
            if self.business.is_active:
                colors = [(60, 100, 60, 255), (40, 80, 40, 255), (20, 60, 20, 255)]
            else:
                colors = [(100, 100, 60, 255), (80, 80, 40, 255), (60, 60, 20, 255)]
        else:
            colors = [(60, 60, 100, 255), (40, 40, 80, 255), (20, 20, 60, 255)]
        
        if self.hovered:
            # Добавляем свечение при наведении
            glow_surf = GradientGenerator.create_rounded_rect(
                (self.rect.width + 10, self.rect.height + 10),
                [(255, 255, 255, 30), (200, 200, 255, 20), (150, 150, 255, 10)],
                15
            )
            surface.blit(glow_surf, (self.rect.x - 5, self.rect.y - 5))
        
        card_surf = GradientGenerator.create_rounded_rect(
            (self.rect.width, self.rect.height),
            colors,
            12
        )
        surface.blit(card_surf, self.rect.topleft)
        
        # Рамка
        border_color = (100, 255, 100) if self.business.is_owned and self.business.is_active else (100, 100, 150)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=12)
        
        # Иконка статуса
        status_icon = "✓" if self.business.is_owned else "💰"
        status_color = (100, 255, 100) if self.business.is_owned else (255, 255, 100)
        icon_font = pygame.font.Font(None, 24)
        icon_surf = icon_font.render(status_icon, True, status_color)
        surface.blit(icon_surf, (self.rect.x + 15, self.rect.y + 15))
        
        # Название
        name_font = pygame.font.Font(None, 22)
        name_surf = name_font.render(self.business.name, True, (255, 255, 255))
        surface.blit(name_surf, (self.rect.x + 45, self.rect.y + 15))
        
        # Уровень и тип
        level_text = f"Ур. {self.business.level}"
        level_surf = font.render(level_text, True, (200, 200, 200))
        surface.blit(level_surf, (self.rect.x + self.rect.width - 70, self.rect.y + 15))
        
        # Доход
        income_text = f"Доход: {self.business.stats.income:.0f}$/10сек"
        income_surf = font.render(income_text, True, (100, 255, 100))
        surface.blit(income_surf, (self.rect.x + 15, self.rect.y + 45))
        
        # Цена/статус
        if self.business.is_owned:
            status_text = "Активен" if self.business.is_active else "Неактивен"
            status_color = (100, 255, 100) if self.business.is_active else (255, 100, 100)
            status_surf = font.render(status_text, True, status_color)
            surface.blit(status_surf, (self.rect.x + 15, self.rect.y + 70))
            
            # Прогресс уровня
            progress_width = (self.rect.width - 30) * (self.business.level / self.business.max_level)
            progress_rect = pygame.Rect(self.rect.x + 15, self.rect.y + 95, progress_width, 8)
            pygame.draw.rect(surface, (0, 150, 255), progress_rect, border_radius=4)
        else:
            price_text = f"Цена: {self.business.base_price}$"
            price_surf = font.render(price_text, True, (255, 255, 100))
            surface.blit(price_surf, (self.rect.x + 15, self.rect.y + 70))
            
            # Риск
            risk_text = f"Риск: {self.business.stats.risk:.0f}%"
            risk_color = (255, 100, 100) if self.business.stats.risk > 50 else (255, 255, 100)
            risk_surf = font.render(risk_text, True, risk_color)
            surface.blit(risk_surf, (self.rect.x + 150, self.rect.y + 70))
        
        # Анимация частиц для активных бизнесов
        if self.business.is_owned and self.business.is_active:
            for particle in self.business.particles:
                if particle['lifetime'] > 0:
                    particle_x = self.rect.x + particle['x']
                    particle_y = self.rect.y + particle['y']
                    color = (*particle['color'], particle['alpha'])
                    pygame.draw.circle(surface, color, (int(particle_x), int(particle_y)), 2)
    
    def click(self):
        """Обработка клика"""
        if self.action:
            self.action(self.business)

class ProfileMenu:
    """Простое меню профиля без скролла."""
    
    def __init__(self, game):
        self.game = game
        self.nav_buttons = []
        self.card_buttons = []  # Кнопки в карточках
        self.initialize_ui()
        
        # Данные профиля
        self.profile_data = {
            "balance": "1,250,000$",
            "level": 15,
            "username": "Игрок123",
            "daily_reward_available": True,
            "tax_amount": "25,000$"
        }
    
    def initialize_ui(self):
        """Инициализация UI элементов профиля."""
        # Кнопки левой панели навигации
        nav_buttons = [
            ("Кликер", lambda: self.game.play_game(), False),
            ("Магазины", lambda: self.game.open_shop_selection(), False),
            ("Инвестиции", lambda: self.game.open_investments(), False),
            ("Бизнесы", lambda: self.game.open_businesses(), False),
            ("Профиль", lambda: None, True)  # Активная кнопка
        ]
        
        # Создаем кнопки навигации
        button_width, button_height = 200, 60
        button_x = 50
        button_y_start = 150
        
        for i, (text, action, is_active) in enumerate(nav_buttons):
            rect = pygame.Rect(button_x, button_y_start + i * 70, button_width, button_height)
            self.nav_buttons.append(NavButton(rect, text, action, is_active))
        
        # Кнопка назад
        self.back_button = Button(
            pygame.Rect(300, 50, 200, 60),
            "Назад",
            None,
            lambda: self.game.back_to_menu()
        )
    
    def draw(self, surface):
        """Отрисовка меню профиля."""
        # Левая панель навигации
        nav_panel_rect = pygame.Rect(30, 120, 240, 500)
        self.draw_panel(surface, nav_panel_rect, (20, 25, 35, 255))
        
        # Основная область контента
        content_panel_rect = pygame.Rect(300, 120, 1100, 600)
        self.draw_panel(surface, content_panel_rect, (26, 34, 48, 255))
        
        # Кнопки навигации
        for button in self.nav_buttons:
            button.draw(surface, self.game.font_manager.get_font('button'))
        
        # Кнопка назад
        if self.back_button:
            icon_x = self.back_button.rect.x + 20
            icon_y = self.back_button.rect.centery - 12
            self.game.icon_renderer.draw_back_icon(surface, icon_x, icon_y, 25)
            self.back_button.draw(surface, self.game.font_manager.get_font('button'), icon_x, icon_y)
        
        # Заголовок профиля
        title = self.game.font_manager.get_rendered_text("Профиль Игрока", 'title', (255, 255, 255), True)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 140))
        
        # Статистика профиля
        self.draw_profile_stats(surface, 320, 180)
        
        # Карточки профиля (компактные, чтобы все поместилось)
        self.draw_profile_cards(surface, 320, 250)
    
    def draw_panel(self, surface, rect, color):
        """Рисует панель с градиентом."""
        gradient = GradientGenerator.create_vertical_gradient(
            (rect.width, rect.height), 
            [(15, 20, 30, 255), (12, 18, 32, 255), (10, 15, 25, 255)]
        )
        surface.blit(gradient, rect.topleft)
        pygame.draw.rect(surface, (40, 50, 70, 255), rect, width=2, border_radius=15)
    
    def draw_profile_stats(self, surface, x, y):
        """Рисует статистику профиля."""
        stats_rect = pygame.Rect(x, y, 1060, 60)
        
        # Фон статистики
        stats_gradient = GradientGenerator.create_vertical_gradient(
            (stats_rect.width, stats_rect.height),
            [(0, 100, 200, 150), (0, 80, 180, 150), (0, 60, 160, 150)]
        )
        surface.blit(stats_gradient, stats_rect.topleft)
        pygame.draw.rect(surface, (0, 150, 255, 255), stats_rect, width=2, border_radius=10)
        
        # Данные статистики
        stats_font = self.game.font_manager.get_font('desc')
        texts = [
            f"Баланс: {self.profile_data['balance']}",
            f"Уровень: {self.profile_data['level']}",
            f"Игрок: {self.profile_data['username']}"
        ]
        
        # Равномерное распределение текста
        for i, text in enumerate(texts):
            text_surf = stats_font.render(text, True, (255, 255, 255))
            text_x = x + 20 + i * (1060 // len(texts))
            surface.blit(text_surf, (text_x, y + 20))
    
    def draw_profile_cards(self, surface, x, y):
        """Рисует компактные карточки профиля."""
        cards_data = self.get_cards_data()
        card_width = 1060
        card_height = 80  # Компактная высота
        spacing = 15      # Уменьшенный отступ
        
        self.card_buttons = []  # Очищаем старые кнопки
        
        for i, card_data in enumerate(cards_data):
            card_y = y + i * (card_height + spacing)
            card_rect = pygame.Rect(x, card_y, card_width, card_height)
            
            # Рисуем карточку
            self.draw_profile_card(surface, card_rect, card_data, i)
    
    def draw_profile_card(self, surface, rect, card_data, card_index):
        """Рисует одну карточку профиля."""
        # Фон карточки
        card_gradient = GradientGenerator.create_vertical_gradient(
            (rect.width, rect.height),
            [(40, 45, 60, 255), (35, 40, 55, 255), (30, 35, 50, 255)]
        )
        surface.blit(card_gradient, rect.topleft)
        
        # Тень
        shadow = pygame.Surface((rect.width + 6, rect.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 80), (3, 3, rect.width, rect.height), border_radius=10)
        surface.blit(shadow, (rect.x - 3, rect.y - 3))
        
        # Рамка
        pygame.draw.rect(surface, (70, 90, 130, 255), rect, width=1, border_radius=10)
        
        # Заголовок карточки
        title_font = self.game.font_manager.get_font('desc')
        title_surf = title_font.render(card_data["title"], True, (255, 255, 255))
        surface.blit(title_surf, (rect.x + 15, rect.y + 10))
        
        # Содержимое карточки (укороченное)
        content_text = card_data["content"][0] if card_data["content"] else ""
        if len(content_text) > 60:  # Обрезаем длинный текст
            content_text = content_text[:57] + "..."
        
        content_font = self.game.font_manager.get_font('desc')
        content_surf = content_font.render(content_text, True, (200, 200, 200))
        surface.blit(content_surf, (rect.x + 15, rect.y + 35))
        
        # Кнопка если есть (компактная)
        if "button" in card_data:
            button_rect = pygame.Rect(rect.x + rect.width - 200, rect.y + 20, 180, 40)
            
            # Сохраняем кнопку для обработки кликов
            self.card_buttons.append({
                "rect": button_rect,
                "action": card_data["button"]["action"],
                "text": card_data["button"]["text"]
            })
            
            # Рисуем кнопку
            self.draw_card_button(surface, button_rect, card_data["button"]["text"])
    
    def draw_card_button(self, surface, rect, button_text):
        """Рисует компактную кнопку в карточке."""
        # Градиент кнопки
        button_gradient = GradientGenerator.create_vertical_gradient(
            (rect.width, rect.height),
            [(0, 150, 255, 200), (0, 120, 220, 200), (0, 100, 200, 200)]
        )
        surface.blit(button_gradient, rect.topleft)
        
        # Рамка кнопки
        pygame.draw.rect(surface, (0, 200, 255, 255), rect, width=1, border_radius=8)
        
        # Текст кнопки (уменьшенный)
        button_font = pygame.font.Font(None, 20)  # Уменьшенный шрифт
        button_surf = button_font.render(button_text, True, (255, 255, 255))
        button_rect_center = button_surf.get_rect(center=rect.center)
        surface.blit(button_surf, button_rect_center)
    
    def get_cards_data(self):
        """Возвращает данные для компактных карточек профиля."""
        return [
            {
                "title": "🎁 Ежедневная награда",
                "content": ["Готово к получению! Награда: 10,000$"],
                "button": {"text": "Получить", "action": self.claim_daily_reward}
            },
            {
                "title": "💼 Налоги и сборы", 
                "content": [f"Общая сумма: {self.profile_data['tax_amount']}"],
                "button": {"text": "Оплатить", "action": self.pay_all_taxes}
            },
            {
                "title": "🏠 Резиденция",
                "content": ["Пентхаус Уровень 5 | Доход: 5,000$/день"],
                "button": {"text": "Управление", "action": self.open_residence_management}
            },
            {
                "title": "🎒 Инвентарь",
                "content": ["4 категории | 16 предметов"],
                "button": {"text": "Просмотр", "action": self.show_inventory}
            },
            {
                "title": "📊 Достижения",
                "content": ["15/20 завершено | 65% прогресс"],
                "button": {"text": "Подробнее", "action": self.show_achievements}
            },
            {
                "title": "⚙️ Настройки",
                "content": ["Персонализация и управление"],
                "button": {"text": "Настроить", "action": self.open_settings}
            }
        ]
    
    def handle_event(self, event):
        """Обработка событий меню профиля."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Навигационные кнопки
            for button in self.nav_buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    self.game.update_navigation_state(button.text)
                    return True
            
            # Кнопка назад
            if self.back_button.rect.collidepoint(mouse_pos):
                self.back_button.click()
                return True
            
            # Кнопки в карточках
            for button_data in self.card_buttons:
                if button_data["rect"].collidepoint(mouse_pos):
                    try:
                        button_data["action"]()
                        return True
                    except Exception as e:
                        print(f"Ошибка при выполнении действия: {e}")
                        return True
        
        return False
    
    # Методы действий кнопок
    def claim_daily_reward(self):
        print("🎁 Ежедневная награда получена!")
        # Здесь можно добавить логику выдачи награды
    
    def pay_all_taxes(self):
        print("💼 Налоги оплачены!")
        # Логика оплаты налогов
    
    def open_residence_management(self):
        print("🏠 Управление резиденцией открыто!")
        # Переход к управлению резиденцией
    
    def show_inventory(self):
        print("🎒 Инвентарь открыт!")
        # Просмотр инвентаря
    
    def show_achievements(self):
        print("📊 Достижения открыты!")
        # Просмотр достижений
    
    def open_settings(self):
        print("⚙️ Настройки открыты!")
        self.game.open_settings()  # Переход в настройки игры

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
        self.business_menu = AdvancedBusinessMenu(self)
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
            'bus': "SKATT x R3DAX", 'title': "Black Empire",
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
        try:
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
        
        except Exception as e:
            while True:
                print(f"ТЫ ЕБАНЫЙ ХУЕСОС: {e}")
                
    def run(self):
        """Основной игровой цикл."""
        try:
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
                    
                    # Обновление кликера если он активен
                    if self.state == ScreenState.CLICKER:
                        self.clicker_menu.update(dt)
                
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
                    self.investment_menu.draw(self.screen)
                elif self.state == ScreenState.CLICKER:
                    self.clicker_menu.draw()  # ← Исправленный вызов
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
        
        except Exception as e:
            print(f"ТЫ КУСОК ЕБАНОГО ДОЛБАЕБА: {e}")

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
        self.clicker_menu.draw()

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
if __name__ == "__main__":
    game = Game()
    game.run()