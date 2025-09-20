import pygame
import sys
import math
import random
import time
from pygame import gfxdraw
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum
# from coreLogic import ExportDB  # Закомментировал, так как этого модуля нет

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1450
SCREEN_HEIGHT = 830

# Color palette
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

@dataclass
class Star:
    """Класс для анимированных звезд."""
    x: float
    y: float
    z: float  # Глубина для параллакс-эффекта
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
        
        for y in range(height):
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

class Button:
    """Интерактивная кнопка с увеличенным закруглением."""
    
    def __init__(self, rect, text, icon_renderer=None, action=None, icon_size=30):
        self.rect = rect
        self.text = text
        self.icon_renderer = icon_renderer
        self.action = action
        self.hovered = False
        self.cache = {}
        self.click_animation = 0
        self.icon_size = icon_size
    
    def draw(self, surface, font, icon_x, icon_y):
        state_key = (self.rect.width, self.rect.height, self.hovered, int(self.click_animation * 10))
        if state_key not in self.cache:
            # Создаем закругленную кнопку с градиентом
            if self.hovered:
                colors = [(180, 60, 255, 200), (120, 20, 220, 200), (55, 0, 110, 200)]
            else:
                colors = [(55, 0, 110, 150), (120, 20, 220, 150), (55, 0, 110, 150)]
            
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
                [(55, 0, 110, 255), (120, 20, 220, 255), (55, 0, 110, 255)],  # Убрали прозрачность
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
                [(55, 0, 110, 255), (120, 20, 220, 255), (55, 0, 110, 255)],  # Убрали прозрачность
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
    def handle_global_events(self, event, dropdowns):
        """Обрабатывает глобальные события для dropdown."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Проверяем, был ли клик по любому dropdown
            clicked_on_dropdown = False
            for dropdown in dropdowns:
                if dropdown.handle_event(event):
                    clicked_on_dropdown = True
                    break
            
            # Если клик был не по dropdown, закрываем все
            if not clicked_on_dropdown:
                # Проверяем, был ли клик по области любого открытого dropdown
                for dropdown in dropdowns:
                    if dropdown.is_open:
                        option_height = 40
                        dropdown_rect = pygame.Rect(
                            dropdown.rect.x, 
                            dropdown.rect.bottom, 
                            dropdown.rect.width, 
                            option_height * len(dropdown.options)
                        )
                        if dropdown_rect.collidepoint(event.pos):
                            clicked_on_dropdown = True
                            break
                
                if not clicked_on_dropdown:
                    Dropdown.close_all_dropdowns()
        
        elif event.type == pygame.MOUSEMOTION:
            # Обрабатываем движение мыши только для активного dropdown
            if Dropdown.active_dropdown:
                Dropdown.active_dropdown.handle_event(event)
            else:
                for dropdown in dropdowns:
                    dropdown.handle_event(event)

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
        self.loading_duration = 5.0  # 5 секунд загрузки
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
        
        # Заполнение
        fill_width = int(bar_width * self.progress)
        if fill_width > 0:
            fill_colors = [(120, 20, 220, 255), (160, 60, 255, 255), (120, 20, 220, 255)]
            fill_gradient = GradientGenerator.create_rounded_rect(
                (fill_width, bar_height), fill_colors, BAR_BORDER_RADIUS
            )
            self.screen.blit(fill_gradient, (bar_x, bar_y))
        
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

class ClickerMenu:
    """Простая временная версия кликера."""
    
    def __init__(self, game):
        self.game = game
        self.balance = 0
        self.click_value = 1
        self.initialize_ui()
    
    def initialize_ui(self):
        """Инициализация UI кликера."""
        # Кнопки левой панели навигации
        self.nav_buttons = []
        nav_options = [
            ("Кликер", lambda: None, True),  # Активная кнопка
            ("Магазины", lambda: print("Магазины"), False),
            ("Инвестиции", lambda: self.game.open_investments(), False),
            ("Бизнесы", lambda: print("Бизнесы"), False),
            ("Профиль", lambda: print("Профиль"), False)
        ]
        
        button_width, button_height = 200, 60
        button_x = 50
        button_y_start = 150
        
        for i, (text, action, is_active) in enumerate(nav_options):
            rect = pygame.Rect(button_x, button_y_start + i * 70, button_width, button_height)
            self.nav_buttons.append(NavButton(rect, text, action, is_active))
    
    def draw(self, surface):
        """Отрисовывает кликер."""
        # Рисуем левую панель навигации
        nav_panel_rect = pygame.Rect(30, 120, 240, 500)
        self.draw_panel(surface, nav_panel_rect, (30, 30, 50, 200))
        
        # Рисуем правую панель с кликером
        content_panel_rect = pygame.Rect(300, 120, 1100, 600)
        self.draw_panel(surface, content_panel_rect, (30, 30, 50, 200))
        
        # Рисуем кнопки навигации
        for button in self.nav_buttons:
            button.draw(surface, self.game.font_manager.get_font('button'))
        
        # Рисуем интерфейс кликера
        self.draw_clicker_interface(surface, 350, 200)
    
    def draw_panel(self, surface, rect, color):
        """Рисует панель с закругленными углами."""
        pygame.draw.rect(surface, color, rect, border_radius=15)
        pygame.draw.rect(surface, (100, 100, 150, 255), rect, width=2, border_radius=15)
    
    def draw_clicker_interface(self, surface, x, y):
        """Рисует интерфейс кликера."""
        # Баланс
        balance_font = self.game.font_manager.get_font('title')
        balance_text = f"Баланс: {self.balance}$"
        balance_surf = balance_font.render(balance_text, True, TEXT_PRIMARY)
        surface.blit(balance_surf, (x, y))
        
        # Кнопка для клика
        click_button_rect = pygame.Rect(x, y + 100, 200, 200)
        pygame.draw.circle(surface, PURPLE_PRIMARY, click_button_rect.center, 100)
        pygame.draw.circle(surface, LIGHT_PURPLE, click_button_rect.center, 100, 5)
        
        click_font = self.game.font_manager.get_font('button')
        click_text = "КЛИК!"
        click_surf = click_font.render(click_text, True, TEXT_PRIMARY)
        click_rect = click_surf.get_rect(center=click_button_rect.center)
        surface.blit(click_surf, click_rect)
        
        # Значение клика
        value_font = self.game.font_manager.get_font('desc')
        value_text = f"+{self.click_value}$ за клик"
        value_surf = value_font.render(value_text, True, TEXT_SECONDARY)
        surface.blit(value_surf, (x + 250, y + 150))
    
    def handle_click(self):
        """Обрабатывает клик по кнопке."""
        self.balance += self.click_value
    
    def handle_event(self, event):
        """Обрабатывает события кликера."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Проверяем клики по кнопкам навигации
            for button in self.nav_buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    return True
            
            # Проверяем клик по кнопке кликера
            click_button_rect = pygame.Rect(350, 300, 200, 200)
            if click_button_rect.collidepoint(mouse_pos):
                self.handle_click()
                return True
        
        return False

