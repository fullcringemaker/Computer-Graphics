import glfw
from OpenGL.GL import *
import math
from collections import deque

# Глобальные переменные
points = []
buffer_width = 640
buffer_height = 640
pixel_buffer = None
filter_buffer = None
show_filtered = False
show_original = True
filter_size = 3
filter_threshold = 0.3
window_width = 640
window_height = 640

def init_pixel_buffer(width, height):
    global pixel_buffer, filter_buffer, buffer_width, buffer_height
    buffer_width = width
    buffer_height = height
    new_pixel_buffer = [[0 for _ in range(height)] for _ in range(width)]
    new_filter_buffer = [[0 for _ in range(height)] for _ in range(width)]
    
    if pixel_buffer is not None:
        for x in range(min(width, len(pixel_buffer))):
            for y in range(min(height, len(pixel_buffer[0]))):
                new_pixel_buffer[x][y] = pixel_buffer[x][y]
                new_filter_buffer[x][y] = filter_buffer[x][y]
    
    pixel_buffer = new_pixel_buffer
    filter_buffer = new_filter_buffer

def clear_buffers():
    global pixel_buffer, filter_buffer
    for x in range(buffer_width):
        for y in range(buffer_height):
            pixel_buffer[x][y] = 0
            filter_buffer[x][y] = 0

def draw_pixel(x, y, color=1):
    if 0 <= x < buffer_width and 0 <= y < buffer_height:
        pixel_buffer[x][y] = color

def draw_line(x1, y1, x2, y2):
    # Вещественный алгоритм Брезенхема
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    x, y = x1, y1
    sx = -1 if x1 > x2 else 1
    sy = -1 if y1 > y2 else 1
    
    if dx > dy:
        err = dx / 2.0
        while x != x2:
            draw_pixel(x, y)
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y2:
            draw_pixel(x, y)
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    draw_pixel(x, y)

def boundary_fill(x, y, fill_color=1, boundary_color=1):
    """Алгоритм заполнения с затравкой (4-связная область)"""
    if x < 0 or x >= buffer_width or y < 0 or y >= buffer_height:
        return
    
    # Используем очередь вместо рекурсии
    queue = deque()
    queue.append((x, y))
    
    while queue:
        x, y = queue.popleft()
        
        if pixel_buffer[x][y] != fill_color and pixel_buffer[x][y] != boundary_color:
            draw_pixel(x, y, fill_color)
            # Добавляем 4-связные соседние пиксели
            queue.append((x + 1, y))
            queue.append((x - 1, y))
            queue.append((x, y + 1))
            queue.append((x, y - 1))

def fill_polygon():
    """Заполнение многоугольника с использованием алгоритма с затравкой"""
    if len(points) < 3:
        return
    
    # 1. Находим внутреннюю точку для затравки
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    seed_x = (min_x + max_x) // 2
    seed_y = (min_y + max_y) // 2
    
    # 2. Проверяем, что точка действительно внутри
    # (упрощенная проверка - в реальном коде нужен алгоритм точки в многоугольнике)
    if seed_x <= min_x or seed_x >= max_x or seed_y <= min_y or seed_y >= max_y:
        seed_x = min_x + 1
        seed_y = min_y + 1
    
    # 3. Применяем алгоритм с затравкой
    boundary_fill(seed_x, seed_y)

def apply_filter():
    half = filter_size // 2
    for y in range(half, buffer_height - half):
        for x in range(half, buffer_width - half):
            total = 0
            count = 0
            for fy in range(-half, half + 1):
                for fx in range(-half, half + 1):
                    nx, ny = x + fx, y + fy
                    if 0 <= nx < buffer_width and 0 <= ny < buffer_height:
                        total += pixel_buffer[nx][ny]
                        count += 1
            filter_buffer[x][y] = 1 if total / count > filter_threshold else 0

def display(window):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    glBegin(GL_POINTS)
    if show_filtered:
        for x in range(buffer_width):
            for y in range(buffer_height):
                if filter_buffer[x][y]:
                    glColor3f(0.0, 1.0, 0.0)
                    glVertex2f(x / buffer_width * 2 - 1, 1 - y / buffer_height * 2)
    else:
        for x in range(buffer_width):
            for y in range(buffer_height):
                if pixel_buffer[x][y]:
                    if len(points) > 0 and x == points[0][0] and y == points[0][1]:
                        glColor3f(1.0, 0.0, 0.0)
                    else:
                        glColor3f(1.0, 1.0, 1.0)
                    glVertex2f(x / buffer_width * 2 - 1, 1 - y / buffer_height * 2)
    glEnd()
    
    glfw.swap_buffers(window)
    glfw.poll_events()

def mouse_button_callback(window, button, action, mods):
    global points, show_filtered, show_original
    
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        show_original = True
        show_filtered = False
        
        x, y = glfw.get_cursor_pos(window)
        width, height = glfw.get_window_size(window)
        x = int(x / width * buffer_width)
        y = int(y / height * buffer_height)
        
        print(f"Added point: ({x}, {y})")
        
        if len(points) > 0:
            draw_line(points[-1][0], points[-1][1], x, y)
        
        points.append((x, y))
        
        if len(points) >= 3:
            clear_buffers()
            # Рисуем границы
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                draw_line(p1[0], p1[1], p2[0], p2[1])
            # Заливаем
            fill_polygon()

def key_callback(window, key, scancode, action, mods):
    global points, show_filtered, show_original
    
    if action == glfw.PRESS:
        if key == glfw.KEY_F and len(points) >= 3:
            apply_filter()
            show_filtered = True
            show_original = False
            print("Filter applied (3x3)")
        elif key == glfw.KEY_O:
            show_original = True
            show_filtered = False
            print("Showing original")
        elif key == glfw.KEY_C:
            points.clear()
            clear_buffers()
            show_original = True
            show_filtered = False
            print("Canvas cleared")

def window_size_callback(window, width, height):
    global window_width, window_height
    window_width = width
    window_height = height
    glViewport(0, 0, width, height)
    init_pixel_buffer(width, height)
    
    if len(points) >= 3:
        clear_buffers()
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            draw_line(p1[0], p1[1], p2[0], p2[1])
        fill_polygon()

def main():
    global window_width, window_height
    
    if not glfw.init():
        return
    
    window = glfw.create_window(window_width, window_height, "Polygon Rasterization with Seed Fill", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_window_size_callback(window, window_size_callback)
    
    init_pixel_buffer(window_width, window_height)
    
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glPointSize(1.0)
    
    while not glfw.window_should_close(window):
        display(window)
    
    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
