import math
import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from math import cos, sin

alpha = 0
beta = 0
size = 0.5
fill = True

vertex_shader = """
#version 330 core
layout(location = 0) in vec3 position;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
}
"""

fragment_shader = """
#version 330 core
out vec4 FragColor;
void main()
{
    FragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Red color
}
"""


def main():
    if not glfw.init():
        return
    window = glfw.create_window(640, 640, "LAB 3", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    shader = create_shader_program()

    while not glfw.window_should_close(window):
        display(window, shader)

    glfw.destroy_window(window)
    glfw.terminate()


def create_shader_program():
    shader = compileProgram(
        compileShader(vertex_shader, GL_VERTEX_SHADER),
        compileShader(fragment_shader, GL_FRAGMENT_SHADER)
    )
    return shader


def display(window, shader):
    glLoadIdentity()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glUseProgram(shader)

    model = np.identity(4, dtype=np.float32)
    view = np.identity(4, dtype=np.float32)
    projection = np.identity(4, dtype=np.float32)

    alpha_rad = np.radians(alpha)
    beta_rad = np.radians(beta)

    rotate_y = np.array([
        [cos(alpha_rad), 0, sin(alpha_rad), 0],
        [0, 1, 0, 0],
        [-sin(alpha_rad), 0, cos(alpha_rad), 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

    rotate_x = np.array([
        [1, 0, 0, 0],
        [0, cos(beta_rad), -sin(beta_rad), 0],
        [0, sin(beta_rad), cos(beta_rad), 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

    model = rotate_x @ rotate_y

    projection_location = glGetUniformLocation(shader, "projection")
    view_location = glGetUniformLocation(shader, "view")
    model_location = glGetUniformLocation(shader, "model")

    glUniformMatrix4fv(projection_location, 1, GL_FALSE, projection)
    glUniformMatrix4fv(view_location, 1, GL_FALSE, view)
    glUniformMatrix4fv(model_location, 1, GL_FALSE, model)

    R = size
    r = size / 3

    torus(R, r, 40, 25)

    glfw.swap_buffers(window)
    glfw.poll_events()


def torus(R, r, N, n):
    for i in range(N):
        for j in range(n):
            theta = (2 * math.pi / N) * i
            phi = (2 * math.pi / n) * j
            theta_next = (2 * math.pi / N) * (i + 1)
            phi_next = (2 * math.pi / n) * (j + 1)

            x0 = (R + r * cos(phi)) * cos(theta)
            y0 = (R + r * cos(phi)) * sin(theta)
            z0 = r * sin(phi)

            x1 = (R + r * cos(phi)) * cos(theta_next)
            y1 = (R + r * cos(phi)) * sin(theta_next)
            z1 = r * sin(phi)

            x2 = (R + r * cos(phi_next)) * cos(theta_next)
            y2 = (R + r * cos(phi_next)) * sin(theta_next)
            z2 = r * sin(phi_next)

            x3 = (R + r * cos(phi_next)) * cos(theta)
            y3 = (R + r * cos(phi_next)) * sin(theta)
            z3 = r * sin(phi_next)

            glBegin(GL_QUADS)
            glVertex3f(x0, y0, z0)
            glVertex3f(x1, y1, z1)
            glVertex3f(x2, y2, z2)
            glVertex3f(x3, y3, z3)
            glEnd()


def key_callback(window, key, scancode, action, mods):
    global alpha
    global beta
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_RIGHT:
            alpha += 3
        elif key == glfw.KEY_LEFT:
            alpha -= 3
        elif key == glfw.KEY_UP:
            beta -= 3
        elif key == glfw.KEY_DOWN:
            beta += 3
        elif key == glfw.KEY_F:
            global fill
            fill = not fill
            if fill:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


def scroll_callback(window, xoffset, yoffset):
    global size
    if xoffset > 0:
        size -= yoffset / 10
    else:
        size += yoffset / 10


if __name__ == "__main__":
    main()
