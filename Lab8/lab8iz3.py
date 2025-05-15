import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders as shaders
import numpy as np
import math

# Глобальные переменные
angle_x = 0.0
angle_y = 0.0
angle_z = 0.0
size = 1.0
wireframe = False
sectors = 10  
stacks = 10 

VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec3 position;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
out vec3 fragNormal;
out vec3 fragPos;
void main() {
    fragPos = vec3(model * vec4(position, 1.0));
    fragNormal = mat3(transpose(inverse(model))) * normalize(position);
    gl_Position = projection * view * model * vec4(position, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330 core
in vec3 fragNormal;
in vec3 fragPos;
out vec4 outColor;

uniform vec3 lightPos = vec3(2.0, 4.0, 4.0);
uniform vec3 lightColor = vec3(1.0, 1.0, 1.0);
uniform vec3 objectColor = vec3(0.2, 0.4, 1.0);
uniform vec3 viewPos = vec3(0.0, 0.0, 5.0);

void main() {
    // Diffuse 
    vec3 norm = normalize(fragNormal);
    vec3 lightDir = normalize(lightPos - fragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor * objectColor;
    
    outColor = vec4(diffuse, 1.0);
}
"""

def compile_shader():
    try:
        shader = shaders.compileProgram(
            shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
            shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        )
        print("Шейдер успешно скомпилирован")
        return shader
    except Exception as e:
        print("Ошибка компиляции шейдера:", str(e))
        raise

def create_vao(vertices, indices):
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)
    vao = glGenVertexArrays(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

    glBindVertexArray(0)
    return vao, len(indices)

def draw_rhombus_vao():
    # Вершины ромба
    vertices = np.array([
        (0, 0, 1),   # 0
        (1, 1, 0),   # 1
        (1, -1, 0),  # 2
        (-1, -1, 0), # 3
        (-1, 1, 0),  # 4
        (0, 0, -1),  # 5
    ], dtype=np.float32)

    faces = [
        (0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1),
        (5, 1, 2), (5, 2, 3), (5, 3, 4), (5, 4, 1)
    ]
    indices = np.array(faces, dtype=np.uint32).flatten()
    return create_vao(vertices, indices)

def draw_sphere_vao(sectors, stacks):
    radius = 1.0
    vertices = []
    indices = []

    for i in range(stacks + 1):
        theta = i * math.pi / stacks
        for j in range(sectors + 1):
            phi = j * 2 * math.pi / sectors
            x = math.sin(theta) * math.cos(phi)
            y = math.sin(theta) * math.sin(phi)
            z = math.cos(theta)
            vertices.append((x, y, z))

    for i in range(stacks):
        for j in range(sectors):
            first = i * (sectors + 1) + j
            second = first + sectors + 1
            indices.extend([first, second, first + 1])
            indices.extend([second, second + 1, first + 1])

    vertices = np.array(vertices, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)
    return create_vao(vertices, indices)

def perspective(fov, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov) / 2)
    return np.array([
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, -(far + near) / (far - near), -1],
        [0, 0, -(2 * far * near) / (far - near), 0]
    ], dtype=np.float32)

def look_at(eye, center, up):
    f = normalize(center - eye)
    r = normalize(np.cross(f, up))
    u = np.cross(f, r)
    return np.array([
        [r[0], u[0], -f[0], 0],
        [r[1], u[1], -f[1], 0],
        [r[2], u[2], -f[2], 0],
        [-np.dot(r, eye), -np.dot(u, eye), np.dot(f, eye), 1]
    ], dtype=np.float32)

def normalize(v):
    norm = np.linalg.norm(v)
    return v / norm if norm != 0 else v

def main():
    global angle_x, angle_y, angle_z, size, wireframe, sectors, stacks

    if not glfw.init():
        return
    window = glfw.create_window(640, 640, "Lab3", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glEnable(GL_DEPTH_TEST)

    shader = compile_shader()

    rhombus_vao, rhombus_index_count = draw_rhombus_vao()
    sphere_vao, sphere_index_count = draw_sphere_vao(sectors, stacks)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        glUseProgram(shader)

        width, height = glfw.get_framebuffer_size(window)
        aspect = width / height if height > 0 else 1

        # Матрицы
        projection = perspective(45, aspect, 0.1, 100)
        view = look_at(np.array([0, 0, 5]), np.array([0, 0, 0]), np.array([0, 1, 0]))
        model = np.identity(4, dtype=np.float32)

        # Вращение
        model = model @ rotate(angle_x, 'x')
        model = model @ rotate(angle_y, 'y')
        model = model @ rotate(angle_z, 'z')
        model = model @ scale(size)

        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, model)
        glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, projection)

        if wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # Пересоздание сферы при изменении параметров
        if sectors <= 4 and stacks <= 4:
            glBindVertexArray(rhombus_vao)
            glDrawElements(GL_TRIANGLES, rhombus_index_count, GL_UNSIGNED_INT, None)
        else:
            sphere_vao, sphere_index_count = draw_sphere_vao(sectors, stacks)
            glBindVertexArray(sphere_vao)
            glDrawElements(GL_TRIANGLES, sphere_index_count, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()

def rotate(angle, axis):
    angle_rad = math.radians(angle)
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    if axis == 'x':
        return np.array([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ])
    elif axis == 'y':
        return np.array([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ])
    elif axis == 'z':
        return np.array([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
    return np.identity(4)

def scale(factor):
    return np.array([
        [factor, 0, 0, 0],
        [0, factor, 0, 0],
        [0, 0, factor, 0],
        [0, 0, 0, 1]
    ])

def key_callback(window, key, scancode, action, mods):
    global angle_x, angle_y, angle_z, wireframe, sectors, stacks
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

def scroll_callback(window, xoffset, yoffset):
    global size
    size += yoffset * 0.1
    size = max(0.1, min(3.0, size))

if __name__ == "__main__":
    main()
