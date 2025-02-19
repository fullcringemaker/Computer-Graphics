import glfw
from OpenGL.GL import *
import math

delta = 0.1
angle = 0
posx = 0
posy = 0
size = 0.5  
sides = 4   

def main():
    if not glfw.init():
        return
    window = glfw.create_window(640, 640, "Lab1", None, None)
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
    global angle
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glPushMatrix()
    glTranslatef(posx, posy, 0.0)  
    glRotatef(angle, 0.0, 0.0, 1.0)  
    glScalef(size, size, 1.0) 
    glColor3f(1.0, 0.5, 0.0) 
    glBegin(GL_POLYGON)
    for i in range(sides):
        theta = 2.0 * math.pi * i / sides
        x = math.cos(theta)
        y = math.sin(theta)
        glVertex2f(x, y)
    glEnd()
    glPopMatrix()
    glfw.swap_buffers(window)
    glfw.poll_events()

def key_callback(window, key, scancode, action, mods):
    global posx, posy, angle, size, sides
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_RIGHT:
            posx += 0.1
        elif key == glfw.KEY_LEFT:
            posx -= 0.1
        elif key == glfw.KEY_UP:
            posy += 0.1
        elif key == glfw.KEY_DOWN:
            posy -= 0.1
        elif key == glfw.KEY_SPACE:
            angle -= 10.0  
        elif key == glfw.KEY_4:  
            sides = 4
        elif key == glfw.KEY_5:  
            sides = 5
        elif key == glfw.KEY_6:  
            sides = 6
        elif key == glfw.KEY_7:  
            sides = 7
        elif key == glfw.KEY_8:  
            sides = 8
        elif key == glfw.KEY_9: 
            sides = 9

def scroll_callback(window, xoffset, yoffset):
    global size
    if xoffset > 0:
        size -= yoffset / 10
    else:
        size += yoffset / 10

if __name__ == "__main__":
    main()
