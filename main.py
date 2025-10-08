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
CARD_BG = (11, 17, 23)
ACCENT1 = (106, 44, 255)
ACCENT2 = (20, 231, 209)
TEXT_MUTED = (159, 176, 195)
GLASS_EFFECT = (255, 255, 255, 5)
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
# Добавить в начало файла после других импортов
class NavButton:
    """Кнопка навигации в левой панели."""
    
    def __init__(self, rect, text, action, is_active=False):
        self.rect = rect
        self.text = text
        self.is_active = is_active
        self.icon_function = None
        self.action = None
    
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
        
        if self.icon_function:
            self.icon_function(surface, self.rect)

        # Текст
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                return True
        return False

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
        self.clicker_icon_img = None
        self.business_icon_img = None
        self.investments_icon_img = None
        self.profile_icon_img = None
        self.shop_icon_img = None
        self.load_image_icons()

    def load_image_icons(self):
        """Загружает иконки из файлов с правильной обработкой ошибок."""
        import os
        icon_files = {
            'play_icon_img':     'images/play_icon.png',
            'settings_icon_img': 'images/settings_icon.png',
            'clicker_icon_img':  'images/clicker_icon.png',
            'business_icon_img': 'images/business_icon.png',
            'investments_icon_img': 'images/investments_icon.png',
            'profile_icon_img':  'images/profile_icon.png',
            'shop_icon_img':     'images/shop_icon.png'
        }
        try:
            for attr, filename in icon_files.items():
                if os.path.exists(filename):
                    img = pygame.image.load(filename).convert_alpha()
                    img = pygame.transform.scale(img, (30, 30))
                    setattr(self, attr, img)
                else:
                    print(f"Файл {filename} не найден, используем векторную иконку")
                    setattr(self, attr, None)
        except pygame.error as e:
            print(f"Ошибка загрузки иконок: {e}")
            for attr in icon_files.keys():
                setattr(self, attr, None)
        except Exception as e:
            print(f"Общая ошибка при загрузке иконок: {e}")
            for attr in icon_files.keys():
                setattr(self, attr, None)

    def _draw_image_icon(self, surface, x, y, size, img_attr, fallback_func):
        img = getattr(self, img_attr, None)
        if img is not None:
            try:
                if size != 30:
                    scaled_icon = pygame.transform.scale(img, (size, size))
                    surface.blit(scaled_icon, (x, y))
                else:
                    surface.blit(img, (x, y))
                return True
            except Exception as e:
                print(f"Ошибка отрисовки изображения {img_attr}: {e}")
        # Fallback на векторную функцию
        fallback_func(surface, x, y, size)
        return False

    # Универсальные методы для каждого типа иконки, вызывают _draw_image_icon
    def draw_play_image_icon(self, surface, x, y, size=30):
        return self._draw_image_icon(surface, x, y, size, "play_icon_img", self.draw_play_icon)

    def draw_settings_image_icon(self, surface, x, y, size=30):
        return self._draw_image_icon(surface, x, y, size, "settings_icon_img", self.draw_settings_icon)

    def draw_clicker_image_icon(self, surface, x, y, size=30):
        return self._draw_image_icon(surface, x, y, size, "clicker_icon_img", self.draw_clicker_icon)

    def draw_business_image_icon(self, surface, x, y, size=30):
        return self._draw_image_icon(surface, x, y, size, "business_icon_img", self.draw_business_icon)

    def draw_investments_image_icon(self, surface, x, y, size=30):
        return self._draw_image_icon(surface, x, y, size, "investments_icon_img", self.draw_investments_icon)

    def draw_profile_image_icon(self, surface, x, y, size=30):
        return self._draw_image_icon(surface, x, y, size, "profile_icon_img", self.draw_profile_icon)

    def draw_shop_image_icon(self, surface, x, y, size=30):
        return self._draw_image_icon(surface, x, y, size, "shop_icon_img", self.draw_shop_icon)

    # Fallback методы для отрисовки векторных иконок
    def draw_play_icon(self, surface, x, y, size=30):
        cache_key = ("play", size)
        if cache_key not in self.icon_cache:
            icon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            points = [(size*0.3, size*0.2), (size*0.8, size*0.5), (size*0.3, size*0.8)]
            pygame.gfxdraw.filled_polygon(icon_surf, points, PURPLE_PRIMARY)
            pygame.gfxdraw.aapolygon(icon_surf, points, TEXT_PRIMARY)
            self.icon_cache[cache_key] = icon_surf
        surface.blit(self.icon_cache[cache_key], (x, y))

    def draw_settings_icon(self, surface, x, y, size=30):
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

    def draw_clicker_icon(self, surface, x, y, size=30):
        # Контур пальца
        icon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # Основание пальца (овал)
        pygame.draw.ellipse(icon_surf, PURPLE_PRIMARY, [size*0.3, size*0.45, size*0.4, size*0.35])
        # Палец (вертикальный прямоугольник)
        pygame.draw.rect(icon_surf, PURPLE_PRIMARY, [size*0.45, size*0.1, size*0.1, size*0.5])
        # Обрисовка
        pygame.draw.ellipse(icon_surf, TEXT_PRIMARY, [size*0.3, size*0.45, size*0.4, size*0.35], 2)
        pygame.draw.rect(icon_surf, TEXT_PRIMARY, [size*0.45, size*0.1, size*0.1, size*0.5], 2)
        surface.blit(icon_surf, (x, y))


    def draw_business_icon(self, surface, x, y, size=30):
        icon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # Здание
        pygame.draw.rect(icon_surf, PURPLE_PRIMARY, [size*0.25, size*0.35, size*0.5, size*0.5])
        pygame.draw.rect(icon_surf, TEXT_PRIMARY, [size*0.25, size*0.35, size*0.5, size*0.5], 2)
        # Окна
        for i in range(2):
            for j in range(2):
                pygame.draw.rect(icon_surf, TEXT_PRIMARY, [
                    size*0.32 + j*size*0.23, size*0.42 + i*size*0.18, size*0.12, size*0.12
                ], 1)
        # Дверь
        pygame.draw.rect(icon_surf, TEXT_PRIMARY, [size*0.47, size*0.68, size*0.06, size*0.17], 1)
        surface.blit(icon_surf, (x, y))
        

    def draw_investments_icon(self, surface, x, y, size=30):
        icon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # Основа графика
        pygame.draw.line(icon_surf, TEXT_PRIMARY, (size*0.2, size*0.8), (size*0.8, size*0.8), 2)
        pygame.draw.line(icon_surf, TEXT_PRIMARY, (size*0.2, size*0.8), (size*0.2, size*0.2), 2)
        # Стрелка (рост)
        pygame.draw.line(icon_surf, PURPLE_PRIMARY, (size*0.2, size*0.7), (size*0.5, size*0.4), 3)
        pygame.draw.line(icon_surf, PURPLE_PRIMARY, (size*0.5, size*0.4), (size*0.7, size*0.6), 3)
        pygame.draw.polygon(icon_surf, PURPLE_PRIMARY, [
            (size*0.7, size*0.6), (size*0.65, size*0.55), (size*0.75, size*0.54)
        ])
        surface.blit(icon_surf, (x, y))
        

    def draw_profile_icon(self, surface, x, y, size=30):
        icon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # Голова
        pygame.draw.circle(icon_surf, PURPLE_PRIMARY, (int(size/2), int(size*0.37)), int(size*0.18))
        pygame.draw.circle(icon_surf, TEXT_PRIMARY, (int(size/2), int(size*0.37)), int(size*0.18), 2)
        # Тело
        pygame.draw.ellipse(icon_surf, PURPLE_PRIMARY, [size*0.23, size*0.55, size*0.54, size*0.32])
        pygame.draw.ellipse(icon_surf, TEXT_PRIMARY, [size*0.23, size*0.55, size*0.54, size*0.32], 2)
        surface.blit(icon_surf, (x, y))
        

    def draw_shop_icon(self, surface, x, y, size=30):
        icon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # Основание магазина
        pygame.draw.rect(icon_surf, PURPLE_PRIMARY, [size*0.2, size*0.6, size*0.6, size*0.25])
        pygame.draw.rect(icon_surf, TEXT_PRIMARY, [size*0.2, size*0.6, size*0.6, size*0.25], 2)
        # Крыша (треугольник)
        roof_points = [(size*0.1, size*0.6), (size*0.5, size*0.2), (size*0.9, size*0.6)]
        pygame.draw.polygon(icon_surf, PURPLE_PRIMARY, roof_points)
        pygame.draw.polygon(icon_surf, TEXT_PRIMARY, roof_points, 2)
        surface.blit(icon_surf, (x, y))
        
    
    def draw_play_icon(self, surface, x, y, size=30):
        cache_key = ("play", size)
        if cache_key not in self.icon_cache:
            icon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            points = [(size*0.3, size*0.2), (size*0.8, size*0.5), (size*0.3, size*0.8)]
            gfxdraw.filled_polygon(icon_surf, points, PURPLE_PRIMARY)
            gfxdraw.aapolygon(icon_surf, points, TEXT_PRIMARY)
            self.icon_cache[cache_key] = icon_surf
        
        surface.blit(self.icon_cache[cache_key], (x, y))
    
    def draw_settings_icon(self, surface, x, y, size=30):
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

    def draw_apply_icon(self, surface, x, y, size=30):
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
         alpha = int(255 * (1 - self.lifetime / self.duration))
         alpha = max(0, min(255, alpha))
         color_with_alpha = (*self.color, alpha)
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

class ButtonFactory:
    '''Создание кнопок в меню игры'''
    def nav_buttons_in_game(self):
        pass

