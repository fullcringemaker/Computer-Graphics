import glfw
from OpenGL.GL import *
import numpy as np

# Глобальные переменные
window_size = (640, 640)
polygon_points = []
raster_buffer = None
filter_buffer = None
drawing_complete = False
show_filtered = False

def init_raster_buffer():
    global raster_buffer, window_size
    if raster_buffer is None or raster_buffer.shape != (window_size[1], window_size[0], 3):
        raster_buffer = np.zeros((window_size[1], window_size[0], 3), dtype=np.float32)

def init_filter_buffer():
    global filter_buffer, window_size
    if filter_buffer is None or filter_buffer.shape != (window_size[1], window_size[0], 3):
        filter_buffer = np.zeros((window_size[1], window_size[0], 3), dtype=np.float32)

def main():
    global window_size
    
    if not glfw.init():
        return
    
    window = glfw.create_window(window_size[0], window_size[1], "Lab3 - Rasterization", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_window_size_callback(window, window_size_callback)
    
    init_raster_buffer()
    init_filter_buffer()
    
    while not glfw.window_should_close(window):
        display(window)
    
    glfw.destroy_window(window)
    glfw.terminate()

def display(window):
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    
    # Отрисовка текущего состояния
    if len(polygon_points) > 1:
        draw_polygon_edges()
    
    # Отображаем либо исходный буфер, либо отфильтрованный
    if show_filtered and drawing_complete:
        apply_filter()
        draw_buffer(filter_buffer)
    elif drawing_complete:
        draw_buffer(raster_buffer)
    
    glfw.swap_buffers(window)
    glfw.poll_events()

def draw_buffer(buffer):
    glDrawPixels(window_size[0], window_size[1], GL_RGB, GL_FLOAT, buffer)

def draw_polygon_edges():
    glColor3f(0.0, 0.0, 0.0)
    glBegin(GL_LINE_LOOP)
    for point in polygon_points:
        glVertex2f(point[0], point[1])
    glEnd()

def rasterize_polygon():
    if len(polygon_points) < 3:
        return
    
    # Реализация алгоритма построчного заполнения с затравкой
    # 1. Находим границы полигона
    min_y = min(p[1] for p in polygon_points)
    max_y = max(p[1] for p in polygon_points)
    
    # 2. Для каждой строки сканирования
    for y in range(int(min_y), int(max_y) + 1):
        intersections = []
        
        # Находим пересечения с ребрами
        for i in range(len(polygon_points)):
            p1 = polygon_points[i]
            p2 = polygon_points[(i + 1) % len(polygon_points)]
            
            if p1[1] > p2[1]:
                p1, p2 = p2, p1
            
            if p1[1] <= y < p2[1] or (p1[1] == p2[1] == y):
                if p1[1] == p2[1]:  # Горизонтальное ребро
                    continue
                
                # Вычисляем x пересечения
                x = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1])
                intersections.append(x)
        
        # Сортируем пересечения
        intersections.sort()
        
        # Заполняем между парами пересечений
        for i in range(0, len(intersections), 2):
            if i + 1 >= len(intersections):
                break
            
            x_start = int(intersections[i])
            x_end = int(intersections[i + 1])
            
            for x in range(x_start, x_end + 1):
                if 0 <= x < window_size[0] and 0 <= y < window_size[1]:
                    raster_buffer[y, x] = [0.0, 0.0, 1.0]  # Синий цвет для заполнения

def apply_filter():
    global filter_buffer, raster_buffer, window_size
    
    # Инициализируем буфер фильтра
    filter_buffer.fill(0.0)
    
    # Размер области усреднения
    N = 3
    half_N = N // 2
    
    for y in range(half_N, window_size[1] - half_N):
        for x in range(half_N, window_size[0] - half_N):
            # Собираем пиксели в области NxN
            total = np.zeros(3, dtype=np.float32)
            count = 0
            
            for dy in range(-half_N, half_N + 1):
                for dx in range(-half_N, half_N + 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < window_size[1] and 0 <= nx < window_size[0]:
                        total += raster_buffer[ny, nx]
                        count += 1
            
            # Усредняем
            if count > 0:
                filter_buffer[y, x] = total / count

def bresenham_line(x0, y0, x1, y1):
    # Вещественный алгоритм Брезенхема
    points = []
    
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1
    
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    
    points.append((x, y))
    return points

def mouse_button_callback(window, button, action, mods):
    global polygon_points, drawing_complete
    
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        x, y = glfw.get_cursor_pos(window)
        y = window_size[1] - y  # Инвертируем Y
        
        if not drawing_complete:
            polygon_points.append((x, y))
    
    elif button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.PRESS:
        if len(polygon_points) >= 3 and not drawing_complete:
            # Замыкаем полигон
            rasterize_polygon()
            drawing_complete = True

def key_callback(window, key, scancode, action, mods):
    global polygon_points, raster_buffer, drawing_complete, show_filtered
    
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            # Очистка экрана
            polygon_points = []
            raster_buffer.fill(0.0)
            filter_buffer.fill(0.0)
            drawing_complete = False
            show_filtered = False
        
        elif key == glfw.KEY_F:
            # Переключение отображения фильтра
            if drawing_complete:
                show_filtered = not show_filtered
        
        elif key == glfw.KEY_ENTER and len(polygon_points) >= 3 and not drawing_complete:
            # Завершение ввода и растеризация
            rasterize_polygon()
            drawing_complete = True

def window_size_callback(window, width, height):
    global window_size
    window_size = (width, height)
    glViewport(0, 0, width, height)
    init_raster_buffer()
    init_filter_buffer()

if __name__ == "__main__":
    main()
