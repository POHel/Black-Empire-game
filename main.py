import pygame
import sys
import math
import random
import sqlite3
import json
#кароче скоро реализую тут логику для сохранения настроек файлом config.json
from coreLogic import AppLogic, export_db, update_db
from typing import Dict, List, Tuple, Optional, Callable, Any
from enum import Enum
from datetime import datetime

# Инициализация pygame
pygame.init()
pygame.font.init()

logic = AppLogic()
# Константы компании
COMPANY_NAME = logic.company_name
VERSION = logic.version

WINDOW_SIZES = {
    '1280x720': (1280, 720),
    '1920x1080': (1920, 1080)
}

# Настройки по умолчанию
WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_SIZES['1920x1080']
FPS = 120
CURRENT_THEME = 'dark'
CURRENT_RESOLUTION = '1920x1080'

# Константы языков
LANGUAGES = {
    'ru': 'Русский',
    'en': 'English', 
    'de': 'Deutsch',
    'fr': 'Français',
    'es': 'Español'
}

CURRENT_LANGUAGE = 'ru'

# Локализация
LOCALIZATION = {
    'ru': {
        'settings': 'Настройки',
        'back': 'Назад',
        'apply': 'Применить',
        'theme': 'Тема',
        'resolution': 'Разрешение',
        'fps': 'Частота кадров',
        'volume': 'Громкость',
        'brightness': 'Яркость',
        'language': 'Язык',
        'dark': 'Тёмная',
        'light': 'Светлая',
        'company_info': f"{COMPANY_NAME} | Версия {VERSION}"
    },
    'en': {
        'settings': 'Settings',
        'back': 'Back',
        'apply': 'Apply',
        'theme': 'Theme',
        'resolution': 'Resolution',
        'fps': 'FPS',
        'volume': 'Volume',
        'brightness': 'Brightness',
        'language': 'Language',
        'dark': 'Dark',
        'light': 'Light',
        'company_info': f"{COMPANY_NAME} | Version {VERSION}"
    },
    'de': {
        'settings': 'Einstellungen',
        'back': 'Zurück',
        'apply': 'Übernehmen',
        'theme': 'Thema',
        'resolution': 'Auflösung',
        'fps': 'Bildrate',
        'volume': 'Lautstärke',
        'brightness': 'Helligkeit',
        'language': 'Sprache',
        'dark': 'Dunkel',
        'light': 'Hell',
        'company_info': f"{COMPANY_NAME} | Version {VERSION}"
    },
    'fr': {
        'settings': 'Paramètres',
        'back': 'Retour',
        'apply': 'Appliquer',
        'theme': 'Thème',
        'resolution': 'Résolution',
        'fps': 'FPS',
        'volume': 'Volume',
        'brightness': 'Luminosité',
        'language': 'Langue',
        'dark': 'Sombre',
        'light': 'Clair',
        'company_info': f"{COMPANY_NAME} | Version {VERSION}"
    },
    'es': {
        'settings': 'Configuración',
        'back': 'Atrás',
        'apply': 'Aplicar',
        'theme': 'Tema',
        'resolution': 'Resolución',
        'fps': 'FPS',
        'volume': 'Volumen',
        'brightness': 'Brillo',
        'language': 'Idioma',
        'dark': 'Oscuro',
        'light': 'Claro',
        'company_info': f"{COMPANY_NAME} | Versión {VERSION}"
    }
}

def get_text(key: str) -> str:
    """Получить локализованный текст"""
    return LOCALIZATION[CURRENT_LANGUAGE].get(key, key)

# Цветовые темы
THEMES = {
    'dark': {
        'bg_primary': (0, 0, 0),
        'bg_secondary': (10, 10, 30),
        'accent': (128, 0, 255),
        'neon_glow': (0, 255, 128, 100),
        'text': (255, 255, 255),
        'panel': (50, 50, 100, 200),
        'success': (0, 255, 0),
        'warning': (255, 255, 0),
        'error': (255, 0, 0),
        'card': (30, 30, 70, 220),
        'card_dark': (20, 20, 40, 220),
        'card_light': (70, 70, 120, 220)
    },
    'light': {
        'bg_primary': (255, 255, 255),
        'bg_secondary': (240, 240, 250),
        'accent': (100, 150, 255),
        'neon_glow': (255, 100, 0, 100),
        'text': (0, 0, 0),
        'panel': (255, 255, 255, 220),
        'success': (0, 200, 0),
        'warning': (200, 200, 0),
        'error': (200, 0, 0),
        'card': (220, 220, 240, 220),
        'card_dark': (200, 200, 220, 220),
        'card_light': (240, 240, 255, 220)
    }
}

# Состояния кнопок
class ButtonState(Enum):
    NORMAL = 0
    HOVER = 1
    PRESSED = 2