class ClickerMenu:
    """Исправленная версия кликера с использованием общей палитры цветов."""

    def __init__(self, game, nav_buttons):  # Добавляем параметр game
        self.game = game  # Сохраняем ссылку на основной игровой объект
        self.nav_buttons = nav_buttons
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
            button.draw(self.screen, self.game.font_manager.get_font('button'))

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
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Проверяем навигационные кнопки
            for button in self.nav_buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    # Обновляем активное состояние
                    self.game.update_navigation_state(button.text)
                    return True

            # Проверяем кнопку инвестирования
            button_rect = pygame.Rect(
                self.config.screen_width - 700,
                self.config.screen_height // 2 - 140,
                400, 450
            )
            if button_rect.collidepoint(mouse_pos):
                self.handle_click()
                return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.handle_click()
                return True
            elif event.key == pygame.K_ESCAPE:
                self.game.back_to_menu()
                return True
        
        elif event.type == pygame.QUIT:
            self.running = False
            self.game.running = False
            return True
            
        elif event.type == pygame.VIDEORESIZE:
            # Обработка изменения размера окна
            self.config.screen_width, self.config.screen_height = event.size
            self.screen = pygame.display.set_mode((self.config.screen_width, self.config.screen_height), 
                                                pygame.RESIZABLE)
            self.cached_surfaces.clear()
            return True
        
        return False

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

    def draw(self, surface, font):
        """Базовая отрисовка кнопки"""
        color = (100, 100, 200) if self.is_hovered else (70, 70, 150)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

#вкладка Инвестиции
class InvestmentMenu:
    """Класс для меню инвестиций."""
    
    def __init__(self, game, nav_buttons):
        self.game = game
        self.nav_buttons = nav_buttons
        self.export = ExportDB()
        self.current_tab = "акции"  # Текущая активная вкладка
        self.buttons = []
        self.tab_buttons = []
        self.initialize_ui()
    
    def initialize_ui(self):
        """Инициализация UI элементов меню инвестиций."""        
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
        for button in self.nav_buttons:
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
            
            for button in self.nav_buttons:
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
    def __init__(self, game, nav_buttons):
        self.game = game
        self.nav_buttons = nav_buttons
        self.buttons = []
        self.initialize_ui()
    
    def initialize_ui(self):        
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
                    self.game.update_navigation_state(button.text)
                    return True
            
            # Проверяем клики по основным кнопкам
            for button in self.buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    return True
        
        return False

class LightShopMenu:
    def __init__(self, game, nav_buttons):
        self.game = game
        self.category_buttons = []
        self.nav_buttons = nav_buttons
        self.initialize_ui() 
    
    def initialize_ui(self):        
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
                    self.game.update_navigation_state(button.text)
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
    def __init__(self, game, nav_buttons):
        self.game = game
        self.nav_buttons = nav_buttons
        self.product_buttons = []
        self.search_box = pygame.Rect(300, 180, 400, 40)
        self.search_active = False
        self.search_text = ""
        self.initialize_ui()
    
    def initialize_ui(self):
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
                    self.game.update_navigation_state(button.text)
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
    
    def __init__(self, game, nav_buttons):
        super().__init__(game, nav_buttons)
        # Переопределяем кнопку назад для черного рынка
        self.nav_buttons = nav_buttons
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
    def __init__(self, game, nav_buttons):
        self.game = game
        self.nav_buttons = nav_buttons
        self.category_buttons = []
        self.initialize_ui()
    
    def initialize_ui(self):        
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
                    self.game.update_navigation_state(button.text)
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
    
class UpgradeType(Enum):
    INCOME = "income"           # Увеличение дохода
    EFFICIENCY = "efficiency"   # Снижение расходов  
    CAPACITY = "capacity"       # Увеличение мощности
    QUALITY = "quality"         # Улучшение качества
    MARKETING = "marketing"     # Увеличение доли рынка
    AUTOMATION = "automation"   # Автоматизация процессов
    SECURITY = "security"       # Безопасность (для темных бизнесов)
    INNOVATION = "innovation"   # Инновации (для IT бизнесов)

@dataclass
class BusinessTemplate:
    """Шаблон бизнеса как в HTML версии"""
    id: str
    name: str
    price: int
    income_per_hour: int
    description: str
    category: str  # "light" или "dark"

@dataclass
class BusinessUpgrade:
    id: str
    name: str
    description: str
    cost: int
    effect: float  # Множитель эффекта
    upgrade_type: UpgradeType
    max_level: int = 10
    current_level: int = 0
    requirements: Optional[List[str]] = None  # Требуемые улучшения
    
    def __post_init__(self):
        if self.requirements is None:
            self.requirements = []
    
    def can_upgrade(self, business) -> bool:
        """Проверяет можно ли улучшить"""
        if self.current_level >= self.max_level:
            return False
        
        # Проверяем требования
        if self.requirements is None:
            self.requirements = []
        for req_id in self.requirements:
            if not any(upg.id == req_id and upg.current_level > 0 
                      for upg in business.upgrades):
                return False
        return True
    
    def apply_effect(self, business):
        """Применяет эффект улучшения к бизнесу"""
        if self.upgrade_type == UpgradeType.INCOME:
            business.income_per_hour = int(business.income_per_hour * (1 + self.effect))
        elif self.upgrade_type == UpgradeType.EFFICIENCY:
            business.expenses_per_hour = max(0, int(business.expenses_per_hour * (1 - self.effect)))
        elif self.upgrade_type == UpgradeType.CAPACITY:
            business.capacity_multiplier *= (1 + self.effect)
        elif self.upgrade_type == UpgradeType.QUALITY:
            business.quality_multiplier *= (1 + self.effect)
        elif self.upgrade_type == UpgradeType.MARKETING:
            business.market_share = min(100.0, business.market_share * (1 + self.effect))
        elif self.upgrade_type == UpgradeType.AUTOMATION:
            business.automation_level += self.effect
        elif self.upgrade_type == UpgradeType.SECURITY:
            business.security_level += self.effect
        elif self.upgrade_type == UpgradeType.INNOVATION:
            business.innovation_level += self.effect

# Индивидуальные улучшения для каждого типа бизнеса
BUSINESS_UPGRADES = {
    # Светлые бизнесы
    "light-1": [  # Продажа (розничная торговля)
        BusinessUpgrade("retail-1", "Улучшение витрин", "Привлекательные витрины увеличивают продажи", 5000, 0.15, UpgradeType.INCOME),
        BusinessUpgrade("retail-2", "Система скидок", "Лояльность клиентов растет", 8000, 0.10, UpgradeType.MARKETING),
        BusinessUpgrade("retail-3", "Оптимизация запасов", "Снижение расходов на хранение", 6000, 0.12, UpgradeType.EFFICIENCY),
        BusinessUpgrade("retail-4", "Обучение персонала", "Улучшение обслуживания клиентов", 7000, 0.08, UpgradeType.QUALITY),
    ],
    
    "light-3": [  # IT-стартап
        BusinessUpgrade("it-1", "Нанять Senior разработчиков", "Увеличивает качество продукта", 15000, 0.20, UpgradeType.QUALITY),
        BusinessUpgrade("it-2", "Запуск рекламной кампании", "Привлечение новых клиентов", 12000, 0.15, UpgradeType.MARKETING),
        BusinessUpgrade("it-3", "Оптимизация серверов", "Снижение расходов на инфраструктуру", 10000, 0.18, UpgradeType.EFFICIENCY),
        BusinessUpgrade("it-4", "Внедрение AI", "Автоматизация процессов разработки", 20000, 0.25, UpgradeType.AUTOMATION),
        BusinessUpgrade("it-5", "Исследование новых технологий", "Инновации увеличивают доход", 25000, 0.30, UpgradeType.INNOVATION),
    ],
    
    "light-15": [  # Банк
        BusinessUpgrade("bank-1", "Расширение филиальной сети", "Увеличение клиентской базы", 50000, 0.20, UpgradeType.INCOME),
        BusinessUpgrade("bank-2", "Цифровизация услуг", "Снижение операционных расходов", 40000, 0.15, UpgradeType.EFFICIENCY),
        BusinessUpgrade("bank-3", "Премиальные пакеты услуг", "Увеличение дохода с клиента", 35000, 0.18, UpgradeType.QUALITY),
        BusinessUpgrade("bank-4", "Система кибербезопасности", "Защита от кибератак", 45000, 0.12, UpgradeType.SECURITY),
    ],
    
    # Темные бизнесы
    "dark-1": [  # Кибер-мошенничество
        BusinessUpgrade("cyber-1", "Анонимные сервера", "Снижение риска обнаружения", 8000, 0.15, UpgradeType.SECURITY),
        BusinessUpgrade("cyber-2", "Фишинговая рассылка", "Увеличение охвата", 6000, 0.20, UpgradeType.MARKETING),
        BusinessUpgrade("cyber-3", "Взлом банковских систем", "Повышение эффективности атак", 12000, 0.25, UpgradeType.INCOME),
        BusinessUpgrade("cyber-4", "Крипто-кошельки", "Анонимные переводы", 10000, 0.18, UpgradeType.SECURITY),
    ],
    
    "dark-9": [  # Нарко-картель
        BusinessUpgrade("cartel-1", "Расширение каналов поставок", "Увеличение объемов", 20000, 0.22, UpgradeType.CAPACITY),
        BusinessUpgrade("cartel-2", "Коррупция чиновников", "Снижение внимания властей", 25000, 0.20, UpgradeType.SECURITY),
        BusinessUpgrade("cartel-3", "Новые точки сбыта", "Расширение рынка", 18000, 0.18, UpgradeType.MARKETING),
        BusinessUpgrade("cartel-4", "Улучшение качества продукта", "Повышение цены", 15000, 0.15, UpgradeType.QUALITY),
    ],
    
    "dark-14": [  # Частная военная компания
        BusinessUpgrade("pmc-1", "Современное вооружение", "Увеличение эффективности", 30000, 0.25, UpgradeType.QUALITY),
        BusinessUpgrade("pmc-2", "Подготовка бойцов", "Повышение квалификации", 25000, 0.20, UpgradeType.INCOME),
        BusinessUpgrade("pmc-3", "Международные контракты", "Расширение географии", 35000, 0.30, UpgradeType.MARKETING),
        BusinessUpgrade("pmc-4", "Техническое оснащение", "Современное оборудование", 28000, 0.22, UpgradeType.CAPACITY),
    ]
}


