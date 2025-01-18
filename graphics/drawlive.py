import pygame
import sys

# Initialize pygame
pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode((800, 600))

# Run until the user asks to quit
running = True
while running:
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with white
    screen.fill((255, 255, 255))
    # Draw complex moire pattern
    for i in range(0, 800, 10):
        pygame.draw.line(screen, (0, 0, 0), (i, 0), (800 - i, 600))
        pygame.draw.line(screen, (0, 0, 0), (0, i), (800, 600 - i))
        pygame.draw.line(screen, (0, 0, 0), (i, 600), (800 - i, 0))
        pygame.draw.line(screen, (0, 0, 0), (0, 600 - i), (800, i))

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()
sys.exit()