import pygame
import sys
import math
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1450
SCREEN_HEIGHT = 830

# Colors
BLACK = (0, 0, 0)
DARK_BG = (5, 5, 20)
DARK_BLUE = (10, 15, 40)
DARK_PURPLE = (30, 10, 60)
DEEP_BLUE = (20, 25, 80)
DEEP_PURPLE = (40, 20, 100)
BLUE_ACCENT = (60, 80, 180)
PURPLE_ACCENT = (100, 40, 160)
LIGHT_BLUE = (80, 100, 200)
LIGHT_PURPLE = (120, 80, 220)
BAR_BASE = (90, 30, 180)
BAR_HIGHLIGHT = (140, 80, 230)
TEXT_PRIMARY = (245, 245, 255)
TEXT_SECONDARY = (180, 180, 200)
TEXT_TERTIARY = (140, 140, 160)

class ImageManager:
    """Менеджер для загрузки и управления изображениями."""
    
    def __init__(self):
        self.images = {}
        self.create_icon_images()
    
    def create_icon_images(self):
        """Создает иконки программно."""
        # Иконка Play
        play_icon = pygame.Surface((40, 40), pygame.SRCALPHA)
        points = [(10, 5), (30, 20), (10, 35)]
        pygame.draw.polygon(play_icon, LIGHT_BLUE, points)
        pygame.draw.polygon(play_icon, TEXT_PRIMARY, points, 2)
        self.images['play'] = play_icon
        
        # Иконка Settings
        settings_icon = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(settings_icon, TEXT_PRIMARY, (20, 20), 15, 2)
        pygame.draw.circle(settings_icon, TEXT_PRIMARY, (20, 20), 8, 2)
        for i in range(8):
            angle = math.radians(i * 45)
            start_x = 20 + 15 * math.cos(angle)
            start_y = 20 + 15 * math.sin(angle)
            end_x = 20 + 22 * math.cos(angle)
            end_y = 20 + 22 * math.sin(angle)
            pygame.draw.line(settings_icon, TEXT_PRIMARY, (start_x, start_y), (end_x, end_y), 2)
        self.images['settings'] = settings_icon
        
        # Иконка Exit
        exit_icon = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.line(exit_icon, TEXT_PRIMARY, (10, 10), (30, 30), 3)
        pygame.draw.line(exit_icon, TEXT_PRIMARY, (30, 10), (10, 30), 3)
        self.images['exit'] = exit_icon

class FontManager:
    """Управление шрифтами."""
    
    def __init__(self):
        self.fonts = {}
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
            # Fallback to default fonts
            self.fonts['title_large'] = pygame.font.Font(None, 80)
            self.fonts['title'] = pygame.font.Font(None, 36)
            self.fonts['subtitle'] = pygame.font.Font(None, 22)
            self.fonts['desc'] = pygame.font.Font(None, 17)
            self.fonts['button'] = pygame.font.Font(None, 26)
            self.fonts['version'] = pygame.font.Font(None, 15)
    
    def get_font(self, name):
        """Возвращает шрифт по имени."""
        return self.fonts.get(name, self.fonts['desc'])

class GlassSurfaceFactory:
    """Фабрика для создания стеклянных поверхностей с сине-фиолетовым градиентом."""
    
    def __init__(self):
        self.cache = {}
    
    def create_glass_surface(self, width, height, alpha_base=150):
        """Создает стеклянную поверхность с сине-фиолетовым градиентом."""
        cache_key = (width, height, alpha_base)
        if cache_key in self.cache:
            return self.cache[cache_key].copy()
        
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Base semi-transparent layer with blue-purple gradient
        for i in range(height):
            # Интерполяция цвета от темно-синего к темно-фиолетовому
            progress = i / height
            r = int(DARK_BLUE[0] * (1 - progress) + DARK_PURPLE[0] * progress)
            g = int(DARK_BLUE[1] * (1 - progress) + DARK_PURPLE[1] * progress)
            b = int(DARK_BLUE[2] * (1 - progress) + DARK_PURPLE[2] * progress)
            color = (r, g, b, alpha_base)
            pygame.draw.line(surf, color, (0, i), (width, i))
        
        # Добавляем легкий переливающийся эффект
        for i in range(0, height, 4):
            progress = i / height
            # Чередуем синие и фиолетовые акценты
            if i % 8 == 0:
                accent_color = (*BLUE_ACCENT, 30)
            else:
                accent_color = (*PURPLE_ACCENT, 20)
            pygame.draw.line(surf, accent_color, (0, i), (width, i))
        
        # Inner border with blue accent
        inner_rect = pygame.Rect(3, 3, width-6, height-6)
        pygame.draw.rect(surf, (*LIGHT_BLUE, 60), inner_rect, border_radius=25, width=1)
        
        # Outer border with purple accent
        base_rect = pygame.Rect(0, 0, width, height)
        pygame.draw.rect(surf, (*LIGHT_PURPLE, 80), base_rect, border_radius=28, width=2)
        
        # Угловые акценты
        corner_size = 15
        corners = [
            (0, 0), (width-corner_size, 0),
            (0, height-corner_size), (width-corner_size, height-corner_size)
        ]
        
        for corner_x, corner_y in corners:
            pygame.draw.rect(surf, (*BLUE_ACCENT, 100), 
                           (corner_x, corner_y, corner_size, corner_size), 
                           border_radius=5, width=1)
        
        self.cache[cache_key] = surf.copy()
        return surf