class ToggleButton:
    def __init__(self, x: float, y: float, width: float, height: float,
                 options: List[str], default_index: int = 0,
                 on_change: Optional[Callable[[str], None]] = None,
                 font_size: int = 20, corner_radius: int = 5):
        self.rect = pygame.Rect(x - width/2, y - height/2, width, height)
        self.options = options
        self.current_index = default_index
        self.on_change = on_change
        self.state = ButtonState.NORMAL
        self.font = pygame.font.SysFont('Arial', font_size)
        self.corner_radius = corner_radius
        self.option_width = width / len(options)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                rel_x = mouse_pos[0] - self.rect.x
                new_index = int(rel_x / self.option_width)
                if new_index != self.current_index:
                    self.current_index = new_index
                    if self.on_change:
                        self.on_change(self.options[new_index])
                    return True
        return False
    
    def draw(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        
        # Фон
        pygame.draw.rect(surface, theme['panel'], self.rect, border_radius=self.corner_radius)
        
        # Активная опция
        active_rect = pygame.Rect(
            self.rect.x + self.current_index * self.option_width,
            self.rect.y,
            self.option_width,
            self.rect.height
        )
        pygame.draw.rect(surface, theme['accent'], active_rect, border_radius=self.corner_radius)
        
        # Разделители и текст
        for i, option in enumerate(self.options):
            option_rect = pygame.Rect(
                self.rect.x + i * self.option_width,
                self.rect.y,
                self.option_width,
                self.rect.height
            )
            
            text_color = theme['text'] if i == self.current_index else theme['text']
            text_surface = self.font.render(option, True, text_color)
            text_rect = text_surface.get_rect(center=option_rect.center)
            surface.blit(text_surface, text_rect)
            
            if i > 0:
                pygame.draw.line(surface, theme['text'], 
                                (option_rect.x, option_rect.y + 5),
                                (option_rect.x, option_rect.y + self.rect.height - 5), 1)

class Slider:
    def __init__(self, x: float, y: float, width: float, height: float,
                 min_value: float, max_value: float, default_value: float,
                 on_change: Optional[Callable[[float], None]] = None):
        self.rect = pygame.Rect(x - width/2, y - height/2, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = default_value
        self.on_change = on_change
        self.dragging = False
        self.font = pygame.font.SysFont('Arial', 16)
    
    def update(self, dt: float):
        # Слайдер не требует обновления в каждом кадре, метод добавлен для совместимости
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.dragging = True
                self.update_value(mouse_pos[0])
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value(event.pos[0])
            return True
        
        return False
    
    def update_value(self, x_pos: float):
        rel_x = max(0, min(x_pos - self.rect.x, self.rect.width))
        new_value = self.min_value + (rel_x / self.rect.width) * (self.max_value - self.min_value)
        if new_value != self.value:
            self.value = new_value
            if self.on_change:
                self.on_change(self.value)
    
    def draw(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        
        # Фон слайдера
        pygame.draw.rect(surface, theme['panel'], self.rect, border_radius=3)
        
        # Заполненная часть
        fill_width = (self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(surface, theme['accent'], fill_rect, border_radius=3)
        
        # Ползунок
        slider_x = self.rect.x + fill_width
        pygame.draw.circle(surface, theme['accent'], (int(slider_x), int(self.rect.y + self.rect.height/2)), 8)
        
        # Текст значения
        value_text = self.font.render(f"{self.value:.1f}", True, theme['text'])
        surface.blit(value_text, (self.rect.x + self.rect.width + 10, self.rect.y))

# Класс частицы для анимаций
class Particle:
    def __init__(self, x: float, y: float, 
                 color: Tuple[int, int, int, int],
                 velocity: Tuple[float, float] = (0, 0),
                 lifetime: float = 1.0,
                 size: float = 5.0):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x, self.velocity_y = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alive = True
    
    def update(self, dt: float):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        self.velocity_x *= 0.95
        self.velocity_y *= 0.95
    
    def draw(self, surface: pygame.Surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        current_color = (
            self.color[0], 
            self.color[1], 
            self.color[2], 
            alpha
        )
        
        size = int(self.size * (self.lifetime / self.max_lifetime))
        if size < 1:
            size = 1
        
        particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, current_color, (size, size), size)
        surface.blit(particle_surface, (int(self.x - size), int(self.y - size)))

class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []
    
    def add_particle(self, particle: Particle):
        self.particles.append(particle)
    
    def burst(self, x: float, y: float, count: int = 10, 
              color: Tuple[int, int, int, int] = (255, 255, 255, 255),
              min_speed: float = 50.0, max_speed: float = 200.0,
              min_lifetime: float = 0.5, max_lifetime: float = 1.5,
              size: float = 5.0):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(min_speed, max_speed)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            lifetime = random.uniform(min_lifetime, max_lifetime)
            self.particles.append(Particle(x, y, color, velocity, lifetime, size))
    
    def update(self, dt: float):
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.alive:
                self.particles.remove(particle)
    
    def draw(self, surface: pygame.Surface):
        for particle in self.particles:
            particle.draw(surface)

# Класс кнопки
class Button:
    def __init__(self, x: float, y: float, width: float, height: float,
                 text: str, on_click: Callable[[], None],
                 font_size: int = 24, corner_radius: int = 10,
                 color: Optional[Tuple[int, int, int, int]] = None):
        self.rect = pygame.Rect(x - width/2, y - height/2, width, height)
        self.text = text
        self.on_click = on_click
        self.state = ButtonState.NORMAL
        self.corner_radius = corner_radius
        self.font = pygame.font.SysFont('Arial', font_size)
        self.scale = 1.0
        self.target_scale = 1.0
        self.custom_color = color
        self.particle_system = ParticleSystem()
    
    def update(self, dt: float):
        self.scale += (self.target_scale - self.scale) * 15 * dt
        self.particle_system.update(dt)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.state = ButtonState.HOVER
                self.target_scale = 1.05
                return True
            else:
                self.state = ButtonState.NORMAL
                self.target_scale = 1.0
                return False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.state = ButtonState.PRESSED
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos) and self.state == ButtonState.PRESSED:
                self.on_click()
                center = self.rect.center
                theme = THEMES[CURRENT_THEME]
                color = self.custom_color or theme['accent']
                self.particle_system.burst(
                    center[0], center[1], 15, 
                    (color[0], color[1], color[2], 150),
                    100, 300, 0.3, 0.8, 3
                )
                self.state = ButtonState.HOVER
                return True
            self.state = ButtonState.NORMAL
            self.target_scale = 1.0
        
        return False
    
    def draw(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        color = self.custom_color or theme['panel']
        
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        scaled_x = self.rect.centerx - scaled_width / 2
        scaled_y = self.rect.centery - scaled_height / 2
        
        button_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        
        if self.state == ButtonState.PRESSED:
            pygame.draw.rect(button_surface, color, 
                            (0, 0, scaled_width, scaled_height), 
                            border_radius=self.corner_radius)
            
            pygame.draw.rect(button_surface, (0, 0, 0, 50),
                            (2, 2, scaled_width-4, scaled_height-4),
                            border_radius=self.corner_radius-2)
        else:
            pygame.draw.rect(button_surface, (255, 255, 255, 50),
                            (0, 0, scaled_width, scaled_height),
                            border_radius=self.corner_radius)
            
            pygame.draw.rect(button_surface, (0, 0, 0, 50),
                            (2, 2, scaled_width-4, scaled_height-4),
                            border_radius=self.corner_radius-2)
            
            pygame.draw.rect(button_surface, color,
                            (4, 4, scaled_width-8, scaled_height-8),
                            border_radius=self.corner_radius-4)
        
        if self.state == ButtonState.HOVER:
            glow_surface = pygame.Surface((scaled_width + 20, scaled_height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*theme['accent'][:3], 30),
                            (0, 0, scaled_width + 20, scaled_height + 20),
                            border_radius=self.corner_radius + 10)
            surface.blit(glow_surface, (scaled_x - 10, scaled_y - 10))
        
        text_surface = self.font.render(self.text, True, theme['text'])
        text_rect = text_surface.get_rect(center=(scaled_width/2, scaled_height/2))
        button_surface.blit(text_surface, text_rect)
        
        surface.blit(button_surface, (scaled_x, scaled_y))
        self.particle_system.draw(surface)

class ProgressBar:
    def __init__(self, x: float, y: float, width: float, height: float,
                 max_value: float = 100.0, corner_radius: int = 5):
        self.rect = pygame.Rect(x - width/2, y - height/2, width, height)
        self.max_value = max_value
        self.current_value = 0.0
        self.target_value = 0.0
        self.corner_radius = corner_radius
        self.pulse_phase = 0.0
    
    def set_value(self, value: float):
        self.target_value = max(0, min(value, self.max_value))
    
    def update(self, dt: float):
        self.current_value += (self.target_value - self.current_value) * 5 * dt
        self.pulse_phase += dt * 2
        if self.pulse_phase > math.pi * 2:
            self.pulse_phase -= math.pi * 2
    
    def draw(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        
        pygame.draw.rect(surface, theme['bg_secondary'], 
                        self.rect, border_radius=self.corner_radius)
        
        if self.current_value > 0:
            fill_width = max(self.corner_radius * 2, 
                            (self.rect.width - self.corner_radius * 2) * 
                            (self.current_value / self.max_value))
            
            fill_rect = pygame.Rect(
                self.rect.x + self.corner_radius,
                self.rect.y + self.corner_radius,
                fill_width,
                self.rect.height - self.corner_radius * 2
            )
            
            fill_surface = pygame.Surface((fill_rect.width, fill_rect.height), pygame.SRCALPHA)
            for i in range(fill_rect.width):
                alpha = 200 + int(55 * math.sin(self.pulse_phase + i * 0.1))
                pygame.draw.rect(fill_surface, 
                                (*theme['accent'][:3], alpha),
                                (i, 0, 1, fill_rect.height))
            
            surface.blit(fill_surface, fill_rect.topleft)
        
        pygame.draw.rect(surface, theme['accent'], 
                        self.rect, 2, border_radius=self.corner_radius)

# Базовый класс представления
class View:
    def __init__(self):
        self.buttons: List[Button] = []
        self.toggle_buttons: List[ToggleButton] = []
        self.sliders: List[Slider] = []
        self.particle_system = ParticleSystem()
        self.alpha = 0
        self.target_alpha = 255
        self.transition_speed = 5.0
    
    def update(self, dt: float):
        self.alpha += (self.target_alpha - self.alpha) * self.transition_speed * dt
        
        for button in self.buttons:
            button.update(dt)
        
        # Слайдеры не требуют обновления в каждом кадре, поэтому пропускаем
        # for slider in self.sliders:
        #     slider.update(dt)
        
        self.particle_system.update(dt)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        for button in self.buttons:
            if button.handle_event(event):
                return True
        
        for toggle_button in self.toggle_buttons:
            if toggle_button.handle_event(event):
                return True
                
        for slider in self.sliders:
            if slider.handle_event(event):
                return True
                
        return False
    
    def draw(self, surface: pygame.Surface):
        if self.alpha < 255:
            temp_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            self._draw_content(temp_surface)
            temp_surface.set_alpha(int(self.alpha))
            surface.blit(temp_surface, (0, 0))
        else:
            self._draw_content(surface)
    
    def _draw_content(self, surface: pygame.Surface):
        for button in self.buttons:
            button.draw(surface)
        
        for toggle_button in self.toggle_buttons:
            toggle_button.draw(surface)
        
        for slider in self.sliders:
            slider.draw(surface)
        
        self.particle_system.draw(surface)
    
    def fade_in(self):
        self.alpha = 0
        self.target_alpha = 255
    
    def fade_out(self):
        self.target_alpha = 0

# Экран загрузки
class LoadingView(View):
    def __init__(self, on_loading_complete: Callable[[], None]):
        super().__init__()
        self.on_loading_complete = on_loading_complete
        self.loading_progress = 0.0
        self.loading_time = 0.0
        self.progress_bar = ProgressBar(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 50, 400, 20)
        
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 36)
        self.small_font = pygame.font.SysFont('Arial', 18)
    
    def update(self, dt: float):
        super().update(dt)
        
        self.loading_time += dt
        self.loading_progress = min(1.0, self.loading_time / 3.0)
        self.progress_bar.set_value(self.loading_progress * 100)
        self.progress_bar.update(dt)
        
        if self.loading_time >= 3.0:
            self.on_loading_complete()
    
    def _draw_content(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        center_x, center_y = WINDOW_WIDTH/2, WINDOW_HEIGHT/2
        
        # Анимированный фон
        time = pygame.time.get_ticks() / 1000
        for y in range(WINDOW_HEIGHT):
            hue_shift = math.sin(time * 0.5 + y * 0.01) * 0.1
            if CURRENT_THEME == 'dark':
                r = int(min(255, max(0, theme['bg_primary'][0] * (1 + hue_shift))))
                g = int(min(255, max(0, theme['bg_primary'][1] * (1 + hue_shift * 0.5))))
                b = int(min(255, max(0, theme['bg_primary'][2] + y * 0.1)))
            else:
                r = int(min(255, max(0, theme['bg_primary'][0] * (1 - hue_shift))))
                g = int(min(255, max(0, theme['bg_primary'][1] * (1 - hue_shift * 0.5))))
                b = int(min(255, max(0, theme['bg_primary'][2] - y * 0.1)))
            pygame.draw.line(surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))
        
        # Логотип компании
        logo_text = self.title_font.render(COMPANY_NAME, True, theme['accent'])
        logo_rect = logo_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 80))
        surface.blit(logo_text, logo_rect)
        
        # Версия игры
        version_text = self.small_font.render(f"Версия {VERSION}", True, theme['text'])
        version_rect = version_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 30))
        surface.blit(version_text, version_rect)
        
        # Панель загрузки
        panel_rect = pygame.Rect(WINDOW_WIDTH/2 - 200, WINDOW_HEIGHT/2, 400, 120)
        panel_surface = pygame.Surface((400, 120), pygame.SRCALPHA)
        
        pygame.draw.rect(panel_surface, theme['panel'], 
                        (0, 0, 400, 120), border_radius=15)
        
        for i in range(120):
            alpha = 30 - int(30 * i / 120)
            pygame.draw.rect(panel_surface, (255, 255, 255, alpha),
                            (10, 10 + i, 380, 1))
        
        surface.blit(panel_surface, panel_rect.topleft)
        
        # Текст загрузки
        loading_text = self.text_font.render("Загрузка...", True, theme['text'])
        loading_rect = loading_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 20))
        surface.blit(loading_text, loading_rect)
        
        # Прогресс-бар
        self.progress_bar.draw(surface)
        
        # Частицы
        self.particle_system.draw(surface)