class BusinessFull:
    def __init__(self, template: BusinessTemplate):
        self.uid = f"b-{random.randint(10000, 99999)}"
        self.template_id = template.id
        self.name = template.name
        self.purchased_at = time.time()
        self.level = 1
        self.income_per_hour = template.income_per_hour
        self.income_accumulated = 0
        self.expenses_per_hour = int(template.income_per_hour * 0.35)
        self.market_share = round(random.uniform(1.0, 7.0), 2)
        self.upgrade_data = BusinessUpgradeData()
        self.upgrades: List[BusinessUpgrade] = []
        self.capacity_multiplier = 1.0
        self.quality_multiplier = 1.0
        self.automation_level = 0
        self.security_level = 0
        self.innovation_level = 0
        self.risk_level = 10.0
        self.notes = template.description
        self.initialize_upgrades()

    def initialize_upgrades(self):
        if self.template_id in BUSINESS_UPGRADES:
            self.upgrades = BUSINESS_UPGRADES[self.template_id]

    def get_available_upgrades(self) -> List[BusinessUpgrade]:
        return [upgrade for upgrade in self.upgrades if upgrade.can_upgrade(self)]

    def purchase_upgrade(self, upgrade_id: str) -> bool:
        upgrade = next((u for u in self.upgrades if u.id == upgrade_id), None)
        if not upgrade or not upgrade.can_upgrade(self):
            return False
        upgrade.current_level += 1
        upgrade.apply_effect(self)
        return True

    def upgrade_income(self) -> bool:
        cost = max(100, int(self.income_per_hour * 6))
        self.income_per_hour = int(self.income_per_hour * 1.25)
        self.upgrade_data.level += 1
        self.level += 1
        return True

    def upgrade_efficiency(self) -> bool:
        cost = max(80, int(self.expenses_per_hour * 4))
        self.expenses_per_hour = max(0, int(self.expenses_per_hour * 0.8))
        self.upgrade_data.automation += 1
        return True

    def upgrade_marketing(self) -> bool:
        cost = max(200, int(self.income_per_hour * 4))
        self.market_share = min(100.0, round(self.market_share + random.uniform(0.7, 3.7), 2))
        self.upgrade_data.marketing += 1
        return True

    def get_net_income_per_hour(self) -> int:
        base_income = self.income_per_hour * self.capacity_multiplier * self.quality_multiplier
        expenses = self.expenses_per_hour * (1 - self.automation_level * 0.1)
        return max(0, int(base_income - expenses))

    def calculate_risk(self) -> float:
        base_risk = 10.0
        risk_reduction = self.security_level * 2.0
        return max(1.0, base_risk - risk_reduction)

    def get_upgrade_progress(self) -> Dict[str, float]:
        progress = {}
        for upgrade_type in UpgradeType:
            upgrades = [u for u in self.upgrades if u.upgrade_type == upgrade_type]
            if upgrades:
                progress[upgrade_type.value] = sum(u.current_level for u in upgrades) / sum(u.max_level for u in upgrades)
            else:
                progress[upgrade_type.value] = 0.0
        return progress

    def get_sell_price(self) -> int:
        return int(self.income_per_hour * 100 * 0.7)

from typing import TYPE_CHECKING

class BusinessManager:
    """Менеджер бизнесов как в HTML версии"""
    
    # Светлые бизнесы (как в HTML)
    LIGHT_BUSINESSES = [
        BusinessTemplate('light-1', 'Продажа', 5000, 50, 'Розничная торговля — стабильный доход.', 'light'),
        BusinessTemplate('light-2', 'Строительство', 25000, 350, 'Контракты на строительно-монтажные работы.', 'light'),
        BusinessTemplate('light-3', 'IT-стартап', 40000, 500, 'Стартап в области ПО / сервисов.', 'light'),
        BusinessTemplate('light-4', 'Электросетевая компания', 75000, 900, 'Инфраструктурный доход.', 'light'),
        BusinessTemplate('light-5', 'Сеть кофеен', 15000, 120, 'Ритейл + фриланс аренда помещений.', 'light'),
        BusinessTemplate('light-6', 'Биотех Лаборатория', 90000, 1100, 'Исследования и сервисы.', 'light'),
        BusinessTemplate('light-7', 'Образовательная платформа', 18000, 150, 'Онлайн курсы и подписки.', 'light'),
        BusinessTemplate('light-8', 'Технопарк', 60000, 650, 'Инкубатор бизнесов.', 'light'),
        BusinessTemplate('light-9', 'Автопром', 85000, 1200, 'Производство автомобилей.', 'light'),
        BusinessTemplate('light-10', 'Кибербезопасность', 30000, 320, 'Услуги по защите данных.', 'light'),
        BusinessTemplate('light-11', 'Медицинский центр', 70000, 750, 'Клиника с платными услугами.', 'light'),
        BusinessTemplate('light-12', 'Робототехника', 65000, 680, 'Разработка роботов и решений.', 'light'),
        BusinessTemplate('light-13', 'Космический туризм', 200000, 3500, 'Эксклюзивные туры.', 'light'),
        BusinessTemplate('light-14', 'AI разработки', 50000, 600, 'Интеграция искусственного интеллекта.', 'light'),
        BusinessTemplate('light-15', 'Банк', 120000, 1800, 'Финансовые услуги и кредитование.', 'light'),
        BusinessTemplate('light-16', 'Нефтегазовая компания', 220000, 4000, 'Энергетический сектор.', 'light'),
        BusinessTemplate('light-17', 'Трейдинг', 45000, 480, 'Финансовые операции на рынках.', 'light'),
        BusinessTemplate('light-18', 'Оборонное предприятие', 250000, 5000, 'Контракты в оборонной сфере.', 'light'),
        BusinessTemplate('light-19', 'УГМК', 300000, 6000, 'Крупный промышленный холдинг.', 'light')
    ]
    
    # Темные бизнесы (как в HTML)
    DARK_BUSINESSES = [
        BusinessTemplate('dark-1', 'Кибер-мошенничество', 12000, 300, 'Тёмная ниша — исключительно как игровой объект.', 'dark'),
        BusinessTemplate('dark-2', 'Теневой банкинг', 40000, 900, 'Подпольные финансовые потоки — игровой объект.', 'dark'),
        BusinessTemplate('dark-3', 'Контрабанда', 30000, 800, 'Игровой элемент — рискованно, но прибыльно.', 'dark'),
        BusinessTemplate('dark-4', 'Пиратское ПО', 7000, 200, 'Нелегальные дистрибуции — демо.', 'dark'),
        BusinessTemplate('dark-5', 'Нелегальные ставки', 15000, 350, 'Игровой рынок ставок — демо.', 'dark'),
        BusinessTemplate('dark-6', 'Фальшивые документы', 10000, 260, 'Игровая услуга (демо).', 'dark'),
        BusinessTemplate('dark-7', 'Нелегальный импорт/экспорт', 28000, 720, 'Игровая логистика.', 'dark'),
        BusinessTemplate('dark-8', 'Теневой майнинг', 18000, 420, 'Майнинг вне законов — демо.', 'dark'),
        BusinessTemplate('dark-9', 'Нарко-картель', 50000, 1400, 'Сильный риск — сильная прибыль (игра).', 'dark'),
        BusinessTemplate('dark-10', 'Отмывание денег', 45000, 1200, 'Игровая механика работы с капиталом.', 'dark'),
        BusinessTemplate('dark-11', 'Подпольный хостинг', 9000, 230, 'Анонимный хостинг — демо.', 'dark'),
        BusinessTemplate('dark-12', 'Нелегальный аутсорсинг', 8000, 190, 'Игровой сервис.', 'dark'),
        BusinessTemplate('dark-13', 'Тёмный арбитраж', 22000, 600, 'Арбитраж и быстрые сделки (игра).', 'dark'),
        BusinessTemplate('dark-14', 'Частная военная компания', 100000, 3000, 'Высокий риск — большие контракты (демо).', 'dark')
    ]
    
    def __init__(self):
        self.my_businesses: List[Business] = []
        self.last_tick_time = time.time()
        self.load_data()
    
    def load_data(self):
        """Загрузка данных (в демо создаем пустой список)"""
        # В реальной реализации здесь будет загрузка из БД
        self.my_businesses = []
    
    def save_data(self):
        pass

    def buy_business(self, template: BusinessTemplate):
        """Покупка бизнеса"""
        business = Business(template)
        self.my_businesses.append(business)
        self.save_data()
        return business
    
    def sell_business(self, business_uid: str) -> bool:
        """Продажа бизнеса"""
        self.my_businesses = [b for b in self.my_businesses if b.uid != business_uid]
        self.save_data()
        return True
    
    def collect_income(self, business_uid: str) -> int:
        """Сбор накопленного дохода"""
        business = self.get_business(business_uid)
        if not business:
            return 0
        
        income = business.income_accumulated
        business.income_accumulated = 0
        self.save_data()
        return income
    
    def get_business(self, business_uid: str) -> Optional["Business"]:
        """Получение бизнеса по ID"""
        return next((b for b in self.my_businesses if b.uid == business_uid), None)

    def update_income(self):
        """Обновление накопленного дохода (вызывается периодически)"""
        current_time = time.time()
        dt_hours = (current_time - self.last_tick_time) / 3600.0  # часы
        
        for business in self.my_businesses:
            gain = business.income_per_hour * dt_hours
            expense = business.expenses_per_hour * dt_hours
            business.income_accumulated += int(max(0, gain - expense))      
        self.last_tick_time = current_time

