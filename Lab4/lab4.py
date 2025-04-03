import glfw
from OpenGL.GL import *

points = []  # Точки многоугольника
original_buffer_size = (640, 640)  # Фиксированный размер буфера с изображением
current_window_size = (640, 640)    # Текущий размер окна
draw_buffer = None  # Буфер для растеризации (будет списком байт)

def init_draw_buffer(width, height):
    """Инициализация буфера для растеризации"""
    global draw_buffer, original_buffer_size
    original_buffer_size = (width, height)
    # Создаем буфер как массив байт (width * height * 3 компоненты RGB)
    draw_buffer = bytearray([255] * (width * height * 3))  # Белый фон

def clear_draw_buffer(silent=False):
    """Очистка буфера для растеризации"""
    global draw_buffer
    if draw_buffer is not None:
        draw_buffer = bytearray([255] * (original_buffer_size[0] * original_buffer_size[1] * 3))
    if not silent:
        print("Холст очищен")

def set_pixel(x, y, color=(0.0, 0.0, 0.0)):
    """Установка пикселя в буфере"""
    global draw_buffer, original_buffer_size
    if 0 <= x < original_buffer_size[0] and 0 <= y < original_buffer_size[1]:
        index = (y * original_buffer_size[0] + x) * 3
        # Преобразуем цвет из [0.0, 1.0] в [0, 255]
        r = int(color[0] * 255)
        g = int(color[1] * 255)
        b = int(color[2] * 255)
        draw_buffer[index] = r
        draw_buffer[index+1] = g
        draw_buffer[index+2] = b

def get_pixel(x, y):
    """Получение цвета пикселя из буфера"""
    global draw_buffer, original_buffer_size
    if 0 <= x < original_buffer_size[0] and 0 <= y < original_buffer_size[1]:
        index = (y * original_buffer_size[0] + x) * 3
        r = draw_buffer[index] / 255.0
        g = draw_buffer[index+1] / 255.0
        b = draw_buffer[index+2] / 255.0
        return (r, g, b)
    return (1.0, 1.0, 1.0)  # Белый цвет для пикселей вне буфера

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
    boundary_rgb = tuple(int(c * 255) for c in boundary_color)
    fill_rgb = tuple(int(c * 255) for c in fill_color)
    
    while stack:
        x, y = stack.pop()
        if (x < 0 or x >= original_buffer_size[0] or 
            y < 0 or y >= original_buffer_size[1]):
            continue
            
        index = (y * original_buffer_size[0] + x) * 3
        pixel = (draw_buffer[index], draw_buffer[index+1], draw_buffer[index+2])
        
        if pixel != boundary_rgb and pixel != fill_rgb:
            # Находим левую границу
            left = x
            while left >= 0:
                idx = (y * original_buffer_size[0] + left) * 3
                px = (draw_buffer[idx], draw_buffer[idx+1], draw_buffer[idx+2])
                if px == boundary_rgb or px == fill_rgb:
                    break
                left -= 1
            left += 1
            
            # Находим правую границу
            right = x
            while right < original_buffer_size[0]:
                idx = (y * original_buffer_size[0] + right) * 3
                px = (draw_buffer[idx], draw_buffer[idx+1], draw_buffer[idx+2])
                if px == boundary_rgb or px == fill_rgb:
                    break
                right += 1
            right -= 1
            
            # Закрашиваем отрезок
            for i in range(left, right + 1):
                idx = (y * original_buffer_size[0] + i) * 3
                draw_buffer[idx:idx+3] = fill_rgb
            
            # Проверяем строки выше и ниже
            for ny in [y - 1, y + 1]:
                if 0 <= ny < original_buffer_size[1]:
                    add_to_stack = False
                    for i in range(left, right + 1):
                        idx = (ny * original_buffer_size[0] + i) * 3
                        px = (draw_buffer[idx], draw_buffer[idx+1], draw_buffer[idx+2])
                        if px != boundary_rgb and px != fill_rgb:
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
    
    new_buffer = bytearray(draw_buffer)
    width, height = original_buffer_size
    
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            # Собираем цвета соседних пикселей
            neighbors = []
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    idx = ((y + dy) * width + (x + dx)) * 3
                    r = draw_buffer[idx] / 255.0
                    g = draw_buffer[idx+1] / 255.0
                    b = draw_buffer[idx+2] / 255.0
                    neighbors.append((r, g, b))
            
            # Усредняем
            avg_r = sum(c[0] for c in neighbors) / 9
            avg_g = sum(c[1] for c in neighbors) / 9
            avg_b = sum(c[2] for c in neighbors) / 9
            
            # Записываем результат
            idx = (y * width + x) * 3
            new_buffer[idx] = int(avg_r * 255)
            new_buffer[idx+1] = int(avg_g * 255)
            new_buffer[idx+2] = int(avg_b * 255)
    
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
        # Масштабирование изображения под текущий размер окна
        glPixelZoom(
            current_window_size[0] / original_buffer_size[0],
            current_window_size[1] / original_buffer_size[1]
        )
        glDrawPixels(original_buffer_size[0], original_buffer_size[1], 
                    GL_RGB, GL_UNSIGNED_BYTE, draw_buffer)
    
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
        # Нормализация координат к оригинальному размеру буфера
        x = int(xpos * original_buffer_size[0] / current_window_size[0])
        y = original_buffer_size[1] - int(ypos * original_buffer_size[1] / current_window_size[1]) - 1
        
        points.append((x, y))
        print(f"Добавлена точка: ({x}, {y})")
        
        if len(points) >= 2:
            clear_draw_buffer(silent=True)
            draw_polygon()

def window_size_callback(window, width, height):
    """Обработка изменения размера окна"""
    global current_window_size
    current_window_size = (width, height)
    glViewport(0, 0, width, height)

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
