import math
import glfw
import os
import json
import internal.logger as logger
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import numpy as np
import time

textures = {}
mtl_ID = {}

# Rotation angles for the cube
angle_x = 0
angle_y = 0

# Camera position
camera_x = 0.0
camera_y = 0.0
camera_z = 5.0

# Camera rotation
camera_yaw = 0.0
camera_pitch = 0.0


# Function to initialize OpenGL
def init():
    logger.info("Initializing OpenGL")
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)


# Function to handle window resizing
def frame_buffer_size_callback(window, width, height):  # noqa
    if height == 0:
        aspect_ratio = 1
    else:
        aspect_ratio = width / height

    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, aspect_ratio, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)


# Function to draw the cube
def draw_from_files(filename):
    global camera_x, camera_y, camera_z

    if filename.endswith('.json'):
        # Load cube data from JSON
        with open(filename, 'r') as data_file:
            data = json.load(data_file)

        glLoadIdentity()
        gluLookAt(camera_x, camera_y, camera_z, 0, 0, 0, 0, 1, 0)
        INIT_DATA = data['init']
        TRANSLATE_CORDS = INIT_DATA['insert_at']
        glTranslatef(TRANSLATE_CORDS[0], TRANSLATE_CORDS[1], TRANSLATE_CORDS[2])

        glBegin(GL_QUADS)
        for face in INIT_DATA['access']:
            currAt = data['faces'][face]
            glColor3f(currAt['color'][0], currAt['color'][1], currAt['color'][2])
            for step in currAt['steps']:
                glVertex3f(step[0], step[1], step[2])
        glEnd()

    if filename.endswith('.obj'):
        # Load OBJ file and render
        vertices, faces, texture_cords = load_obj(filename)
        if vertices and faces:
            glLoadIdentity()
            gluLookAt(camera_x, camera_y, camera_z, 0, 0, 0, 0, 1, 0)

            # Enable texture mapping
            glEnable(GL_TEXTURE_2D)

            # Bind texture
            glBindTexture(GL_TEXTURE_2D, load_texture("objects/sample.png"))

            glBegin(GL_TRIANGLES)
            for face, tex_cords in zip(faces, texture_cords):
                for i, vertex_index in enumerate(face):
                    vertex = vertices[vertex_index]
                    if i < len(tex_cords) and tex_cords[i]:  # Check if a texture coordinate exists and is not None
                        glTexCoord2f(tex_cords[0], tex_cords[1])
                    else:
                        # Use a default texture coordinate if none is provided
                        glTexCoord2f(0.0, 0.0)
                    glVertex3f(*vertex)

            glEnd()

            # Disable texture mapping
            glDisable(GL_TEXTURE_2D)


def load_obj(filename):
    vertices = []
    faces = []
    texture_cords = []

    with open(filename, 'r') as obj_file:
        for line in obj_file:
            if line.startswith('v '):
                # Parse vertex position
                vertex = list(map(float, line.strip().split()[1:]))
                vertices.append(vertex)
            elif line.startswith('vt '):
                # Parse texture coordinates
                tex_coord = list(map(float, line.strip().split()[1:]))
                texture_cords.append(tex_coord)
            elif line.startswith('f '):
                # Parse face indices and texture coordinate indices
                face_data = line.strip().split()[1:]
                face = []
                tex_cords = []
                for vertex_data in face_data:
                    data = vertex_data.split('/')
                    vertex_index = int(data[0]) - 1
                    face.append(vertex_index)
                    if len(data) >= 2 and data[1]:  # Check if texture coordinate exists
                        tex_coord_index = int(data[1]) - 1
                        tex_cords.append(texture_cords[tex_coord_index])
                    else:
                        logger.warning("Texture cords not defined, defaulting cords to (0, 0)")
                        tex_cords.append((0.0, 0.0))  # Default texture coordinate
                faces.append(face)
                texture_cords.append(tex_cords)
    return vertices, faces, texture_cords


