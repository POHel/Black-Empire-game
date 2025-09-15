import pygame
import sys
import math
from typing import List, Tuple, Dict, Any

# Initialize Pygame with optimized settings
pygame.init()
pygame.mixer.quit()  # Отключаем звук для экономии ресурсов

# Screen dimensions
SCREEN_WIDTH = 1450
SCREEN_HEIGHT = 830

# Colors
BLACK = (0, 0, 0)
DARK_BG = (5, 5, 20)
DARK_BLUE = (8, 12, 35)
DARK_PURPLE = (25, 8, 50)
DEEP_BLUE = (15, 20, 65)
DEEP_PURPLE = (35, 15, 85)
BLUE_ACCENT = (50, 70, 160)
PURPLE_ACCENT = (85, 35, 140)
LIGHT_BLUE = (70, 90, 180)
LIGHT_PURPLE = (110, 70, 200)
NEON_BLUE = (100, 150, 255)
NEON_PURPLE = (180, 100, 255)
NEON_GREEN = (57, 255, 20)
BAR_BASE = (90, 30, 180)
BAR_HIGHLIGHT = (140, 80, 230)
TEXT_PRIMARY = (245, 245, 255)
TEXT_SECONDARY = (180, 180, 200)
TEXT_TERTIARY = (140, 140, 160)

class ImageManager:
    """Менеджер для загрузки и управления изображениями с кэшированием."""
    
    def __init__(self):
        self.images: Dict[str, pygame.Surface] = {}
        self.create_icon_images()
    
    def create_icon_images(self):
        """Создает иконки программно с антиалиасингом."""
        # Иконка Play
        play_icon = pygame.Surface((40, 40), pygame.SRCALPHA)
        points = [(10, 5), (30, 20), (10, 35)]
        pygame.draw.polygon(play_icon, NEON_BLUE, points)
        pygame.draw.polygon(play_icon, TEXT_PRIMARY, points, 2)
        self.images['play'] = play_icon
        
        # Иконка Settings
        settings_icon = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(settings_icon, NEON_PURPLE, (20, 20), 15, 2)
        pygame.draw.circle(settings_icon, NEON_PURPLE, (20, 20), 8, 2)
        for i in range(8):
            angle = math.radians(i * 45)
            start_x = 20 + 15 * math.cos(angle)
            start_y = 20 + 15 * math.sin(angle)
            end_x = 20 + 22 * math.cos(angle)
            end_y = 20 + 22 * math.sin(angle)
            pygame.draw.line(settings_icon, NEON_PURPLE, (start_x, start_y), (end_x, end_y), 2)
        self.images['settings'] = settings_icon
        
        # Иконка Exit
        exit_icon = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.line(exit_icon, NEON_BLUE, (10, 10), (30, 30), 3)
        pygame.draw.line(exit_icon, NEON_BLUE, (30, 10), (10, 30), 3)
        self.images['exit'] = exit_icon

class FontManager:
    """Управление шрифтами с кэшированием рендеренного текста."""
    
    def __init__(self):
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.text_cache: Dict[Tuple, pygame.Surface] = {}
        self.initialize_fonts()
    
    def initialize_fonts(self):
        """Инициализирует все шрифты."""
        try:
            self.fonts['title_large'] = pygame.font.SysFont('arial', 80, bold=True)
            self.fonts['title'] = pygame.font.SysFont('arial', 36, bold=True)
            self.fonts['subtitle'] = pygame.font.SysFont('arial', 22)
            self.fonts['desc'] = pygame.font.SysFont('arial', 17)
            self.fonts['button'] = pygame.font.SysFont('arial', 26, bold=True)
            self.fonts['version'] = pygame.font.SysFont('arial', 15)
        except:
            self.fonts['title_large'] = pygame.font.Font(None, 80)
            self.fonts['title'] = pygame.font.Font(None, 36)
            self.fonts['subtitle'] = pygame.font.Font(None, 22)
            self.fonts['desc'] = pygame.font.Font(None, 17)
            self.fonts['button'] = pygame.font.Font(None, 26)
            self.fonts['version'] = pygame.font.Font(None, 15)
    
    def get_font(self, name: str) -> pygame.font.Font:
        """Возвращает шрифт по имени."""
        return self.fonts.get(name, self.fonts['desc'])
    
    def get_rendered_text(self, text: str, font_name: str, color: Tuple[int, int, int], 
                         alpha: int = 255) -> pygame.Surface:
        """Возвращает рендеренный текст с кэшированием."""
        cache_key = (text, font_name, color, alpha)
        if cache_key in self.text_cache:
            return self.text_cache[cache_key]
        
        font = self.get_font(font_name)
        text_surface = font.render(text, True, color)
        if alpha < 255:
            text_surface = text_surface.copy()
            text_surface.set_alpha(alpha)
        
        self.text_cache[cache_key] = text_surface
        return text_surface

