from OpenGL.GL import *


class Shader:
    def __init__(self, vertex_shader_source, fragment_shader_source):
        # Создаем буфер вершин и массив вершин для использования в шейдерах
        self.VBO = glGenBuffers(1)
        self.VAO = glGenVertexArrays(1)

        # Создаем вершинный шейдер
        self.vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(self.vertex_shader, vertex_shader_source)
        glCompileShader(self.vertex_shader)
        if not glGetShaderiv(self.vertex_shader, GL_COMPILE_STATUS):
            raise RuntimeError("Failed to compile vertex shader:", glGetShaderInfoLog(self.vertex_shader))

        # Создаем фрагментный шейдер
        self.fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.fragment_shader, fragment_shader_source)
        glCompileShader(self.fragment_shader)
        if not glGetShaderiv(self.fragment_shader, GL_COMPILE_STATUS):
            raise RuntimeError("Failed to compile fragment shader:", glGetShaderInfoLog(self.fragment_shader))

        # Создаем программу шейдеров и привязываем вершинный и фрагментный шейдеры к ней
        self.program_id = glCreateProgram()
        glAttachShader(self.program_id, self.vertex_shader)
        glAttachShader(self.program_id, self.fragment_shader)
        glLinkProgram(self.program_id)
        if not glGetProgramiv(self.program_id, GL_LINK_STATUS):
            raise RuntimeError("Failed to link shader program:", glGetProgramInfoLog(self.program_id))

        # Удаляем вершинный и фрагментный шейдеры (они уже привязаны к программе шейдеров)
        glDeleteShader(self.vertex_shader)
        glDeleteShader(self.fragment_shader)

        # Создаем буфер вершин и массив вершин для использования в шейдерах
        self.VBO = glGenBuffers(1)
        self.VAO = glGenVertexArrays(1)

    def use(self):
        glUseProgram(self.program_id)

    def set_uniform_matrix4fv(self, name, value):
        glUniformMatrix4fv(glGetUniformLocation(self.program_id, name), 1, GL_FALSE, value)

    def set_uniform_float(self, name, value):
        glUniform1f(glGetUniformLocation(self.program_id, name), value)

    def set_uniform_int(self, name, value):
        glUniform1i(glGetUniformLocation(self.program_id, name), value)

    def __del__(self):
        glDeleteVertexArrays(1, [self.VAO])
        glDeleteBuffers(1, [self.VBO])
        glDeleteProgram(self.program_id)
