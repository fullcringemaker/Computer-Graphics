import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
from PIL import Image

# Глобальные переменные
angle_x, angle_y, angle_z = 0.0, 0.0, 0.0
size = 1.0
wireframe = False
sectors, stacks = 20, 20
light_enabled = True
texture_enabled = True
attenuation_enabled = True

# Параметры движения
position = [0.0, 0.0, 0.0]
velocity = [0.02, 0.03, 0.01]
box_size = 3.0

# Текстура
texture_id = 0

def main():
    global texture_id
    
    if not glfw.init():
        return
    
    window = glfw.create_window(640, 640, "Lab3 - Lighting and Textures", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    
    # Инициализация OpenGL
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)
    
    # Загрузка текстуры
    texture_id = load_texture("texture.bmp")  # Создайте файл texture.bmp или используйте процедурную генерацию
    
    # Настройка освещения
    setup_lighting()
    
    while not glfw.window_should_close(window):
        display(window)
        update_position()
    
    glfw.destroy_window(window)
    glfw.terminate()

def setup_lighting():
    # Параметры глобального освещения
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    
    # Параметры источника света
    light_pos = [2.0, 2.0, 2.0, 1.0]  # Позиция (w=1 - точечный источник)
    light_diffuse = [1.0, 1.0, 1.0, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    light_ambient = [0.2, 0.2, 0.2, 1.0]
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    
    # Параметры ослабления света
    if attenuation_enabled:
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
        glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.01)
    else:
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.0)
        glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.0)
    
    # Параметры материала
    material_diffuse = [0.8, 0.8, 0.8, 1.0]
    material_specular = [1.0, 1.0, 1.0, 1.0]
    material_ambient = [0.2, 0.2, 0.2, 1.0]
    material_shininess = [50.0]
    
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
    glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambient)
    glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

def load_texture(filename):
    try:
        img = Image.open(filename)
        img_data = np.array(list(img.getdata()), np.uint8)
    except:
        # Процедурная генерация текстуры (шахматная доска)
        width, height = 64, 64
        img_data = np.zeros((width, height, 3), dtype=np.uint8)
        for i in range(width):
            for j in range(height):
                if (i//8 + j//8) % 2 == 0:
                    img_data[i,j] = [255, 0, 0]  # Красный
                else:
                    img_data[i,j] = [0, 255, 0]  # Зеленый
        img_data = img_data.flatten()
    
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 64, 64, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    return texture_id

def display(window):
    global angle_x, angle_y, angle_z
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    
    # Настройка проекции
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = 640 / 640
    gluPerspective(45, aspect, 0.1, 50.0)
    
    # Настройка вида
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 10, 0, 0, 0, 0, 1, 0)
    
    # Рисуем ограничивающий объем
    draw_bounding_box()
    
    # Включение/выключение освещения
    if light_enabled:
        glEnable(GL_LIGHTING)
    else:
        glDisable(GL_LIGHTING)
    
    # Включение/выключение текстуры
    if texture_enabled:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
    else:
        glDisable(GL_TEXTURE_2D)
    
    # Применяем трансформации к объекту
    glPushMatrix()
    glTranslatef(position[0], position[1], position[2])
    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 1, 0)
    glRotatef(angle_z, 0, 0, 1)
    glScalef(size, size, size)
    
    # Режим отрисовки (каркас/заполненный)
    if wireframe:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    # Рисуем объект
    if sectors <= 4 and stacks <= 4:
        draw_rhombus()
    else:
        draw_sphere(sectors, stacks)
    
    glPopMatrix()
    
    glfw.swap_buffers(window)
    glfw.poll_events()

def draw_bounding_box():
    glPushMatrix()
    glColor3f(1.0, 1.0, 1.0)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    
    half_size = box_size / 2
    vertices = [
        [-half_size, -half_size, -half_size],
        [half_size, -half_size, -half_size],
        [half_size, half_size, -half_size],
        [-half_size, half_size, -half_size],
        [-half_size, -half_size, half_size],
        [half_size, -half_size, half_size],
        [half_size, half_size, half_size],
        [-half_size, half_size, half_size]
    ]
    
    edges = [
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    ]
    
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()
    
    glEnable(GL_LIGHTING)
    glPopMatrix()

