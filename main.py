import pygame
import sys
import math
import random
import time
from pygame import gfxdraw
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum

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
PANEL_BORDER_RADIUS = 35  # Увеличено закругление панелей
BUTTON_BORDER_RADIUS = 25  # Увеличено закругление кнопок
BAR_BORDER_RADIUS = 12    # Увеличено закругление графиков

class ScreenState(Enum):
    LOADING = 0
    MENU = 1

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
    alpha: int
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
            'loading': ('segoeui.ttf', 32, True)
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

class Button:
    """Интерактивная кнопка с увеличенным закруглением."""
    
    def __init__(self, rect, text, icon_renderer=None, action=None):
        self.rect = rect
        self.text = text
        self.icon_renderer = icon_renderer
        self.action = action
        self.hovered = False
        self.cache = {}
        self.click_animation = 0
    
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
            self.icon_renderer(surface, icon_x, icon_y)
        
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

class BarGraphRenderer:
    """Рендерер графика с увеличенным закруглением."""
    
    def __init__(self):
        self.bar_cache = {}
    
    def draw_bar_graph(self, surface, x, y, bar_width, heights, bar_count=5):
        """Рисует столбчатую диаграмму."""
        spacing = 50
        max_height = max(heights) if heights else 1
        
        for i in range(bar_count):
            bar_x = x + i * spacing
            bar_height = heights[i] if i < len(heights) else 0
            scaled_height = int(bar_height * 200 / max_height)
            
            cache_key = (bar_width, scaled_height)
            if cache_key not in self.bar_cache:
                # Создаем закругленный столбец
                bar_surf = pygame.Surface((bar_width, scaled_height), pygame.SRCALPHA)
                
                gradient_colors = [
                    (BAR_HIGHLIGHT[0], BAR_HIGHLIGHT[1], BAR_HIGHLIGHT[2], 255),
                    (BAR_BASE[0], BAR_BASE[1], BAR_BASE[2], 255),
                    (DEEP_PURPLE[0], DEEP_PURPLE[1], DEEP_PURPLE[2], 255)
                ]
                
                # Рисуем закругленный прямоугольник
                pygame.draw.rect(bar_surf, (0, 0, 0, 0), (0, 0, bar_width, scaled_height))
                pygame.draw.rect(bar_surf, gradient_colors[0], (0, 0, bar_width, scaled_height), 
                               border_radius=BAR_BORDER_RADIUS)
                
                # Градиент
                for j in range(scaled_height):
                    pos = j / scaled_height
                    r = int(gradient_colors[0][0] + (gradient_colors[1][0] - gradient_colors[0][0]) * pos)
                    g = int(gradient_colors[0][1] + (gradient_colors[1][1] - gradient_colors[0][1]) * pos)
                    b = int(gradient_colors[0][2] + (gradient_colors[1][2] - gradient_colors[0][2]) * pos)
                    pygame.draw.line(bar_surf, (r, g, b, 255), (0, j), (bar_width, j))
                
                # Бордюр
                pygame.draw.rect(bar_surf, PURPLE_ACCENT, (0, 0, bar_width, scaled_height), 
                               1, border_radius=BAR_BORDER_RADIUS)
                
                self.bar_cache[cache_key] = bar_surf
            
            surface.blit(self.bar_cache[cache_key], (bar_x, y - scaled_height))

