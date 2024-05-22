import math

import glfw
import numpy as np
from OpenGL.GL import *
from math import cos, sin

from PIL import Image

alpha = 0
beta = 0
size = 0.5
fill = True

torus_position = [0.0, 0.0, 0.0]
torus_velocity = [0.001, 0.002, 0.005]  # Начальная скорость


def main():
    if not glfw.init():
        return
    window = glfw.create_window(640, 640, "LAB 6", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    setup_lighting()
    texture_id = load_texture("texture2.jpg")

    vertex_shader_source = """
    #version 330 core
    layout(location = 0) in vec3 aPos;
    layout(location = 1) in vec2 aTexCoord;
    out vec2 TexCoord;
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;
    void main()
    {
        gl_Position = projection * view * model * vec4(aPos, 1.0);
        TexCoord = aTexCoord;
    }
    """

    fragment_shader_source = """
    #version 330 core
    out vec4 FragColor;
    in vec2 TexCoord;
    uniform sampler2D texture1;
    void main()
    {
        FragColor = texture(texture1, TexCoord);
    }
    """

    shader_program = create_shader_program(vertex_shader_source, fragment_shader_source)
    glUseProgram(shader_program)

    while not glfw.window_should_close(window):
        display(window, texture_id, shader_program)
    glfw.destroy_window(window)
    glfw.terminate()


def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Установка позиции источника света
    light_pos = [10.0, 10.0, 10.0, 1.0]  # Позиция в пространстве (x, y, z, w)
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)

    # Установка свойств источника света (диффузное и зеркальное освещение)
    light_diffuse = [1.0, 1.0, 1.0, 1.0]  # Цвет света (r, g, b, a)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    light_specular = [1.0, 1.0, 1.0, 1.0]  # Цвет отраженного света
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    # Установка свойств материала (диффузное, зеркальное, эмиссивное и окружающее свечение)
    material_diffuse = [0.8, 0.8, 0.8, 1.0]  # Цвет материала
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
    material_specular = [1.0, 1.0, 1.0, 1.0]  # Цвет отраженного света материала
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
    material_shininess = [100.0]  # Коэффициент блеска материала
    glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)


def load_texture(filename):
    img = Image.open(filename)
    img_data = np.array(list(img.getdata()), np.uint8)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    return texture_id


def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)

    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        raise RuntimeError(glGetShaderInfoLog(shader))

    return shader


def create_shader_program(vertex_source, fragment_source):
    program = glCreateProgram()
    vertex_shader = compile_shader(vertex_source, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_source, GL_FRAGMENT_SHADER)

    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)

    if glGetProgramiv(program, GL_LINK_STATUS) != GL_TRUE:
        raise RuntimeError(glGetProgramInfoLog(program))

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return program


def display(window, texture_id, shader_program):
    global alpha
    global beta
    global size
    global torus_position
    global torus_velocity

    glLoadIdentity()
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)

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

    projection = np.identity(4, dtype=np.float32)
    model = np.dot(rotate_x, rotate_y)
    view = np.identity(4, dtype=np.float32)

    R = size
    r = size / 3

    for i in range(3):
        torus_position[i] += torus_velocity[i]

    for i in range(3):
        if torus_position[i] + size > 1.0 or torus_position[i] - size < -1.0:
            torus_velocity[i] *= -1.0

    model = np.dot(model, np.array([
        [1, 0, 0, torus_position[0]],
        [0, 1, 0, torus_position[1]],
        [0, 0, 1, torus_position[2]],
        [0, 0, 0, 1]
    ], dtype=np.float32))

    model_loc = glGetUniformLocation(shader_program, "model")
    view_loc = glGetUniformLocation(shader_program, "view")
    projection_loc = glGetUniformLocation(shader_program, "projection")

    glUniformMatrix4fv(model_loc, 1, GL_TRUE, model)
    glUniformMatrix4fv(view_loc, 1, GL_TRUE, view)
    glUniformMatrix4fv(projection_loc, 1, GL_TRUE, projection)

    torus(R, r, 40, 25, shader_program, texture_id)

    glfw.swap_buffers(window)
    glfw.poll_events()


def torus(R, r, N, n, shader_program, texture_id):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    vertices = []
    tex_coords = []

    for i in range(N):
        for j in range(n):
            theta = (2 * math.pi / N) * i
            phi = (2 * math.pi / n) * j
            theta_next = (2 * math.pi / N) * (i + 1)
            phi_next = (2 * math.pi / n) * (j + 1)

            x0 = (R + r * cos(phi)) * cos(theta)
            y0 = (R + r * cos(phi)) * sin(theta)
            z0 = r * sin(phi)
            vertices.extend([x0, y0, z0])
            tex_coords.extend([j / n, i / N])

            x1 = (R + r * cos(phi)) * cos(theta_next)
            y1 = (R + r * cos(phi)) * sin(theta_next)
            z1 = r * sin(phi)
            vertices.extend([x1, y1, z1])
            tex_coords.extend([(j + 1) / n, i / N])

            x2 = (R + r * cos(phi_next)) * cos(theta_next)
            y2 = (R + r * cos(phi_next)) * sin(theta_next)
            z2 = r * sin(phi_next)
            vertices.extend([x2, y2, z2])
            tex_coords.extend([(j + 1) / n, (i + 1) / N])

            x3 = (R + r * cos(phi_next)) * cos(theta)
            y3 = (R + r * cos(phi_next)) * sin(theta)
            z3 = r * sin(phi_next)
            vertices.extend([x3, y3, z3])
            tex_coords.extend([j / n, (i + 1) / N])

    vertices = np.array(vertices, dtype=np.float32)
    tex_coords = np.array(tex_coords, dtype=np.float32)

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(2)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, vbo[1])
    glBufferData(GL_ARRAY_BUFFER, tex_coords.nbytes, tex_coords, GL_STATIC_DRAW)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(1)

    glBindVertexArray(vao)
    glDrawArrays(GL_QUADS, 0, len(vertices) // 3)

    glDisable(GL_TEXTURE_2D)
    glBindVertexArray(0)


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
        elif key == glfw.KEY_L and action == glfw.PRESS:
            # Включение и выключение источника света
            light_enabled = glIsEnabled(GL_LIGHT0)
            if light_enabled:
                glDisable(GL_LIGHT0)
            else:
                glEnable(GL_LIGHT0)


def scroll_callback(window, xoffset, yoffset):
    global size

    if xoffset > 0:
        size -= yoffset / 10
    else:
        size += yoffset / 10


if __name__ == "__main__":
    main()
