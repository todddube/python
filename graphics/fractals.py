import pygame
import numpy as np
import random
import colorsys
import sys
from PIL import Image
import io

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
SIDEBAR_WIDTH = 250
MAX_ITER_DEFAULT = 100
FONT_SIZE = 24

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (100, 100, 100)
BLUE = (0, 120, 255)
PURPLE = (120, 0, 200)

# Existing mandelbrot function
def mandelbrot(h, w, max_iter, random_params=True):
    if random_params:
        x_min, x_max = -2 + random.uniform(-0.5, 0.5), 0.5 + random.uniform(-0.2, 0.2)
        y_min, y_max = -1.5 + random.uniform(-0.3, 0.3), 1.5 + random.uniform(-0.3, 0.3)
    else:
        x_min, x_max = -2, 0.5
        y_min, y_max = -1.5, 1.5
        
    x, y = np.linspace(x_min, x_max, w), np.linspace(y_min, y_max, h)
    X, Y = np.meshgrid(x, y)
    Z = X + Y*1j
    C = Z.copy()
    divtime = max_iter + np.zeros(Z.shape, dtype=int)
    
    for i in range(max_iter):
        Z = Z**2 + C
        diverge = Z*np.conj(Z) > 2**2
        div_now = diverge & (divtime == max_iter)
        divtime[div_now] = i
        Z[diverge] = 2
    
    return divtime

# Existing julia function
def julia(h, w, max_iter, c):
    x = np.linspace(-2, 2, w)
    y = np.linspace(-2, 2, h)
    X, Y = np.meshgrid(x, y)
    Z = X + Y*1j
    divtime = max_iter + np.zeros(Z.shape, dtype=int)
    
    for i in range(max_iter):
        Z = Z**2 + c
        diverge = Z*np.conj(Z) > 2**2
        div_now = diverge & (divtime == max_iter)
        divtime[div_now] = i
        Z[diverge] = 2
    
    return divtime

def create_colormap(max_iter):
    colors = []
    for i in range(max_iter):
        hue = (i / max_iter + random.uniform(-0.1, 0.1)) % 1.0
        saturation = random.uniform(0.8, 1.0)
        value = random.uniform(0.8, 1.0)
        rgb = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(hue, saturation, value))
        colors.append(rgb)
    colors.append((0, 0, 0))
    return colors

def generate_fractal(fractal_type, width, height, max_iter):
    """Generate fractal based on type and parameters"""
    if fractal_type == "random":
        fractal_type = random.choice(["mandelbrot", "julia"])
    
    status_text = ""
    if fractal_type == "mandelbrot":
        fractal = mandelbrot(height, width, max_iter, random_params=True)
        status_text = "Generated a Mandelbrot Set"
    else:  # julia
        c = complex(random.uniform(-1, 1), random.uniform(-1, 1))
        fractal = julia(height, width, max_iter, c)
        status_text = f"Generated a Julia Set with c = {c:.2f}"
    
    colors = create_colormap(max_iter)
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    for i in range(width):
        for j in range(height):
            pixels[i, j] = colors[fractal[j, i]]
    
    # Convert PIL Image to pygame surface
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return pygame.image.load(img_bytes), status_text

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.SysFont('Arial', FONT_SIZE)
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)
        
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

