import pygame
import random
import sys
import math

# Initialize pygame
pygame.init()

# Get screen dimensions for fullscreen
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Snow Storm")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (25, 25, 50)

# Snow simulation parameters - these can be adjusted
SNOWFLAKE_COUNT = 5000      # Number of active snowflakes
SNOW_RATE = 10              # How many snowflakes to add per frame (higher = more snow)
SNOW_SPEED_MIN = 1          # Minimum snow falling speed
SNOW_SPEED_MAX = 3          # Maximum snow falling speed
WIND_FACTOR = 0.5           # How much wind affects the snowflakes horizontally
SNOWFLAKE_SIZE_MIN = 1      # Minimum size of a snowflake
SNOWFLAKE_SIZE_MAX = 3      # Maximum size of a snowflake
GROUND_HEIGHT = 10          # Height of snow accumulation area at the bottom

# Settings dialog class
class SettingsDialog:
    def __init__(self):
        self.dialog_rect = pygame.Rect(SCREEN_WIDTH//4, SCREEN_HEIGHT//4, 500, 750)
        self.active = False
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.settings = {
            "SNOWFLAKE_COUNT": SNOWFLAKE_COUNT,
            "SNOW_RATE": SNOW_RATE,
            "SNOW_SPEED_MIN": SNOW_SPEED_MIN,
            "SNOW_SPEED_MAX": SNOW_SPEED_MAX,
            "WIND_FACTOR": WIND_FACTOR,
            "SNOWFLAKE_SIZE_MIN": SNOWFLAKE_SIZE_MIN,
            "SNOWFLAKE_SIZE_MAX": SNOWFLAKE_SIZE_MAX,
            "GROUND_HEIGHT": GROUND_HEIGHT
        }
        self.selected = None
        self.input_text = ""
        self.setting_descriptions = {
            "SNOWFLAKE_COUNT": "Number of active snowflakes",
            "SNOW_RATE": "Snowflakes added per frame",
            "SNOW_SPEED_MIN": "Minimum falling speed",
            "SNOW_SPEED_MAX": "Maximum falling speed",
            "WIND_FACTOR": "Wind strength factor",
            "SNOWFLAKE_SIZE_MIN": "Minimum snowflake size",
            "SNOWFLAKE_SIZE_MAX": "Maximum snowflake size",
            "GROUND_HEIGHT": "Height of snow accumulation"
        }
        # Create plus/minus buttons for each setting
        self.plus_buttons = {}
        self.minus_buttons = {}
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Draw dialog background with semi-transparency
        s = pygame.Surface((self.dialog_rect.width, self.dialog_rect.height))
        s.set_alpha(230)
        s.fill((200, 200, 220))
        screen.blit(s, (self.dialog_rect.left, self.dialog_rect.top))
        pygame.draw.rect(screen, (100, 100, 140), self.dialog_rect, 2)
        
        # Draw title
        title = self.font.render("Snow Storm Settings", True, (50, 50, 100))
        screen.blit(title, (self.dialog_rect.centerx - title.get_width() // 2, self.dialog_rect.top + 10))
        
        y = self.dialog_rect.top + 50
        for setting, value in self.settings.items():
            # Determine text color based on selection
            text_color = (0, 0, 180) if setting == self.selected else BLACK
            
            # Draw setting name and description
            name_text = self.font.render(f"{setting}:", True, text_color)
            screen.blit(name_text, (self.dialog_rect.left + 10, y))
            desc_text = self.small_font.render(self.setting_descriptions[setting], True, (80, 80, 80))
            screen.blit(desc_text, (self.dialog_rect.left + 10, y + 25))
            
            # Draw input box
            input_rect = pygame.Rect(self.dialog_rect.left + 250, y, 100, 30)
            pygame.draw.rect(screen, (255, 255, 255), input_rect)
            pygame.draw.rect(screen, (100, 100, 140) if setting == self.selected else (150, 150, 180), input_rect, 2)
            
            # Draw value or current input
            if setting == self.selected:
                value_text = self.font.render(self.input_text, True, BLACK)
                # Draw cursor
                cursor_text = self.font.render(self.input_text + "|", True, BLACK)
                cursor_width = cursor_text.get_width() - value_text.get_width()
                screen.blit(value_text, (input_rect.left + 5, input_rect.top + 5))
                # Blink cursor every half second
                if pygame.time.get_ticks() % 1000 < 500:
                    cursor_pos = input_rect.left + 5 + value_text.get_width()
                    pygame.draw.line(screen, BLACK, (cursor_pos, input_rect.top + 5), 
                                    (cursor_pos, input_rect.top + 25), 2)
            else:
                value_text = self.font.render(str(value), True, BLACK)
                screen.blit(value_text, (input_rect.left + 5, input_rect.top + 5))
            
            # Draw plus/minus buttons
            minus_rect = pygame.Rect(self.dialog_rect.left + 365, y, 30, 30)
            plus_rect = pygame.Rect(self.dialog_rect.left + 405, y, 30, 30)
            
            pygame.draw.rect(screen, (180, 180, 200), minus_rect)
            pygame.draw.rect(screen, (180, 180, 200), plus_rect)
            pygame.draw.rect(screen, (100, 100, 140), minus_rect, 2)
            pygame.draw.rect(screen, (100, 100, 140), plus_rect, 2)
            
            # Store button positions for click handling
            self.minus_buttons[setting] = minus_rect
            self.plus_buttons[setting] = plus_rect
            
            # Draw plus and minus symbols
            minus_text = self.font.render("-", True, BLACK)
            plus_text = self.font.render("+", True, BLACK)
            screen.blit(minus_text, (minus_rect.centerx - 5, minus_rect.centery - 11))
            screen.blit(plus_text, (plus_rect.centerx - 5, plus_rect.centery - 11))
            
            y += 60
            
        # Draw buttons
        ok_rect = pygame.Rect(self.dialog_rect.centerx - 110, self.dialog_rect.bottom - 40, 100, 30)
        cancel_rect = pygame.Rect(self.dialog_rect.centerx + 10, self.dialog_rect.bottom - 40, 100, 30)
        
        pygame.draw.rect(screen, (150, 200, 150), ok_rect)
        pygame.draw.rect(screen, (200, 150, 150), cancel_rect)
        
        pygame.draw.rect(screen, (50, 100, 50), ok_rect, 2)
        pygame.draw.rect(screen, (100, 50, 50), cancel_rect, 2)
        
        ok_text = self.font.render("Apply", True, BLACK)
        cancel_text = self.font.render("Cancel", True, BLACK)
        
        screen.blit(ok_text, (ok_rect.centerx - ok_text.get_width() // 2, ok_rect.centery - ok_text.get_height() // 2))
        screen.blit(cancel_text, (cancel_rect.centerx - cancel_text.get_width() // 2, cancel_rect.centery - cancel_text.get_height() // 2))
        
    def handle_click(self, pos):
        if not self.active:
            self.active = True
            return True
            
        if not self.dialog_rect.collidepoint(pos):
            return False
            
        # Check if OK button clicked
        ok_rect = pygame.Rect(self.dialog_rect.centerx - 110, self.dialog_rect.bottom - 40, 100, 30)
        if ok_rect.collidepoint(pos):
            # Apply settings but keep dialog open
            self.apply_settings()
            # Return False to indicate the dialog is still active
            return True
        
        # Check if Cancel button clicked
        cancel_rect = pygame.Rect(self.dialog_rect.centerx + 10, self.dialog_rect.bottom - 40, 100, 30)
        if cancel_rect.collidepoint(pos):
            # Reset settings to original values
            self.settings = {
                "SNOWFLAKE_COUNT": SNOWFLAKE_COUNT,
                "SNOW_RATE": SNOW_RATE,
                "SNOW_SPEED_MIN": SNOW_SPEED_MIN,
                "SNOW_SPEED_MAX": SNOW_SPEED_MAX,
                "WIND_FACTOR": WIND_FACTOR,
                "SNOWFLAKE_SIZE_MIN": SNOWFLAKE_SIZE_MIN,
                "SNOWFLAKE_SIZE_MAX": SNOWFLAKE_SIZE_MAX,
                "GROUND_HEIGHT": GROUND_HEIGHT
            }
            self.active = False
            return False
            
        # Check which setting was clicked
        y = self.dialog_rect.top + 50
        old_selected = self.selected
        for setting in self.settings:
            # Check if input field was clicked
            input_rect = pygame.Rect(self.dialog_rect.left + 250, y, 100, 30)
            if input_rect.collidepoint(pos):
                self.selected = setting
                self.input_text = str(self.settings[setting])
            
            # Check if plus/minus buttons were clicked
            if setting in self.minus_buttons and self.minus_buttons[setting].collidepoint(pos):
                self.adjust_setting(setting, -1)
            if setting in self.plus_buttons and self.plus_buttons[setting].collidepoint(pos):
                self.adjust_setting(setting, 1)
                
            y += 60
            
        # If we clicked elsewhere and had a selection, apply the input text
        if old_selected and old_selected != self.selected:
            self.apply_input_text(old_selected)
            
        return True

    def adjust_setting(self, setting, direction):
        """Adjust setting value up or down"""
        if setting in ["SNOWFLAKE_COUNT", "SNOW_RATE", "SNOWFLAKE_SIZE_MIN", "SNOWFLAKE_SIZE_MAX", "GROUND_HEIGHT"]:
            # Integer settings
            self.settings[setting] = max(1, int(self.settings[setting]) + direction)
        else:
            # Float settings
            self.settings[setting] = max(0.1, round(float(self.settings[setting]) + direction * 0.1, 1))
        
        # Update input text if this setting is currently selected
        if self.selected == setting:
            self.input_text = str(self.settings[setting])
        
    def apply_input_text(self, setting):
        """Apply the current input text to the selected setting"""
        if not self.input_text:
            return
            
        try:
            if setting in ["SNOWFLAKE_COUNT", "SNOW_RATE", "SNOWFLAKE_SIZE_MIN", "SNOWFLAKE_SIZE_MAX", "GROUND_HEIGHT"]:
                # Integer settings
                self.settings[setting] = max(1, int(float(self.input_text)))
            else:
                # Float settings
                self.settings[setting] = max(0.1, round(float(self.input_text), 1))
        except ValueError:
            # If conversion fails, revert to previous value
            self.input_text = str(self.settings[setting])
            
    def handle_keydown(self, event):
        if not self.active or self.selected is None:
            return
            
        if event.key == pygame.K_RETURN:
            self.apply_input_text(self.selected)
            self.selected = None
        elif event.key == pygame.K_ESCAPE:
            # Cancel editing
            self.input_text = str(self.settings[self.selected])
            self.selected = None
        elif event.key == pygame.K_TAB:
            # Move to next setting
            self.apply_input_text(self.selected)
            settings_list = list(self.settings.keys())
            current_idx = settings_list.index(self.selected)
            next_idx = (current_idx + 1) % len(settings_list)
            self.selected = settings_list[next_idx]
            self.input_text = str(self.settings[self.selected])
        elif event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
        elif event.unicode in '0123456789.' and (event.unicode != '.' or '.' not in self.input_text):
            # Only allow one decimal point
            self.input_text += event.unicode
            
    def get_values(self):
        return self.settings
        
    def apply_settings(self):
        """Apply current settings to the simulation"""
        global SNOWFLAKE_COUNT, SNOW_RATE, SNOW_SPEED_MIN, SNOW_SPEED_MAX, WIND_FACTOR
        global SNOWFLAKE_SIZE_MIN, SNOWFLAKE_SIZE_MAX, GROUND_HEIGHT, accumulated_snow, snowflakes
        
        # Make sure any selected input is applied first
        if self.selected:
            self.apply_input_text(self.selected)
        
        # Update global settings
        SNOWFLAKE_COUNT = int(self.settings["SNOWFLAKE_COUNT"])
        SNOW_RATE = int(self.settings["SNOW_RATE"])
        SNOW_SPEED_MIN = float(self.settings["SNOW_SPEED_MIN"])
        SNOW_SPEED_MAX = float(self.settings["SNOW_SPEED_MAX"])
        WIND_FACTOR = float(self.settings["WIND_FACTOR"])
        SNOWFLAKE_SIZE_MIN = int(self.settings["SNOWFLAKE_SIZE_MIN"])
        SNOWFLAKE_SIZE_MAX = int(self.settings["SNOWFLAKE_SIZE_MAX"])
        
        # Handle ground height change which requires recreating accumulated snow
        old_ground_height = GROUND_HEIGHT
        GROUND_HEIGHT = int(self.settings["GROUND_HEIGHT"])
        if GROUND_HEIGHT != old_ground_height:
            accumulated_snow = [[0 for _ in range(SCREEN_WIDTH)] for _ in range(GROUND_HEIGHT)]
        
        # Update existing snowflakes to use new settings
        for flake in snowflakes:
            flake.reset()
        
        # Adjust snowflake count if needed
        current_count = len(snowflakes)
        if current_count < SNOWFLAKE_COUNT:
            # Add more snowflakes if needed
            for _ in range(SNOWFLAKE_COUNT - current_count):
                snowflakes.append(Snowflake())
        elif current_count > SNOWFLAKE_COUNT:
            # Remove excess snowflakes if needed
            snowflakes[:] = snowflakes[:SNOWFLAKE_COUNT]

settings_dialog = SettingsDialog()

# Snow accumulation
global accumulated_snow
accumulated_snow = [[0 for _ in range(SCREEN_WIDTH)] for _ in range(GROUND_HEIGHT)]
max_accumulation = 80  # Maximum height of accumulated snow

class Snowflake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-50, 0)
        self.size = random.randint(SNOWFLAKE_SIZE_MIN, SNOWFLAKE_SIZE_MAX)
        self.speed = random.uniform(SNOW_SPEED_MIN, SNOW_SPEED_MAX)
        self.wind_effect = random.uniform(-WIND_FACTOR, WIND_FACTOR)
        
    def update(self):
        self.y += self.speed
        self.x += self.wind_effect
        
        # Wrap around screen edges
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
            
        # Check if the snowflake reaches the ground or accumulated snow
        ground_level = SCREEN_HEIGHT - GROUND_HEIGHT
        x_int = int(min(max(0, self.x), SCREEN_WIDTH - 1))
        
        if self.y >= ground_level - accumulated_snow[0][x_int]:
            # Accumulate snow where the snowflake landed
            col_index = int(min(self.x, SCREEN_WIDTH - 1))
            
            # Calculate accumulation amount - faster and more pronounced
            # Snowflakes in the middle third of screen accumulate more
            screen_middle = SCREEN_WIDTH / 2
            distance_from_middle = abs(col_index - screen_middle) / (SCREEN_WIDTH / 2)
            # More snow in the middle, less at edges (inverse of distance)
            middle_factor = 1.0 - (distance_from_middle * 0.6)
            
            # Snowflakes with larger sizes accumulate more
            size_factor = self.size / SNOWFLAKE_SIZE_MAX
            
            # Calculate how many units of snow to add (1-4 based on factors)
            snow_amount = max(1, int(2 * size_factor * middle_factor + random.random()))
            
            # Find available positions in this column and add snow
            empty_spaces = 0
            for i in range(GROUND_HEIGHT - 1):
                if accumulated_snow[i][col_index] == 0:
                    empty_spaces += 1
                    
            # Add snow up to calculated amount, if there's space
            snow_added = 0
            for i in range(GROUND_HEIGHT - 1):
                if accumulated_snow[i][col_index] == 0 and snow_added < snow_amount:
                    accumulated_snow[i][col_index] = 1
                    snow_added += 1
                    
            self.reset()
        elif self.y > SCREEN_HEIGHT:
            self.reset()

# Create initial snowflakes
snowflakes = [Snowflake() for _ in range(SNOWFLAKE_COUNT)]

# Clock for controlling frame rate
clock = pygame.time.Clock()

def draw_accumulated_snow():
    for y in range(GROUND_HEIGHT):
        for x in range(SCREEN_WIDTH):
            if accumulated_snow[y][x] == 1:
                # Add a subtle gradient effect - whiter at the top, slightly blue-tinted at the bottom
                # This creates a more natural snow pile look
                depth_factor = 1.0 - (y / GROUND_HEIGHT * 0.2)  # 0.8-1.0 range based on depth
                snow_color = (int(255 * depth_factor), int(255 * depth_factor), int(255 * 0.95 * depth_factor))
                
                # Make snow pixels slightly larger near the bottom for a more pronounced look
                pixel_size = 1
                if y > GROUND_HEIGHT * 0.7:  # Bottom 30%
                    pixel_size = 2
                
                pygame.draw.rect(screen, snow_color, (x, SCREEN_HEIGHT - GROUND_HEIGHT + y, pixel_size, pixel_size))

# Main game loop
running = True
frame_count = 0

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Toggle settings dialog with Ctrl+S
                settings_dialog.active = not settings_dialog.active
            # Handle key presses for settings dialog
            if settings_dialog.active:
                settings_dialog.handle_keydown(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle mouse clicks for settings dialog
            if event.button == 1:  # Left mouse button
                settings_dialog.handle_click(event.pos)
                # Note: We don't need to manually apply settings here anymore
                # as it's handled by the apply_settings method when the Apply button is clicked
    
    # Fill the screen with dark blue
    screen.fill(DARK_BLUE)
    
    # Add new snowflakes occasionally based on SNOW_RATE
    if frame_count % (60 // SNOW_RATE) == 0:
        for _ in range(SNOW_RATE):
            if len(snowflakes) < 2000:  # Cap total snowflakes
                snowflakes.append(Snowflake())
    
    # Draw snowflakes
    for flake in snowflakes:
        flake.update()
        pygame.draw.circle(screen, WHITE, (int(flake.x), int(flake.y)), flake.size)
    
    # Draw accumulated snow
    draw_accumulated_snow()
    
    # Draw settings dialog if active
    settings_dialog.draw(screen)
    
    # Draw settings instructions when dialog is not active
    if not settings_dialog.active:
        instructions_text = "Press CTRL+S to open settings"
        instructions_surf = pygame.font.Font(None, 24).render(instructions_text, True, (200, 200, 200))
        screen.blit(instructions_surf, (10, 10))
    
    # Update display
    pygame.display.flip()
    
    # Control frame rate
    clock.tick(60)
    frame_count += 1

# Quit pygame
pygame.quit()
sys.exit()