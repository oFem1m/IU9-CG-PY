import pygame
from pygame.locals import *
from OpenGL.GL import *

pygame.init()

display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)


def init_pentagon():
    glBegin(GL_POLYGON)
    glColor3fv((1, 0, 0))
    glVertex2fv((0, 0.5))
    glVertex2fv((-0.4, 0))
    glVertex2fv((-0.2, -0.5))
    glVertex2fv((0.2, -0.5))
    glVertex2fv((0.4, 0))
    glEnd()


def draw_pentagon():
    # Очиста от старого пятиугольника
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    init_pentagon()
    pygame.display.flip()


def main():
    angle = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    angle += 10

        # Режим проекции
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # Ортогональная проекция
        glOrtho(-1, 1, -1, 1, -1, 1)
        # Режим моделирования
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Поворот
        glRotatef(angle, 0, 0, 1)
        draw_pentagon()


if __name__ == "__main__":
    main()