class Slider:
    def __init__(self, x, y, width, height, min_value, max_value, start_value, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.handle_rect = pygame.Rect(x + (start_value - min_value) * width / (max_value - min_value), y - 10, 20, 20)
        self.min_value = min_value
        self.max_value = max_value
        self.value = start_value
        self.label = label
        self.active = False
        self.font = pygame.font.SysFont('Arial', FONT_SIZE - 4)
        
    def draw(self, screen):
        # Draw slider track
        pygame.draw.rect(screen, DARK_GRAY, self.rect, border_radius=4)
        
        # Draw slider handle
        pygame.draw.rect(screen, BLUE, self.handle_rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.handle_rect, 2, border_radius=10)
        
        # Draw label and value
        label_text = self.font.render(f"{self.label}: {self.value}", True, BLACK)
        screen.blit(label_text, (self.rect.x, self.rect.y - 30))
        
    def update(self, mouse_pos):
        if self.active:
            x_pos = max(self.rect.left, min(mouse_pos[0], self.rect.right))
            self.handle_rect.centerx = x_pos
            self.value = int(self.min_value + (x_pos - self.rect.left) * 
                          (self.max_value - self.min_value) / self.rect.width)
            
    def check_click(self, mouse_pos, mouse_clicked):
        if mouse_clicked and self.handle_rect.collidepoint(mouse_pos):
            self.active = True
        elif not pygame.mouse.get_pressed()[0]:
            self.active = False

class RadioButton:
    def __init__(self, x, y, options, default_idx=0):
        self.options = options
        self.selected_idx = default_idx
        self.rects = []
        self.font = pygame.font.SysFont('Arial', FONT_SIZE - 4)
        
        for i, opt in enumerate(options):
            self.rects.append(pygame.Rect(x, y + i * 30, 20, 20))
            
    def draw(self, screen):
        title = self.font.render("Fractal Type:", True, BLACK)
        screen.blit(title, (self.rects[0].x, self.rects[0].y - 30))
        
        for i, (rect, opt) in enumerate(zip(self.rects, self.options)):
            # Draw circle
            pygame.draw.circle(screen, WHITE, rect.center, 10)
            pygame.draw.circle(screen, BLACK, rect.center, 10, 2)
            
            # Draw selected circle
            if i == self.selected_idx:
                pygame.draw.circle(screen, BLUE, rect.center, 6)
                
            # Draw label
            text = self.font.render(opt, True, BLACK)
            screen.blit(text, (rect.x + 25, rect.y - 2))
            
    def handle_click(self, mouse_pos, mouse_clicked):
        if mouse_clicked:
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_idx = i
                    return True
        return False

def main():
    # Set up the display
    screen = pygame.display.set_mode((WIDTH + SIDEBAR_WIDTH, HEIGHT))
    pygame.display.set_caption("Fractal Generator")
    clock = pygame.time.Clock()
    
    # Initialize fonts
    title_font = pygame.font.SysFont('Arial', FONT_SIZE + 8)
    font = pygame.font.SysFont('Arial', FONT_SIZE)
    small_font = pygame.font.SysFont('Arial', FONT_SIZE - 6)
    
    # Initialize UI components
    fractal_radio = RadioButton(SIDEBAR_WIDTH + 40, 60, ["Random", "Mandelbrot", "Julia"])
    max_iter_slider = Slider(30, 180, SIDEBAR_WIDTH - 60, 10, 50, 200, MAX_ITER_DEFAULT, "Max Iterations")
    width_slider = Slider(30, 240, SIDEBAR_WIDTH - 60, 10, 400, 1200, 800, "Width")
    height_slider = Slider(30, 300, SIDEBAR_WIDTH - 60, 10, 300, 900, 600, "Height")
    generate_button = Button(30, 360, SIDEBAR_WIDTH - 60, 40, "Generate New Fractal", LIGHT_GRAY, GRAY)
    
    # Initialize fractal image
    fractal_surface = None
    fractal_status = "Click 'Generate New Fractal' to start"
    loading = False
    
    # Main game loop
    running = True
    while running:
        # Handle events
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True
                
        # Update UI components
        generate_button.check_hover(mouse_pos)
        max_iter_slider.check_click(mouse_pos, mouse_clicked)
        max_iter_slider.update(mouse_pos)
        width_slider.check_click(mouse_pos, mouse_clicked)
        width_slider.update(mouse_pos)
        height_slider.check_click(mouse_pos, mouse_clicked)
        height_slider.update(mouse_pos)
        
        if fractal_radio.handle_click(mouse_pos, mouse_clicked):
            pass  # Handle radio button selection
            
        # Check for button click
        if generate_button.is_clicked(mouse_pos, mouse_clicked):
            loading = True
            fractal_status = "Generating fractal..."
            
            # Use the selected parameters to generate a new fractal
            fractal_type = fractal_radio.options[fractal_radio.selected_idx].lower()
            max_iter = max_iter_slider.value
            width = width_slider.value
            height = height_slider.value
            
            # Generate the fractal
            fractal_surface, fractal_status = generate_fractal(
                fractal_type, 
                width, 
                height, 
                max_iter
            )
            loading = False
            
        # Draw UI
        # Clear the screen
        screen.fill(WHITE)
        
        # Draw sidebar background
        pygame.draw.rect(screen, LIGHT_GRAY, (0, 0, SIDEBAR_WIDTH, HEIGHT))
        pygame.draw.line(screen, DARK_GRAY, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, HEIGHT), 2)
        
        # Draw title in sidebar
        title_text = title_font.render("Fractal Generator", True, BLACK)
        screen.blit(title_text, (30, 20))
        
        # Draw UI components
        max_iter_slider.draw(screen)
        width_slider.draw(screen)
        height_slider.draw(screen)
        generate_button.draw(screen)
        fractal_radio.draw(screen)
        
        # Draw About section
        about_y = 420
        about_text = font.render("About", True, BLACK)
        screen.blit(about_text, (30, about_y))
        
        about_lines = [
            "This app generates beautiful fractals using:",
            "- Mandelbrot Set",
            "- Julia Set",
            "",
            "Adjust parameters and click 'Generate'!"
        ]
        
        for i, line in enumerate(about_lines):
            text = small_font.render(line, True, BLACK)
            screen.blit(text, (30, about_y + 40 + i * 20))
            
        # Draw fractal image if available
        if fractal_surface:
            # Calculate scaled size to fit within the display area
            img_width, img_height = fractal_surface.get_size()
            scale = min((WIDTH - SIDEBAR_WIDTH) / img_width, HEIGHT / img_height)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Center the image in the display area
            pos_x = SIDEBAR_WIDTH + ((WIDTH - SIDEBAR_WIDTH) - new_width) // 2
            pos_y = (HEIGHT - new_height) // 2
            
            scaled_surface = pygame.transform.scale(fractal_surface, (new_width, new_height))
            screen.blit(scaled_surface, (pos_x, pos_y))
            
        # Draw status text
        status_text = font.render(fractal_status, True, BLACK)
        screen.blit(status_text, (SIDEBAR_WIDTH + 20, 20))
        
        # Draw footer
        footer_text = small_font.render("Made with PyGame", True, BLACK)
        screen.blit(footer_text, (WIDTH - footer_text.get_width() - 20, HEIGHT - 30))
        
        # Update the display
        pygame.display.update()
        clock.tick(60)  # Limit to 60 FPS
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()