class GlassSurfaceFactory:
    """Фабрика для создания стеклянных поверхностей с улучшенным градиентом и кэшированием."""
    
    def __init__(self):
        self.cache: Dict[Tuple, pygame.Surface] = {}
        self.gradient_cache: Dict[Tuple, pygame.Surface] = {}
    
    def create_glass_surface(self, width: int, height: int, alpha_base: int = 180, 
                           border_radius: int = 35) -> pygame.Surface:
        """Создает стеклянную поверхность с улучшенным сине-фиолетовым градиентом."""
        cache_key = (width, height, alpha_base, border_radius)
        if cache_key in self.cache:
            return self.cache[cache_key].copy()
        
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Создаем базовый градиент
        gradient = self._create_gradient_surface(width, height, alpha_base)
        surf.blit(gradient, (0, 0))
        
        # Добавляем эффекты
        self._add_glass_effects(surf, width, height, border_radius)
        self._add_border_effects(surf, width, height, border_radius)
        
        self.cache[cache_key] = surf.copy()
        return surf
    
    def _create_gradient_surface(self, width: int, height: int, alpha_base: int) -> pygame.Surface:
        """Создает поверхность с градиентом."""
        cache_key = (width, height, alpha_base)
        if cache_key in self.gradient_cache:
            return self.gradient_cache[cache_key].copy()
        
        gradient = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Предварительно вычисляем цвета для каждой линии
        for i in range(height):
            progress = i / height
            r = int(self._bezier(DARK_BLUE[0], BLUE_ACCENT[0], PURPLE_ACCENT[0], DARK_PURPLE[0], progress))
            g = int(self._bezier(DARK_BLUE[1], BLUE_ACCENT[1], PURPLE_ACCENT[1], DARK_PURPLE[1], progress))
            b = int(self._bezier(DARK_BLUE[2], BLUE_ACCENT[2], PURPLE_ACCENT[2], DARK_PURPLE[2], progress))
            
            color = (r, g, b, alpha_base)
            pygame.draw.line(gradient, color, (0, i), (width, i))
        
        self.gradient_cache[cache_key] = gradient.copy()
        return gradient
    
    def _add_glass_effects(self, surf: pygame.Surface, width: int, height: int, border_radius: int):
        """Добавляет стеклянные эффекты."""
        # Легкое свечение по краям
        edge_glow = 20
        for i in range(edge_glow):
            alpha = int(80 * (1 - i / edge_glow))
            pygame.draw.line(surf, (*NEON_BLUE[:3], alpha), (i, 0), (i, height))
            pygame.draw.line(surf, (*NEON_PURPLE[:3], alpha), (width - i - 1, 0), (width - i - 1, height))
    
    def _add_border_effects(self, surf: pygame.Surface, width: int, height: int, border_radius: int):
        """Добавляет эффекты границ."""
        # Внешняя граница с мягким переходом
        base_rect = pygame.Rect(0, 0, width, height)
        pygame.draw.rect(surf, (*NEON_PURPLE, 80), base_rect, border_radius=border_radius, width=2)
        
        # Внутренняя подсветка
        inner_rect = pygame.Rect(2, 2, width-4, height-4)
        pygame.draw.rect(surf, (*NEON_BLUE, 40), inner_rect, border_radius=border_radius-2, width=1)
    
    def _bezier(self, p0: float, p1: float, p2: float, p3: float, t: float) -> float:
        """Кривая Безье для плавной интерполяции."""
        return (1-t)**3 * p0 + 3*(1-t)**2 * t * p1 + 3*(1-t)*t**2 * p2 + t**3 * p3