def load_mil(filename):
    vertices = []
    faces = []

    with open(filename, 'r') as mil_file:
        for line in mil_file:
            if line.startswith('vertex '):
                # Parse vertex position
                vertex = list(map(float, line.strip().split()[1:]))
                vertices.append(vertex)
            elif line.startswith('face '):
                # Parse face indices
                face = [int(vertex) - 1 for vertex in line.strip().split()[1:]]
                faces.append(face)

    return vertices, faces


def camera_updating(window):  # noqa
    global angle_x, angle_y, camera_x, camera_y, camera_z, camera_yaw, camera_pitch

    # Update camera direction
    camera_dir_x = math.cos(math.radians(camera_yaw)) * math.cos(math.radians(camera_pitch))
    camera_dir_y = math.sin(math.radians(camera_pitch))
    camera_dir_z = math.sin(math.radians(camera_yaw)) * math.cos(math.radians(camera_pitch))

    camera_dir_length = math.hypot(camera_dir_x ** 2 + camera_dir_y ** 2 + camera_dir_z ** 2)
    camera_dir_x /= camera_dir_length
    camera_dir_y /= camera_dir_length
    camera_dir_z /= camera_dir_length

    # Update camera position
    speed = 0.01
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera_x += speed * camera_dir_x
        camera_y += speed * camera_dir_y
        camera_z += speed * camera_dir_z
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera_x -= speed * camera_dir_x
        camera_y -= speed * camera_dir_y
        camera_z -= speed * camera_dir_z

    # Keyboard controls for camera rotation
    rotation_speed = 0.5
    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
        camera_yaw += rotation_speed
    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
        camera_yaw -= rotation_speed
    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
        camera_pitch += rotation_speed
    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
        camera_pitch -= rotation_speed

    # Clamp camera pitch to avoid flipping
    camera_pitch = max(-90.0, min(90.0, camera_pitch))


def load_texture(texture_path):
    if texture_path in textures:
        return textures[texture_path]

    # Load texture
    image = Image.open(texture_path)
    img_data = np.array(list(image.getdata()), np.uint8)
    width, height = image.size

    # Generate texture ID
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Set texture parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Load texture data
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    textures[texture_path] = texture_id

    return texture_id


# Main function
def main():
    global window  # noqa

    # Initialize GLFW
    if not glfw.init():
        return

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(800, 600, "3D Rendering", None, None)
    if not window:
        logger.warning("Terminating Window")
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, frame_buffer_size_callback)
    init()

    # Loop until the user closes the window

    while not glfw.window_should_close(window):
        # Render here
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        objects = [f for f in os.listdir("objects") if f.endswith('.json') or f.endswith('.obj') or f.endswith('.mtl')]

        try:
            for fObject in objects:
                draw_from_files(f"objects/{fObject}")
        except FileNotFoundError as FileChangeError:
            logger.error(FileChangeError)

        # Update rotation angles and camera position
        camera_updating(window)

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    logger.info("Terminating window")
    glfw.terminate()


def mtl_to_id():
    materials = [f for f in os.listdir("objects") if f.endswith('.mtl')]
    newmtl_second_parts = [] # noqa

    for material_file in materials:
        with open(os.path.join("objects", material_file), 'r') as file:
            for line in file:
                if 'newmtl' in line: # noqa
                    parts = line.split()
                    if len(parts) >= 2:
                        newmtl_second_parts.append(parts[1])
                        mtl_ID[parts[1]] = file.name.split("\\")[1].split('.mtl')[0]
    del newmtl_second_parts, materials


if __name__ == "__main__":
    logger.info("Registering mtl files")
    start_time = time.time() * 1000
    mtl_to_id()
    end_time = time.time() * 1000
    elapsed_time = end_time - start_time
    logger.info("Completed registration in {:.3f} ms".format(elapsed_time))
    del elapsed_time, start_time, end_time
    logger.info("Running main")
    main()
    logger.info("Completed main")
else:
    logger.error("Could not start program. __name__ is not __main__")
