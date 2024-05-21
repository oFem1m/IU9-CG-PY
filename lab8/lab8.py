import glfw
from OpenGL.GL import *
import numpy as np
from Shader import Shader  # Предполагается, что у вас есть класс Shader для работы с шейдерами
import math

alpha = 0
beta = 0
size = 0.5
fill = True


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

    shader = Shader("vertex_shader.glsl", "fragment_shader.glsl")  # Загрузка и компиляция шейдеров

    while not glfw.window_should_close(window):
        display(window, shader)
    glfw.destroy_window(window)
    glfw.terminate()


def display(window, shader):
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)

    projection = np.identity(4)
    view = np.identity(4)
    model = np.identity(4)

    projection_loc = glGetUniformLocation(shader.program_id, "projection")
    view_loc = glGetUniformLocation(shader.program_id, "view")
    model_loc = glGetUniformLocation(shader.program_id, "model")

    glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)

    R = size
    r = size / 3

    torus(shader, R, r, 40, 25)

    glfw.swap_buffers(window)
    glfw.poll_events()


def torus(shader, R, r, N, n):
    for i in range(N):
        for j in range(n):
            theta = (2 * math.pi / N) * i
            phi = (2 * math.pi / n) * j
            theta_next = (2 * math.pi / N) * (i + 1)
            phi_next = (2 * math.pi / n) * (j + 1)

            x0 = (R + r * math.cos(phi)) * math.cos(theta)
            y0 = (R + r * math.cos(phi)) * math.sin(theta)
            z0 = r * math.sin(phi)

            x1 = (R + r * math.cos(phi)) * math.cos(theta_next)
            y1 = (R + r * math.cos(phi)) * math.sin(theta_next)
            z1 = r * math.sin(phi)

            x2 = (R + r * math.cos(phi_next)) * math.cos(theta_next)
            y2 = (R + r * math.cos(phi_next)) * math.sin(theta_next)
            z2 = r * math.sin(phi_next)

            x3 = (R + r * math.cos(phi_next)) * math.cos(theta)
            y3 = (R + r * math.cos(phi_next)) * math.sin(theta)
            z3 = r * math.sin(phi_next)

            vertices = np.array([
                [x0, y0, z0],
                [x1, y1, z1],
                [x2, y2, z2],
                [x3, y3, z3]
            ], dtype=np.float32)

            glBindVertexArray(shader.VAO)
            glBindBuffer(GL_ARRAY_BUFFER, shader.VBO)
            glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GL_FLOAT), ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)

            glDrawArrays(GL_QUADS, 0, 4)


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