class BarGraphRenderer:
    """Рендерер графика с оптимизированной отрисовкой."""
    
    @staticmethod
    def draw_bar_graph(surface: pygame.Surface, x: int, y: int, bar_width: int, 
                      heights: List[int], bar_count: int = 5):
        """Рисует столбчатую диаграмму с предварительно вычисленными градиентами."""
        spacing = 50
        
        # Предварительно создаем поверхности для столбцов
        max_height = max(heights)
        for i in range(bar_count):
            bar_x = x + i * spacing
            bar_height = heights[i]
            
            # Создаем поверхность для столбца
            bar_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            
            # Заполняем градиентом
            for j in range(bar_height):
                progress = j / bar_height
                r = int(DEEP_BLUE[0] * (1 - progress) + NEON_PURPLE[0] * progress)
                g = int(DEEP_BLUE[1] * (1 - progress) + NEON_PURPLE[1] * progress)
                b = int(DEEP_BLUE[2] * (1 - progress) + NEON_PURPLE[2] * progress)
                pygame.draw.line(bar_surface, (r, g, b), (0, j), (bar_width, j))
            
            # Добавляем бордюр
            pygame.draw.rect(bar_surface, NEON_BLUE, (0, 0, bar_width, bar_height), 
                           border_radius=8, width=1)
            
            # Верхняя подсветка
            pygame.draw.rect(bar_surface, NEON_PURPLE, (0, 0, bar_width, 3), border_radius=2)
            
            # Рисуем столбец
            surface.blit(bar_surface, (bar_x, y - bar_height))