def draw_rhombus():
    vertices = [
        (0, 0, 1),
        (1, 1, 0),
        (1, -1, 0),
        (-1, -1, 0),
        (-1, 1, 0),
        (0, 0, -1)
    ]
    faces = [
        (0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1),
        (5, 1, 2), (5, 2, 3), (5, 3, 4), (5, 4, 1)
    ]
    
    for face in faces:
        glBegin(GL_TRIANGLES)
        for vertex in face:
            v = vertices[vertex]
            # Нормаль для плоских граней
            if vertex == 0 or vertex == 5:
                normal = (0, 0, 1 if vertex == 0 else -1)
            else:
                normal = (v[0], v[1], v[2])
            
            glNormal3fv(normal)
            if texture_enabled:
                # Простые текстурные координаты
                tex_coord = (v[0]/2 + 0.5, v[1]/2 + 0.5)
                glTexCoord2fv(tex_coord)
            glVertex3fv(v)
        glEnd()

def draw_sphere(sectors, stacks):
    radius = 1.0
    for i in range(stacks):
        theta1 = i * math.pi / stacks
        theta2 = (i + 1) * math.pi / stacks
        for j in range(sectors):
            phi1 = j * 2 * math.pi / sectors
            phi2 = (j + 1) * 2 * math.pi / sectors
            
            p1 = spherical_to_cartesian(radius, theta1, phi1)
            p2 = spherical_to_cartesian(radius, theta2, phi1)
            p3 = spherical_to_cartesian(radius, theta2, phi2)
            p4 = spherical_to_cartesian(radius, theta1, phi2)
            
            # Нормали для каждой вершины
            n1 = spherical_to_cartesian(1.0, theta1, phi1)
            n2 = spherical_to_cartesian(1.0, theta2, phi1)
            n3 = spherical_to_cartesian(1.0, theta2, phi2)
            n4 = spherical_to_cartesian(1.0, theta1, phi2)
            
            glBegin(GL_TRIANGLES)
            # Первый треугольник
            if texture_enabled:
                glTexCoord2f(j/sectors, i/stacks)
            glNormal3fv(n1)
            glVertex3fv(p1)
            
            if texture_enabled:
                glTexCoord2f(j/sectors, (i+1)/stacks)
            glNormal3fv(n2)
            glVertex3fv(p2)
            
            if texture_enabled:
                glTexCoord2f((j+1)/sectors, (i+1)/stacks)
            glNormal3fv(n3)
            glVertex3fv(p3)
            
            # Второй треугольник
            if texture_enabled:
                glTexCoord2f(j/sectors, i/stacks)
            glNormal3fv(n1)
            glVertex3fv(p1)
            
            if texture_enabled:
                glTexCoord2f((j+1)/sectors, (i+1)/stacks)
            glNormal3fv(n3)
            glVertex3fv(p3)
            
            if texture_enabled:
                glTexCoord2f((j+1)/sectors, i/stacks)
            glNormal3fv(n4)
            glVertex3fv(p4)
            glEnd()

def spherical_to_cartesian(r, theta, phi):
    x = r * math.sin(theta) * math.cos(phi)
    y = r * math.sin(theta) * math.sin(phi)
    z = r * math.cos(theta)
    return (x, y, z)

def update_position():
    global position, velocity
    
    # Обновляем позицию
    for i in range(3):
        position[i] += velocity[i]
    
    # Проверяем столкновения с границами
    half_size = box_size / 2 - size * 1.1  # Учитываем размер объекта
    
    for i in range(3):
        if position[i] > half_size:
            position[i] = half_size
            velocity[i] = -velocity[i]
        elif position[i] < -half_size:
            position[i] = -half_size
            velocity[i] = -velocity[i]

def key_callback(window, key, scancode, action, mods):
    global angle_x, angle_y, angle_z, wireframe, sectors, stacks
    global light_enabled, texture_enabled, attenuation_enabled
    
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_X: angle_x += 5
        elif key == glfw.KEY_Y: angle_y += 5
        elif key == glfw.KEY_Z: angle_z += 5
        elif key == glfw.KEY_SPACE: wireframe = not wireframe
        elif key == glfw.KEY_UP:
            sectors += 1
            stacks += 1
        elif key == glfw.KEY_DOWN:
            sectors = max(4, sectors - 1)
            stacks = max(4, stacks - 1)
        elif key == glfw.KEY_L: light_enabled = not light_enabled
        elif key == glfw.KEY_T: texture_enabled = not texture_enabled
        elif key == glfw.KEY_A: attenuation_enabled = not attenuation_enabled
        elif key == glfw.KEY_R:  # Сброс положения и скорости
            global position, velocity
            position = [0.0, 0.0, 0.0]
            velocity = [0.02, 0.03, 0.01]

def scroll_callback(window, xoffset, yoffset):
    global size
    size += yoffset * 0.1
    size = max(0.1, min(3.0, size))

if __name__ == "__main__":
    main()
