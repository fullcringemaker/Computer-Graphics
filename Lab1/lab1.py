import glfw
from OpenGL.GL import *
import math

# Инициализация переменных (как в исходном коде)
delta = 0.1
angle = 0
posx = 0
posy = 0
size = 0.5 # Размер фигуры

def main():
    if not glfw.init():
        return
    window = glfw.create_window(640, 640, "Lab1", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glClearColor(1.0, 1.0, 1.0, 1.0)  # Белый фон
    while not glfw.window_should_close(window):
        display(window)
    glfw.destroy_window(window)
    glfw.terminate()

def display(window):
    global angle
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    # Применение трансформаций
    glPushMatrix()
    glTranslatef(posx, posy, 0.0)  # Перемещение
    glRotatef(angle, 0.0, 0.0, 1.0)  # Поворот
    glScalef(size, size, 1.0)  # Масштабирование

    # Рисование восьмиугольника
    glColor3f(1.0, 0.5, 0.0)  # Оранжевый цвет
    glBegin(GL_POLYGON)
    for i in range(8):
        theta = 2.0 * math.pi * i / 8
        x = math.cos(theta)
        y = math.sin(theta)
        glVertex2f(x, y)
    glEnd()

    glPopMatrix()
    glfw.swap_buffers(window)
    glfw.poll_events()

def key_callback(window, key, scancode, action, mods):
    global posx, posy, angle, size
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_RIGHT:
            posx += 0.1
        elif key == glfw.KEY_LEFT:
            posx -= 0.1
        elif key == glfw.KEY_UP:
            posy += 0.1
        elif key == glfw.KEY_DOWN:
            posy -= 0.1
        elif key == glfw.KEY_SPACE:
            angle -= 10.0  # Поворот против часовой стрелки

def scroll_callback(window, xoffset, yoffset):
    global size
    if xoffset > 0:
        size -= yoffset / 10
    else:
        size += yoffset / 10  
        
if __name__ == "__main__":
    main()