class Game:
    """Основной класс игры."""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Black Empire')
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = ScreenState.LOADING
        
        self.font_manager = FontManager()
        self.icon_renderer = IconRenderer()
        self.bar_renderer = BarGraphRenderer()
        self.loading_screen = LoadingScreen(self.screen, self.font_manager)
        
        self.stars = []
        self.background_cache = None
        self.panel_cache = {}
        self.last_time = time.time()
        
        self.initialize_ui()
    
    def create_stars(self):
        """Создает анимированные звезды."""
        stars = []
        for _ in range(300):
            stars.append(Star(
                x=random.uniform(0, SCREEN_WIDTH),
                y=random.uniform(0, SCREEN_HEIGHT),
                z=random.uniform(0, 1),
                size=random.uniform(0.5, 3.0),
                speed=random.uniform(10, 100),
                pulse_speed=random.uniform(0.01, 0.05),
                pulse_offset=random.uniform(0, 2 * math.pi),
                alpha=random.randint(100, 255),
                alpha_change=random.choice([-1, 1]) * random.uniform(0.5, 2)
            ))
        return stars
    
    def play_game(self):
        print("Запуск игры...")
    
    def open_settings(self):
        print("Открытие настроек...")
    
    def exit_game(self):
        self.running = False
    
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
        
        # Увеличено закругление панелей
        self.left_panel_rect = pygame.Rect(80, 120, 580, 680)
        self.right_panel_rect = pygame.Rect(740, 120, 580, 680)
        
        button_width, button_height = 460, 65
        button_y_start = self.right_panel_rect.y + 200
        
        self.buttons = [
            Button(
                pygame.Rect(self.right_panel_rect.x + 60, button_y_start, button_width, button_height),
                "Играть", 
                lambda s, x, y: self.icon_renderer.draw_play_icon(s, x, y), 
                self.play_game
            ),
            Button(
                pygame.Rect(self.right_panel_rect.x + 60, button_y_start + 100, button_width, button_height),
                "Настройки", 
                lambda s, x, y: self.icon_renderer.draw_settings_icon(s, x, y), 
                self.open_settings
            ),
            Button(
                pygame.Rect(self.right_panel_rect.x + 60, button_y_start + 200, button_width, button_height),
                "Выход", 
                lambda s, x, y: self.icon_renderer.draw_exit_icon(s, x, y), 
                self.exit_game
            )
        ]
        
        self.bar_heights = [70, 130, 100, 160, 85]
    
    def load_resources(self):
        """Загрузка ресурсов."""
        self.stars = self.create_stars()
        self.create_background()
        self.create_panel_surfaces()
        return True
    
    def create_background(self):
        """Создает градиентный фон."""
        self.background_cache = GradientGenerator.create_vertical_gradient(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            [
                (5, 5, 40, 255), (15, 5, 50, 255), (25, 5, 60, 255),
                (40, 10, 80, 255), (25, 5, 60, 255), (15, 5, 50, 255), (5, 5, 40, 255)
            ]
        )
    
    def create_panel_surfaces(self):
        """Создает поверхности панелей с увеличенным закруглением."""
        for rect, name in [(self.left_panel_rect, "left"), (self.right_panel_rect, "right")]:
            # Создаем закругленную панель с градиентом
            panel_colors = [(160, 60, 255, 40), (160, 60, 255, 15), (160, 60, 255, 5), (0, 0, 0, 0)]
            surf = GradientGenerator.create_rounded_rect((rect.width, rect.height), panel_colors, PANEL_BORDER_RADIUS)
            
            # Добавляем блики
            for _ in range(rect.width * rect.height // 1000):
                x = random.randint(10, rect.width-10)
                y = random.randint(10, rect.height-10)
                size = random.randint(1, 2)
                alpha = random.randint(5, 15)
                pygame.draw.circle(surf, (255, 255, 255, alpha), (x, y), size)
            
            # Мягкая обводка
            pygame.draw.rect(surf, (255, 255, 255, 30), (0, 0, rect.width, rect.height), 
                           2, border_radius=PANEL_BORDER_RADIUS)
            
            self.panel_cache[name] = surf
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    for button in self.buttons:
                        if button.is_hovered(mouse_pos):
                            button.click()
            elif event.type == pygame.MOUSEMOTION:
                for button in self.buttons:
                    button.hovered = button.is_hovered(mouse_pos)
    
    def draw_stars(self, dt):
        """Отрисовывает анимированные звезды."""
        for star in self.stars:
            star.update(dt)
            x, y = star.get_screen_pos()
            size = star.get_current_size()
            color = (255, 255, 255, star.alpha)
            
            # Рисуем звезду с свечением
            pygame.draw.circle(self.screen, color, (int(x), int(y)), int(size))
            if size > 1.5:
                pygame.draw.circle(self.screen, (255, 255, 255, star.alpha//2), (int(x), int(y)), int(size*1.5), 1)
    
    def draw_panel(self, rect, name):
        if name in self.panel_cache:
            self.screen.blit(self.panel_cache[name], rect.topleft)
    
    def draw_ui(self):
        # Левая панель
        x, y = self.left_panel_rect.topleft
        
        # Заголовки
        texts_to_draw = [
            (self.texts['bus'], 'title_large', PURPLE_PRIMARY, (x+100, y+60)),
            (self.texts['title'], 'title', TEXT_PRIMARY, (x+120, y+140)),
            (self.texts['subtitle1'], 'subtitle', TEXT_SECONDARY, (x+110, y+190)),
            (self.texts['subtitle2'], 'subtitle', TEXT_SECONDARY, (x+180, y+220))
        ]
        
        for text, font_name, color, pos in texts_to_draw:
            text_surf = self.font_manager.get_rendered_text(text, font_name, color, True)
            self.screen.blit(text_surf, pos)
        
        # Описание
        desc_y = y + 270
        for line in self.texts['desc']:
            text_surf = self.font_manager.get_rendered_text(line, 'desc', TEXT_TERTIARY, True)
            self.screen.blit(text_surf, (x+105, desc_y))
            desc_y += 30
        
        # График
        self.bar_renderer.draw_bar_graph(self.screen, x+40, y+550, 40, self.bar_heights)
        
        # Правая панель
        x, y = self.right_panel_rect.topleft
        
        # Заголовок меню
        title_text = self.font_manager.get_rendered_text("Главное Меню", 'title', TEXT_PRIMARY, True)
        title_x = x + (self.right_panel_rect.width - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, y+60))
        
        # Кнопки
        for i, button in enumerate(self.buttons):
            icon_x = x + 70
            icon_y = y + 200 + i * 100 + 20
            button.draw(self.screen, self.font_manager.get_font('button'), icon_x, icon_y)
            button.update(1/60)
        
        # Версия
        version_text = self.font_manager.get_rendered_text(self.texts['version'], 'version', TEXT_SECONDARY)
        version_x = x + self.right_panel_rect.width - version_text.get_width() - 20
        version_y = y + self.right_panel_rect.height - version_text.get_height() - 20
        self.screen.blit(version_text, (version_x, version_y))
    
    def run_loading(self):
        if self.loading_screen.update():
            if self.load_resources():
                self.state = ScreenState.MENU
        self.loading_screen.draw()
    
    def run_menu(self):
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        
        self.handle_events()
        
        # Фон и звезды
        self.screen.blit(self.background_cache, (0, 0))
        self.draw_stars(dt)
        
        # Панели
        self.draw_panel(self.left_panel_rect, "left")
        self.draw_panel(self.right_panel_rect, "right")
        
        # Интерфейс
        self.draw_ui()
    
    def run(self):
        while self.running:
            if self.state == ScreenState.LOADING:
                self.run_loading()
            elif self.state == ScreenState.MENU:
                self.run_menu()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()