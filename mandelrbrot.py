import pygame
import random
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 1024, 768
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Mandelbrot Set")

# Mandelbrot parameters
max_iter = 256

def mandelbrot(c, max_iter):
    z = c
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return max_iter

def draw_mandelbrot():
    for x in range(width):
        for y in range(height):
            # Convert pixel coordinate to complex number
            c = complex(-2 + (x / width) * 3, -1.5 + (y / height) * 3)
            m = mandelbrot(c, max_iter)
            color = (m % 8 * 32, m % 16 * 16, m % 32 * 8)
            screen.set_at((x, y), color)

def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_mandelbrot()
        pygame.display.flip()

        # Randomize colors
        global max_iter
        max_iter = random.randint(100, 256)

    pygame.quit()

if __name__ == "__main__":
    main()