class Business:
    def __init__(self, template: BusinessTemplate):
        self.uid = f"b-{random.randint(10000, 99999)}"
        self.template_id = template.id
        self.name = template.name
        self.purchased_at = time.time()
        self.level = 1
        self.income_per_hour = template.income_per_hour
        self.income_accumulated = 0
        self.expenses_per_hour = int(template.income_per_hour * 0.35)
        self.market_share = round(random.uniform(1.0, 7.0), 2)
        
        # Разделяем улучшения на данные и объекты
        self.upgrade_data = BusinessUpgradeData()  # Простые данные
        self.upgrades: List[BusinessUpgrade] = []  # Объекты улучшений
        
        # Новые атрибуты для улучшений
        self.capacity_multiplier = 1.0
        self.quality_multiplier = 1.0
        self.automation_level = 0
        self.security_level = 0
        self.innovation_level = 0
        self.risk_level = 10.0  # Уровень риска (для темных бизнесов)
        
        self.notes = template.description
        self.initialize_upgrades()
    
    def initialize_upgrades(self):
        """Инициализирует улучшения для этого бизнеса"""
        if self.template_id in BUSINESS_UPGRADES:
            # Создаем копии улучшений для этого бизнеса
            for upgrade_template in BUSINESS_UPGRADES[self.template_id]:
                self.upgrades.append(BusinessUpgrade(
                    id=upgrade_template.id,
                    name=upgrade_template.name,
                    description=upgrade_template.description,
                    cost=upgrade_template.cost,
                    effect=upgrade_template.effect,
                    upgrade_type=upgrade_template.upgrade_type,
                    max_level=upgrade_template.max_level
                ))

    def get_upgrade_progress(self) -> Dict[str, float]:
        """Возвращает прогресс по всем типам улучшений"""
        progress = {}
        for upgrade_type in UpgradeType:
            upgrades_of_type = [u for u in self.upgrades if u.upgrade_type == upgrade_type]
            if upgrades_of_type:
                total_levels = sum(u.current_level for u in upgrades_of_type)
                max_levels = sum(u.max_level for u in upgrades_of_type)
                progress[upgrade_type.value] = total_levels / max_levels if max_levels > 0 else 0
            else:
                progress[upgrade_type.value] = 0.0
        return progress
    
    def get_available_upgrades(self) -> List[BusinessUpgrade]:
        """Возвращает доступные для покупки улучшения"""
        return [upgrade for upgrade in self.upgrades if upgrade.can_upgrade(self)]
    
    def purchase_upgrade(self, upgrade_id: str) -> bool:
        """Покупка улучшения"""
        upgrade = next((u for u in self.upgrades if u.id == upgrade_id), None)
        if not upgrade or not upgrade.can_upgrade(self):
            return False
        
        # В реальной реализации проверяем баланс игрока
        # if player_balance < upgrade.cost: return False
        
        upgrade.current_level += 1
        upgrade.apply_effect(self)
        return True
    
    def upgrade_income(self) -> bool:
        """Улучшение дохода"""
        cost = max(100, int(self.income_per_hour * 6))
        # В демо всегда успешно
        self.income_per_hour = int(self.income_per_hour * 1.25)
        self.upgrade_data.level += 1  # Используем upgrade_data вместо upgrades
        self.level += 1
        return True
    
    def upgrade_efficiency(self) -> bool:
        """Улучшение эффективности (снижение расходов)"""
        cost = max(80, int(self.expenses_per_hour * 4))
        self.expenses_per_hour = max(0, int(self.expenses_per_hour * 0.8))
        self.upgrade_data.automation += 1  # Используем upgrade_data вместо upgrades
        return True
    
    def upgrade_marketing(self) -> bool:
        """Улучшение маркетинга (увеличение доли рынка)"""
        cost = max(200, int(self.income_per_hour * 4))
        self.market_share = min(100.0, round(self.market_share + random.uniform(0.7, 3.7), 2))
        self.upgrade_data.marketing += 1  # Используем upgrade_data вместо upgrades
        return True
    
    def get_net_income_per_hour(self) -> int:
        """Чистый доход в час с учетом всех модификаторов"""
        base_income = self.income_per_hour * self.capacity_multiplier * self.quality_multiplier
        expenses = self.expenses_per_hour * (1 - self.automation_level * 0.1)
        return max(0, int(base_income - expenses))
    
    def calculate_risk(self) -> float:
        """Расчет уровня риска (для темных бизнесов)"""
        base_risk = 10.0
        risk_reduction = self.security_level * 2.0
        return max(1.0, base_risk - risk_reduction)
    
    def get_sell_price(self) -> int:
        """Цена продажи (70% от вложений)"""
        return int(self.income_per_hour * 100 * 0.7)

class ModernBusinessCard:
    """Современная карточка бизнеса в стиле HTML"""
    
    def __init__(self, rect: pygame.Rect, business: Business, on_click):
        self.rect = rect
        self.business = business
        self.on_click = on_click
        self.hovered = False
    
    def draw(self, surface, font_manager):
        """Отрисовка карточки в современном стиле"""
        # Основной фон карточки
        card_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Градиентный фон как в HTML
        colors = [
            (255, 255, 255, 10),  # Стеклянный эффект
            (255, 255, 255, 5),
            (255, 255, 255, 2)
        ]
        gradient = self.create_vertical_gradient((self.rect.width, self.rect.height), colors)
        card_surface.blit(gradient, (0, 0))
        
        # Рамка
        pygame.draw.rect(card_surface, (255, 255, 255, 20), 
                        (0, 0, self.rect.width, self.rect.height), 
                        width=1, border_radius=14)
        
        # Бейдж с инициалами (как в HTML)
        badge_size = 44
        badge_x, badge_y = 14, 14
        badge_colors = [ACCENT1, ACCENT2]
        badge_gradient = self.create_vertical_gradient((badge_size, badge_size), 
                                                     [(c[0], c[1], c[2], 255) for c in badge_colors])
        card_surface.blit(badge_gradient, (badge_x, badge_y))
        
        # Инициалы названия
        initials = ''.join([word[0] for word in self.business.name.split()[:2]]).upper()
        initials_font = pygame.font.Font(None, 18)
        initials_surf = initials_font.render(initials, True, (7, 16, 24))
        initials_rect = initials_surf.get_rect(center=(badge_x + badge_size//2, badge_y + badge_size//2))
        card_surface.blit(initials_surf, initials_rect)
        
        # Название бизнеса
        name_font = pygame.font.Font(None, 16)
        name_surf = name_font.render(self.business.name, True, TEXT_PRIMARY)
        card_surface.blit(name_surf, (badge_x + badge_size + 10, badge_y + 5))
        
        # Описание
        desc_font = pygame.font.Font(None, 13)
        desc_text = self.business.notes
        if len(desc_text) > 30:
            desc_text = desc_text[:27] + "..."
        desc_surf = desc_font.render(desc_text, True, TEXT_MUTED)
        card_surface.blit(desc_surf, (badge_x + badge_size + 10, badge_y + 25))
        
        # Доход и уровень справа
        income_text = f"{self.format_money(self.business.income_per_hour)}/час"
        income_surf = name_font.render(income_text, True, TEXT_PRIMARY)
        income_rect = income_surf.get_rect(topright=(self.rect.width - 14, badge_y + 5))
        card_surface.blit(income_surf, income_rect)
        
        level_text = f"Уровень {self.business.level}"
        level_surf = desc_font.render(level_text, True, TEXT_MUTED)
        level_rect = level_surf.get_rect(topright=(self.rect.width - 14, badge_y + 25))
        card_surface.blit(level_surf, level_rect)
        
        # Статистика внизу (как в HTML)
        stats_y = badge_y + badge_size + 10
        stats = [
            (f"{self.format_money(self.business.income_accumulated)}", "Баланс"),
            (f"{self.format_money(self.business.expenses_per_hour)}", "Расход/час"),
            (f"{self.business.market_share}%", "Доля рынка")
        ]
        
        stat_width = (self.rect.width - 28) // 3
        for i, (value, label) in enumerate(stats):
            stat_x = 14 + i * stat_width
            
            # Фон статистики
            stat_bg = pygame.Surface((stat_width - 4, 40), pygame.SRCALPHA)
            pygame.draw.rect(stat_bg, (255, 255, 255, 10), 
                           (0, 0, stat_width - 4, 40), border_radius=8)
            card_surface.blit(stat_bg, (stat_x, stats_y))
            
            # Значение
            value_surf = desc_font.render(value, True, TEXT_PRIMARY)
            value_rect = value_surf.get_rect(center=(stat_x + (stat_width - 4)//2, stats_y + 15))
            card_surface.blit(value_surf, value_rect)
            
            # Метка
            label_surf = pygame.font.Font(None, 11).render(label, True, TEXT_MUTED)
            label_rect = label_surf.get_rect(center=(stat_x + (stat_width - 4)//2, stats_y + 30))
            card_surface.blit(label_surf, label_rect)
        
        # Эффект при наведении
        if self.hovered:
            glow = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 255, 255, 30), 
                          (0, 0, self.rect.width, self.rect.height), 
                          border_radius=14)
            card_surface.blit(glow, (0, 0))
            
            # Тень при наведении
            shadow = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 80), 
                          (5, 5, self.rect.width, self.rect.height), 
                          border_radius=16)
            final_surface = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
            final_surface.blit(shadow, (0, 0))
            final_surface.blit(card_surface, (5, 5))
            surface.blit(final_surface, (self.rect.x - 5, self.rect.y - 5))
        else:
            surface.blit(card_surface, self.rect.topleft)
    
    def create_vertical_gradient(self, size, colors):
        """Создает вертикальный градиент"""
        width, height = size
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if len(colors) == 1:
            surface.fill(colors[0])
            return surface
        
        for y in range(height):
            pos = y / max(height - 1, 1)
            color_index = pos * (len(colors) - 1)
            idx1 = min(int(color_index), len(colors) - 2)
            idx2 = idx1 + 1
            blend = color_index - idx1
            
            if len(colors[idx1]) == 3:
                r1, g1, b1 = colors[idx1]
                a1 = 255
            else:
                r1, g1, b1, a1 = colors[idx1]
                
            if len(colors[idx2]) == 3:
                r2, g2, b2 = colors[idx2]
                a2 = 255
            else:
                r2, g2, b2, a2 = colors[idx2]
            
            r = int(r1 + (r2 - r1) * blend)
            g = int(g1 + (g2 - g1) * blend)
            b = int(b1 + (b2 - b1) * blend)
            a = int(a1 + (a2 - a1) * blend)
            
            pygame.draw.line(surface, (r, g, b, a), (0, y), (width, y))
        
        return surface
    
    def format_money(self, amount):
        """Форматирование денег как в HTML"""
        if amount >= 1000000:
            return f"${amount/1000000:.1f}M"
        elif amount >= 1000:
            return f"${amount/1000:.0f}K"
        return f"${int(amount)}"
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

class ModernBusinessButton:
    """Современная кнопка в стиле HTML"""
    
    def __init__(self, rect: pygame.Rect, text: str, on_click, is_primary=False):
        self.rect = rect
        self.text = text
        self.on_click = on_click
        self.is_primary = is_primary
        self.hovered = False
    
    def draw(self, surface, font_manager):
        """Отрисовка кнопки"""
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        if self.is_primary:
            # Основная кнопка с градиентом
            colors = [(106, 44, 255, 255), (20, 231, 209, 255)]
            gradient = self.create_vertical_gradient((self.rect.width, self.rect.height), colors)
            button_surface.blit(gradient, (0, 0))
            text_color = (7, 16, 24)
        else:
            # Вторичная кнопка
            bg_color = (255, 255, 255, 10) if not self.hovered else (255, 255, 255, 20)
            pygame.draw.rect(button_surface, bg_color, (0, 0, self.rect.width, self.rect.height), 
                           border_radius=12)
            pygame.draw.rect(button_surface, (255, 255, 255, 30), (0, 0, self.rect.width, self.rect.height), 
                           width=1, border_radius=12)
            text_color = TEXT_MUTED if not self.hovered else TEXT_PRIMARY
        
        # Текст
        font = pygame.font.Font(None, 14)
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=(self.rect.width//2, self.rect.height//2))
        button_surface.blit(text_surf, text_rect)
        
        surface.blit(button_surface, self.rect.topleft)
    
    def create_vertical_gradient(self, size, colors):
        """Создает вертикальный градиент"""
        width, height = size
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        for y in range(height):
            pos = y / max(height - 1, 1)
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * pos)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * pos)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * pos)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
        return surface
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

