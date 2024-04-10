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


def bresenhamfloat(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    x, y = x1, y1
    sx = sign(x1, x2)
    sy = sign(y1, y2)
    if dx > dy:
        err = dx / 2.0
        while x != x2:
            if 0 <= x < size and 0 <= y < size:
                position = (x + y * size) * 3
                pixels[position] = 255
                pixels[position + 1] = 255
                pixels[position + 2] = 255
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y2:
            if 0 <= x < size and 0 <= y < size:
                position = (x + y * size) * 3
                pixels[position] = 255
                pixels[position + 1] = 255
                pixels[position + 2] = 255
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    if 0 <= x < size and 0 <= y < size:
        position = (x + y * size) * 3
        pixels[position] = 255
        pixels[position + 1] = 255
        pixels[position + 2] = 255


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
        bresenhamfloat(points[i - 1][0], points[i - 1][1], points[i][0], points[i][1])

    if len(points) > 2:
        bresenhamfloat(points[-1][0], points[-1][1], points[0][0], points[0][1])


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


def apply_post_filter(N):
    global pixels, size
    filtered_pixels = pixels.copy()

    radius = N // 2
    weights = [[1, 2, 1],
               [2, 4, 2],
               [1, 2, 1]]

    for y in range(size):
        for x in range(size):
            sum_r = sum_g = sum_b = 0
            weight_sum = 0

            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < size and 0 <= ny < size:
                        index = (ny * size + nx) * 3
                        weight = weights[dy + radius][dx + radius]
                        sum_r += pixels[index] * weight
                        sum_g += pixels[index + 1] * weight
                        sum_b += pixels[index + 2] * weight
                        weight_sum += weight

            avg_r = int(sum_r / weight_sum)
            avg_g = int(sum_g / weight_sum)
            avg_b = int(sum_b / weight_sum)

            index = (y * size + x) * 3
            filtered_pixels[index] = avg_r
            filtered_pixels[index + 1] = avg_g
            filtered_pixels[index + 2] = avg_b

    pixels = filtered_pixels


def key_callback(window, key, scancode, action, mods):
    global pixels, points, edges
    if action == glfw.PRESS:
        if key == glfw.KEY_ENTER:
            if len(points) > 2:
                bresenhamfloat(points[-1][0], points[-1][1], points[0][0], points[0][1])
                min_x = min(points, key=lambda x: x[0])[0]
                max_x = max(points, key=lambda x: x[0])[0]
                min_y = min(points, key=lambda x: x[1])[1]
                max_y = max(points, key=lambda x: x[1])[1]
                x = (min_x + max_x) // 2
                y = (min_y + max_y) // 2
                if x and y:
                    fill(x, y)
                apply_post_filter(N=3)
        elif key == glfw.KEY_BACKSPACE:
            pixels = [255 for _ in range(size * size * 3)]
            points.clear()
            edges.clear()


def display(window):
    # glClear(GL_COLOR_BUFFER_BIT)
    glDrawPixels(size, size, GL_RGB, GL_UNSIGNED_BYTE, pixels)

    # glColor3f(1, 1, 1)
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

    # glClearColor(1.0, 1.0, 1.0, 1.0)

    while not glfw.window_should_close(window):
        display(window)

    glfw.terminate()


if __name__ == "__main__":
    main()