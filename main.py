import pygame
import sys
import math
import random
from pygame import gfxdraw  # For anti-aliased drawing
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Screen dimensions (fine-tuned to closely match image aspect ratio ~1.75:1)
SCREEN_WIDTH = 1450
SCREEN_HEIGHT = 830

# Precise color palette extracted/approximated from image
BLACK = (0, 0, 0)
DARK_BG = (5, 5, 20)  # Deeper navy blue
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

class FontManager:
    """Управление шрифтами с fallback-механизмом."""
    
    def __init__(self):
        self.fonts = {}
        self.initialize_fonts()
    
    def initialize_fonts(self) -> None:
        """Инициализирует все шрифты с fallback-механизмом."""
        font_specs = {
            'title_large': ('segoeui.ttf', 80, True),
            'title': ('segoeui.ttf', 36, True),
            'subtitle': ('segoeui.ttf', 22, False),
            'desc': ('segoeui.ttf', 17, False),
            'button': ('segoeui.ttf', 26, True),
            'version': ('segoeui.ttf', 15, False)
        }
        
        for name, (font_name, size, bold) in font_specs.items():
            try:
                self.fonts[name] = pygame.font.Font(font_name, size)
                if bold:
                    self.fonts[name].set_bold(True)
            except (FileNotFoundError, pygame.error):
                self.fonts[name] = pygame.font.SysFont('arial', size, bold)
    
    def get_font(self, name: str) -> pygame.font.Font:
        """Возвращает шрифт по имени."""
        return self.fonts.get(name, pygame.font.SysFont('arial', 17))

