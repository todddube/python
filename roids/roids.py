import pygame
import math
import random
import time

# Game Constants
WIDTH = 800
HEIGHT = 600
PLAYER_LIVES = 3  # Default number of lives

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialize Font
pygame.font.init()
FONT = pygame.font.SysFont('Arial', 30)

# Asteroid class
class Asteroid:
    def __init__(self, x=None, y=None, size=None):
        # Random position at screen edge if not specified
        if x is None or y is None:
            if random.random() < 0.5:
                self.x = random.choice([0, WIDTH])
                self.y = random.randint(0, HEIGHT)
            else:
                self.x = random.randint(0, WIDTH)
                self.y = random.choice([0, HEIGHT])
        else:
            self.x = x
            self.y = y
        
        self.angle = random.randint(0, 360)
        self.speed = random.uniform(1, 3)
        self.size = size if size else random.randint(20, 50)
        self.points = []
        
        # Create irregular polygon
        for i in range(8):
            angle = i * 45 + random.uniform(-10, 10)
            rad = math.radians(angle)
            dist = self.size + random.uniform(-5, 5)
            self.points.append((dist * math.cos(rad), dist * math.sin(rad)))
        
    def move(self):
        rad = math.radians(self.angle)
        self.x += self.speed * math.sin(rad)
        self.y -= self.speed * math.cos(rad)
        self.x %= WIDTH
        self.y %= HEIGHT
        
    def draw(self, surface):
        points = [(self.x + x, self.y + y) for x, y in self.points]
        pygame.draw.polygon(surface, WHITE, points, 2)

    def get_rect(self):
        points = [(self.x + x, self.y + y) for x, y in self.points]
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

# Player ship
class Ship:
    def __init__(self):
        self.reset_position()
        self.points = [(0, -20), (-10, 10), (10, 10)]
        self.exploding = False
        self.explosion_particles = []
        self.explosion_start = 0
        self.flame_colors = [(255,0,0), (255,255,0), (0,255,0)]  # Red, Yellow, Green
        
    def reset_position(self):
        """Reset ship to center of screen"""
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.speed = 0
        
    def respawn(self):
        """Reset ship after explosion"""
        self.exploding = False
        self.explosion_particles = []
        self.reset_position()
        
    def rotate(self, direction):
        self.angle += direction * 5
        
    def move(self):
        rad = math.radians(self.angle)
        self.x += self.speed * math.sin(rad)
        self.y -= self.speed * math.cos(rad)
        
        # Wrap around screen
        self.x %= WIDTH
        self.y %= HEIGHT
        
    def start_explosion(self):
        if not self.exploding:
            self.exploding = True
            self.explosion_start = time.time()
            # Create explosion particles from ship points
            for _ in range(20):
                particle = Particle(
                    self.x, 
                    self.y,
                    random.uniform(0, 360),
                    random.uniform(1, 5)
                )
                self.explosion_particles.append(particle)
    
    def draw(self, surface):
        if self.exploding:
            # Draw explosion particles
            for particle in self.explosion_particles:
                particle.move()
                particle.draw(surface)
        else:
            # Draw ship
            rotated_points = []
            for point in self.points:
                rad = math.radians(self.angle)
                x = point[0] * math.cos(rad) - point[1] * math.sin(rad)
                y = point[0] * math.sin(rad) + point[1] * math.cos(rad)
                rotated_points.append((self.x + x, self.y + y))
            pygame.draw.polygon(surface, WHITE, rotated_points, 2)
            
            # Draw flame when moving
            if self.speed > 0:
                rad = math.radians(self.angle)
                for i, color in enumerate(self.flame_colors):
                    flame_length = random.randint(5, 15) * (1 - i/3)  # Decreasing flame size
                    flame_x = self.x - flame_length * math.sin(rad)
                    flame_y = self.y + flame_length * math.cos(rad)
                    pygame.draw.line(surface, color, 
                                   (self.x - 5 * math.sin(rad), 
                                    self.y + 5 * math.cos(rad)),
                                   (flame_x, flame_y), 
                                   3-i)  # Decreasing line width

    def get_rect(self):
        rotated_points = []
        for point in self.points:
            rad = math.radians(self.angle)
            x = point[0] * math.cos(rad) - point[1] * math.sin(rad)
            y = point[0] * math.sin(rad) + point[1] * math.cos(rad)
            rotated_points.append((self.x + x, self.y + y))
        min_x = min(p[0] for p in rotated_points)
        max_x = max(p[0] for p in rotated_points)
        min_y = min(p[1] for p in rotated_points)
        max_y = max(p[1] for p in rotated_points)
        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