class ModernBusinessMenu:
    """Современное меню бизнесов в стиле HTML версии"""
    
    def __init__(self, game):
        self.game = game
        self.business_manager = BusinessManager()
        self.current_view = "mine"  # "mine", "catalog_light", "catalog_dark", "single"
        self.selected_business_uid: Optional[str] = None
        self.upgrade_menu: Optional[BusinessUpgradeMenu] = None
        self.business_cards = []
        self.catalog_items = []
        self.buttons = []
        self.scroll_offset = 0
        
        self.initialize_ui()
        
    def initialize_ui(self):
        """Инициализация UI"""
        self.nav_buttons = [
            ModernBusinessButton(pygame.Rect(50, 150, 200, 50), "Кликер", lambda: self.game.play_game()),
            ModernBusinessButton(pygame.Rect(50, 210, 200, 50), "Магазины", lambda: self.game.open_shop_selection()),
            ModernBusinessButton(pygame.Rect(50, 270, 200, 50), "Инвестиции", lambda: self.game.open_investments()),
            ModernBusinessButton(pygame.Rect(50, 330, 200, 50), "Бизнесы", lambda: None, True),
            ModernBusinessButton(pygame.Rect(50, 390, 200, 50), "Профиль", lambda: self.game.open_profile())
        ]
        
        # Кнопки вкладок
        self.tab_buttons = [
            ModernBusinessButton(pygame.Rect(280, 100, 180, 40), "Светлые бизнесы", 
                               lambda: self.open_catalog("light")),
            ModernBusinessButton(pygame.Rect(470, 100, 180, 40), "Тёмные бизнесы", 
                               lambda: self.open_catalog("dark"), True),
            ModernBusinessButton(pygame.Rect(660, 100, 150, 40), "Мои бизнесы", 
                               lambda: self.show_my_businesses(), True)
        ]

    def show_upgrades(self, business_uid: str):
        """Показывает меню улучшений для бизнеса"""
        business = self.business_manager.get_business(business_uid)
        if business:
            self.upgrade_menu = BusinessUpgradeMenu(business)
            self.current_view = "upgrades"
    
    def open_catalog(self, category: str):
        """Открытие каталога бизнесов"""
        self.current_view = f"catalog_{category}"
        self.selected_business_uid = None
        self.update_catalog_view(category)
    
    def show_my_businesses(self):
        """Показать мои бизнесы"""
        self.current_view = "mine"
        self.selected_business_uid = None
        self.update_business_cards()
    
    def show_single_business(self, business_uid: str):
        """Показать детали бизнеса"""
        self.current_view = "single"
        self.selected_business_uid = business_uid  # Теперь точно строка
        self.update_single_view()
    
    def update_business_cards(self):
        """Обновление карточек бизнесов"""
        self.business_cards = []
        
        businesses = self.business_manager.my_businesses
        card_width, card_height = 320, 140
        start_x = 280
        start_y = 160
        spacing = 16
        columns = 3
        
        for i, business in enumerate(businesses):
            row = i // columns
            col = i % columns
            
            x = start_x + col * (card_width + spacing)
            y = start_y + row * (card_height + spacing) - self.scroll_offset
            
            # Пропускаем карточки за пределами видимой области
            if y + card_height < 150 or y > 700:
                continue
                
            rect = pygame.Rect(x, y, card_width, card_height)
            self.business_cards.append(
                ModernBusinessCard(rect, business, lambda b=business: self.show_single_business(b.uid))
            )
    
    def update_catalog_view(self, category: str):
        """Обновление вида каталога"""
        self.catalog_items = []
        
        templates = (BusinessManager.LIGHT_BUSINESSES if category == "light" 
                    else BusinessManager.DARK_BUSINESSES)
        
        card_width, card_height = 260, 120
        start_x = 300
        start_y = 160
        spacing = 12
        columns = 3
        
        for i, template in enumerate(templates):
            row = i // columns
            col = i % columns
            
            x = start_x + col * (card_width + spacing)
            y = start_y + row * (card_height + spacing) - self.scroll_offset
            
            # Пропускаем элементы за пределами видимой области
            if y + card_height < 150 or y > 700:
                continue
                
            rect = pygame.Rect(x, y, card_width, card_height)
            self.catalog_items.append({
                'rect': rect,
                'template': template,
                'on_click': lambda t=template: self.buy_business(t)
            })
    
    def update_single_view(self):
        """Обновление детального вида бизнеса"""
        self.buttons = []    
        if self.selected_business_uid is None:
            return
            
        business_uid = self.selected_business_uid
        business = self.business_manager.get_business(business_uid)
        if not business:
            return
     
        # Кнопки действий
        action_y = 400
        self.buttons.extend([
            ModernBusinessButton(pygame.Rect(300, action_y, 300, 45), 
                               "Забрать доход", 
                               lambda: self.collect_income(), True),
            ModernBusinessButton(pygame.Rect(620, action_y, 280, 45), 
                               f"Увеличить доход", 
                               lambda: business.upgrade_income() and self.update_single_view()),
            ModernBusinessButton(pygame.Rect(300, action_y + 55, 280, 45), 
                               "Снизить расходы", 
                               lambda: business.upgrade_efficiency() and self.update_single_view()),
            ModernBusinessButton(pygame.Rect(620, action_y + 55, 280, 45), 
                               "Маркетинг", 
                               lambda: business.upgrade_marketing() and self.update_single_view()),
        ])
        
        # Кнопка улучшений (только если есть улучшения)
        if business.upgrades:
            self.buttons.append(
                ModernBusinessButton(
                    pygame.Rect(300, 340, 600, 45), 
                    "🗲 Улучшения бизнеса", 
                    lambda: self.show_upgrades(business_uid),  # Используем business_uid вместо self.selected_business_uid
                    True  # primary button
                )
            )
        
        # Кнопка продажи и назад
        self.buttons.extend([
            ModernBusinessButton(pygame.Rect(300, action_y + 110, 600, 45), 
                               f"Продать бизнес за {business.get_sell_price()}$", 
                               lambda: self.sell_business()),
            ModernBusinessButton(pygame.Rect(300, action_y + 165, 600, 45), 
                               "← Назад к списку", 
                               lambda: self.show_my_businesses())
        ])
    
    def buy_business(self, template: BusinessTemplate):
        """Покупка бизнеса"""
        business = self.business_manager.buy_business(template)
        self.show_my_businesses()
        self.show_single_business(business.uid)
        print(f"Бизнес '{business.name}' куплен!")
    
    def collect_income(self):
        """Сбор дохода"""
        if not self.selected_business_uid:
            return
        
        income = self.business_manager.collect_income(self.selected_business_uid)
        if income > 0:
            print(f"Собрано {income}$ дохода!")
            self.update_single_view()
    
    def sell_business(self):
        """Продажа бизнеса"""
        if not self.selected_business_uid:
            return
        
        business = self.business_manager.get_business(self.selected_business_uid)
        if business:
            self.business_manager.sell_business(self.selected_business_uid)
            self.show_my_businesses()
            print(f"Бизнес '{business.name}' продан!")
    
    def draw(self, surface):
        """Отрисовка меню"""
        # Фон
        surface.fill(DARK_BG)
        
        # Градиентные акценты как в HTML
        self.draw_background_accents(surface)
        
        # Основной контейнер
        self.draw_main_container(surface)
        
        # Навигация
        self.draw_navigation(surface)

        if self.current_view == "upgrades" and self.upgrade_menu:
            self.draw_upgrades_view(surface)
        # Контент в зависимости от текущего вида
        if self.current_view == "mine":
            self.draw_my_businesses(surface)
        elif self.current_view.startswith("catalog_"):
            self.draw_catalog(surface)
        elif self.current_view == "single":
            self.draw_single_business(surface)

    def draw_upgrades_view(self, surface):
        """Отрисовка вида улучшений"""
        content_rect = pygame.Rect(280, 150, 1120, 600)
        self.draw_modern_panel(surface, content_rect, (11, 17, 23, 200))
        
        # Кнопка назад
        back_button = ModernBusinessButton(
            pygame.Rect(300, 100, 150, 40),
            "← Назад",
            lambda: self.show_single_business(self.selected_business_uid if self.selected_business_uid is not None else "")
        )
        back_button.draw(surface, None)
        
        # Меню улучшений
        if self.upgrade_menu:
            self.upgrade_menu.draw(surface)
    
    def draw_background_accents(self, surface):
        """Рисует градиентные акценты фона как в HTML"""
        accent_surf = pygame.Surface((1450, 300), pygame.SRCALPHA)
        
        # Левый акцент
        left_gradient = self.create_radial_gradient((400, 400), ACCENT1 + (20,), (0, 0, 0, 0), (200, 100))
        accent_surf.blit(left_gradient, (0, 0))
        
        # Правый акцент  
        right_gradient = self.create_radial_gradient((400, 400), ACCENT1 + (20,), (0, 0, 0, 0), (1200, 150))
        accent_surf.blit(right_gradient, (1000, 0))
        
        surface.blit(accent_surf, (0, 0))
    
    def draw_main_container(self, surface):
        """Рисует основной контейнер как в HTML"""
        container_rect = pygame.Rect(20, 20, 1410, 790)
        self.draw_modern_panel(surface, container_rect)
        
        # Заголовок
        title_font = pygame.font.Font(None, 32)
        title_surf = title_font.render("Black Empire — Business Hub", True, TEXT_PRIMARY)
        surface.blit(title_surf, (1450//2 - title_surf.get_width()//2, 40))
        
        # Подзаголовок
        subtitle_font = pygame.font.Font(None, 16)
        subtitle_text = self.get_subtitle_text()
        subtitle_surf = subtitle_font.render(subtitle_text, True, TEXT_MUTED)
        surface.blit(subtitle_surf, (1450//2 - subtitle_surf.get_width()//2, 75))
    
    def draw_navigation(self, surface):
        """Рисует навигацию"""
        # Левая панель навигации
        nav_panel = pygame.Rect(30, 120, 240, 500)
        self.draw_modern_panel(surface, nav_panel, (15, 26, 34, 180))
        
        for button in self.nav_buttons:
            button.draw(surface, None)
        
        # Вкладки
        for tab in self.tab_buttons:
            tab.draw(surface, None)
        
        # Кнопки каталога (только в режиме моих бизнесов)
        #if self.current_view == "mine":
        #    self.open_light_btn.draw(surface, None)
        #    self.open_dark_btn.draw(surface, None)
    
    def draw_my_businesses(self, surface):
        """Отрисовка моих бизнесов"""
        content_rect = pygame.Rect(280, 150, 1120, 600)
        self.draw_modern_panel(surface, content_rect, (11, 17, 23, 200))
        
        if not self.business_manager.my_businesses:
            # Сообщение об отсутствии бизнесов
            empty_font = pygame.font.Font(None, 24)
            empty_text = "У тебя пока нет бизнесов. Открой каталог и купи первый бизнес."
            empty_surf = empty_font.render(empty_text, True, TEXT_MUTED)
            surface.blit(empty_surf, (content_rect.centerx - empty_surf.get_width()//2, 
                                    content_rect.centery - empty_surf.get_height()//2))
        else:
            # Сетка бизнесов
            for card in self.business_cards:
                card.draw(surface, None)
    
    def draw_catalog(self, surface):
        """Отрисовка каталога"""
        content_rect = pygame.Rect(280, 150, 1120, 600)
        self.draw_modern_panel(surface, content_rect, (11, 17, 23, 200))
        
        category = "light" if self.current_view == "catalog_light" else "dark"
        templates = (BusinessManager.LIGHT_BUSINESSES if category == "light" 
                    else BusinessManager.DARK_BUSINESSES)
        
        for item in self.catalog_items:
            self.draw_catalog_item(surface, item['rect'], item['template'])
    
    def draw_single_business(self, surface):
        """Отрисовка детального вида бизнеса"""
        content_rect = pygame.Rect(280, 150, 1120, 600)
        self.draw_modern_panel(surface, content_rect, (11, 17, 23, 200))
        
        if self.selected_business_uid is None:
            return
        business = self.business_manager.get_business(self.selected_business_uid)
        if not business:
            return
       
        # Заголовок и основная информация
        self.draw_business_detail(surface, business, content_rect)
        
        # Кнопки действий
        for button in self.buttons:
            button.draw(surface, None)
    
    def draw_modern_panel(self, surface, rect, color=(255, 255, 255, 10)):
        """Рисует современную панель с эффектом стекла"""
        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Основной фон
        pygame.draw.rect(panel_surface, color, (0, 0, rect.width, rect.height), border_radius=18)
        
        # Стеклянный эффект
        glass_gradient = self.create_vertical_gradient((rect.width, rect.height), 
                                                     [(255, 255, 255, 10), (255, 255, 255, 5)])
        panel_surface.blit(glass_gradient, (0, 0))
        
        # Рамка
        pygame.draw.rect(panel_surface, (255, 255, 255, 30), 
                        (0, 0, rect.width, rect.height), 
                        width=1, border_radius=18)
        
        surface.blit(panel_surface, rect.topleft)
    
    def draw_catalog_item(self, surface, rect, template):
        """Рисует элемент каталога"""
        item_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Фон
        pygame.draw.rect(item_surface, (255, 255, 255, 10), 
                        (0, 0, rect.width, rect.height), border_radius=12)
        pygame.draw.rect(item_surface, (255, 255, 255, 20), 
                        (0, 0, rect.width, rect.height), width=1, border_radius=12)
        
        # Название
        name_font = pygame.font.Font(None, 16)
        name_surf = name_font.render(template.name, True, TEXT_PRIMARY)
        item_surface.blit(name_surf, (12, 12))
        
        # Цена
        price_font = pygame.font.Font(None, 14)
        price_text = f"{self.format_money(template.price)}"
        price_surf = price_font.render(price_text, True, ACCENT2)
        price_rect = price_surf.get_rect(topright=(rect.width - 12, 12))
        item_surface.blit(price_surf, price_rect)
        
        # Описание
        desc_font = pygame.font.Font(None, 12)
        desc_text = template.description
        if len(desc_text) > 50:
            desc_text = desc_text[:47] + "..."
        desc_surf = desc_font.render(desc_text, True, TEXT_MUTED)
        item_surface.blit(desc_surf, (12, 35))
        
        # Доход в час
        income_text = f"Доход/час: {self.format_money(template.income_per_hour)}"
        income_surf = desc_font.render(income_text, True, TEXT_MUTED)
        income_rect = income_surf.get_rect(bottomleft=(12, rect.height - 12))
        item_surface.blit(income_surf, income_rect)
        
        # Кнопка покупки
        buy_btn = ModernBusinessButton(pygame.Rect(rect.width - 80, rect.height - 35, 70, 25), 
                                     "Купить", lambda: None)
        buy_btn.draw(item_surface, None)
        
        surface.blit(item_surface, rect.topleft)
    
    def draw_business_detail(self, surface, business, container_rect):
        """Рисует детальную информацию о бизнесе"""
        # Бейдж и основная информация
        badge_size = 84
        badge_x, badge_y = container_rect.x + 30, container_rect.y + 30
        
        # Бейдж с градиентом
        badge_gradient = self.create_vertical_gradient((badge_size, badge_size), [ACCENT1, ACCENT2])
        surface.blit(badge_gradient, (badge_x, badge_y))
        
        # Инициалы
        initials_font = pygame.font.Font(None, 24)
        initials = ''.join([word[0] for word in business.name.split()[:2]]).upper()
        initials_surf = initials_font.render(initials, True, (7, 16, 24))
        initials_rect = initials_surf.get_rect(center=(badge_x + badge_size//2, badge_y + badge_size//2))
        surface.blit(initials_surf, initials_rect)
        
        # Информация справа от бейджа
        info_x = badge_x + badge_size + 20
        info_y = badge_y
        
        name_font = pygame.font.Font(None, 24)
        name_surf = name_font.render(business.name, True, TEXT_PRIMARY)
        surface.blit(name_surf, (info_x, info_y))
        
        desc_font = pygame.font.Font(None, 14)
        desc_surf = desc_font.render(business.notes, True, TEXT_MUTED)
        surface.blit(desc_surf, (info_x, info_y + 30))
        
        stats_font = pygame.font.Font(None, 12)
        stats_text = f"Уровень: {business.level} · Доля рынка: {business.market_share}%"
        stats_surf = stats_font.render(stats_text, True, TEXT_MUTED)
        surface.blit(stats_surf, (info_x, info_y + 50))
        
        # Статистика доходов и расходов
        stats_y = badge_y + badge_size + 30
        self.draw_business_stats(surface, business, container_rect.x + 30, stats_y)
    
    def draw_business_stats(self, surface, business, x, y):
        """Рисует статистику бизнеса"""
        stats_width = 500
        stats_height = 100
        
        # Доходы
        income_rect = pygame.Rect(x, y, stats_width//2 - 10, stats_height)
        self.draw_stat_panel(surface, income_rect, "Доход / час", 
                        self.format_money(business.income_per_hour), 
                        f"Накоплено: {self.format_money(business.income_accumulated)}")
        
        # Расходы
        expense_rect = pygame.Rect(x + stats_width//2 + 10, y, stats_width//2 - 10, stats_height)
        
        # ИСПРАВЛЕННАЯ СТРОКА - используем upgrade_data вместо upgrades
        upgrade_info = f"Апгрейды: {business.upgrade_data.level}/{business.upgrade_data.automation}/{business.upgrade_data.marketing}"
        
        self.draw_stat_panel(surface, expense_rect, "Расход / час", 
                        self.format_money(business.expenses_per_hour), 
                        upgrade_info)
    
    def draw_stat_panel(self, surface, rect, title, value, note):
        """Рисует панель статистики"""
        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Фон
        pygame.draw.rect(panel_surface, (255, 255, 255, 10), 
                        (0, 0, rect.width, rect.height), border_radius=12)
        pygame.draw.rect(panel_surface, (255, 255, 255, 20), 
                        (0, 0, rect.width, rect.height), width=1, border_radius=12)
        
        # Заголовок
        title_font = pygame.font.Font(None, 12)
        title_surf = title_font.render(title, True, TEXT_MUTED)
        panel_surface.blit(title_surf, (12, 12))
        
        # Значение
        value_font = pygame.font.Font(None, 18)
        value_surf = value_font.render(value, True, TEXT_PRIMARY)
        panel_surface.blit(value_surf, (12, 30))
        
        # Примечание
        note_font = pygame.font.Font(None, 10)
        note_surf = note_font.render(note, True, TEXT_MUTED)
        panel_surface.blit(note_surf, (12, rect.height - 20))
        
        surface.blit(panel_surface, rect.topleft)
    
    def create_radial_gradient(self, size, inner_color, outer_color, center):
        """Создает радиальный градиент"""
        width, height = size
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        center_x, center_y = center
        
        for x in range(width):
            for y in range(height):
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                max_distance = math.sqrt(center_x**2 + center_y**2)
                ratio = min(distance / max_distance, 1.0)
                
                if len(inner_color) == 3:
                    r1, g1, b1 = inner_color
                    a1 = 255
                else:
                    r1, g1, b1, a1 = inner_color
                    
                if len(outer_color) == 3:
                    r2, g2, b2 = outer_color
                    a2 = 255
                else:
                    r2, g2, b2, a2 = outer_color
                
                r = int(r1 + (r2 - r1) * ratio)
                g = int(g1 + (g2 - g1) * ratio)
                b = int(b1 + (b2 - b1) * ratio)
                a = int(a1 + (a2 - a1) * ratio)
                
                surface.set_at((x, y), (r, g, b, a))
        
        return surface
    
    def create_vertical_gradient(self, size, colors):
        """Создает вертикальный градиент"""
        width, height = size
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if len(colors) == 1:
            surface.fill(colors[0])
            return surface
        
        for y in range(height):
            pos = y / max(height - 1, 1)
            color_index = pos * (len(colors) - 1)
            idx1 = min(int(color_index), len(colors) - 2)
            idx2 = idx1 + 1
            blend = color_index - idx1
            
            if len(colors[idx1]) == 3:
                r1, g1, b1 = colors[idx1]
                a1 = 255
            else:
                r1, g1, b1, a1 = colors[idx1]
                
            if len(colors[idx2]) == 3:
                r2, g2, b2 = colors[idx2]
                a2 = 255
            else:
                r2, g2, b2, a2 = colors[idx2]
            
            r = int(r1 + (r2 - r1) * blend)
            g = int(g1 + (g2 - g1) * blend)
            b = int(b1 + (b2 - b1) * blend)
            a = int(a1 + (a2 - a1) * blend)
            
            pygame.draw.line(surface, (r, g, b, a), (0, y), (width, y))
        
        return surface
    
    def format_money(self, amount):
        """Форматирование денег как в HTML версии"""
        if amount >= 1000000:
            return f"${amount/1000000:.1f}M"
        elif amount >= 1000:
            return f"${amount/1000:.0f}K"
        return f"${int(amount)}"
    
    def get_subtitle_text(self):
        """Получает текст подзаголовка в зависимости от текущего вида"""
        if self.current_view == "mine":
            count = len(self.business_manager.my_businesses)
            return f"У тебя куплено: {count} бизнес(ов). Кликни на карточку для деталей."
        elif self.current_view == "catalog_light":
            return "Светлые бизнесы — выберите бизнес для покупки"
        elif self.current_view == "catalog_dark":
            return "Тёмные бизнесы — выберите бизнес для покупки"
        elif self.current_view == "single":
            return "Детальная информация о бизнесе"
        return "Демо: покупка бизнеса, управление и апгрейды"
    
    def handle_event(self, event):
        """Обработка событий"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            
            # Навигационные кнопки
            for button in self.nav_buttons:
                if button.is_clicked(pos):
                    button.on_click()
                    return
            
            # Кнопки вкладок
            for tab in self.tab_buttons:
                if tab.is_clicked(pos):
                    tab.on_click()
                    return
            
            # Карточки бизнесов
            if self.current_view == "mine":
                for card in self.business_cards:
                    if card.is_clicked(pos):
                        card.on_click()
                        return
            
            # Элементы каталога
            elif self.current_view.startswith("catalog_"):
                for item in self.catalog_items:
                    if item['rect'].collidepoint(pos):
                        item['on_click']()
                        return
            
            # Кнопки в детальном виде
            elif self.current_view == "single":
                if hasattr(self, 'buttons'):
                    for button in self.buttons:
                        if button.is_clicked(pos):
                            button.on_click()
                            return
            
            # Кнопки в меню улучшений
            elif self.current_view == "upgrades" and self.upgrade_menu:
                for button in self.upgrade_menu.upgrade_buttons:
                    if button.is_clicked(pos):
                        button.on_click(button.upgrade)
                        return
                
                for button in self.upgrade_menu.stats_buttons:
                    if button.is_clicked(pos):
                        button.on_click()
                        return
        
        elif event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            
            # Обновление состояния наведения для всех интерактивных элементов
            all_buttons = []
            all_buttons.extend(self.nav_buttons)
            all_buttons.extend(self.tab_buttons)
            
            # Добавляем дополнительные кнопки, если они существуют
            if hasattr(self, 'buttons'):
                all_buttons.extend(self.buttons)
            
            # Добавляем кнопки улучшений если они активны
            if self.current_view == "upgrades" and self.upgrade_menu:
                all_buttons.extend(self.upgrade_menu.upgrade_buttons)
                all_buttons.extend(self.upgrade_menu.stats_buttons)
            
            for button in all_buttons:
                button.update_hover(pos)
            
            if self.current_view == "mine":
                for card in self.business_cards:
                    card.update_hover(pos)
    
    def update(self):
        """Обновление состояния меню"""
        self.business_manager.update_income()
        
        # Обновление UI в зависимости от текущего вида
        if self.current_view == "mine":
            self.update_business_cards()
        elif self.current_view.startswith("catalog_"):
            category = self.current_view.split("_")[1]
            self.update_catalog_view(category)
        elif self.current_view == "single":
            self.update_single_view()

@dataclass
class BusinessUpgradeData:
    """Отдельный класс для хранения данных об улучшениях"""
    level: int = 0
    automation: int = 0
    marketing: int = 0

"""
class Business:
    def __init__(self, template: BusinessTemplate):
        self.uid = f"b-{random.randint(10000, 99999)}"
        self.template_id = template.id
        self.name = template.name
        self.purchased_at = time.time()
        self.level = 1
        self.income_per_hour = template.income_per_hour
        self.income_accumulated = 0
        self.expenses_per_hour = int(template.income_per_hour * 0.35)
        self.market_share = round(random.uniform(1.0, 7.0), 2)
        
        # Разделяем улучшения на данные и объекты
        self.upgrade_data = BusinessUpgradeData()  # Простые данные
        self.upgrades: List[BusinessUpgrade] = []  # Объекты улучшений
        
        # Новые атрибуты для улучшений
        self.capacity_multiplier = 1.0
        self.quality_multiplier = 1.0
        self.automation_level = 0
        self.security_level = 0
        self.innovation_level = 0
        self.risk_level = 10.0  # Уровень риска (для темных бизнесов)
        
        self.notes = template.description
        self.initialize_upgrades()
    
    def initialize_upgrades(self):
        #Инициализирует улучшения для этого бизнеса
        if self.template_id in BUSINESS_UPGRADES:
            # Создаем копии улучшений для этого бизнеса
            for upgrade_template in BUSINESS_UPGRADES[self.template_id]:
                self.upgrades.append(BusinessUpgrade(
                    id=upgrade_template.id,
                    name=upgrade_template.name,
                    description=upgrade_template.description,
                    cost=upgrade_template.cost,
                    effect=upgrade_template.effect,
                    upgrade_type=upgrade_template.upgrade_type,
                    max_level=upgrade_template.max_level
                ))
    
    def get_available_upgrades(self) -> List[BusinessUpgrade]:
        #Возвращает доступные для покупки улучшения
        return [upgrade for upgrade in self.upgrades if upgrade.can_upgrade(self)]
    
    def purchase_upgrade(self, upgrade_id: str) -> bool:
        #Покупка улучшения
        upgrade = next((u for u in self.upgrades if u.id == upgrade_id), None)
        if not upgrade or not upgrade.can_upgrade(self):
            return False
        
        # В реальной реализации проверяем баланс игрока
        # if player_balance < upgrade.cost: return False
        
        upgrade.current_level += 1
        upgrade.apply_effect(self)
        return True
    
    def upgrade_income(self) -> bool:
        #Улучшение дохода
        cost = max(100, int(self.income_per_hour * 6))
        # В демо всегда успешно
        self.income_per_hour = int(self.income_per_hour * 1.25)
        self.upgrade_data.level += 1  # Используем upgrade_data вместо upgrades
        self.level += 1
        return True
    
    def upgrade_efficiency(self) -> bool:
        #Улучшение эффективности (снижение расходов)
        cost = max(80, int(self.expenses_per_hour * 4))
        self.expenses_per_hour = max(0, int(self.expenses_per_hour * 0.8))
        self.upgrade_data.automation += 1  # Используем upgrade_data вместо upgrades
        return True
    
    def upgrade_marketing(self) -> bool:
        #Улучшение маркетинга (увеличение доли рынка)
        cost = max(200, int(self.income_per_hour * 4))
        self.market_share = min(100.0, round(self.market_share + random.uniform(0.7, 3.7), 2))
        self.upgrade_data.marketing += 1  # Используем upgrade_data вместо upgrades
        return True
    
    def get_net_income_per_hour(self) -> int:
        #Чистый доход в час с учетом всех модификаторов
        base_income = self.income_per_hour * self.capacity_multiplier * self.quality_multiplier
        expenses = self.expenses_per_hour * (1 - self.automation_level * 0.1)
        return max(0, int(base_income - expenses))
    
    def calculate_risk(self) -> float:
        #Расчет уровня риска (для темных бизнесов)
        base_risk = 10.0
        risk_reduction = self.security_level * 2.0
        return max(1.0, base_risk - risk_reduction)
    
    def get_upgrade_progress(self) -> Dict[str, float]:
        #Возвращает прогресс по всем типам улучшений
        progress = {}
        for upgrade_type in UpgradeType:
            upgrades_of_type = [u for u in self.upgrades if u.upgrade_type == upgrade_type]
            if upgrades_of_type:
                total_levels = sum(u.current_level for u in upgrades_of_type)
                max_levels = sum(u.max_level for u in upgrades_of_type)
                progress[upgrade_type.value] = total_levels / max_levels if max_levels > 0 else 0
        return progress
    
    def get_sell_price(self) -> int:
        #Цена продажи (70% от вложений)
        return int(self.income_per_hour * 100 * 0.7)"""

class BusinessUpgradeMenu:
    def __init__(self, business: Business):
        self.business = business
        self.upgrade_buttons = []
        self.stats_buttons = []
        self.initialize_ui()
    
    def initialize_ui(self):
        """Инициализация UI для улучшений"""
        # Кнопки статистики
        stats_rect = pygame.Rect(300, 150, 400, 50)
        self.stats_buttons.append(
            ModernBusinessButton(stats_rect, "Общая статистика", self.show_stats)
        )
        
        # Кнопки по типам улучшений
        upgrade_types = list(UpgradeType)
        button_width, button_height = 180, 40
        start_x = 300
        start_y = 220
        
        for i, upgrade_type in enumerate(upgrade_types):
            x = start_x + (i % 3) * (button_width + 10)
            y = start_y + (i // 3) * (button_height + 10)
            
            # Проверяем есть ли такие улучшения у бизнеса
            has_upgrades = any(u.upgrade_type == upgrade_type for u in self.business.upgrades)
            if has_upgrades:
                self.stats_buttons.append(
                    ModernBusinessButton(
                        pygame.Rect(x, y, button_width, button_height),
                        upgrade_type.value.capitalize(),
                        lambda ut=upgrade_type: self.show_upgrades_by_type(ut)
                    )
                )

    def show_stats(self):
        """Показывает общую статистику улучшений"""
        # Очищаем кнопки улучшений, показываем только статистику
        self.upgrade_buttons.clear()
    
    def show_upgrades_by_type(self, upgrade_type: UpgradeType):
        """Показывает улучшения определенного типа"""
        self.upgrade_buttons.clear()
        
        upgrades = [u for u in self.business.get_available_upgrades() 
                   if u.upgrade_type == upgrade_type]
        
        start_x, start_y = 300, 300
        button_width, button_height = 350, 80
        
        for i, upgrade in enumerate(upgrades):
            y = start_y + i * (button_height + 10)
            rect = pygame.Rect(start_x, y, button_width, button_height)
            
            self.upgrade_buttons.append(
                UpgradeButton(rect, upgrade, self.purchase_upgrade)
            )
    
    def purchase_upgrade(self, upgrade: BusinessUpgrade):
        """Покупка улучшения"""
        if self.business.purchase_upgrade(upgrade.id):
            print(f"Улучшение '{upgrade.name}' куплено!")
            self.initialize_ui()  # Обновляем UI
    
    def draw(self, surface):
        """Отрисовка меню улучшений"""
        # Заголовок
        title_font = pygame.font.Font(None, 32)
        title_text = f"Улучшения: {self.business.name}"
        title_surf = title_font.render(title_text, True, TEXT_PRIMARY)
        surface.blit(title_surf, (300, 100))
        
        # Кнопки статистики и фильтров
        for button in self.stats_buttons:
            button.draw(surface, None)
        
        # Кнопки улучшений
        for button in self.upgrade_buttons:
            button.draw(surface)
        
        # Если нет активных улучшений, показываем статистику
        if not self.upgrade_buttons:
            self.draw_upgrade_progress(surface, 720, 150)
    
    def draw_upgrade_progress(self, surface, x, y):
        """Рисует прогресс по типам улучшений"""
        progress = self.business.get_upgrade_progress()
        
        progress_font = pygame.font.Font(None, 16)
        title_surf = progress_font.render("Прогресс улучшений:", True, TEXT_PRIMARY)
        surface.blit(title_surf, (x, y))
        
        for i, (upgrade_type, progress_value) in enumerate(progress.items()):
            progress_y = y + 30 + i * 25
            
            # Текст типа
            type_surf = progress_font.render(upgrade_type.capitalize(), True, TEXT_MUTED)
            surface.blit(type_surf, (x, progress_y))
            
            # Полоска прогресса
            bar_width, bar_height = 150, 12
            bar_x = x + 120
            
            # Фон полоски
            pygame.draw.rect(surface, (50, 50, 50), 
                           (bar_x, progress_y, bar_width, bar_height), border_radius=6)
            
            # Заполнение
            fill_width = int(bar_width * progress_value)
            if fill_width > 0:
                color = self.get_progress_color(progress_value)
                pygame.draw.rect(surface, color, 
                               (bar_x, progress_y, fill_width, bar_height), border_radius=6)
            
            # Процент
            percent_text = f"{int(progress_value * 100)}%"
            percent_surf = progress_font.render(percent_text, True, TEXT_PRIMARY)
            surface.blit(percent_surf, (bar_x + bar_width + 10, progress_y - 2))
    
    def get_progress_color(self, progress: float):
        """Возвращает цвет прогресса в зависимости от значения"""
        if progress < 0.3:
            return (220, 50, 50)    # Красный
        elif progress < 0.7:
            return (220, 180, 50)   # Желтый
        else:
            return (50, 220, 50)    # Зеленый

class UpgradeButton:
    """Кнопка улучшения бизнеса"""
    
    def __init__(self, rect: pygame.Rect, upgrade: BusinessUpgrade, on_click):
        self.rect = rect
        self.upgrade = upgrade
        self.on_click = on_click
        self.hovered = False
    
    def draw(self, surface):
        """Отрисовка кнопки улучшения"""
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Фон кнопки
        bg_color = (60, 60, 80, 200) if not self.hovered else (80, 80, 100, 200)
        pygame.draw.rect(button_surface, bg_color, 
                        (0, 0, self.rect.width, self.rect.height), border_radius=10)
        
        # Рамка
        border_color = (100, 100, 150) if not self.hovered else (120, 120, 180)
        pygame.draw.rect(button_surface, border_color, 
                        (0, 0, self.rect.width, self.rect.height), 
                        width=2, border_radius=10)
        
        # Текст улучшения
        font = pygame.font.Font(None, 16)
        name_surf = font.render(self.upgrade.name, True, TEXT_PRIMARY)
        button_surface.blit(name_surf, (10, 10))
        
        # Описание
        desc_font = pygame.font.Font(None, 12)
        desc_surf = desc_font.render(self.upgrade.description, True, TEXT_MUTED)
        button_surface.blit(desc_surf, (10, 30))
        
        # Стоимость и уровень
        cost_text = f"Стоимость: {self.upgrade.cost}$"
        level_text = f"Уровень: {self.upgrade.current_level}/{self.upgrade.max_level}"
        
        cost_surf = desc_font.render(cost_text, True, ACCENT2)
        level_surf = desc_font.render(level_text, True, TEXT_MUTED)
        
        button_surface.blit(cost_surf, (10, 50))
        button_surface.blit(level_surf, (self.rect.width - 100, 50))
        
        surface.blit(button_surface, self.rect.topleft)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

class ProfileMenu:
    """Простое меню профиля без скролла."""
    
    def __init__(self, game, nav_buttons):
        self.game = game
        self.card_buttons = []  # Кнопки в карточках
        self.nav_buttons = nav_buttons
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

        self.icon_renderer = IconRenderer()
        self.nav_buttons = self.create_nav_buttons()
        self.shop_system = ShopSystem(self)
        self.shop_selection_menu = ShopSelectionMenu(self, self.nav_buttons)
        self.light_shop_menu = LightShopMenu(self, self.nav_buttons)
        self.light_category_products_menu = LightCategoryProductsMenu(self, self.nav_buttons)
        self.black_market_category_products_menu = BlackMarketCategoryProductsMenu(self, self.nav_buttons)
        self.black_market_menu = BlackMarketMenu(self, self.nav_buttons)
        self.business_menu = ModernBusinessMenu(self)
        self.profile_menu = ProfileMenu(self, self.nav_buttons)
        
        
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
        self.clicker_menu = ClickerMenu(self, self.nav_buttons)
        self.investment_menu = InvestmentMenu(self, self.nav_buttons)
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

    def create_nav_buttons(self):
        """Создает навигационные кнопки для всех меню"""
        nav_buttons = []
        
        nav_positions = [
            ("Кликер", 10, 20, 80, 150),
            ("Магазины", 10, 180, 80, 150),
            ("Инвестиции", 10, 340, 80, 150),
            ("Бизнесы", 10, 500, 80, 150),
            ("Профиль", 10, 660, 80, 150)
        ]

        nav_actions = {
            "Кликер": (
                lambda surface, rect: self.draw_icon_in_center(surface, rect, "clicker"),
                self.play_game
            ),
            "Магазины": (
                lambda surface, rect: self.draw_icon_in_center(surface, rect, "shop"),
                self.open_shop_selection
            ),
            "Инвестиции": (
                lambda surface, rect: self.draw_icon_in_center(surface, rect, "investments"),
                self.open_investments
            ),
            "Бизнесы": (
                lambda surface, rect: self.draw_icon_in_center(surface, rect, "business"),
                self.open_businesses
            ),
            "Профиль": (
                lambda surface, rect: self.draw_icon_in_center(surface, rect, "profile"),
                self.open_profile
            )
        }

        for text, x, y, width, height in nav_positions:
            rect = pygame.Rect(x, y, width, height)
            icon_func, action = nav_actions[text]
            is_active = (text == "Кликер")
            button = NavButton(rect, text, is_active)
            button.icon_function = icon_func
            button.action = action
            nav_buttons.append(button)

        return nav_buttons

    def draw_icon_in_center(self, surface, rect, icon_type, icon_size=50):
        """Вспомогательная функция для рисования иконки по центру кнопки"""
        icon_x = rect.centerx - icon_size // 2 - 2
        icon_y = rect.centery - icon_size // 2 + 35

        if icon_type == "clicker":
            self.icon_renderer.draw_clicker_image_icon(surface, icon_x, icon_y, icon_size)
        elif icon_type == "shop":
            self.icon_renderer.draw_shop_image_icon(surface, icon_x, icon_y, icon_size)
        elif icon_type == "investments":
            self.icon_renderer.draw_investments_image_icon(surface, icon_x, icon_y, icon_size)
        elif icon_type == "business":
            self.icon_renderer.draw_business_image_icon(surface, icon_x, icon_y, icon_size)
        elif icon_type == "profile":
            self.icon_renderer.draw_profile_image_icon(surface, icon_x, icon_y, icon_size)

    def draw_nav_buttons(self, surface):
        """Отрисовывает навигационные кнопки с иконками"""
        for nav_button in self.nav_buttons:
            nav_button.draw(surface)
            if hasattr(nav_button, 'icon_function'):
                button.icon_function(surface, nav_button.rect)

    def update_navigation_state(self, active_button_text):
        """Обновляет состояние кнопок навигации во всех меню"""
        menus = [
            getattr(self, 'clicker_menu', None),
            getattr(self, 'investment_menu', None),
            getattr(self, 'shop_selection_menu', None),
            getattr(self, 'light_shop_menu', None),
            getattr(self, 'black_market_menu', None),
            getattr(self, 'business_menu', None)
        ]

        # Обновляем основные навигационные кнопки
        for button in self.nav_buttons:
            button.is_active = (button.text == active_button_text)

        # Обновляем кнопки в меню
        for menu in menus:
            if menu is not None:
                buttons = None
                for attr_name in ['nav_buttons', 'buttons', 'navigation_buttons']:
                    if hasattr(menu, attr_name):
                        buttons = getattr(menu, attr_name)
                        break
                if buttons:
                    for button in buttons:
                        if hasattr(button, 'text') and hasattr(button, 'is_active'):
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
            print(f"ТЫ ЕБАНЫЙ ХУЕСОС: {e}")
            import traceback
            traceback.print_exc()
                
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
            import traceback
            traceback.print_exc()
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

        # self.draw_nav_buttons(self.screen)

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