class GlassSurfaceFactory:
    """Фабрика для создания стеклянных поверхностей."""
    
    def __init__(self):
        self.cache = {}
    
    def create_glass_surface(self, width: int, height: int, alpha_base: int = 25) -> pygame.Surface:
        """Создает стеклянную поверхность с кэшированием."""
        cache_key = (width, height, alpha_base)
        if cache_key in self.cache:
            return self.cache[cache_key].copy()
        
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Base semi-transparent layer
        base_rect = pygame.Rect(0, 0, width, height)
        pygame.draw.rect(surf, (*PURPLE_ACCENT[:3], alpha_base), base_rect, border_radius=28)
        
        # Gradient overlay
        for i in range(height):
            alpha_grad = int(alpha_base * (1 - i / height * 0.3))
            color_grad = (*PURPLE_ACCENT[:3], alpha_grad)
            pygame.draw.line(surf, color_grad, (0, i), (width, i))
        
        # Frosted noise simulation
        for _ in range(width * height // 200):
            x, y = random.randint(0, width-1), random.randint(0, height-1)
            pygame.draw.circle(surf, (255, 255, 255, 8), (x, y), 1)
        
        # Inner border
        inner_rect = pygame.Rect(3, 3, width-6, height-6)
        pygame.draw.rect(surf, (*LIGHT_PURPLE[:3], 40), inner_rect, border_radius=25, width=1)
        
        # Outer border
        pygame.draw.rect(surf, (*DEEP_PURPLE[:3], 60), base_rect, border_radius=28, width=1)
        
        self.cache[cache_key] = surf.copy()
        return surf

class IconRenderer:
    """Рендерер иконок."""
    
    @staticmethod
    def draw_play_icon(surface: pygame.Surface, x: int, y: int, size: int = 30) -> None:
        """Рисует иконку воспроизведения."""
        points = [(x + 10, y + 5), (x + 30, y + 17), (x + 10, y + 29)]
        gfxdraw.filled_polygon(surface, points, PURPLE_PRIMARY)
        gfxdraw.aapolygon(surface, points, TEXT_PRIMARY)
    
    @staticmethod
    def draw_settings_icon(surface: pygame.Surface, x: int, y: int, size: int = 40) -> None:
        """Рисует иконку настроек."""
        center_x, center_y = x + size // 2, y + size // 2
        radius_outer, radius_inner = 18, 10
        
        gfxdraw.aacircle(surface, center_x, center_y, radius_outer, TEXT_PRIMARY)
        gfxdraw.aacircle(surface, center_x, center_y, radius_inner, TEXT_PRIMARY)
        
        for i in range(12):
            angle = math.radians(i * 30)
            start_x = center_x + radius_outer * math.cos(angle)
            start_y = center_y + radius_outer * math.sin(angle)
            end_x = center_x + (radius_outer + 8) * math.cos(angle)
            end_y = center_y + (radius_outer + 8) * math.sin(angle)
            gfxdraw.line(surface, int(start_x), int(start_y), int(end_x), int(end_y), TEXT_PRIMARY)
    
    @staticmethod
    def draw_exit_icon(surface: pygame.Surface, x: int, y: int, size: int = 30) -> None:
        """Рисует иконку выхода."""
        points = [(x + 15, y + 8), (x + 35, y + 28), (x + 15, y + 28)]
        gfxdraw.filled_polygon(surface, points, PURPLE_PRIMARY)
        gfxdraw.aapolygon(surface, points, TEXT_PRIMARY)
        gfxdraw.line(surface, x + 25, y + 28, x + 25, y + 39, TEXT_PRIMARY)

class BarGraphRenderer:
    """Рендерер графика."""
    
    @staticmethod
    def draw_bar_graph(surface: pygame.Surface, x: int, y: int, bar_width: int, 
                      heights: List[int], bar_count: int = 5) -> None:
        """Рисует столбчатую диаграмму."""
        spacing = 50
        for i in range(bar_count):
            bar_x = x + i * spacing
            bar_height = heights[i]
            bar_rect = pygame.Rect(bar_x, y - bar_height, bar_width, bar_height)
            
            # Base bar
            pygame.draw.rect(surface, BAR_BASE, bar_rect, border_radius=6)
            
            # Gradient
            for j in range(bar_height):
                grad_alpha = int(255 * (1 - j / bar_height * 0.4))
                grad_color = (*BAR_HIGHLIGHT[:3], grad_alpha)
                pygame.draw.line(surface, grad_color, 
                               (bar_x, y - bar_height + j), 
                               (bar_x + bar_width, y - bar_height + j))
            
            # Border
            pygame.draw.rect(surface, PURPLE_ACCENT, bar_rect, 1, border_radius=6)

class Button:
    """Класс кнопки."""
    
    def __init__(self, rect: pygame.Rect, text: str, icon_renderer: callable = None):
        self.rect = rect
        self.text = text
        self.icon_renderer = icon_renderer
        self.hovered = False
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font, 
            icon_x: int, icon_y: int) -> None:
        """Рисует кнопку."""
        # Тень
        shadow_rect = self.rect.move(2, 2)
        pygame.draw.rect(surface, (0, 0, 0, 80), shadow_rect, border_radius=15)
        
        # Основа
        pygame.draw.rect(surface, DEEP_PURPLE, self.rect, border_radius=15)
        
        # Иконка
        if self.icon_renderer:
            self.icon_renderer(surface, icon_x, icon_y)
        
        # Текст
        text_surf = font.render(self.text, True, TEXT_PRIMARY)
        text_rect = text_surf.get_rect(midleft=(icon_x + 60, self.rect.centery))
        surface.blit(text_surf, text_rect)
    
    def is_hovered(self, mouse_pos: Tuple[int, int]) -> bool:
        """Проверяет, наведена ли мышь на кнопку."""
        return self.rect.collidepoint(mouse_pos)