# Missile class
class Missile:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        
    def move(self):
        rad = math.radians(self.angle)
        self.x += self.speed * math.sin(rad)
        self.y -= self.speed * math.cos(rad)
        
    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 2)

# Particle class
class Particle:
    def __init__(self, x, y, angle, speed):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.lifetime = 255  # Fade out counter
        
    def move(self):
        rad = math.radians(self.angle)
        self.x += self.speed * math.sin(rad)
        self.y -= self.speed * math.cos(rad)
        self.lifetime -= 3
        
    def draw(self, surface):
        if self.lifetime > 0:
            color = (255, self.lifetime, self.lifetime)
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 2)

def show_game_over(screen, score):
    """Display game over screen with final score"""
    screen.fill(BLACK)
    
    game_over_text = FONT.render('GAME OVER', True, WHITE)
    score_text = FONT.render(f'Final Score: {score}', True, WHITE)
    restart_text = FONT.render('Press SPACE to play again', True, WHITE)
    
    screen.blit(game_over_text, 
                (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 60))
    screen.blit(score_text, 
                (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    screen.blit(restart_text, 
                (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
    return False

def main():
    while True:
        # Initialize game state
        clock = pygame.time.Clock()
        ship = Ship()
        missiles = []
        asteroids = [Asteroid() for _ in range(5)]
        running = True
        score = 0
        lives = PLAYER_LIVES
        
        # Main game loop
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        missiles.append(Missile(ship.x, ship.y, ship.angle))
            
            # Handle continuous key presses
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                ship.rotate(-1)
            if keys[pygame.K_RIGHT]:
                ship.rotate(1)
            if keys[pygame.K_UP]:
                ship.speed = min(ship.speed + 0.1, 5)
            if keys[pygame.K_DOWN]:
                ship.speed = max(ship.speed - 0.1, 0)
                
            # Update
            ship.move()
            for missile in missiles[:]:
                missile.move()
                if (missile.x < 0 or missile.x > WIDTH or 
                    missile.y < 0 or missile.y > HEIGHT):
                    missiles.remove(missile)
                    continue
                    
                # Check missile collisions with asteroids
                for asteroid in asteroids[:]:
                    if asteroid.get_rect().collidepoint(missile.x, missile.y):
                        missiles.remove(missile)
                        asteroids.remove(asteroid)
                        score += 10  # Add 10 points for hitting asteroid
                        
                        # Create smaller asteroids if size permits
                        if asteroid.size > 10:
                            for _ in range(3):
                                new_size = asteroid.size // 2
                                new_asteroid = Asteroid(
                                    x=asteroid.x + random.uniform(-20, 20),
                                    y=asteroid.y + random.uniform(-20, 20),
                                    size=new_size
                                )
                                asteroids.append(new_asteroid)
                        break
            for asteroid in asteroids:
                asteroid.move()
                if ship.get_rect().colliderect(asteroid.get_rect()) and not ship.exploding:
                    ship.start_explosion()
                    
            # Update explosion state and handle lives
            if ship.exploding:
                if time.time() - ship.explosion_start > 2:  # Reduced to 2 seconds
                    lives -= 1
                    if lives > 0:
                        ship.respawn()
                        # Give player brief invulnerability by clearing nearby asteroids
                        asteroids = [ast for ast in asteroids 
                                   if math.hypot(ast.x - ship.x, ast.y - ship.y) > 100]
                    else:
                        running = False
            
            # Draw
            screen.fill(BLACK)
            
            # Draw score and lives at top of screen
            score_text = FONT.render(f'Score: {score}', True, WHITE)
            lives_text = FONT.render(f'Lives: {lives}', True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(lives_text, (WIDTH - 120, 10))
            
            ship.draw(screen)
            for missile in missiles:
                missile.draw(screen)
            for asteroid in asteroids:
                asteroid.draw(screen)
            pygame.display.flip()
            
            # Control game speed
            clock.tick(60)
        
        # Show game over screen and handle restart
        if not show_game_over(screen, score):
            break
            
    pygame.quit()

if __name__ == "__main__":
    main()