import glfw
from OpenGL.GL import *
import math

# Глобальные переменные
points = []  # Точки многоугольника
polygon_complete = False
buffer_width = 640
buffer_height = 640
pixel_buffer = None
filter_buffer = None
show_filtered = False
show_original = True

def init_pixel_buffer(width, height):
    global pixel_buffer, filter_buffer, buffer_width, buffer_height
    buffer_width = width
    buffer_height = height
    pixel_buffer = [ [0 for _ in range(height)] for _ in range(width) ]
    filter_buffer = [ [0 for _ in range(height)] for _ in range(width) ]

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

def fill_polygon():
    global points, pixel_buffer
    
    if len(points) < 3:
        return
    
    # Находим min и max Y
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    # Для каждой строки сканирования
    for y in range(min_y, max_y + 1):
        intersections = []
        
        # Находим пересечения со всеми ребрами
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            
            # Проверяем, пересекает ли ребро текущую строку сканирования
            if (p1[1] <= y < p2[1]) or (p2[1] <= y < p1[1]):
                # Вычисляем X пересечения
                if p1[1] != p2[1]:
                    x = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1])
                    intersections.append(x)
        
        # Сортируем точки пересечения
        intersections.sort()
        
        # Заполняем пиксели между парами пересечений
        for i in range(0, len(intersections), 2):
            if i + 1 < len(intersections):
                x_start = int(intersections[i])
                x_end = int(intersections[i + 1])
                for x in range(x_start, x_end + 1):
                    draw_pixel(x, y)

def apply_filter():
    global pixel_buffer, filter_buffer
    
    # Размер фильтра
    N = 3
    half = N // 2
    
    for y in range(half, buffer_height - half):
        for x in range(half, buffer_width - half):
            total = 0
            count = 0
            
            # Суммируем значения в области NxN
            for fy in range(-half, half + 1):
                for fx in range(-half, half + 1):
                    nx, ny = x + fx, y + fy
                    if 0 <= nx < buffer_width and 0 <= ny < buffer_height:
                        total += pixel_buffer[nx][ny]
                        count += 1
            
            # Усредняем
            if count > 0:
                filter_buffer[x][y] = 1 if total / count > 0.5 else 0

def display(window):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    # Отрисовка буфера
    glBegin(GL_POINTS)
    if show_filtered:
        # Отрисовка отфильтрованного изображения
        for x in range(buffer_width):
            for y in range(buffer_height):
                if filter_buffer[x][y]:
                    glVertex2f(x / buffer_width * 2 - 1, 1 - y / buffer_height * 2)
    elif show_original:
        # Отрисовка оригинального изображения
        for x in range(buffer_width):
            for y in range(buffer_height):
                if pixel_buffer[x][y]:
                    glVertex2f(x / buffer_width * 2 - 1, 1 - y / buffer_height * 2)
    glEnd()
    
    glfw.swap_buffers(window)
    glfw.poll_events()

def mouse_button_callback(window, button, action, mods):
    global points, polygon_complete
    
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        x, y = glfw.get_cursor_pos(window)
        width, height = glfw.get_window_size(window)
        
        # Масштабируем координаты в размер буфера
        x = int(x / width * buffer_width)
        y = int(y / height * buffer_height)
        
        if polygon_complete:
            # Если многоугольник уже завершен, начинаем новый
            points = []
            clear_buffers()
            polygon_complete = False
        
        points.append((x, y))
        print(f"Added point: ({x}, {y})")
        
        # Отрисовываем линии между точками
        if len(points) > 1:
            draw_line(points[-2][0], points[-2][1], points[-1][0], points[-1][1])

def key_callback(window, key, scancode, action, mods):
    global polygon_complete, show_filtered, show_original
    
    if action == glfw.PRESS:
        if key == glfw.KEY_ENTER and len(points) >= 3 and not polygon_complete:
            # Завершаем многоугольник
            draw_line(points[-1][0], points[-1][1], points[0][0], points[0][1])
            fill_polygon()
            polygon_complete = True
            print("Polygon completed and filled")
        
        elif key == glfw.KEY_F:
            # Применяем фильтр
            if polygon_complete:
                apply_filter()
                show_filtered = True
                show_original = False
                print("Filter applied")
        
        elif key == glfw.KEY_O:
            # Показываем оригинал
            show_original = True
            show_filtered = False
            print("Showing original")
        
        elif key == glfw.KEY_C:
            # Очищаем
            points.clear()
            clear_buffers()
            polygon_complete = False
            show_original = True
            show_filtered = False
            print("Canvas cleared")

def window_size_callback(window, width, height):
    glViewport(0, 0, width, height)
    init_pixel_buffer(width, height)

def main():
    if not glfw.init():
        return
    
    window = glfw.create_window(640, 640, "Polygon Rasterization", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_window_size_callback(window, window_size_callback)
    
    # Инициализация буфера
    width, height = glfw.get_window_size(window)
    init_pixel_buffer(width, height)
    
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glPointSize(1.0)
    
    while not glfw.window_should_close(window):
        display(window)
    
    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