#вкладка Инвестиции
class InvestmentMenu:
    """Класс для меню инвестиций."""
    
    def __init__(self, game):
        self.game = game
        # self.export = ExportDB()  # Закомментировал, так как ExportDB не определен
        self.current_tab = "акции"  # Текущая активная вкладка
        self.buttons = []
        self.tab_buttons = []
        self.initialize_ui()
    
    def initialize_ui(self):
        """Инициализация UI элементов меню инвестиций."""
        # Кнопки левой панели навигации
        nav_buttons = [
            ("Кликер", lambda: print("Переход в кликер")),
            ("Магазины", lambda: print("Переход в магазины")),
            ("Инвестиции", lambda: None),  # Активная кнопка
            ("Бизнесы", lambda: print("Переход в бизнесы")),
            ("Профиль", lambda: print("Переход в профиль"))
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
        
        # Получаем данные портфеля (заглушка - в реальности из ExportDB)
        # portfolio_data = self.game.export_db.get_bag() if hasattr(self.game, 'export_db') else (0, 0, 0, 0, 0, 0)
        portfolio_data = (1000, 5, 50, 15, 200, 5000)  # Заглушка
        
        labels = [
            f"Стоимость всего портфеля: {portfolio_data[0]}$",
            f"Дивидендная доходность: {portfolio_data[1]}%",
            f"Стабильный доход: {portfolio_data[2]}$",
            f"Потенциал роста: {portfolio_data[3]}%",
            f"Доход от аренды: {portfolio_data[4]}$",
            f"Общая стоимость криптовалюты: {portfolio_data[5]}$"
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
        
        # Получаем список акций (заглушка - в реальности из базы данных)
        # В реальном коде: stocks = self.get_available_stocks()
        # actives = self.export.get_actives()
        # if actives:
        #     stocks = actives
        # else:
        #     stocks = ["Все акции куплены"]
        stocks = ["Apple", "Google", "Microsoft", "Tesla", "Amazon"]  # Заглушка
        
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
        
        # actives = self.export.get_homes()
        # if actives:
        #     stocks = actives
        # else:
        #     stocks = ["Вся недвижимость куплена"]
        stocks = ["Квартира в центре", "Загородный дом", "Офисное здание"]  # Заглушка
        
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
        
        # actives = self.export.get_crypto()
        # if actives:
        #     stocks = actives
        # else:
        #     stocks = ["Вся криптовалюта куплена"]
        stocks = ["Bitcoin", "Ethereum", "Litecoin", "Ripple"]  # Заглушка
        
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
        """Обрабатывает события меню инвестиций."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Проверяем клики по кнопкам навигации
            for button in self.buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    return True
            
            # Проверяем клики по кнопкам вкладок
            for button in self.tab_buttons:
                if button.rect.collidepoint(mouse_pos):
                    button.click()
                    return True
            
            # Проверяем клики по акциям/недвижимости/крипте
            if self.current_tab == "акции":
                # Логика обработки кликов по акциям
                pass
            
            # Аналогично для других вкладок
        
        return False


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

class Game:
    """Основной класс игры."""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Black Empire')
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = ScreenState.LOADING
        
        # Инициализируем options до создания dropdown
        self.theme_options = ["Тёмная", "Светлая", "Системная"]
        self.resolution_options = ["1280x720", "1920x1080", "2560x1440"]
        self.fps_options = ["30 fps", "60 fps", "120 fps"]
        self.language_options = ["Русский", "English"]
        
        self.font_manager = FontManager()
        self.icon_renderer = IconRenderer()
        self.clicker_menu = ClickerMenu(self)
        self.investment_menu = InvestmentMenu(self)
        self.loading_screen = LoadingScreen(self.screen, self.font_manager)
        
        self.stars = []
        self.background_cache = None
        self.panel_cache = {}
        self.last_time = time.time()
        
        # Настройки игры
        self.settings = {
            "theme": "Тёмная",
            "resolution": "1280x720",
            "fps": "30 fps",
            "language": "Русский"
        }

        self.initialize_ui()

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
    
    def play_game(self):
        """Переход в игровой режим (кликер)."""
        self.state = ScreenState.CLICKER
        print("Запуск игры...")
    
    def open_investments(self):
        """Открывает меню инвестиций."""
        self.state = ScreenState.INVESTMENTS
        print("Открытие инвестиций...")
    
    def open_settings(self):
        """Открывает настройки."""
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
            'version': "v0.0.1"
        }
        
        # Панели главного меню
        self.left_panel_rect = pygame.Rect(80, 120, 580, 680)
        self.right_panel_rect = pygame.Rect(740, 120, 580, 680)
        
        button_width, button_height = 460, 65
        button_y_start = self.right_panel_rect.y + 200
        
        # Исправляем лямбда-функции - убираем лишние параметры
        self.buttons = [
            Button(
                pygame.Rect(self.right_panel_rect.x + 60, button_y_start, button_width, button_height),
                "Играть", 
                lambda surface, icon_x, icon_y, size=30: self.icon_renderer.draw_play_icon(surface, icon_x, icon_y, size), 
                self.play_game
            ),
            Button(
                pygame.Rect(self.right_panel_rect.x + 60, button_y_start + 100, button_width, button_height),
                "Настройки", 
                lambda surface, icon_x, icon_y, size=40: self.icon_renderer.draw_settings_icon(surface, icon_x, icon_y, size), 
                self.open_settings
            ),
            Button(
                pygame.Rect(self.right_panel_rect.x + 60, button_y_start + 200, button_width, button_height),
                "Выход", 
                lambda surface, icon_x, icon_y, size=30: self.icon_renderer.draw_exit_icon(surface, icon_x, icon_y, size), 
                self.exit_game
            ),
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
        
        # Dropdown для настроек - создаем здесь, после инициализации options
        # Dropdown позиции (правее надписей)
        dropdown_theme_x = SCREEN_WIDTH//2 - 350 + 70
        dropdown_resolution_x = SCREEN_WIDTH//2 + 30 + 135
        dropdown_fps_x = SCREEN_WIDTH//2 - 350 + 60
        dropdown_language_x = SCREEN_WIDTH//2 + 30 + 70

        dropdown_width, dropdown_height = 200, 50

        self.theme_dropdown = Dropdown(
            pygame.Rect(dropdown_theme_x, 230, dropdown_width, dropdown_height),
            self.theme_options,
            self.theme_options.index(self.settings["theme"])
        )

        self.resolution_dropdown = Dropdown(
            pygame.Rect(dropdown_resolution_x, 230, dropdown_width, dropdown_height),
            self.resolution_options,
            self.resolution_options.index(self.settings["resolution"])
        )

        self.fps_dropdown = Dropdown(
            pygame.Rect(dropdown_fps_x, 410, dropdown_width, dropdown_height),
            self.fps_options,
            self.fps_options.index(self.settings["fps"])
        )

        self.language_dropdown = Dropdown(
            pygame.Rect(dropdown_language_x, 410, dropdown_width, dropdown_height),
            self.language_options,
            self.language_options.index(self.settings["language"])
        )
        
        self.dropdowns = [
            self.theme_dropdown,
            self.resolution_dropdown,
            self.fps_dropdown,
            self.language_dropdown
        ]
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state in [ScreenState.SETTINGS, ScreenState.CLICKER, ScreenState.INVESTMENTS]:
                        self.back_to_menu()
                    else:
                        self.running = False
            
            # Глобальная обработка dropdown событий
            if self.state == ScreenState.SETTINGS:
                # Обрабатываем события dropdown перед другими событиями
                dropdown_handled = False
                for dropdown in self.dropdowns:
                    if dropdown.handle_event(event):
                        dropdown_handled = True
                        break
                
                # Если dropdown обработал событие, пропускаем остальную обработку
                if dropdown_handled:
                    continue
            
            if self.state == ScreenState.MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Левая кнопка мыши
                        for button in self.buttons:
                            if button.is_hovered(mouse_pos):
                                button.click()
                elif event.type == pygame.MOUSEMOTION:
                    for button in self.buttons:
                        button.hovered = button.is_hovered(mouse_pos)
            
            elif self.state == ScreenState.SETTINGS:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.back_button.is_hovered(mouse_pos):
                            self.back_button.click()
                        # Закрываем все dropdown при клике вне их области
                        elif not any(dropdown.rect.collidepoint(mouse_pos) for dropdown in self.dropdowns):
                            # Проверяем, не кликнули ли по открытому dropdown меню
                            click_on_dropdown_menu = False
                            for dropdown in self.dropdowns:
                                if dropdown.is_open:
                                    option_height = 40
                                    dropdown_menu_rect = pygame.Rect(
                                        dropdown.rect.x,
                                        dropdown.rect.bottom,
                                        dropdown.rect.width,
                                        option_height * len(dropdown.options)
                                    )
                                    if dropdown_menu_rect.collidepoint(mouse_pos):
                                        click_on_dropdown_menu = True
                                        break
                            
                            if not click_on_dropdown_menu:
                                Dropdown.close_all_dropdowns()
                
                if event.type == pygame.MOUSEMOTION:
                    self.back_button.hovered = self.back_button.is_hovered(mouse_pos)
            
            elif self.state == ScreenState.CLICKER:
                if self.clicker_menu.handle_event(event):
                    continue

            elif self.state == ScreenState.INVESTMENTS:
                if self.investment_menu.handle_event(event):
                    continue
    
    def run(self):
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
        icon_x = self.back_button.rect.x + 20
        icon_y = self.back_button.rect.centery - 12
        self.back_button.draw(self.screen, self.font_manager.get_font('button'), icon_x, icon_y)
        
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
    
        options = [
            ("Тема:", self.theme_dropdown, theme_x, 240),
            ("Разрешение:", self.resolution_dropdown, resolution_x, 240),
            ("FPS:", self.fps_dropdown, fps_x, 420),
            ("Язык:", self.language_dropdown, language_x, 420)
        ]
        
        for label, dropdown, x_pos, y_pos in options:
            # Метка
            label_text = self.font_manager.get_rendered_text(label, 'settings_option', TEXT_PRIMARY)
            self.screen.blit(label_text, (x_pos, y_pos))
            
            # Dropdown
            dropdown.draw(self.screen, self.font_manager.get_font('settings_value'))

if __name__ == "__main__":
    game = Game()
    game.run()