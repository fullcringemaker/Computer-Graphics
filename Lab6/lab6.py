import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math

angle_x, angle_y, angle_z = 0.0, 0.0, 0.0
size = 1.0
wireframe = False
sectors, stacks = 20, 20
light_enabled = True
texture_enabled = True
attenuation_enabled = True
position = [0.0, 0.0, 0.0]
velocity = [0.03, 0.05, 0.02] 
box_size = 4.0 
texture_id = 0

def main():
    global texture_id
    if not glfw.init():
        return
    window = glfw.create_window(640, 640, "Lab6", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)
    texture_id = generate_checkerboard_texture()
    setup_lighting()
    while not glfw.window_should_close(window):
        display(window)
        update_position()
    glfw.destroy_window(window)
    glfw.terminate()

def setup_lighting():
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
    light_pos = [4.0, 4.0, 4.0, 1.0] 
    light_diffuse = [1.0, 1.0, 1.0, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    light_ambient = [0.2, 0.2, 0.2, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    if attenuation_enabled:
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.2) 
        glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.1)  
    else:
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.0)
        glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.0)
    material_diffuse = [0.7, 0.7, 0.7, 1.0]
    material_specular = [0.9, 0.9, 0.9, 1.0]
    material_ambient = [0.1, 0.1, 0.1, 1.0]
    material_shininess = [50.0]
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
    glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambient)
    glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

def generate_checkerboard_texture():
    width, height = 64, 64
    texture_data = []
    for i in range(height):
        for j in range(width):
            if (i // 8 + j // 8) % 2 == 0:
                texture_data.extend([200, 200, 200])
            else:
                texture_data.extend([50, 50, 50])
    texture_bytes = bytes(texture_data)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, 
                GL_RGB, GL_UNSIGNED_BYTE, texture_bytes)
    return texture_id

def display(window):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = 640 / 640
    gluPerspective(45, aspect, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 8, 0, 0, 0, 0, 1, 0) 
    draw_bounding_box()
    if light_enabled:
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
    else:
        glDisable(GL_LIGHTING)
    if texture_enabled:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
    else:
        glDisable(GL_TEXTURE_2D)
    glPushMatrix()
    glTranslatef(position[0], position[1], position[2])
    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 1, 0)
    glRotatef(angle_z, 0, 0, 1)
    glScalef(size, size, size)
    if wireframe:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    draw_sphere(sectors, stacks)
    glPopMatrix()
    glfw.swap_buffers(window)
    glfw.poll_events()

def draw_bounding_box():
    glPushMatrix()
    glColor3f(0.8, 0.8, 0.8)
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
            n1 = spherical_to_cartesian(1.0, theta1, phi1)
            n2 = spherical_to_cartesian(1.0, theta2, phi1)
            n3 = spherical_to_cartesian(1.0, theta2, phi2)
            n4 = spherical_to_cartesian(1.0, theta1, phi2)
            glBegin(GL_TRIANGLES)
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
    for i in range(3):
        position[i] += velocity[i]
    half_size = box_size / 2 - size * 1.1
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
        elif key == glfw.KEY_L:
            light_enabled = not light_enabled
            print(f"Освещение: {'ВКЛ' if light_enabled else 'ВЫКЛ'}")
        elif key == glfw.KEY_T:
            texture_enabled = not texture_enabled
            print(f"Текстура: {'ВКЛ' if texture_enabled else 'ВЫКЛ'}")
        elif key == glfw.KEY_A:
            attenuation_enabled = not attenuation_enabled
            setup_lighting() 
            print(f"Ослабление света: {'ВКЛ' if attenuation_enabled else 'ВЫКЛ'}")
        elif key == glfw.KEY_R: 
            global position, velocity
            position = [0.0, 0.0, 0.0]
            velocity = [0.03, 0.05, 0.02]

if __name__ == "__main__":
    main()
