import math
import time

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
torus_velocity = [0.00001, 0.00002, 0.00005]

last_frame_time = 0.0
frame_count = 0
fps = 0.0

torus_display_list = None
vbo = None


def create_torus_display_list():
    global torus_display_list

    # Создание нового дисплейного списка
    torus_display_list = glGenLists(1)
    glNewList(torus_display_list, GL_COMPILE)

    R = size
    r = size / 3
    N = 40
    n = 25

    for i in range(N):
        glBegin(GL_QUAD_STRIP)
        for j in range(n + 1):
            for k in range(2):
                s = (i + k) % N + 0.5
                t = j % (n + 1)
                theta = 2 * math.pi * s / N
                phi = 2 * math.pi * t / n
                x = (R + r * cos(phi)) * cos(theta)
                y = (R + r * cos(phi)) * sin(theta)
                z = r * sin(phi)
                glTexCoord2f(s / N, t / n)
                glVertex3f(x, y, z)
        glEnd()

    glEndList()


vertices = []


def create_vbo():
    global vbo

    # Создание массива вершин для тора

    R = size
    r = size / 3
    N = 40
    n = 25

    for i in range(N):
        for j in range(n + 1):
            for k in range(2):
                s = (i + k) % N + 0.5
                t = j % (n + 1)
                theta = 2 * math.pi * s / N
                phi = 2 * math.pi * t / n
                x = (R + r * cos(phi)) * cos(theta)
                y = (R + r * cos(phi)) * sin(theta)
                z = r * sin(phi)
                vertices.extend([x, y, z])

    # Создание буфера вершин
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, np.array(vertices, dtype=np.float32), GL_STATIC_DRAW)


def draw_torus_with_vbo():
    global vertices

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, None)
    glDrawArrays(GL_QUAD_STRIP, 0, int(len(vertices) / 3))
    glDisableClientState(GL_VERTEX_ARRAY)


def main():
    global last_frame_time, frame_count, fps
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

    # Создание дисплейного списка для тора
    create_torus_display_list()

    # Создание буфера вершин для тора
    create_vbo()

    last_frame_time = time.time()

    while not glfw.window_should_close(window):
        display(window, texture_id)

    glfw.destroy_window(window)
    glfw.terminate()


def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Установка позиции источника света - оптимизация
    light_pos = [10.0, 10.0, 10.0, 0.0]  # Позиция в пространстве (x, y, z, w)
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
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data) # Использование UNSIGNED_BYTE - оптиимизация
    return texture_id


def display(window, texture_id):
    global alpha
    global beta
    global size
    global torus_position
    global torus_velocity
    global frame_count, last_frame_time, fps

    glLoadIdentity()
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)

    def projection():
        alpha_rad = np.radians(alpha)
        beta_rad = np.radians(beta)

        rotate_y = np.array([
            [cos(alpha_rad), 0, sin(alpha_rad), 0],
            [0, 1, 0, 0],
            [-sin(alpha_rad), 0, cos(alpha_rad), 0],
            [0, 0, 0, 1]
        ])

        rotate_x = np.array([
            [1, 0, 0, 0],
            [0, cos(beta_rad), -sin(beta_rad), 0],
            [0, sin(beta_rad), cos(beta_rad), 0],
            [0, 0, 0, 1]
        ])

        glMultMatrixf(rotate_x)
        glMultMatrixf(rotate_y)

    def torus(R, r, N, n):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        # Использование дисплейного списка для рисования тора
        glCallList(torus_display_list)

        # Или использование буфера вершин для рисования тора
        draw_torus_with_vbo()

        glDisable(GL_TEXTURE_2D)

    glLoadIdentity()

    projection()
    R = size
    r = size / 3

    # Обновление позиции Тора на каждом кадре
    for i in range(3):
        torus_position[i] += torus_velocity[i]

    # Проверка столкновения Тора с границами окна и отражение его скорости при необходимости
    for i in range(3):
        if torus_position[i] + size > 1.0 or torus_position[i] - size < -1.0:
            torus_velocity[i] *= -1.0

    # Рисование Тора
    glTranslatef(torus_position[0], torus_position[1], torus_position[2])
    torus(R, r, 40, 25)

    # Вывод FPS
    current_time = time.time()
    delta_time = current_time - last_frame_time
    frame_count += 1
    if delta_time >= 1.0:
        fps = frame_count / delta_time
        print("FPS:", fps)
        frame_count = 0
        last_frame_time = current_time

    glfw.swap_buffers(window)
    glfw.poll_events()


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
