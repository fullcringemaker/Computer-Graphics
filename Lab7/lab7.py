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
sphere_list = None
vbo_vertices = None
vbo_normals = None
vbo_texcoords = None
index_count = 0
last_frame_time = 0.0

def main():
    global texture_id, sphere_list, vbo_vertices, vbo_normals, vbo_texcoords, index_count, last_frame_time
    if not glfw.init():
        return
    window = glfw.create_window(640, 640, "Lab7", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)
    texture_id = generate_checkerboard_texture()
    setup_lighting()
    sphere_list, vbo_vertices, vbo_normals, vbo_texcoords, index_count = create_sphere_vbo(sectors, stacks)
    last_frame_time = glfw.get_time()
    frame_count = 0
    last_fps_time = last_frame_time
    while not glfw.window_should_close(window):
        display(window)
        current_time = glfw.get_time()
        delta_time = current_time - last_frame_time
        last_frame_time = current_time
        update_position(delta_time)
        frame_count += 1
        if current_time - last_fps_time >= 1.0:
            print(f"FPS: {frame_count}")
            frame_count = 0
            last_fps_time = current_time
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
            color = [200, 200, 200] if (i // 8 + j // 8) % 2 == 0 else [50, 50, 50]
            texture_data.extend(color)
    texture_bytes = bytes(texture_data)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGB, width, height, GL_RGB, GL_UNSIGNED_BYTE, texture_bytes)
    return texture_id

def create_sphere_vbo(sectors, stacks):
    radius = 1.0
    vertices = []
    normals = []
    tex_coords = []
    indices = []
    sector_step = 2 * math.pi / sectors
    stack_step = math.pi / stacks
    def add_vertex(theta, phi):
        x = math.sin(theta) * math.cos(phi)
        y = math.sin(theta) * math.sin(phi)
        z = math.cos(theta)
        s = phi / (2 * math.pi)
        t = theta / math.pi
        vertices.append((radius * x, radius * y, radius * z))
        normals.append((x, y, z))
        tex_coords.append((s, t))
    index = 0
    for i in range(stacks):
        theta1 = i * stack_step
        theta2 = (i + 1) * stack_step
        for j in range(sectors):
            phi1 = j * sector_step
            phi2 = (j + 1) * sector_step
            add_vertex(theta1, phi1)
            add_vertex(theta2, phi1)
            add_vertex(theta2, phi2)
            add_vertex(theta1, phi2)
            indices.append(index)
            indices.append(index + 1)
            indices.append(index + 2)
            indices.append(index)
            indices.append(index + 2)
            indices.append(index + 3)
            index += 4
    vbo_vertices = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
    glBufferData(GL_ARRAY_BUFFER, len(vertices)*3*4, (GLfloat * len(vertices*3))(*sum(vertices, ())), GL_STATIC_DRAW)
    vbo_normals = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_normals)
    glBufferData(GL_ARRAY_BUFFER, len(normals)*3*4, (GLfloat * len(normals*3))(*sum(normals, ())), GL_STATIC_DRAW)
    vbo_texcoords = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_texcoords)
    glBufferData(GL_ARRAY_BUFFER, len(tex_coords)*2*4, (GLfloat * len(tex_coords*2))(*sum(tex_coords, ())), GL_STATIC_DRAW)
    sphere_list = glGenLists(1)
    glNewList(sphere_list, GL_COMPILE)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
    glVertexPointer(3, GL_FLOAT, 0, None)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_normals)
    glNormalPointer(GL_FLOAT, 0, None)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_texcoords)
    glTexCoordPointer(2, GL_FLOAT, 0, None)
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, (GLuint * len(indices))(*indices))
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
    glEndList()
    return sphere_list, vbo_vertices, vbo_normals, vbo_texcoords, len(indices)

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
        glDisable(GL_LIGHT0)
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
    glCallList(sphere_list)
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

def update_position(delta_time):
    global position, velocity
    speed_factor = 30.0 
    for i in range(3):
        position[i] += velocity[i] * delta_time * speed_factor
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
    global sphere_list, vbo_vertices, vbo_normals, vbo_texcoords, index_count
    global position, velocity
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_X: angle_x += 5
        elif key == glfw.KEY_Y: angle_y += 5
        elif key == glfw.KEY_Z: angle_z += 5
        elif key == glfw.KEY_SPACE: wireframe = not wireframe
        elif key == glfw.KEY_UP:
            sectors += 1
            stacks += 1
            sphere_list, vbo_vertices, vbo_normals, vbo_texcoords, index_count = create_sphere_vbo(sectors, stacks)
        elif key == glfw.KEY_DOWN:
            sectors = max(4, sectors - 1)
            stacks = max(4, stacks - 1)
            sphere_list, vbo_vertices, vbo_normals, vbo_texcoords, index_count = create_sphere_vbo(sectors, stacks)
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
            position = [0.0, 0.0, 0.0]
            velocity = [0.03, 0.05, 0.02]

if __name__ == "__main__":
    main()
