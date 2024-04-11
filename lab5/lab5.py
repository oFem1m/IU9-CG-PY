from OpenGL.GL import *
import glfw
import collections

size = 400
pixels = [0] * (size * size * 3)
points = []
edges = []
clipped_edges = []


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


def clip_line(xmin, xmax, ymin, ymax, x1, y1, x2, y2):
    # Функция для определения кода точки
    def compute_code(x, y):
        code = 0
        if x < xmin:
            code |= 1
        elif x > xmax:
            code |= 2
        if y < ymin:
            code |= 4
        elif y > ymax:
            code |= 8
        return code

    # Инициализация кодов концов отрезка
    code1 = compute_code(x1, y1)
    code2 = compute_code(x2, y2)

    while True:
        # Проверяем, является ли отрезок тривиально видимым
        if not (code1 | code2):
            return int(x1), int(y1), int(x2), int(y2)  # Отрезок целиком видим

        # Проверяем, является ли отрезок тривиально невидимым
        elif code1 & code2:
            return None  # Отрезок тривиально невидим

        else:
            # Выбираем точку с ненулевым кодом
            if code1:
                code = code1
            else:
                code = code2

            # Находим точку пересечения с границей окна
            if code & 1:  # Левая граница
                x = xmin
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
            elif code & 2:  # Правая граница
                x = xmax
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            elif code & 4:  # Нижняя граница
                y = ymin
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
            elif code & 8:  # Верхняя граница
                y = ymax
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)

            # Обновляем координаты точки
            if code == code1:
                x1, y1 = x, y
                code1 = compute_code(x1, y1)
            else:
                x2, y2 = x, y
                code2 = compute_code(x2, y2)



def clip_edges():
    global edges, clipped_edges
    clipped_edges.clear()
    min_x_rect = 150
    max_x_rect = 250
    min_y_rect = 150
    max_y_rect = 250
    for edge in edges:
        p1, p2 = edge
        clipped_p1 = clip_line((min_x_rect, min_y_rect), (max_x_rect, max_y_rect), p1, p2)
        clipped_p2 = clip_line((min_x_rect, min_y_rect), (max_x_rect, max_y_rect), p2, p1)
        print(clipped_p1, clipped_p2)
        if clipped_p1 and clipped_p2:
            clipped_edges.append((clipped_p1, clipped_p2))


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
        elif key == glfw.KEY_ENTER:
            print(len(points))
            if len(points) > 2:
                # Вызов функции для обработки пересечений и отсечения ребер
                clip_edges()
                redraw_clipped_polygon()

        elif key == glfw.KEY_BACKSPACE:
            pixels = [0 for _ in range(size * size * 3)]
            points.clear()
            edges.clear()


def redraw_clipped_polygon():
    global pixels, points, edges, clipped_edges, size
    pixels = [0] * (size * size * 3)
    for i in range(1, len(points)):
        bresenham(points[i - 1][0], points[i - 1][1], points[i][0], points[i][1], color=(255, 255, 255))
        if len(points) > 2:
            bresenham(points[-1][0], points[-1][1], points[0][0], points[0][1], color=(255, 255, 255))

        for edge in clipped_edges:
            print(edge)
            p1, p2 = edge
            bresenham(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), color=(0, 255, 0))


def display(window):
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