class Button:
    """Класс кнопки с улучшенным градиентом и анимацией при наведении."""
    
    def __init__(self, rect: pygame.Rect, text: str, icon_name: str = None, 
                 image_manager: ImageManager = None):
        self.rect = rect
        self.text = text
        self.icon_name = icon_name
        self.image_manager = image_manager
        self.hovered = False
        self.hover_progress = 0
        self.gradient_cache: Dict[float, pygame.Surface] = {}
    
    def update(self):
        """Обновляет анимацию кнопки."""
        target_progress = 1.0 if self.hovered else 0.0
        self.hover_progress += (target_progress - self.hover_progress) * 0.15
    
    def draw(self, surface: pygame.Surface, font_manager: FontManager, icon_x: int, icon_y: int):
        """Рисует кнопку с улучшенным градиентом и анимацией."""
        # Кэшируем градиенты для разных состояний наведения
        if self.hover_progress not in self.gradient_cache:
            self.gradient_cache[self.hover_progress] = self._create_gradient_surface()
        
        # Рисуем кэшированный градиент
        surface.blit(self.gradient_cache[self.hover_progress], self.rect.topleft)
        
        # Иконка
        if self.icon_name and self.image_manager:
            icon = self.image_manager.images.get(self.icon_name)
            if icon:
                glow_alpha = 20 + int(40 * self.hover_progress)
                glow_color = (*NEON_GREEN, glow_alpha) if self.hovered else (*NEON_BLUE, 20)
                
                glow = pygame.Surface((50, 50), pygame.SRCALPHA)
                pygame.draw.circle(glow, glow_color, (25, 25), 25)
                surface.blit(glow, (icon_x - 5, icon_y - 5))
                surface.blit(icon, (icon_x, icon_y))
        
        # Текст
        text_color = NEON_GREEN if self.hovered else TEXT_PRIMARY
        text_surf = font_manager.get_rendered_text(self.text, 'button', text_color)
        text_rect = text_surf.get_rect(midleft=(icon_x + 60, self.rect.centery))
        
        # Тень текста
        shadow_surf = font_manager.get_rendered_text(self.text, 'button', (0, 0, 0, 100))
        surface.blit(shadow_surf, text_rect.move(2, 2))
        surface.blit(text_surf, text_rect)
    
    def _create_gradient_surface(self) -> pygame.Surface:
        """Создает поверхность с градиентом для текущего состояния."""
        surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Основной градиент
        for i in range(self.rect.height):
            progress = i / self.rect.height
            
            if self.hover_progress > 0:
                r = int(self._bezier(DEEP_BLUE[0], BLUE_ACCENT[0], PURPLE_ACCENT[0], 
                                   DEEP_PURPLE[0], progress) * (1 - self.hover_progress * 0.7) + 
                       NEON_GREEN[0] * self.hover_progress * 0.7)
                g = int(self._bezier(DEEP_BLUE[1], BLUE_ACCENT[1], PURPLE_ACCENT[1], 
                                   DEEP_PURPLE[1], progress) * (1 - self.hover_progress * 0.7) + 
                       NEON_GREEN[1] * self.hover_progress * 0.7)
                b = int(self._bezier(DEEP_BLUE[2], BLUE_ACCENT[2], PURPLE_ACCENT[2], 
                                   DEEP_PURPLE[2], progress) * (1 - self.hover_progress * 0.7) + 
                       NEON_GREEN[2] * self.hover_progress * 0.7)
            else:
                r = int(self._bezier(DEEP_BLUE[0], BLUE_ACCENT[0], PURPLE_ACCENT[0], 
                                   DEEP_PURPLE[0], progress))
                g = int(self._bezier(DEEP_BLUE[1], BLUE_ACCENT[1], PURPLE_ACCENT[1], 
                                   DEEP_PURPLE[1], progress))
                b = int(self._bezier(DEEP_BLUE[2], BLUE_ACCENT[2], PURPLE_ACCENT[2], 
                                   DEEP_PURPLE[2], progress))
            
            pygame.draw.line(surf, (r, g, b), (0, i), (self.rect.width, i))
        
        # Бордюр
        border_color = (
            int(LIGHT_BLUE[0] * (1 - self.hover_progress) + NEON_GREEN[0] * self.hover_progress),
            int(LIGHT_BLUE[1] * (1 - self.hover_progress) + NEON_GREEN[1] * self.hover_progress),
            int(LIGHT_BLUE[2] * (1 - self.hover_progress) + NEON_GREEN[2] * self.hover_progress)
        )
        pygame.draw.rect(surf, border_color, (0, 0, self.rect.width, self.rect.height), 
                       border_radius=18, width=2)
        
        return surf
    
    def _bezier(self, p0: float, p1: float, p2: float, p3: float, t: float) -> float:
        """Кривая Безье для плавной интерполяции."""
        return (1-t)**3 * p0 + 3*(1-t)**2 * t * p1 + 3*(1-t)*t**2 * p2 + t**3 * p3
    
    def is_hovered(self, mouse_pos: Tuple[int, int]) -> bool:
        """Проверяет, наведена ли мышь на кнопку."""
        return self.rect.collidepoint(mouse_pos)

