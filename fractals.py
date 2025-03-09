import turtle
import random

def draw_fractal(t, length, depth):
    if depth == 0:
        return
    t.forward(length)
    t.left(45)
    draw_fractal(t, length / 2, depth - 1)
    t.right(90)
    draw_fractal(t, length / 2, depth - 1)
    t.left(45)
    t.backward(length)

def random_color():
    return (random.random(), random.random(), random.random())

def main():
    screen = turtle.Screen()
    screen.colormode(1.0)  # Use RGB colors in the range [0, 1]
    t = turtle.Turtle()
    t.speed(0)

    for _ in range(10):
        t.color(random_color())
        draw_fractal(t, 100, 4)
        t.right(36)

    screen.mainloop()

if __name__ == "__main__":
    main()