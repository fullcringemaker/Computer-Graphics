import glfw
from OpenGL.GL import *
import numpy as np

# Глобальные переменные
points = []  # Точки многоугольника
buffer_size = (640, 640)  # Начальный размер буфера
draw_buffer = None  # Буфер для растеризации

def init_draw_buffer(width, height):
    """Инициализация буфера для растеризации"""
    global draw_buffer
    draw_buffer = np.zeros((height, width, 3), dtype=np.float32)
    clear_draw_buffer(silent=True)

def clear_draw_buffer(silent=False):
    """Очистка буфера для растеризации"""
    global draw_buffer
    if draw_buffer is not None:
        draw_buffer.fill(1.0)  # Белый цвет
    if not silent:
        print("Холст очищен")

def resize_draw_buffer(width, height):
    """Изменение размера буфера"""
    global draw_buffer, buffer_size
    old_buffer = draw_buffer
    init_draw_buffer(width, height)
    if old_buffer is not None:
        h = min(height, old_buffer.shape[0])
        w = min(width, old_buffer.shape[1])
        draw_buffer[:h, :w] = old_buffer[:h, :w]
    buffer_size = (width, height)

def set_pixel(x, y, color=(0.0, 0.0, 0.0)):
    """Установка пикселя в буфере"""
    global draw_buffer
    if 0 <= x < buffer_size[0] and 0 <= y < buffer_size[1]:
        draw_buffer[y, x] = color

def get_pixel(x, y):
    """Получение цвета пикселя из буфера"""
    global draw_buffer
    if 0 <= x < buffer_size[0] and 0 <= y < buffer_size[1]:
        return draw_buffer[y, x]
    return (1.0, 1.0, 1.0)

def bresenham_line(x0, y0, x1, y1):
    """Алгоритм Брезенхема для растеризации отрезка"""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1
    
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            set_pixel(x, y)
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            set_pixel(x, y)
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    set_pixel(x, y)

def boundary_fill(x, y, boundary_color, fill_color):
    """Алгоритм построчного заполнения с затравкой"""
    stack = [(x, y)]
    while stack:
        x, y = stack.pop()
        if (get_pixel(x, y) != boundary_color).any() and (get_pixel(x, y) != fill_color).any():
            left = x
            while left >= 0 and (get_pixel(left, y) != boundary_color).any() and (get_pixel(left, y) != fill_color).any():
                left -= 1
            left += 1
            
            right = x
            while right < buffer_size[0] and (get_pixel(right, y) != boundary_color).any() and (get_pixel(right, y) != fill_color).any():
                right += 1
            right -= 1
            
            for i in range(left, right + 1):
                set_pixel(i, y, fill_color)
            
            for ny in [y - 1, y + 1]:
                if 0 <= ny < buffer_size[1]:
                    add_to_stack = False
                    for i in range(left, right + 1):
                        if (get_pixel(i, ny) != boundary_color).any() and (get_pixel(i, ny) != fill_color).any():
                            if not add_to_stack:
                                stack.append((i, ny))
                                add_to_stack = True
                        else:
                            add_to_stack = False

def apply_box_filter():
    """Применение фильтра усреднения 3x3"""
    global draw_buffer
    if draw_buffer is None:
        return
    
    new_buffer = np.copy(draw_buffer)
    height, width = draw_buffer.shape[0], draw_buffer.shape[1]
    
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            neighbors = [
                draw_buffer[y-1][x-1], draw_buffer[y-1][x], draw_buffer[y-1][x+1],
                draw_buffer[y][x-1],   draw_buffer[y][x],   draw_buffer[y][x+1],
                draw_buffer[y+1][x-1], draw_buffer[y+1][x], draw_buffer[y+1][x+1]
            ]
            avg_color = np.mean(neighbors, axis=0)
            new_buffer[y][x] = avg_color
    
    draw_buffer = new_buffer
    print("Применена постфильтрация")

def draw_polygon():
    """Отрисовка и заполнение многоугольника"""
    if len(points) < 2:
        return
    
    # Отрисовка границ
    for i in range(len(points) - 1):
        bresenham_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
    
    if len(points) >= 3:
        bresenham_line(points[-1][0], points[-1][1], points[0][0], points[0][1])
        
        # Автоматическая заливка
        cx = sum(p[0] for p in points) // len(points)
        cy = sum(p[1] for p in points) // len(points)
        boundary_fill(cx, cy, (0.0, 0.0, 0.0), (0.5, 0.5, 0.5))

def display(window):
    """Основная функция отрисовки"""
    glClear(GL_COLOR_BUFFER_BIT)
    
    if draw_buffer is not None:
        glDrawPixels(buffer_size[0], buffer_size[1], GL_RGB, GL_FLOAT, draw_buffer)
    
    glfw.swap_buffers(window)
    glfw.poll_events()

def key_callback(window, key, scancode, action, mods):
    """Обработка клавиш"""
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            points.clear()
            clear_draw_buffer()
        elif key == glfw.KEY_P:
            apply_box_filter()

def mouse_button_callback(window, button, action, mods):
    """Обработка кликов мыши"""
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        xpos, ypos = glfw.get_cursor_pos(window)
        width, height = glfw.get_window_size(window)
        x = int(xpos * buffer_size[0] / width)
        y = buffer_size[1] - int(ypos * buffer_size[1] / height) - 1
        
        points.append((x, y))
        print(f"Добавлена точка: ({x}, {y})")
        
        if len(points) >= 2:
            clear_draw_buffer(silent=True)
            draw_polygon()

def window_size_callback(window, width, height):
    """Обработка изменения размера окна"""
    glViewport(0, 0, width, height)
    new_width = max(1, int(buffer_size[0] * width / 640))
    new_height = max(1, int(buffer_size[1] * height / 640))
    resize_draw_buffer(new_width, new_height)

def main():
    if not glfw.init():
        return
    
    window = glfw.create_window(640, 640, "Lab3 - Rasterization", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_window_size_callback(window, window_size_callback)
    
    init_draw_buffer(640, 640)
    
    while not glfw.window_should_close(window):
        display(window)
    
    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