class Game:
    """Основной класс игры с оптимизированным рендерингом."""
    
    def __init__(self):
        # Создаем экран с двойной буферизацией и аппаратным ускорением
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 
                                            pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption('Black Empire')
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Оптимизация: предварительный рендеринг статических элементов
        self.background = None
        self.left_panel = None
        self.right_panel = None
        
        self.image_manager = ImageManager()
        self.font_manager = FontManager()
        self.glass_factory = GlassSurfaceFactory()
        self.bar_renderer = BarGraphRenderer()
        
        self.initialize_ui()
        self.prerender_static_elements()
    
    def initialize_ui(self):
        """Инициализирует UI элементы."""
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
        
        self.left_panel_rect = pygame.Rect(60, 100, 620, 720)
        self.right_panel_rect = pygame.Rect(720, 100, 620, 720)
        
        button_width, button_height = 500, 80
        button_y_start = self.right_panel_rect.y + 200
        button_spacing = 110
        
        self.buttons = [
            Button(
                pygame.Rect(self.right_panel_rect.x + 60, button_y_start, button_width, button_height),
                "Играть",
                'play',
                self.image_manager
            ),
            Button(
                pygame.Rect(self.right_panel_rect.x + 60, button_y_start + button_spacing, button_width, button_height),
                "Настройки",
                'settings',
                self.image_manager
            ),
            Button(
                pygame.Rect(self.right_panel_rect.x + 60, button_y_start + 2 * button_spacing, button_width, button_height),
                "Выход",
                'exit',
                self.image_manager
            )
        ]
        
        self.bar_heights = [70, 130, 100, 160, 85]
    
    def prerender_static_elements(self):
        """Предварительно рендерит статические элементы для оптимизации."""
        # Фон
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for i in range(SCREEN_HEIGHT):
            progress = i / SCREEN_HEIGHT
            r = int(DARK_BG[0] * (1 - progress) + DARK_BLUE[0] * progress)
            g = int(DARK_BG[1] * (1 - progress) + DARK_BLUE[1] * progress)
            b = int(DARK_BG[2] * (1 - progress) + DARK_BLUE[2] * progress)
            pygame.draw.line(self.background, (r, g, b), (0, i), (SCREEN_WIDTH, i))
        
        # Панели
        self.left_panel = self.glass_factory.create_glass_surface(
            self.left_panel_rect.width, self.left_panel_rect.height, 200, 35
        )
        self.right_panel = self.glass_factory.create_glass_surface(
            self.right_panel_rect.width, self.right_panel_rect.height, 200, 35
        )
    
    def handle_events(self):
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
    
    def update(self):
        """Обновляет состояние игры."""
        for button in self.buttons:
            button.update()
    
    def draw(self):
        """Отрисовывает все элементы игры."""
        # Фон
        self.screen.blit(self.background, (0, 0))
        
        # Панели
        self.screen.blit(self.left_panel, self.left_panel_rect.topleft)
        self.screen.blit(self.right_panel, self.right_panel_rect.topleft)
        
        # Динамический контент
        self.draw_left_panel_content()
        self.draw_right_panel_content()
    
    def draw_left_panel_content(self):
        """Рисует содержимое левой панели."""
        x, y = self.left_panel_rect.topleft
        
        # Тексты
        self.draw_text_with_shadow(self.texts['bus'], 'title_large', (x + 140, y + 80), NEON_BLUE)
        self.draw_text_with_shadow(self.texts['title'], 'title', (x + 150, y + 160), TEXT_PRIMARY)
        
        self.draw_text_with_shadow(self.texts['subtitle1'], 'subtitle', (x + 140, y + 210), TEXT_SECONDARY)
        self.draw_text_with_shadow(self.texts['subtitle2'], 'subtitle', (x + 220, y + 240), TEXT_SECONDARY)
        
        desc_y = y + 290
        for line in self.texts['desc']:
            self.draw_text_with_shadow(line, 'desc', (x + 125, desc_y), TEXT_TERTIARY)
            desc_y += 30
        
        # График
        self.bar_renderer.draw_bar_graph(
            self.screen, 
            x + 50, 
            y + 580, 
            40, 
            self.bar_heights
        )
    
    def draw_right_panel_content(self):
        """Рисует содержимое правой панели."""
        x, y = self.right_panel_rect.topleft
        
        # Заголовок
        self.draw_text_with_shadow("Главное Меню", 'title', 
                                 (x + self.right_panel_rect.width // 2 - 100, y + 60), 
                                 TEXT_PRIMARY)
        
        # Кнопки
        for i, button in enumerate(self.buttons):
            icon_x = x + 80
            icon_y = y + 200 + i * 110 + 20
            button.draw(self.screen, self.font_manager, icon_x, icon_y)
        
        # Версия
        version_surf = self.font_manager.get_rendered_text(self.texts['version'], 'version', TEXT_SECONDARY)
        version_rect = version_surf.get_rect(
            bottomright=(x + self.right_panel_rect.width - 20, y + self.right_panel_rect.height - 20)
        )
        self.screen.blit(version_surf, version_rect)
    
    def draw_text_with_shadow(self, text: str, font_name: str, pos: Tuple[int, int], 
                            color: Tuple[int, int, int]):
        """Рисует текст с тенью."""
        # Тень
        for i in range(3, 0, -1):
            shadow_surf = self.font_manager.get_rendered_text(text, font_name, (0, 0, 0, 80 - i * 25))
            self.screen.blit(shadow_surf, (pos[0] + i, pos[1] + i))
        
        # Основной текст
        text_surf = self.font_manager.get_rendered_text(text, font_name, color)
        self.screen.blit(text_surf, pos)
    
    def run(self):
        """Запускает главный цикл игры."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()