class Game:
    """Основной класс игры."""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Black Empire')
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.font_manager = FontManager()
        self.glass_factory = GlassSurfaceFactory()
        self.icon_renderer = IconRenderer()
        self.bar_renderer = BarGraphRenderer()
        
        self.initialize_ui()
    
    def initialize_ui(self) -> None:
        """Инициализирует UI элементы."""
        # Тексты
        self.texts = {
            'bus': "SKATT",
            'title': "Black Empire",
            'subtitle1': "Построй империю от старта до",
            'subtitle2': "корпорации",
            'desc': [
                "Стартуй маленьким бизнесом: закупи сырье,",
                "управляй активами, инвестируй в улучшения",
                "своего бизнеса. Пройди — это вызов —",
                "старте."
            ],
            'version': "v0.0.1"
        }
        
        # Панели
        self.left_panel_rect = pygame.Rect(60, 100, 620, 720)
        self.right_panel_rect = pygame.Rect(720, 100, 620, 720)
        
        # Кнопки
        button_width, button_height = 500, 80
        button_y_start = self.right_panel_rect.y + 200
        button_spacing = 110
        
        self.buttons = [
            Button(
                pygame.Rect(self.right_panel_rect.x + 60, button_y_start, button_width, button_height),
                "Играть",
                self.icon_renderer.draw_play_icon
            ),
            Button(
                pygame.Rect(self.right_panel_rect.x + 60, button_y_start + button_spacing, button_width, button_height),
                "Настройки",
                self.icon_renderer.draw_settings_icon
            ),
            Button(
                pygame.Rect(self.right_panel_rect.x + 60, button_y_start + 2 * button_spacing, button_width, button_height),
                "Выход",
                self.icon_renderer.draw_exit_icon
            )
        ]
        
        # График
        self.bar_heights = [70, 130, 100, 160, 85]
    
    def handle_events(self) -> None:
        """Обрабатывает события."""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEMOTION:
                for button in self.buttons:
                    button.hovered = button.is_hovered(mouse_pos)
    
    def draw_background(self) -> None:
        """Рисует фон с градиентом."""
        for i in range(SCREEN_HEIGHT):
            bg_alpha = int(255 * (1 - i / SCREEN_HEIGHT * 0.1))
            bg_color = (*DARK_BG[:3], bg_alpha)
            pygame.draw.line(self.screen, bg_color, (0, i), (SCREEN_WIDTH, i))
    
    def draw_panel(self, rect: pygame.Rect) -> None:
        """Рисует стеклянную панель."""
        glass_surf = self.glass_factory.create_glass_surface(rect.width, rect.height)
        self.screen.blit(glass_surf, rect.topleft)
    
    def draw_text_with_shadow(self, text: str, font_name: str, 
                            pos: Tuple[int, int], color: Tuple[int, int, int]) -> None:
        """Рисует текст с тенью."""
        font = self.font_manager.get_font(font_name)
        
        # Тень
        shadow_surf = font.render(text, True, BLACK)
        self.screen.blit(shadow_surf, (pos[0] + 1, pos[1] + 1))
        
        # Основной текст
        text_surf = font.render(text, True, color)
        self.screen.blit(text_surf, pos)
    
    def draw_left_panel(self) -> None:
        """Рисует левую панель."""
        x, y = self.left_panel_rect.topleft
        
        # Логотип и заголовок
        self.draw_text_with_shadow(self.texts['bus'], 'title_large', (x + 140, y + 80), PURPLE_PRIMARY)
        self.draw_text_with_shadow(self.texts['title'], 'title', (x + 150, y + 160), TEXT_PRIMARY)
        
        # Подзаголовок
        self.draw_text_with_shadow(self.texts['subtitle1'], 'subtitle', (x + 140, y + 210), TEXT_SECONDARY)
        self.draw_text_with_shadow(self.texts['subtitle2'], 'subtitle', (x + 220, y + 240), TEXT_SECONDARY)
        
        # Описание
        desc_y = y + 290
        for line in self.texts['desc']:
            self.draw_text_with_shadow(line, 'desc', (x + 125, desc_y), TEXT_TERTIARY)
            desc_y += 30
        
        # График
        #self.bar_renderer.draw_bar_graph(
        #    self.screen, 
        #    x + 50, 
        #    y + 580, 
        #    40, 
        #    self.bar_heights
        
    
    def draw_right_panel(self) -> None:
        """Рисует правую панель."""
        x, y = self.right_panel_rect.topleft
        
        # Заголовок
        self.draw_text_with_shadow("Главное Меню", 'title', 
                                 (x + self.right_panel_rect.width // 2 - 100, y + 60), 
                                 TEXT_PRIMARY)
        
        # Кнопки
        for i, button in enumerate(self.buttons):
            icon_x = x + 80
            icon_y = y + 200 + i * 110 + 15
            button.draw(self.screen, self.font_manager.get_font('button'), icon_x, icon_y)
        
        # Версия
        version_font = self.font_manager.get_font('version')
        version_surf = version_font.render(self.texts['version'], True, TEXT_SECONDARY)
        version_rect = version_surf.get_rect(
            bottomright=(x + self.right_panel_rect.width - 20, y + self.right_panel_rect.height - 20)
        )
        self.screen.blit(version_surf, version_rect)
    
    def run(self) -> None:
        """Запускает главный цикл игры."""
        while self.running:
            self.handle_events()
            
            # Отрисовка
            self.draw_background()
            self.draw_panel(self.left_panel_rect)
            self.draw_panel(self.right_panel_rect)
            self.draw_left_panel()
            self.draw_right_panel()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()