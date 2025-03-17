import glfw
from OpenGL.GL import *
import math

# Глобальные переменные
angle_x = 0.0
angle_y = 0.0
angle_z = 0.0
size = 1.0
wireframe = False  # Режим каркасного отображения
sectors = 4  # Минимальное количество секторов (октаэдр)
stacks = 4  # Минимальное количество стеков (октаэдр)

def main():
    if not glfw.init():
        return
    window = glfw.create_window(640, 640, "3D Sphere", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glEnable(GL_DEPTH_TEST)
    
    while not glfw.window_should_close(window):
        display(window)
    
    glfw.destroy_window(window)
    glfw.terminate()

def display(window):
    global angle_x, angle_y, angle_z
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glClearColor(1.0, 1.0, 1.0, 1.0)
    
    # Настройка перспективной проекции
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = 640 / 640
    glFrustum(-aspect, aspect, -1, 1, 2, 50)
    glTranslatef(0, 0, -5)
    glMatrixMode(GL_MODELVIEW)
    
    glPushMatrix()
    glRotatef(angle_x, 1, 0, 0)  # Вращение по оси X
    glRotatef(angle_y, 0, 1, 0)  # Вращение по оси Y
    glRotatef(angle_z, 0, 0, 1)  # Вращение по оси Z
    glScalef(size, size, size)
    
    if wireframe:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)  # Каркасное отображение
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)  # Твердотельное отображение
    
    draw_sphere(sectors, stacks)
    
    glPopMatrix()
    
    glfw.swap_buffers(window)
    glfw.poll_events()

def draw_sphere(sectors, stacks):
    radius = 1.0
    if sectors == 4 and stacks == 4:
        # Отрисовка октаэдра (минимальная полигональная модель)
        draw_octahedron(radius)
    else:
        # Отрисовка сферы с заданным количеством секторов и стеков
        for i in range(stacks):
            theta1 = i * math.pi / stacks
            theta2 = (i + 1) * math.pi / stacks
            
            for j in range(sectors):
                phi1 = j * 2 * math.pi / sectors
                phi2 = (j + 1) * 2 * math.pi / sectors
                
                # Вершины квада
                p1 = spherical_to_cartesian(radius, theta1, phi1)
                p2 = spherical_to_cartesian(radius, theta2, phi1)
                p3 = spherical_to_cartesian(radius, theta2, phi2)
                p4 = spherical_to_cartesian(radius, theta1, phi2)
                
                glColor3f(0.2, 0.4, 1.0)
                glBegin(GL_TRIANGLES)
                glVertex3f(*p1)
                glVertex3f(*p2)
                glVertex3f(*p3)
                
                glVertex3f(*p1)
                glVertex3f(*p3)
                glVertex3f(*p4)
                glEnd()

def draw_octahedron(radius):
    # Вершины октаэдра
    vertices = [
        (0, 0, radius),    # Верхняя вершина
        (0, 0, -radius),   # Нижняя вершина
        (-radius, -radius, 0),
        (radius, -radius, 0),
        (radius, radius, 0),
        (-radius, radius, 0)
    ]
    
    # Грани октаэдра (каждая грань — треугольник)
    faces = [
        (0, 2, 3), (0, 3, 4), (0, 4, 5), (0, 5, 2),  # Верхние грани
        (1, 2, 3), (1, 3, 4), (1, 4, 5), (1, 5, 2)   # Нижние грани
    ]
    
    glColor3f(0.2, 0.4, 1.0)
    for face in faces:
        glBegin(GL_TRIANGLES)
        for vertex in face:
            glVertex3f(*vertices[vertex])
        glEnd()

def spherical_to_cartesian(r, theta, phi):
    x = r * math.sin(theta) * math.cos(phi)
    y = r * math.sin(theta) * math.sin(phi)
    z = r * math.cos(theta)
    return (x, y, z)

def key_callback(window, key, scancode, action, mods):
    global angle_x, angle_y, angle_z, wireframe, sectors, stacks
    
    if action == glfw.PRESS or action == glfw.REPEAT:
        # Управление вращением
        if key == glfw.KEY_X: angle_x += 5
        elif key == glfw.KEY_Y: angle_y += 5
        elif key == glfw.KEY_Z: angle_z += 5
        
        # Переключение между каркасным и твердотельным режимом
        elif key == glfw.KEY_SPACE: wireframe = not wireframe
        
        # Управление полигональностью
        elif key == glfw.KEY_UP:
            sectors += 1
            stacks += 1
        elif key == glfw.KEY_DOWN:
            sectors = max(4, sectors - 1)  # Минимальное значение — 4 (октаэдр)
            stacks = max(4, stacks - 1)

def scroll_callback(window, xoffset, yoffset):
    global size
    size += yoffset * 0.1
    size = max(0.1, min(3.0, size))

if __name__ == "__main__":
    main()
