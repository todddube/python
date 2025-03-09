import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# Asteroid class
class Asteroid:
    def __init__(self):
        # Random position at screen edge
        if random.random() < 0.5:
            self.x = random.choice([0, WIDTH])
            self.y = random.randint(0, HEIGHT)
        else:
            self.x = random.randint(0, WIDTH)
            self.y = random.choice([0, HEIGHT])
        
        self.angle = random.randint(0, 360)
        self.speed = random.uniform(1, 3)
        self.size = random.randint(20, 50)
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
# Player ship
class Ship:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.speed = 0
        self.points = [(0, -20), (-10, 10), (10, 10)]
        
    def rotate(self, direction):
        self.angle += direction * 5
        
    def move(self):
        rad = math.radians(self.angle)
        self.x += self.speed * math.sin(rad)
        self.y -= self.speed * math.cos(rad)
        
        # Wrap around screen
        self.x %= WIDTH
        self.y %= HEIGHT
        
    def draw(self, surface):
        rotated_points = []
        for point in self.points:
            rad = math.radians(self.angle)
            x = point[0] * math.cos(rad) - point[1] * math.sin(rad)
            y = point[0] * math.sin(rad) + point[1] * math.cos(rad)
            rotated_points.append((self.x + x, self.y + y))
        pygame.draw.polygon(surface, WHITE, rotated_points, 2)

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

# Game loop
def main():
    clock = pygame.time.Clock()
    ship = Ship()
    missiles = []
    running = True
    
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
        
        # Draw
        screen.fill(BLACK)
        ship.draw(screen)
        for missile in missiles:
            missile.draw(screen)
        pygame.display.flip()
        
        # Control game speed
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()