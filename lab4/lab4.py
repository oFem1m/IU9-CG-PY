import glfw
from OpenGL.GL import *
import numpy as np

# Глобальные переменные
points = []  # Список вершин многоугольника
edges_list = []  # Список рёбер многоугольника
polygon_filled = False  # Флаг для отрисовки заполненного многоугольника
window_size = (800, 600)  # Размер окна


def draw_polygon():
    glColor3f(1.0, 1.0, 1.0)  # Устанавливаем цвет рисования (белый)
    glBegin(GL_LINE_LOOP)
    for point in points:
        glVertex2f(point[0], point[1])
    glEnd()


def fill_polygon_with_edge_list():
    global edges_list
    edges_list.sort(key=lambda edge: edge[0][1])  # Сортируем рёбра по y координате начальной точки
    active_edges = []

    # Проходимся по каждой строке сканирования
    for y in range(window_size[1]):
        # Удаляем из списка активных рёбер те, которые закончились
        active_edges = [edge for edge in active_edges if edge[2] > y]

        # Добавляем новые рёбра в список активных рёбер
        for edge in edges_list:
            if edge[0][1] <= y < edge[1][1]:
                active_edges.append((edge[0], edge[1], edge[2]))

        # Сортируем активные рёбра по x координате текущей точки сканирования
        active_edges.sort(key=lambda edge: edge[0][0])

        # Заполняем интервалы между рёбрами
        for i in range(0, len(active_edges), 2):
            for x in range(int(active_edges[i][0][0]), int(active_edges[i + 1][0][0]) + 1):
                glVertex2f(x, y)


def key_callback(window, key, scancode, action, mods):
    global points, edges_list, polygon_filled
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_C:
            # Очистка списка вершин и рёбер
            points = []
            edges_list = []
            polygon_filled = False
        elif key == glfw.KEY_F:
            polygon_filled = not polygon_filled


def mouse_button_callback(window, button, action, mods):
    global points, edges_list
    if action == glfw.PRESS and button == glfw.MOUSE_BUTTON_LEFT:
        x, y = glfw.get_cursor_pos(window)
        points.append((x, window_size[1] - y))
        if len(points) > 1:
            edges_list.append((points[-2], points[-1], max(points[-2][1], points[-1][1])))


def main():
    global window_size
    # Инициализация GLFW
    if not glfw.init():
        return

    # Создание окна
    window = glfw.create_window(window_size[0], window_size[1], "Polygon Rasterization", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    # Устанавливаем параметры OpenGL
    glViewport(0, 0, window_size[0], window_size[1])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, window_size[0], 0, window_size[1], -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Основной цикл программы
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)

        if len(points) >= 2:
            draw_polygon()
            if polygon_filled:
                glColor3f(0.0, 1.0, 0.0)  # Устанавливаем цвет рисования (зеленый)
                glBegin(GL_POINTS)
                fill_polygon_with_edge_list()
                glEnd()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()
