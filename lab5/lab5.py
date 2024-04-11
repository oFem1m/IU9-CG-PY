from OpenGL.GL import *
import glfw
import collections

size = 400
pixels = [0] * (size * size * 3)
points = []
edges = []


def sign(a, b):
    if a > b:
        return -1
    return 1


def bresenham(x1, y1, x2, y2, color):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    x, y = x1, y1
    sx = sign(x1, x2)
    sy = sign(y1, y2)
    if dx > dy:
        err = dx / 2
        while x != x2:
            if 0 <= x < size and 0 <= y < size:
                position = (x + y * size) * 3
                # красим с учетом интенсивности
                pixels[position] = color[0]
                pixels[position + 1] = color[1]
                pixels[position + 2] = color[2]
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2
        while y != y2:
            if 0 <= x < size and 0 <= y < size:
                position = (x + y * size) * 3
                # и тут тоже
                pixels[position] = color[0]
                pixels[position + 1] = color[1]
                pixels[position + 2] = color[2]
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    if 0 <= x < size and 0 <= y < size:
        position = (x + y * size) * 3
        pixels[position] = color[0]
        pixels[position + 1] = color[1]
        pixels[position + 2] = color[2]


def mouse_button_callback(window, button, action, mods):
    global points, edges, size
    if action == glfw.PRESS and button == glfw.MOUSE_BUTTON_LEFT:
        x, y = glfw.get_cursor_pos(window)
        y = size - y
        points.append((int(x), int(y)))

        redraw_polygon()


def redraw_polygon():
    global pixels, points, edges, size
    pixels = [0] * (size * size * 3)
    edges = create_edge_list()

    for i in range(1, len(points)):
        bresenham(points[i - 1][0], points[i - 1][1], points[i][0], points[i][1], color=(255, 255, 255))

    if len(points) > 2:
        bresenham(points[-1][0], points[-1][1], points[0][0], points[0][1], color=(255, 255, 255))


def create_edge_list():
    edge_list = []
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]
        edge_list.append((p1, p2))
    return edge_list


def fill(x, y):
    q = collections.deque([(x, y)])
    while q:
        x, y = q.popleft()
        current_pos = (x + y * size) * 3
        if x < 0 or x >= size or y < 0 or y >= size:
            continue
        if pixels[current_pos] == pixels[current_pos + 1] == pixels[current_pos + 2] == 0:
            if 0 <= x < size and 0 <= y < size:
                position = (x + y * size) * 3
                pixels[position] = 255
                pixels[position + 1] = 255
                pixels[position + 2] = 255
            q.append((x + 1, y))
            q.append((x - 1, y))
            q.append((x, y + 1))
            q.append((x, y - 1))

def clip_line(coordinate_min, coordinate_max, P1, P2):
    dx = P2[0] - P1[0]
    dy = P2[1] - P1[1]

    # параметры t для пересечения с границами отсекателя
    t_enter = 0.0
    t_exit = 1.0

    # проверка пересечения с каждой границей отсекателя
    for edge in range(4):
        if edge == 0:  # левая граница
            normal = (-1, 0)
            constant = -coordinate_min[0]
        elif edge == 1:  # нижняя граница
            normal = (0, -1)
            constant = -coordinate_min[1]
        elif edge == 2:  # правая граница
            normal = (1, 0)
            constant = coordinate_max[0]
        elif edge == 3:  # верхняя граница
            normal = (0, 1)
            constant = coordinate_max[1]

        numerator = normal[0] * (P1[0] - coordinate_min[0]) + normal[1] * (P1[1] - coordinate_min[1])
        denominator = normal[0] * dx + normal[1] * dy

        # отрезок параллелен текущей границе
        if denominator == 0:
            if numerator < 0:
                return None  # отрезок полностью виден
        else:
            t = -numerator / denominator

            if denominator > 0:  # пересечение с входной границей
                if t > t_exit:
                    return None
                if t > t_enter:
                    t_enter = t
            else:  # пересечение с выходной границей
                if t < t_enter:
                    return None
                if t < t_exit:
                    t_exit = t

    # отрезок полностью внутри отсекателя
    if t_exit > 0:
        return P2

    # нахождение координаты точки пересечения с границей
    clipped_point = (P1[0] + t_enter * dx, P1[1] + t_enter * dy)
    return clipped_point


def key_callback(window, key, scancode, action, mods):
    global pixels, points, edges
    if action == glfw.PRESS:
        if key == glfw.KEY_F:
            if len(points) > 2:
                bresenham(points[-1][0], points[-1][1], points[0][0], points[0][1], color=(255, 255, 255))
                min_x = min(points, key=lambda x: x[0])[0]
                max_x = max(points, key=lambda x: x[0])[0]
                min_y = min(points, key=lambda x: x[1])[1]
                max_y = max(points, key=lambda x: x[1])[1]
                x = (min_x + max_x) // 2
                y = (min_y + max_y) // 2
                if x and y:
                    fill(x, y)

        # elif key == glfw.KEY_ENTER:
        #     if len(points) > 2:
        #         # Вызов алгоритма отсечения средней точкой
        #         clipped_points = midpoint_line_clipping(points)
        #         points = clipped_points
        #         redraw_polygon()

        elif key == glfw.KEY_BACKSPACE:
            pixels = [0 for _ in range(size * size * 3)]
            points.clear()
            edges.clear()


def display(window):
    # Рисование прямоугольной области D
    min_x_rect = 150
    max_x_rect = 250
    min_y_rect = 150
    max_y_rect = 250
    bresenham(min_x_rect, min_y_rect, max_x_rect, min_y_rect, color=(255, 0, 0))
    bresenham(min_x_rect, min_y_rect, min_x_rect, max_y_rect, color=(255, 0, 0))
    bresenham(min_x_rect, max_y_rect, max_x_rect, max_y_rect, color=(255, 0, 0))
    bresenham(max_x_rect, min_y_rect, max_x_rect, max_y_rect, color=(255, 0, 0))

    glDrawPixels(size, size, GL_RGB, GL_UNSIGNED_BYTE, pixels)
    glBegin(GL_LINES)
    for edge in edges:
        for p in edge:
            glVertex2f(*p)
    glEnd()

    glfw.swap_buffers(window)
    glfw.poll_events()


def main():
    if not glfw.init():
        return
    window = glfw.create_window(size, size, "Lab4", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    while not glfw.window_should_close(window):
        display(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