# Главное меню
class MenuView(View):
    def __init__(self, on_play: Callable[[], None], on_settings: Callable[[], None]):
        super().__init__()
        self.on_play = on_play
        self.on_settings = on_settings
        
        button_y = WINDOW_HEIGHT / 2
        self.buttons = [
            Button(WINDOW_WIDTH/2, button_y, 300, 80, "Играть", on_play, 36),
            Button(WINDOW_WIDTH/2, button_y + 100, 300, 80, "Настройки", on_settings, 36),
            Button(WINDOW_WIDTH/2, button_y + 200, 300, 80, "Выход", sys.exit, 36)
        ]
        
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 16)
    
    def _draw_content(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        
        # Градиентный фон
        for y in range(WINDOW_HEIGHT):
            if CURRENT_THEME == 'dark':
                r = int(theme['bg_primary'][0] + (theme['bg_secondary'][0] - theme['bg_primary'][0]) * y / WINDOW_HEIGHT)
                g = int(theme['bg_primary'][1] + (theme['bg_secondary'][1] - theme['bg_primary'][1]) * y / WINDOW_HEIGHT)
                b = int(theme['bg_primary'][2] + (theme['bg_secondary'][2] - theme['bg_primary'][2]) * y / WINDOW_HEIGHT)
            else:
                r = int(theme['bg_primary'][0] + (theme['bg_secondary'][0] - theme['bg_primary'][0]) * y / WINDOW_HEIGHT)
                g = int(theme['bg_primary'][1] + (theme['bg_secondary'][1] - theme['bg_primary'][1]) * y / WINDOW_HEIGHT)
                b = int(theme['bg_primary'][2] + (theme['bg_secondary'][2] - theme['bg_primary'][2]) * y / WINDOW_HEIGHT)
            pygame.draw.line(surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))
        
        # Заголовок
        title_text = self.title_font.render("Black Empire", True, theme['accent'])
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH/2, 100))
        surface.blit(title_text, title_rect)
        
        # Кнопки
        for button in self.buttons:
            button.draw(surface)
        
        # Информация о компании
        company_text = self.small_font.render(f"{COMPANY_NAME} | Версия {VERSION}", True, theme['text'])
        surface.blit(company_text, (20, WINDOW_HEIGHT - 30))
        
        # Частицы
        self.particle_system.draw(surface)

