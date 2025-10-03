import pygame
import sys
import math
import random
from typing import Tuple, List, Dict, Any

# Инициализация Pygame
pygame.init()

# Конфигурация цветов (соответствует оригинальному дизайну)
COLORS = {
    "bg": (7, 6, 19),
    "panel": (15, 18, 32),
    "accent1": (122, 47, 255),
    "accent2": (59, 15, 94),
    "muted": (154, 160, 173),
    "text": (232, 234, 246),
    "white": (247, 247, 251),
    "gold": (255, 215, 0),
    "orange": (255, 165, 0)
}

# Конфигурация игры
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

# Частица для визуальных эффектов
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

# Основной класс игры
class CorporateClicker:
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
        """Загружает шрифты разных размеров"""
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
        surface.fill(COLORS["bg"])
        
        # Рисуем радиальные градиенты (упрощенная версия)
        for i in range(2):
            center_x = width * 0.1 if i == 0 else width * 0.9
            center_y = height * 0.2 if i == 0 else height * 0.8
            radius = min(width, height) * 0.3
            
            # Упрощенный градиент - рисуем полупрозрачные круги
            for r in range(int(radius), 0, -10):
                alpha = max(0, 10 - int(r / (radius / 10)))
                if alpha > 0:
                    color = (*COLORS["accent1"], alpha) if i == 0 else (*COLORS["accent2"], alpha)
                    gradient_surface = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                    pygame.draw.circle(gradient_surface, color, (r, r), r)
                    surface.blit(gradient_surface, (int(center_x - r), int(center_y - r)))
        
        return surface
    
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
        pygame.draw.rect(panel_surface, (*COLORS["panel"], 200), 
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
    
    def draw_button(self, surface: pygame.Surface, rect: pygame.Rect, text: str, 
                   subtitle: str, is_pressed: bool = False, is_hovered: bool = False):
        """Рисует кнопку инвестирования"""
        button_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        
        # Основной цвет кнопки
        if is_pressed:
            base_color = (*COLORS["accent2"], 180)
        elif is_hovered:
            base_color = (*COLORS["accent1"], 200)
        else:
            base_color = (*COLORS["accent1"], 150)
        
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
        
        pygame.draw.rect(button_surface, (*COLORS["accent1"], 220), 
                        (icon_x, icon_y, icon_size, icon_size), border_radius=20)
        
        # Треугольник воспроизведения
        triangle_points = [
            (icon_x + icon_size // 3, icon_y + icon_size // 4),
            (icon_x + icon_size // 3, icon_y + 3 * icon_size // 4),
            (icon_x + 2 * icon_size // 3, icon_y + icon_size // 2)
        ]
        pygame.draw.polygon(button_surface, COLORS["white"], triangle_points)
        
        # Текст кнопки
        title_font = self.fonts["xlarge"]
        subtitle_font = self.fonts["medium"]
        
        title_text = title_font.render(text, True, COLORS["white"])
        subtitle_text = subtitle_font.render(subtitle, True, COLORS["muted"])
        
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
            pygame.draw.rect(pulse_surface, (*COLORS["accent1"], pulse_alpha), 
                            (0, 0, rect.width, rect.height), border_radius=40, width=3)
            button_surface.blit(pulse_surface, (0, 0))
        
        surface.blit(button_surface, rect)
    
    def create_click_effects(self, x: float, y: float):
        """Создает визуальные эффекты при клике"""
        # Частицы
        for _ in range(self.config.animations["click_effect_particles"]):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            color = random.choice([COLORS["accent1"], COLORS["accent2"], (203, 168, 255)])
            particle = Particle(x, y, color, random.randint(3, 6), velocity, 
                              self.config.animations["particle_duration"])
            self.particles.append(particle)
        
        # "Монеты"
        for _ in range(self.config.animations["click_effect_coins"]):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 6)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            particle = Particle(x, y, COLORS["gold"], random.randint(4, 8), velocity, 
                              self.config.animations["particle_duration"])
            self.particles.append(particle)
        
        # Всплывающий текст
        text = f"+{self.format_money(self.per_click)}"
        floating_text = FloatingText(x, y - 50, text, (189, 168, 255), 
                                   self.config.font_sizes["large"])
        self.floating_texts.append(floating_text)
    
    def handle_events(self):
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
    
    def draw(self):
        """Отрисовывает игру"""
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
        
        title_text = title_font.render("Корпоративный Кликер", True, COLORS["white"])
        brand_text = brand_font.render("Black Empire", True, COLORS["accent1"])
        
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
            
            value_text = stat_font.render(value, True, COLORS["white"])
            label_text = label_font.render(label, True, COLORS["muted"])
            
            self.screen.blit(value_text, (x + stat_width // 2 - value_text.get_width() // 2, stats_y))
            self.screen.blit(label_text, (x + stat_width // 2 - label_text.get_width() // 2, stats_y + 40))
        
        # Разделительная линия
        pygame.draw.line(self.screen, COLORS["muted"], 
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
            True, COLORS["muted"]
        )
        self.screen.blit(instruction_text, 
                        (self.config.screen_width // 2 - instruction_text.get_width() // 2, 
                         self.config.screen_height - 80))
        
        
        # Отрисовываем всплывающий текст
        for text in self.floating_texts:
            text.draw(self.screen, self.fonts["large"])
        
        pygame.display.flip()
    
    def run(self):
        """Основной игровой цикл"""
        while self.running:
            current_time = pygame.time.get_ticks()
            dt = current_time - self.last_time
            self.last_time = current_time
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
            self.clock.tick(60)  # Ограничение FPS
        
        pygame.quit()
        sys.exit()

# Запуск игры
if __name__ == "__main__":
    game = CorporateClicker()
    game.run()