import numpy as np
import matplotlib.pyplot as plt

def mandelbrot(c, max_iter=100):
    """Checks if a complex number c belongs to the Mandelbrot set."""
    z = 0
    n = 0
    while abs(z) <= 2 and n < max_iter:
        z = z*z + c
        n += 1
    return n

def create_mandelbrot_set(width, height, x_min, x_max, y_min, y_max, max_iter=100):
    """Creates a Mandelbrot set image."""
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    image = np.zeros((height, width))

    for i in range(height):
        for j in range(width):
            c = complex(x[j], y[i])
            image[i, j] = mandelbrot(c, max_iter)

    return image

# Set parameters
width, height = 800, 600
x_min, x_max = -2.0, 1.0
y_min, y_max = -1.5, 1.5
max_iter = 100

# Generate and plot the Mandelbrot set
image = create_mandelbrot_set(width, height, x_min, x_max, y_min, y_max, max_iter)

plt.imshow(image, extent=(x_min, x_max, y_min, y_max), cmap='hot')
plt.colorbar()
plt.title("Mandelbrot Set")
plt.show()