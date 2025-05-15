import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders as shaders
import numpy as np
import math

angle_x = angle_y = angle_z = 0.0
size = 1.0
wireframe = False
sectors = stacks = 20
light_enabled = True
texture_enabled = True
attenuation_enabled = True
position = [0.0, 0.0, 0.0]
velocity = [0.0003, 0.0005, 0.0002]
box_size = 4.0
sphere_vao = None
sphere_index_count = 0
texture_id = 0

VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texCoord;
layout(location = 2) in vec3 normal;
out vec2 fragTexCoord;
out vec3 fragNormal;
out vec3 fragPos;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    fragPos = vec3(model * vec4(position, 1.0));
    fragNormal = mat3(transpose(inverse(model))) * normal;
    fragTexCoord = texCoord;
    gl_Position = projection * view * model * vec4(position, 1.0);
}
"""

FRAGMENT_SHADER = """
in vec2 fragTexCoord;
in vec3 fragNormal;
in vec3 fragPos;
out vec4 outColor;
uniform int useTexture;
uniform sampler2D texture0;
uniform vec3 lightPos;
uniform vec3 viewPos;
uniform int useLighting;
uniform int useAttenuation;

void main() {
    if (useLighting == 0) {
        if (useTexture == 1)
            outColor = texture(texture0, fragTexCoord);
        else
            outColor = vec4(0.7, 0.7, 1.0, 1.0);
        return;
    }
    vec3 lightColor = vec3(1.0, 1.0, 1.0);
    vec3 objectColor = vec3(0.7, 0.7, 1.0);
    if (useTexture == 1)
        objectColor = texture(texture0, fragTexCoord).rgb;
    vec3 norm = normalize(fragNormal);
    vec3 lightDir = normalize(lightPos - fragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    float distance = length(lightPos - fragPos);
    float attenuation = 1.0;
    if (useAttenuation == 1) {
        attenuation = 1.0 / (1.0 + 0.2 * distance + 0.1 * distance * distance);
    }
    vec3 result = (diffuse * objectColor) * attenuation;
    outColor = vec4(result, 1.0);
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

def create_sphere_vao(sectors, stacks):
    radius = 1.0
    vertices = []
    normals = []
    uvs = []
    indices = []
    for i in range(stacks + 1):
        theta = i * math.pi / stacks
        sinTheta = math.sin(theta)
        cosTheta = math.cos(theta)
        for j in range(sectors + 1):
            phi = j * 2 * math.pi / sectors
            sinPhi = math.sin(phi)
            cosPhi = math.cos(phi)
            x = cosPhi * sinTheta
            y = cosTheta
            z = sinPhi * sinTheta
            u = j / sectors
            v = 1 - i / stacks
            normals.append((x, y, z))
            vertices.append((radius * x, radius * y, radius * z))
            uvs.append((u, v))
    for i in range(stacks):
        for j in range(sectors):
            first = i * (sectors + 1) + j
            second = first + sectors + 1
            indices.extend([first, second, first + 1])
            indices.extend([second, second + 1, first + 1])
    vertex_data = np.array(vertices, dtype=np.float32)
    normal_data = np.array(normals, dtype=np.float32)
    uv_data = np.array(uvs, dtype=np.float32)
    index_data = np.array(indices, dtype=np.uint32)
    vbo_positions = glGenBuffers(1)
    vbo_normals = glGenBuffers(1)
    vbo_uvs = glGenBuffers(1)
    ebo = glGenBuffers(1)
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_positions)
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_normals)
    glBufferData(GL_ARRAY_BUFFER, normal_data.nbytes, normal_data, GL_STATIC_DRAW)
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_uvs)
    glBufferData(GL_ARRAY_BUFFER, uv_data.nbytes, uv_data, GL_STATIC_DRAW)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)
    glBindVertexArray(0)
    return vao, len(index_data)

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

def look_at(eye, center, up):
    f = normalize(np.array(center) - np.array(eye))
    r = normalize(np.cross(f, np.array(up)))
    u = np.cross(r, f)
    return np.array([
        [r[0], u[0], -f[0], 0],
        [r[1], u[1], -f[1], 0],
        [r[2], u[2], -f[2], 0],
        [-np.dot(r, eye), -np.dot(u, eye), np.dot(f, eye), 1]
    ], dtype=np.float32)

def perspective(fov, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov) / 2)
    return np.array([
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, -(far + near) / (far - near), -1],
        [0, 0, -(2 * far * near) / (far - near), 0]
    ], dtype=np.float32)

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

def normalize(v):
    norm = np.linalg.norm(v)
    return v / norm if norm != 0 else v

def main():
    global sphere_vao, sphere_index_count, texture_id
    if not glfw.init():
        return
    window = glfw.create_window(640, 640, "Lab8", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glEnable(GL_DEPTH_TEST)
    shader = compile_shader()
    texture_id = generate_checkerboard_texture()
    sphere_vao, sphere_index_count = create_sphere_vao(sectors, stacks)
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glUseProgram(shader)
        width, height = glfw.get_framebuffer_size(window)
        aspect = width / height if height > 0 else 1
        projection = perspective(45, aspect, 0.1, 50)
        view = look_at([0, 0, 8], [0, 0, 0], [0, 1, 0])
        model = np.identity(4, dtype=np.float32)
        model = model @ rotate(angle_x, 'x')
        model = model @ rotate(angle_y, 'y')
        model = model @ rotate(angle_z, 'z')
        model = model @ scale(size)
        translation = np.identity(4)
        translation[3][0] = position[0]
        translation[3][1] = position[1]
        translation[3][2] = position[2]
        model = translation @ model
        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, model)
        glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, projection)
        glUniform3f(glGetUniformLocation(shader, "lightPos"), 4.0, 4.0, 4.0)
        glUniform3f(glGetUniformLocation(shader, "viewPos"), 0.0, 0.0, 8.0)
        glUniform1i(glGetUniformLocation(shader, "useTexture"), texture_enabled)
        glUniform1i(glGetUniformLocation(shader, "useLighting"), light_enabled)
        glUniform1i(glGetUniformLocation(shader, "useAttenuation"), attenuation_enabled)
        if texture_enabled:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glUniform1i(glGetUniformLocation(shader, "texture0"), 0)
        if wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glBindVertexArray(sphere_vao)
        glDrawElements(GL_TRIANGLES, sphere_index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        glfw.swap_buffers(window)
        glfw.poll_events()
        update_position()
    glfw.destroy_window(window)
    glfw.terminate()

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
            print(f"Ослабление света: {'ВКЛ' if attenuation_enabled else 'ВЫКЛ'}")
        elif key == glfw.KEY_R:
            global position, velocity
            position = [0.0, 0.0, 0.0]
            velocity = [0.0003, 0.0005, 0.0002]

if __name__ == "__main__":
    main()
