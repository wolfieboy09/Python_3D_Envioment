import math
import glfw
import json
import os
import internal.logger as logger # another class I created
from OpenGL.GL import *
from OpenGL.GLU import *

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
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)


# Function to handle window resizing
# Function to handle window resizing
def frame_buffer_size_callback(window, width, height):  # noqa comment
    """Window has to be like that to prevent crash"""
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

    elif filename.endswith('.obj'):
        vertices, faces = load_obj(filename)
        if vertices and faces:
            glLoadIdentity()
            gluLookAt(camera_x, camera_y, camera_z, 0, 0, 0, 0, 1, 0)

            glBegin(GL_TRIANGLES)
            for face in faces:
                for vertex_index in face:
                    vertex = vertices[vertex_index]
                    glVertex3f(*vertex)
            glEnd()


def load_obj(filename):
    vertices = []
    faces = []

    with open(filename, 'r') as obj_file:
        for line in obj_file:
            if line.startswith('v '):
                # Parse vertex position
                vertex = list(map(float, line.strip().split()[1:]))
                vertices.append(vertex)
            elif line.startswith('f '):
                # Parse face indices
                face = [int(vertex.split('/')[0]) - 1 for vertex in line.strip().split()[1:]]
                faces.append(face)

    return vertices, faces


# Function to update the rotation angles and camera position
# I hope
def doCameraUpdateAndThings():
    # this is camera system never works, send help ;-;
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
    # it does not rotate at all
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
    # I'm in pain
    # print(camera_dir_x, camera_dir_y, camera_dir_z)


# Main function
def main():
    global window  # noqa comment

    # Initialize GLFW
    if not glfw.init():
        return

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(800, 600, "Rotating Cube", None, None)
    if not window:
        logger.warning("Terminating Window")
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)

    # Register callbacks
    glfw.set_framebuffer_size_callback(window, frame_buffer_size_callback)

    # Initialize OpenGL
    init()

    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Render here
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Get list of JSON files in the "objects" directory
        objects = [f for f in os.listdir("objects") if f.endswith('.json') or f.endswith('.obj')]

        try:
            for fObject in objects:
                draw_from_files(f"objects/{fObject}")
        except Exception as ERROR:
            logger.error(ERROR)
        else:
            pass

        # Update rotation angles and camera position
        doCameraUpdateAndThings()

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    print("[INFO] Terminating")
    glfw.terminate()


if __name__ == "__main__":
    print("[INFO] Running main")
    main()
else:
    print("[ERROR] __name__ is not __main__")
