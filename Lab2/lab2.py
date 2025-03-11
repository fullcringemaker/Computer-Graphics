import glfw
from OpenGL.GL import *
import math

delta = 0.1
angle_x = 0
angle_y = 0
angle_z = 0
posx = 0
posy = 0
size = 1.0
wireframe = False

def main():
    if not glfw.init():
        return
    window = glfw.create_window(640, 640, "Lab2", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glClearColor(1.0, 1.0, 1.0, 1.0)  
    while not glfw.window_should_close(window):
        display(window)
    glfw.destroy_window(window)
    glfw.terminate()

def display(window):
    global angle_x, angle_y, angle_z, wireframe

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    width, height = glfw.get_window_size(window)
    half_width = width // 2
    half_height = height // 2

    glViewport(0, half_height, half_width, half_height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-2, 2, -2, 2, -2, 2)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    draw_cube(angle_x, angle_y, angle_z, wireframe)

    glViewport(half_width, half_height, half_width, half_height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-2, 2, -2, 2, -2, 2)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glRotatef(90, 0, 1, 0)
    draw_cube(0, 0, 0, wireframe)

    glViewport(0, 0, half_width, half_height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-2, 2, -2, 2, -2, 2)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glRotatef(90, 1, 0, 0)
    draw_cube(0, 0, 0, wireframe)

    glViewport(half_width, 0, half_width, half_height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-2, 2, -2, 2, -2, 2)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    draw_cube(0, 0, 0, wireframe)

    glfw.swap_buffers(window)
    glfw.poll_events()

def draw_cube(angle_x, angle_y, angle_z, wireframe):
    if wireframe:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glPushMatrix()
    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 1, 0)
    glRotatef(angle_z, 0, 0, 1)
    glScalef(size, size, size)

    glBegin(GL_QUADS)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-1.0, -1.0,  1.0)
    glVertex3f( 1.0, -1.0,  1.0)
    glVertex3f( 1.0,  1.0,  1.0)
    glVertex3f(-1.0,  1.0,  1.0)

    glColor3f(0.0, 1.0, 1.0)  
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f( 1.0, -1.0, -1.0)
    glVertex3f( 1.0,  1.0, -1.0)
    glVertex3f(-1.0,  1.0, -1.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-1.0,  1.0, -1.0)
    glVertex3f( 1.0,  1.0, -1.0)
    glVertex3f( 1.0,  1.0,  1.0)
    glVertex3f(-1.0,  1.0,  1.0)

    glColor3f(1.0, 1.0, 0.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f( 1.0, -1.0, -1.0)
    glVertex3f( 1.0, -1.0,  1.0)
    glVertex3f(-1.0, -1.0,  1.0)

    glColor3f(1.0, 0.0, 1.0)
    glVertex3f( 1.0, -1.0, -1.0)
    glVertex3f( 1.0,  1.0, -1.0)
    glVertex3f( 1.0,  1.0,  1.0)
    glVertex3f( 1.0, -1.0,  1.0)

    glColor3f(0.0, 1.0, 0.0)  
    glVertex3f(-1.0, -1.0, -1.0)
    glVertex3f(-1.0,  1.0, -1.0)
    glVertex3f(-1.0,  1.0,  1.0)
    glVertex3f(-1.0, -1.0,  1.0)
    glEnd()

    glPopMatrix()

def key_callback(window, key, scancode, action, mods):
    global angle_x, angle_y, angle_z, wireframe

    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_X:
            angle_x += delta * 10
        elif key == glfw.KEY_Y:
            angle_y += delta * 10
        elif key == glfw.KEY_Z:
            angle_z += delta * 10
        elif key == glfw.KEY_SPACE:
            wireframe = not wireframe

def scroll_callback(window, xoffset, yoffset):
    global size
    if yoffset > 0:
        size += 0.1
    else:
        size -= 0.1

if __name__ == "__main__":
    main()
