import glfw
from OpenGL.GL import *
from math import cos, sin, sqrt, asin

alpha = 0.0
beta = 0.0
fill = True


def main():
    if not glfw.init():
        return
    window = glfw.create_window(640, 640, "LAB 2", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    while not glfw.window_should_close(window):
        display(window)
    glfw.destroy_window(window)
    glfw.terminate()


def display(window):
    glLoadIdentity()
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)

    # move
    glMultMatrixf([1, 0, 0, 0,
                   0, 1, 0, 0,
                   0, 0, 1, 0,
                   0.75, 0.75, 0, 1])

    fz = 0
    theta = 0.61557763
    phi = 0.785398

    def projection():
        glMultMatrixf([
            cos(phi), sin(phi) * sin(theta), sin(theta) * cos(theta), 0,
            0, cos(theta), -sin(theta), 0,
            sin(phi), -cos(phi) * sin(theta), -cos(phi) * cos(theta), 0,
            0, 0, 0, 1,
        ])

    projection()

    def cube(sz):
        glBegin(GL_QUADS)
        glColor3f(0.0, 0.0, 1.0);
        glVertex3f(-sz / 2, -sz / 2, -sz / 2)
        glVertex3f(-sz / 2, sz / 2, -sz / 2)
        glVertex3f(-sz / 2, sz / 2, sz / 2)
        glVertex3f(-sz / 2, -sz / 2, sz / 2)
        glColor3f(1.0, 0.0, 0.0);
        glVertex3f(sz / 2, -sz / 2, -sz / 2)
        glVertex3f(sz / 2, -sz / 2, sz / 2)
        glVertex3f(sz / 2, sz / 2, sz / 2)
        glVertex3f(sz / 2, sz / 2, -sz / 2)
        glColor3f(0.0, 1.0, 0.0);
        glVertex3f(-sz / 2, -sz / 2, -sz / 2)
        glVertex3f(-sz / 2, -sz / 2, sz / 2)
        glVertex3f(sz / 2, -sz / 2, sz / 2)
        glVertex3f(sz / 2, -sz / 2, -sz / 2)
        glColor3f(1.0, 1.0, 0.0);
        glVertex3f(-sz / 2, sz / 2, -sz / 2)
        glVertex3f(-sz / 2, sz / 2, sz / 2)
        glVertex3f(sz / 2, sz / 2, sz / 2)
        glVertex3f(sz / 2, sz / 2, -sz / 2)
        glColor3f(0.0, 1.0, 1.0);
        glVertex3f(-sz / 2, -sz / 2, -sz / 2)
        glVertex3f(sz / 2, -sz / 2, -sz / 2)
        glVertex3f(sz / 2, sz / 2, -sz / 2)
        glVertex3f(-sz / 2, sz / 2, -sz / 2)
        glColor3f(1.0, 0.0, 1.0);
        glVertex3f(-sz / 2, -sz / 2, sz / 2)
        glVertex3f(sz / 2, -sz / 2, sz / 2)
        glVertex3f(sz / 2, sz / 2, sz / 2)
        glVertex3f(-sz / 2, sz / 2, sz / 2)
        glEnd()

    cube(0.2)

    glLoadIdentity()

    global alpha
    global beta
    x = 0.7
    y = 0.7
    fz = sqrt(x * x + y * y)
    theta = asin(fz / sqrt(2)) + alpha
    phi = asin(fz / sqrt(2 - fz * fz)) + beta
    projection()

    cube(0.7)

    glfw.swap_buffers(window)
    glfw.poll_events()


def key_callback(window, key, scancode, action, mods):
    global alpha
    global beta
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_RIGHT:
            beta += 0.1
        elif key == glfw.KEY_LEFT:
            beta -= 0.1
        elif key == glfw.KEY_UP:
            alpha += 0.1
        elif key == glfw.KEY_DOWN:
            alpha -= 0.1
        elif key == glfw.KEY_F:
            global fill
            fill = not fill
            if fill:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);


if __name__ == "__main__":
    main()