class BarGraphRenderer:
    """Рендерер графика."""
    
    @staticmethod
    def draw_bar_graph(surface, x, y, bar_width, heights, bar_count=5):
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
    """Класс кнопки с сине-фиолетовым стилем."""
    
    def __init__(self, rect, text, icon_name=None, image_manager=None):
        self.rect = rect
        self.text = text
        self.icon_name = icon_name
        self.image_manager = image_manager
        self.hovered = False
    
    def draw(self, surface, font, icon_x, icon_y):
        """Рисует кнопку с сине-фиолетовым градиентом."""
        # Тень
        shadow_rect = self.rect.move(3, 3)
        pygame.draw.rect(surface, (0, 0, 0, 60), shadow_rect, border_radius=15)
        
        # Градиентная основа
        for i in range(self.rect.height):
            progress = i / self.rect.height
            r = int(DEEP_BLUE[0] * (1 - progress) + DEEP_PURPLE[0] * progress)
            g = int(DEEP_BLUE[1] * (1 - progress) + DEEP_PURPLE[1] * progress)
            b = int(DEEP_BLUE[2] * (1 - progress) + DEEP_PURPLE[2] * progress)
            color = (r, g, b)
            pygame.draw.line(surface, color, 
                           (self.rect.x, self.rect.y + i), 
                           (self.rect.x + self.rect.width, self.rect.y + i))
        
        # Бордюр
        pygame.draw.rect(surface, LIGHT_BLUE, self.rect, border_radius=15, width=2)
        
        # Иконка
        if self.icon_name and self.image_manager:
            icon = self.image_manager.images.get(self.icon_name)
            if icon:
                surface.blit(icon, (icon_x, icon_y))
        
        # Текст
        text_surf = font.render(self.text, True, TEXT_PRIMARY)
        text_rect = text_surf.get_rect(midleft=(icon_x + 60, self.rect.centery))
        surface.blit(text_surf, text_rect)
        
        # Эффект при наведении
        if self.hovered:
            highlight = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(highlight, (255, 255, 255, 30), highlight.get_rect(), border_radius=15)
            surface.blit(highlight, self.rect.topleft)
    
    def is_hovered(self, mouse_pos):
        """Проверяет, наведена ли мышь на кнопку."""
        return self.rect.collidepoint(mouse_pos)

class Game:
    """Основной класс игры."""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Black Empire')
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.image_manager = ImageManager()
        self.font_manager = FontManager()
        self.glass_factory = GlassSurfaceFactory()
        self.bar_renderer = BarGraphRenderer()
        
        self.initialize_ui()
    
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
    
    def draw_background(self):
        """Рисует темный фон без анимированного графика."""
        # Сплошной темный фон
        self.screen.fill(DARK_BG)
        
        # Легкий градиентный эффект
        for i in range(SCREEN_HEIGHT):
            alpha = int(50 * (i / SCREEN_HEIGHT))
            color = (10, 15, 30, alpha)
            pygame.draw.line(self.screen, color, (0, i), (SCREEN_WIDTH, i))
    
    def draw_panel(self, rect):
        """Рисует стеклянную панель с сине-фиолетовым градиентом."""
        glass_surf = self.glass_factory.create_glass_surface(rect.width, rect.height, 160)
        self.screen.blit(glass_surf, rect.topleft)
    
    def draw_text_with_shadow(self, text, font_name, pos, color):
        """Рисует текст с тенью."""
        font = self.font_manager.get_font(font_name)
        
        # Тень
        shadow_surf = font.render(text, True, BLACK)
        self.screen.blit(shadow_surf, (pos[0] + 2, pos[1] + 2))
        
        # Основной текст
        text_surf = font.render(text, True, color)
        self.screen.blit(text_surf, pos)
    
    def draw_left_panel(self):
        """Рисует левую панель."""
        x, y = self.left_panel_rect.topleft
        
        # Логотип и заголовок
        self.draw_text_with_shadow(self.texts['bus'], 'title_large', (x + 140, y + 80), LIGHT_BLUE)
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
        self.bar_renderer.draw_bar_graph(
            self.screen, 
            x + 50, 
            y + 580, 
            40, 
            self.bar_heights
        )
    
    def draw_right_panel(self):
        """Рисует правую панель."""
        x, y = self.right_panel_rect.topleft
        
        # Заголовок
        self.draw_text_with_shadow("Главное Меню", 'title', 
                                 (x + self.right_panel_rect.width // 2 - 100, y + 60), 
                                 TEXT_PRIMARY)
        
        # Кнопки
        for i, button in enumerate(self.buttons):
            icon_x = x + 80
            icon_y = y + 200 + i * 110 + 20
            button.draw(self.screen, self.font_manager.get_font('button'), icon_x, icon_y)
        
        # Версия
        version_font = self.font_manager.get_font('version')
        version_surf = version_font.render(self.texts['version'], True, TEXT_SECONDARY)
        version_rect = version_surf.get_rect(
            bottomright=(x + self.right_panel_rect.width - 20, y + self.right_panel_rect.height - 20)
        )
        self.screen.blit(version_surf, version_rect)
    
    def run(self):
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