# Настройки
class SettingsView(View):
    def __init__(self, on_back: Callable[[], None], game_window: Any):
        super().__init__()
        self.on_back = on_back
        self.game_window = game_window
        
        # Рассчитаем позиции для равномерного распределения
        start_y = 150
        spacing = 70
        
        self.buttons = [
            Button(100, 100, 120, 50, get_text('back'), on_back),
            Button(WINDOW_WIDTH/2, WINDOW_HEIGHT - 80, 200, 60, get_text('apply'), self.apply_settings)
        ]
        
        # Создаем переключатели с правильными позициями
        self.toggle_buttons = [
            ToggleButton(WINDOW_WIDTH/2, start_y, 300, 30, 
                        [get_text('dark'), get_text('light')], 
                        0 if CURRENT_THEME == 'dark' else 1, self.on_theme_change),
            
            ToggleButton(WINDOW_WIDTH/2, start_y + spacing, 400, 40, 
                        ['800x600', '1280x720', '1920x1080'],
                        list(WINDOW_SIZES.keys()).index(CURRENT_RESOLUTION), self.on_resolution_change),
            
            ToggleButton(WINDOW_WIDTH/2, start_y + spacing * 2, 300, 40, 
                        ['30 FPS', '60 FPS', '120 FPS'],
                        1 if FPS == 60 else (2 if FPS == 120 else 0), self.on_fps_change),
            
            ToggleButton(WINDOW_WIDTH/2, start_y + spacing * 3, 350, 40,
                        list(LANGUAGES.values()),
                        list(LANGUAGES.keys()).index(CURRENT_LANGUAGE), self.on_language_change)
        ]
        
        # Слайдеры располагаем после переключателей
        slider_start_y = start_y + spacing * 4 + 20
        self.sliders = [
            Slider(WINDOW_WIDTH/2, slider_start_y, 300, 20, 0.0, 1.0, 1.0, self.on_volume_change),
            Slider(WINDOW_WIDTH/2, slider_start_y + 50, 300, 20, 0.0, 1.0, 0.5, self.on_brightness_change)
        ]
        
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 22)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        self.new_theme = CURRENT_THEME
        self.new_resolution = CURRENT_RESOLUTION
        self.new_fps = FPS
        self.new_language = CURRENT_LANGUAGE
        self.volume = 1.0
        self.brightness = 0.5
    
    def on_theme_change(self, theme_name: str):
        # Простой и надежный способ определения темы
        if theme_name == get_text('light'):
            self.new_theme = 'light'
        elif theme_name == get_text('dark'):
            self.new_theme = 'dark'
        else:
            # Для других языков - используем прямое сравнение
            light_translations = {
                'English': 'Light',
                'Deutsch': 'Hell', 
                'Français': 'Clair',
                'Español': 'Claro'
            }
            dark_translations = {
                'English': 'Dark',
                'Deutsch': 'Dunkel',
                'Français': 'Sombre',
                'Español': 'Oscuro'
            }
            
            current_lang_name = LANGUAGES[self.new_language]
            
            if theme_name == light_translations.get(current_lang_name, 'Light'):
                self.new_theme = 'light'
            elif theme_name == dark_translations.get(current_lang_name, 'Dark'):
                self.new_theme = 'dark'
            else:
                self.new_theme = 'dark'  # fallback
        
        print(f"Theme changed: {theme_name} -> {self.new_theme}")
    
    def on_resolution_change(self, resolution: str):
        self.new_resolution = resolution
    
    def on_fps_change(self, fps_str: str):
        self.new_fps = int(fps_str.split()[0])
    
    def on_language_change(self, language_name: str):
        # Находим ключ языка по названию
        for key, name in LANGUAGES.items():
            if name == language_name:
                self.new_language = key
                break
    
    def on_volume_change(self, volume: float):
        self.volume = volume
    
    def on_brightness_change(self, brightness: float):
        self.brightness = brightness
    
    def apply_settings(self):
        global CURRENT_THEME, WINDOW_WIDTH, WINDOW_HEIGHT, FPS, CURRENT_RESOLUTION, CURRENT_LANGUAGE
        
        CURRENT_THEME = self.new_theme
        CURRENT_RESOLUTION = self.new_resolution
        CURRENT_LANGUAGE = self.new_language
        WINDOW_WIDTH, WINDOW_HEIGHT = WINDOW_SIZES[self.new_resolution]
        FPS = self.new_fps
        
        self.game_window.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Black Empire")
        
        # Пересоздаем view с новыми настройками
        self.on_back()
    
    def _draw_content(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        
        # Фон
        surface.fill(theme['bg_primary'])
        
        # Заголовок
        title_text = self.title_font.render(get_text('settings'), True, theme['accent'])
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH/2, 80))
        surface.blit(title_text, title_rect)
        
        # Информация о компании
        company_text = self.small_font.render(get_text('company_info'), True, theme['text'])
        surface.blit(company_text, (20, WINDOW_HEIGHT - 30))
        
        # Рисуем панель настроек с фоном
        panel_rect = pygame.Rect(WINDOW_WIDTH/2 - 300, 120, 600, 500)
        panel_surface = pygame.Surface((600, 500), pygame.SRCALPHA)
        
        # Стеклянный эффект для панели
        pygame.draw.rect(panel_surface, theme['panel'], (0, 0, 600, 500), border_radius=15)
        
        # Внутренний градиент
        for i in range(500):
            alpha = 20 - int(20 * i / 500)
            pygame.draw.rect(panel_surface, (255, 255, 255, alpha), (10, 10 + i, 580, 1))
        
        surface.blit(panel_surface, panel_rect.topleft)
        
        # Надписи настроек с иконками (простыми символами)
        settings_labels = [
            (get_text('theme'), 150),
            (get_text('resolution'), 220),
            (get_text('fps'), 290),
            (get_text('language'), 360),
            (get_text('volume'), 450),
            (get_text('brightness'), 500)
        ]
        
        for text, y in settings_labels:
            label_text = self.text_font.render(text, True, theme['text'])
            surface.blit(label_text, (WINDOW_WIDTH/2 - 280, y))
        
        # Текущие значения для слайдеров
        volume_text = self.text_font.render(f"{int(self.volume * 100)}%", True, theme['accent'])
        surface.blit(volume_text, (WINDOW_WIDTH/2 + 220, 445))
        
        brightness_text = self.text_font.render(f"{int(self.brightness * 100)}%", True, theme['accent'])
        surface.blit(brightness_text, (WINDOW_WIDTH/2 + 220, 495))
        
        # Разделительные линии между настройками
        for y in [185, 255, 325, 395]:
            pygame.draw.line(surface, (theme['text'][0], theme['text'][1], theme['text'][2], 50),
                           (WINDOW_WIDTH/2 - 280, y), (WINDOW_WIDTH/2 + 280, y), 1)
        
        # Элементы управления
        for button in self.buttons:
            button.draw(surface)
        
        for toggle_button in self.toggle_buttons:
            toggle_button.draw(surface)
        
        for slider in self.sliders:
            slider.draw(surface)
        
        # Дополнительная информация
        info_text = self.small_font.render(
            f"{get_text('theme')}: {get_text('light' if self.new_theme == 'light' else 'dark')} | "
            f"{get_text('resolution')}: {self.new_resolution} | "
            f"{get_text('fps')}: {self.new_fps} | "
            f"{get_text('language')}: {LANGUAGES[self.new_language]}",
            True, theme['text']
        )
        surface.blit(info_text, (WINDOW_WIDTH - 1700, WINDOW_HEIGHT - 30))
        
        self.particle_system.draw(surface)

# Карточка для отображения элементов
class Card:
    def __init__(self, x: float, y: float, width: float, height: float,
                 title: str = "", value: str = "", on_click: Optional[Callable[[], None]] = None,
                 color: Optional[Tuple[int, int, int, int]] = None):
        self.rect = pygame.Rect(x - width/2, y - height/2, width, height)
        self.title = title
        self.value = value
        self.on_click = on_click
        self.color = color
        self.title_font = pygame.font.SysFont('Arial', 20, bold=True)
        self.value_font = pygame.font.SysFont('Arial', 18)
        self.state = ButtonState.NORMAL
        self.scale = 1.0
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.state = ButtonState.HOVER
                self.scale = 1.05
                return True
            else:
                self.state = ButtonState.NORMAL
                self.scale = 1.0
                return False
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos) and self.on_click:
                self.on_click()
                return True
        
        return False
    
    def draw(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        color = self.color or theme['card']
        
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        scaled_x = self.rect.centerx - scaled_width / 2
        scaled_y = self.rect.centery - scaled_height / 2
        
        card_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
        
        # Стеклянный эффект
        pygame.draw.rect(card_surface, color, 
                        (0, 0, scaled_width, scaled_height), 
                        border_radius=10)
        
        # Эффект при наведении
        if self.state == ButtonState.HOVER:
            pygame.draw.rect(card_surface, (255, 255, 255, 30),
                            (2, 2, scaled_width-4, scaled_height-4),
                            border_radius=8)
        
        # Текст
        if self.title:
            title_text = self.title_font.render(self.title, True, theme['text'])
            card_surface.blit(title_text, (10, 10))
        
        if self.value:
            value_text = self.value_font.render(self.value, True, theme['text'])
            card_surface.blit(value_text, (10, 40))
        
        surface.blit(card_surface, (scaled_x, scaled_y))

# Основной игровой экран
class MainGameView(View):
    def __init__(self, on_back: Callable[[], None], show_detail_view: Callable[[View], None]):
        super().__init__()
        self.on_back = on_back
        self.show_detail_view = show_detail_view
        self.current_subview = "Кликер"
        self.export = export_db()
        self.updated = update_db()
        self.money = self.export.balance()
        self.click = self.export.earn_one_click()
        self.click_level = self.export.show_earn_click_level()
        self.taxes = self.export.taxes()
        
        # Нижняя панель вкладок
        tab_width = WINDOW_WIDTH / 6
        self.tab_buttons = [
            Button(tab_width * 0.5, 30, tab_width - 10, 50, "Кликер", lambda: self.set_subview("Кликер")),
            Button(tab_width * 1.5, 30, tab_width - 10, 50, "Инвестиции", lambda: self.set_subview("Инвестиции")),
            Button(tab_width * 2.5, 30, tab_width - 10, 50, "Бизнес", lambda: self.set_subview("Бизнес")),
            Button(tab_width * 3.5, 30, tab_width - 10, 50, "Предметы", lambda: self.set_subview("Предметы")),
            Button(tab_width * 4.5, 30, tab_width - 10, 50, "Профиль", lambda: self.set_subview("Профиль")),
            Button(tab_width * 5.5, 30, tab_width - 10, 50, "Магазины", lambda: self.set_subview("Магазины"))
        ]
        
        # Кнопка меню
        self.buttons = [Button(WINDOW_WIDTH - 80, WINDOW_HEIGHT - 40, 120, 50, "Меню", on_back)]
        
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 24)
        self.money_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 18)
        self.big_font = pygame.font.SysFont('Arial', 42, bold=True)
        
        self.displayed_money = self.money
        self.money_change_animation = 0.0
        
        self.create_cards()
        self.create_business_cards()
    
    def create_cards(self):
        theme = THEMES[CURRENT_THEME]
        
        self.cards = {
            "Инвестиции": [
                Card(WINDOW_WIDTH/2 - 200, 250, 300, 100, "Акции", "+$500/час", 
                     lambda: self.show_investment_detail("Акции"), theme['card_light']),
                Card(WINDOW_WIDTH/2 + 200, 250, 300, 100, "Недвижимость", "+$300/час",
                     lambda: self.show_investment_detail("Недвижимость"), theme['card']),
                Card(WINDOW_WIDTH/2 - 200, 400, 300, 100, "Криптовалюта", "+$200/час",
                     lambda: self.show_investment_detail("Криптовалюта"), theme['card_dark']),
                Card(WINDOW_WIDTH/2 + 200, 400, 300, 100, "Облигации", "+$150/час",
                     lambda: self.show_investment_detail("Облигации"), theme['card_light'])
            ],
            "Бизнес": [
                Card(WINDOW_WIDTH/2 - 300, 350, 250, 100, "Ресторан", "Уровень 2",
                     lambda: self.show_business_detail("Ресторан"), theme['card_light']),
                Card(WINDOW_WIDTH/2, 350, 250, 100, "Магазин", "Уровень 1",
                     lambda: self.show_business_detail("Магазин"), theme['card']),
                Card(WINDOW_WIDTH/2 + 300, 350, 250, 100, "Фабрика", "Уровень 3",
                     lambda: self.show_business_detail("Фабрика"), theme['card_dark'])
            ],
            "Предметы": [
                Card(WINDOW_WIDTH/4, 250, 250, 80, "Автомобили", "5 шт.",
                     lambda: self.show_items_category("Автомобили"), theme['card']),
                Card(WINDOW_WIDTH/2, 250, 250, 80, "Недвижимость", "3 шт.",
                     lambda: self.show_items_category("Недвижимость"), theme['card_light']),
                Card(3*WINDOW_WIDTH/4, 250, 250, 80, "Яхты", "2 шт.",
                     lambda: self.show_items_category("Яхты"), theme['card_dark'])
            ],
            "Магазины": [
                Card(WINDOW_WIDTH/3, 250, 280, 100, "Белый рынок", "Легальные товары",
                     lambda: self.show_shop("Белый рынок"), theme['card_light']),
                Card(2*WINDOW_WIDTH/3, 250, 280, 100, "Чёрный рынок", "Эксклюзивные и запрещённые товары",
                     lambda: self.show_shop("Чёрный рынок"), theme['card_dark'])
            ]
        }
        
        # Кнопки для бизнеса - располагаем их выше карточек
        self.business_buttons = [
            Button(WINDOW_WIDTH/2 - 350, 200, 200, 60, "Открыть бизнес", self.open_business),
            Button(WINDOW_WIDTH/2 - 100, 200, 200, 60, "Слияние", self.merge_businesses),
            Button(WINDOW_WIDTH/2 + 150, 200, 200, 60, "Слоты", self.buy_slots)
        ]
    
    def create_business_cards(self):
        theme = THEMES[CURRENT_THEME]
        # Карточки категорий бизнеса - располагаем их под кнопками
        self.business_category_cards = [
            Card(WINDOW_WIDTH/2 - 200, 500, 300, 100, "Светлый бизнес", "Легальные предприятия",
                 lambda: self.show_business_category("Светлый"), theme['card_light']),
            Card(WINDOW_WIDTH/2 + 200, 500, 300, 100, "Тёмный бизнес", "Специальные операции",
                 lambda: self.show_business_category("Тёмный"), theme['card_dark'])
        ]
    
    def show_investment_detail(self, investment_type: str):
        detail_view = InvestmentDetailView(investment_type, lambda: self.show_detail_view(self))
        self.show_detail_view(detail_view)
    
    def show_business_detail(self, business_name: str):
        detail_view = BusinessDetailView(business_name, lambda: self.show_detail_view(self))
        self.show_detail_view(detail_view)
    
    def show_items_category(self, category: str):
        detail_view = ItemsCategoryView(category, lambda: self.show_detail_view(self))
        self.show_detail_view(detail_view)
    
    def show_shop(self, shop_name: str):
        detail_view = ShopView(shop_name, lambda: self.show_detail_view(self))
        self.show_detail_view(detail_view)
    
    def open_business(self):
        print("Открыть окно создания бизнеса")
        # TODO: Реализовать окно создания бизнеса
    
    def merge_businesses(self):
        print("Открыть окно слияния бизнесов")
        # TODO: Реализовать окно слияния бизнесов
    
    def buy_slots(self):
        print("Открыть окно покупки слотов")
        # TODO: Реализовать окно покупки слотов
    
    def show_business_category(self, category: str):
        detail_view = BusinessCategoryView(category, lambda: self.show_detail_view(self))
        self.show_detail_view(detail_view)
    
    def set_subview(self, subview: str):
        self.current_subview = subview
    
    def update(self, dt: float):
        super().update(dt)
        
        self.displayed_money += (self.money - self.displayed_money) * 5 * dt
        self.money_change_animation = max(0, self.money_change_animation - dt)
        
        for button in self.tab_buttons:
            button.update(dt)
        
        for button in self.business_buttons:
            button.update(dt)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if super().handle_event(event):
            return True
        
        for button in self.tab_buttons:
            if button.handle_event(event):
                return True
        
        for button in self.business_buttons:
            if button.handle_event(event):
                return True
        
        # Обработка карточек
        if self.current_subview in self.cards:
            for card in self.cards[self.current_subview]:
                if card.handle_event(event):
                    return True
        
        if self.current_subview == "Бизнес":
            for card in self.business_category_cards:
                if card.handle_event(event):
                    return True
        
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            if self.current_subview == "Кликер":
                click_area = pygame.Rect(200, 100, WINDOW_WIDTH - 400, 400)
                if click_area.collidepoint(mouse_pos):
                    self.updated.earn_click()
                    self.money = self.export.balance()
                    self.money_change_animation = 1.0
                    
                    self.particle_system.burst(
                        mouse_pos[0], mouse_pos[1], 10, 
                        (0, 255, 0, 150), 100, 300, 0.5, 1.0, 3
                    )
                    return True
        
        return False
    
    def _draw_content(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        
        # Анимированный градиент фона
        time = pygame.time.get_ticks() / 1000
        for y in range(WINDOW_HEIGHT):
            hue_shift = math.sin(time * 0.1 + y * 0.005) * 0.1
            if CURRENT_THEME == 'dark':
                r = int(min(255, max(0, theme['bg_primary'][0] * (1 + hue_shift))))
                g = int(min(255, max(0, theme['bg_primary'][1] * (1 + hue_shift * 0.5))))
                b = int(min(255, max(0, theme['bg_primary'][2] + y * 0.1)))
            else:
                r = int(min(255, max(0, theme['bg_primary'][0] * (1 - hue_shift))))
                g = int(min(255, max(0, theme['bg_primary'][1] * (1 - hue_shift * 0.5))))
                b = int(min(255, max(0, theme['bg_primary'][2] - y * 0.1)))
            pygame.draw.line(surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))
        
        # Верхняя панель с балансом
        balance_rect = pygame.Rect(0, WINDOW_HEIGHT - 60, WINDOW_WIDTH, 60)
        balance_surface = pygame.Surface((WINDOW_WIDTH, 60), pygame.SRCALPHA)
        
        pygame.draw.rect(balance_surface, theme['panel'], (0, 0, WINDOW_WIDTH, 60))
        
        for i in range(60):
            alpha = 30 - int(30 * i / 60)
            pygame.draw.rect(balance_surface, (255, 255, 255, alpha), (0, i, WINDOW_WIDTH, 1))
        
        surface.blit(balance_surface, balance_rect.topleft)
        
        # Текст баланса
        money_color = theme['text']
        if self.money_change_animation > 0:
            money_color = (
                int(theme['text'][0] * (1 - self.money_change_animation) + 0 * self.money_change_animation),
                int(theme['text'][1] * (1 - self.money_change_animation) + 255 * self.money_change_animation),
                int(theme['text'][2] * (1 - self.money_change_animation) + 0 * self.money_change_animation)
            )
        
        money_text = self.money_font.render(f"Баланс: ${int(self.displayed_money):,}", True, money_color)
        money_rect = money_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT - 30))
        surface.blit(money_text, money_rect)
        
        # Рисуем текущее под-представление
        self._draw_subview(surface)
        
        # Нижняя панель вкладок
        tab_bar_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 60)
        tab_bar_surface = pygame.Surface((WINDOW_WIDTH, 60), pygame.SRCALPHA)
        
        pygame.draw.rect(tab_bar_surface, theme['panel'], (0, 0, WINDOW_WIDTH, 60))
        
        for i in range(60):
            alpha = 30 - int(30 * i / 60)
            pygame.draw.rect(tab_bar_surface, (255, 255, 255, alpha), (0, 59 - i, WINDOW_WIDTH, 1))
        
        surface.blit(tab_bar_surface, tab_bar_rect.topleft)
        
        # Кнопки вкладок
        for button in self.tab_buttons:
            button.draw(surface)
        
        # Кнопка меню
        for button in self.buttons:
            button.draw(surface)
        
        # Информация о компании
        company_text = self.small_font.render(f"{COMPANY_NAME} | Версия {VERSION}", True, theme['text'])
        surface.blit(company_text, (20, WINDOW_HEIGHT - 30))
        
        self.particle_system.draw(surface)
    
    def _draw_subview(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        
        title_text = self.title_font.render(self.current_subview, True, theme['accent'])
        surface.blit(title_text, (50, WINDOW_HEIGHT - 120))
        
        if self.current_subview == "Кликер":
            self._draw_clicker_view(surface)
        elif self.current_subview == "Инвестиции":
            self._draw_investments_view(surface)
        elif self.current_subview == "Бизнес":
            self._draw_business_view(surface)
        elif self.current_subview == "Предметы":
            self._draw_items_view(surface)
        elif self.current_subview == "Профиль":
            self._draw_profile_view(surface)
        elif self.current_subview == "Магазины":
            self._draw_shops_view(surface)
    
    def _draw_clicker_view(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        
        click_area = pygame.Rect(200, 100, WINDOW_WIDTH - 400, 400)
        click_surface = pygame.Surface((click_area.width, click_area.height), pygame.SRCALPHA)
        
        pygame.draw.rect(click_surface, theme['panel'], 
                        (0, 0, click_area.width, click_area.height), 
                        border_radius=15)
        
        pygame.draw.rect(click_surface, (255, 255, 255, 30),
                        (0, 0, click_area.width, click_area.height),
                        border_radius=15)
        pygame.draw.rect(click_surface, (0, 0, 0, 30),
                        (4, 4, click_area.width - 8, click_area.height - 8),
                        border_radius=11)
        
        surface.blit(click_surface, click_area.topleft)
        
        click_text = self.text_font.render("Кликай чтобы зарабатывать!", True, theme['text'])
        click_text_rect = click_text.get_rect(center=click_area.center)
        surface.blit(click_text, click_text_rect)
        
        card_rect = pygame.Rect(WINDOW_WIDTH/2 - 200, 520, 400, 150)
        card_surface = pygame.Surface((400, 150), pygame.SRCALPHA)
        
        for i in range(150):
            alpha = 200 - int(100 * i / 150)
            color = (
                theme['accent'][0],
                theme['accent'][1],
                theme['accent'][2],
                alpha
            )
            pygame.draw.rect(card_surface, color, (0, i, 400, 1))
        
        level_text = self.text_font.render(f"Уровень {self.click_level}/15", True, theme['text'])
        card_surface.blit(level_text, (20, 20))
        
        income_text = self.text_font.render(f"${self.click} за клик", True, theme['text'])
        card_surface.blit(income_text, (20, 50))
        
        surface.blit(card_surface, card_rect.topleft)
        
        progress_bar = ProgressBar(WINDOW_WIDTH/2, 500, 360, 15)
        progress_bar.set_value(75)
        progress_bar.update(0.016)
        progress_bar.draw(surface)
    
    def _draw_investments_view(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        
        # Большой жирный текст дохода
        income_text = self.big_font.render("Доход от инвестиций: $1150/час", True, theme['accent'])
        surface.blit(income_text, (WINDOW_WIDTH/2 - 300, 120))
        
        for card in self.cards["Инвестиции"]:
            card.draw(surface)
    
    def _draw_business_view(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        
        # Большой жирный текст дохода
        income_text = self.big_font.render("Доход от бизнеса: $800/час", True, theme['accent'])
        surface.blit(income_text, (WINDOW_WIDTH/2 - 250, 120))
        
        for card in self.cards["Бизнес"]:
            card.draw(surface)
        
        for button in self.business_buttons:
            button.draw(surface)
        
        for card in self.business_category_cards:
            card.draw(surface)
    
    def _draw_items_view(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        
        # Большой жирный текст дохода
        income_text = self.big_font.render("Общая стоимость имущества: $2,500,000", True, theme['accent'])
        surface.blit(income_text, (WINDOW_WIDTH/2 - 250, 120))

        for card in self.cards["Предметы"]:
            card.draw(surface)
    
    def _draw_profile_view(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        
        # Статистика игрока
        stats = [
            f"Общий баланс: ${self.money:,}",
            f"Уровень: {self.click_level}",
            f"Опыт: 1250/2000",
            f"Игровое время: 25 часов",
            f"Всего кликов: 12,500",
            f"Налоги: ${self.taxes}/мес",
            f"Рейтинг Forbes: #156",
            f"Транспорт: Lamborghini Aventador"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.text_font.render(stat, True, theme['text'])
            surface.blit(stat_text, (WINDOW_WIDTH/2 - 200, 150 + i * 40))
        
        daily_button = Button(WINDOW_WIDTH/2, 500, 250, 60, "Получить награду", lambda: None)
        daily_button.draw(surface)
    
    def _draw_shops_view(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        
        # Большой жирный текст
        shop_text = self.big_font.render("Торговые площадки", True, theme['accent'])
        surface.blit(shop_text, (WINDOW_WIDTH/2 - 200, 120))
        
        for card in self.cards["Магазины"]:
            card.draw(surface)
        
        desc_text = self.text_font.render("Выберите торговую площадку для покупки товаров", True, theme['text'])
        surface.blit(desc_text, (WINDOW_WIDTH/2 - 250, 350))

# Новые классы для окон деталей
class InvestmentDetailView(View):
    def __init__(self, investment_type: str, on_back: Callable[[], None]):
        super().__init__()
        self.investment_type = investment_type
        self.on_back = on_back
        
        self.buttons = [Button(100, 100, 120, 50, "Назад", on_back)]
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 24)
    
    def _draw_content(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        surface.fill(theme['bg_primary'])
        
        title_text = self.title_font.render(f"Инвестиции: {self.investment_type}", True, theme['accent'])
        surface.blit(title_text, (WINDOW_WIDTH/2 - 200, 100))
        
        info_text = self.text_font.render("Детальная информация о инвестициях...", True, theme['text'])
        surface.blit(info_text, (WINDOW_WIDTH/2 - 250, 200))
        
        for button in self.buttons:
            button.draw(surface)

class BusinessDetailView(View):
    def __init__(self, business_name: str, on_back: Callable[[], None]):
        super().__init__()
        self.business_name = business_name
        self.on_back = on_back
        
        self.buttons = [Button(100, 100, 120, 50, "Назад", on_back)]
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 24)
    
    def _draw_content(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        surface.fill(theme['bg_primary'])
        
        title_text = self.title_font.render(f"Бизнес: {self.business_name}", True, theme['accent'])
        surface.blit(title_text, (WINDOW_WIDTH/2 - 200, 100))
        
        info_text = self.text_font.render("Детальная информация о бизнесе...", True, theme['text'])
        surface.blit(info_text, (WINDOW_WIDTH/2 - 250, 200))
        
        for button in self.buttons:
            button.draw(surface)

class BusinessCategoryView(View):
    def __init__(self, category: str, on_back: Callable[[], None]):
        super().__init__()
        self.category = category
        self.on_back = on_back
        
        self.buttons = [Button(100, 100, 120, 50, "Назад", on_back)]
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 24)
    
    def _draw_content(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        surface.fill(theme['bg_primary'])
        
        title_text = self.title_font.render(f"Категория: {self.category}", True, theme['accent'])
        surface.blit(title_text, (WINDOW_WIDTH/2 - 200, 100))
        
        info_text = self.text_font.render("Список бизнесов в этой категории...", True, theme['text'])
        surface.blit(info_text, (WINDOW_WIDTH/2 - 250, 200))
        
        for button in self.buttons:
            button.draw(surface)

class ItemsCategoryView(View):
    def __init__(self, category: str, on_back: Callable[[], None]):
        super().__init__()
        self.category = category
        self.on_back = on_back
        
        self.buttons = [Button(100, 100, 120, 50, "Назад", on_back)]
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 24)
    
    def _draw_content(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        surface.fill(theme['bg_primary'])
        
        title_text = self.title_font.render(f"Предметы: {self.category}", True, theme['accent'])
        surface.blit(title_text, (WINDOW_WIDTH/2 - 200, 100))
        
        info_text = self.text_font.render("Список предметов в этой категории...", True, theme['text'])
        surface.blit(info_text, (WINDOW_WIDTH/2 - 250, 200))
        
        for button in self.buttons:
            button.draw(surface)

class ShopView(View):
    def __init__(self, shop_name: str, on_back: Callable[[], None]):
        super().__init__()
        self.shop_name = shop_name
        self.on_back = on_back
        
        self.buttons = [Button(100, 100, 120, 50, "Назад", on_back)]
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 24)
    
    def _draw_content(self, surface: pygame.Surface):
        theme = THEMES[CURRENT_THEME]
        surface.fill(theme['bg_primary'])
        
        title_text = self.title_font.render(f"Магазин: {self.shop_name}", True, theme['accent'])
        surface.blit(title_text, (WINDOW_WIDTH/2 - 200, 100))
        
        info_text = self.text_font.render("Товары в магазине...", True, theme['text'])
        surface.blit(info_text, (WINDOW_WIDTH/2 - 250, 200))
        
        for button in self.buttons:
            button.draw(surface)

# Главное окно игры
class GameWindow:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Black Empire")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.view_stack = []  # Стек для навигации между видами
        self.current_view = LoadingView(self.on_loading_complete)
        self.current_view.fade_in()
        
        self.last_time = pygame.time.get_ticks()
    
    def show_view(self, view: View):
        if self.current_view:
            self.view_stack.append(self.current_view)
        self.current_view = view
        self.current_view.fade_in()
    
    def show_detail_view(self, detail_view: View):
        self.show_view(detail_view)
    
    def go_back(self):
        if self.view_stack:
            self.current_view = self.view_stack.pop()
            self.current_view.fade_in()
    
    def on_loading_complete(self):
        self.show_view(MenuView(self.on_play, self.on_settings))
    
    def on_play(self):
        main_game_view = MainGameView(self.on_back_to_menu, self.show_detail_view)
        self.show_view(main_game_view)
    
    def on_settings(self):
        settings_view = SettingsView(self.on_back_to_menu, self)
        self.show_view(settings_view)
    
    def on_back_to_menu(self):
        self.view_stack = []  # Очищаем стек при возврате в меню
        self.show_view(MenuView(self.on_play, self.on_settings))
    
    def run(self):
        while self.running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_time) / 1000.0
            self.last_time = current_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.go_back()
                
                if self.current_view:
                    self.current_view.handle_event(event)
            
            if self.current_view:
                self.current_view.update(dt)
            
            self.screen.fill(THEMES[CURRENT_THEME]['bg_primary'])
            
            if self.current_view:
                self.current_view.draw(self.screen)
            
            pygame.display.flip()
            
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = GameWindow()
    game.run()