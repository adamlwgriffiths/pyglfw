
import time
import os

import glfw
import ctypes


GL_TRUE = 0x1
GL_FALSE = 0x0


def error_callback(code, error):
    print 'Error', code, error

def window_close_callback(window):
    print 'window_close_callback', window

def window_pos_callback(window, x, y):
    print 'window_pos_callback', window, x, y

def window_size_callback(window, width, height):
    print 'window_size_callback', window, width, height

def window_refresh_callback(window):
    print 'window_refresh_callback', window

def window_focus_callback(window, focused):
    print 'window_focus_callback', window, focused

def window_iconify_callback(window, iconified):
    print 'window_iconify_callback', window, iconified

def framebuffer_size_callback(window, width, height):
    print 'framebuffer_size_callback', window, width, height

def monitor_callback(monitor, status):
    print 'monitor_callback', monitor, status

def key_callback(window, key, scancode, action, mods):
    print 'key_callback', window, key, scancode, action, mods

def char_callback(window, char, action):
    print 'char_callback', window, char, action

def mouse_button_callback(window, button, action, mods):
    print 'mouse_button_callback', window, button, action, mods

def cursor_pos_callback(window, x, y):
    print 'cursor_pos_callback', window, x, y

def cursor_enter_callback(window, entered):
    print 'cursor_enter_callback', window, entered

def scroll_callback(window, x, y):
    print 'scroll_callback', window, x, y


glfw.SetErrorCallback(error_callback)
glfw.SetMonitorCallback(monitor_callback)

glfw.Init()



monitors = glfw.GetMonitors()
primary = glfw.GetPrimaryMonitor()
print 'Monitors', monitors
print 'Primary', primary
#assert primary in monitors

for monitor in monitors:
    print 'Monitor', monitor, glfw.GetMonitorName(monitor)
    print 'pos', glfw.GetMonitorPos(monitor)
    print 'size', glfw.GetMonitorPhysicalSize(monitor)

    video_modes = glfw.GetVideoModes(monitor)
    for mode in video_modes:
        print 'video mode', mode

    video_mode = glfw.GetVideoMode(monitor)
    print 'current video mode', video_mode

    gamma_ramp = glfw.GetGammaRamp(monitor)
    print 'gamma ramp', gamma_ramp



glfw.DefaultWindowHints()

glfw.WindowHint(glfw.RESIZABLE, GL_TRUE)
glfw.WindowHint(glfw.DECORATED, GL_FALSE)

window = glfw.CreateWindow(640, 480, "Hello World", primary, None)
window2 = glfw.CreateWindow(640, 480, "Second Window", primary, window)


glfw.SetWindowPosCallback(window, window_pos_callback)
glfw.SetWindowSizeCallback(window, window_size_callback)
glfw.SetWindowRefreshCallback(window, window_refresh_callback)
glfw.SetWindowCloseCallback(window, window_close_callback)
glfw.SetWindowIconifyCallback(window, window_iconify_callback)
glfw.SetWindowFocusCallback(window, window_focus_callback)
glfw.SetFramebufferSizeCallback(window, framebuffer_size_callback)

glfw.SetKeyCallback(window, key_callback)
glfw.SetCharCallback(window, char_callback)

glfw.SetMouseButtonCallback(window, mouse_button_callback)
glfw.SetCursorPosCallback(window, cursor_pos_callback)
glfw.SetCursorEnterCallback(window, cursor_enter_callback)
glfw.SetScrollCallback(window, scroll_callback)


monitor = glfw.GetWindowMonitor(window)
print 'window''s monitor', monitor

glfw.MakeContextCurrent(window)

glfw.SetWindowTitle(window, "I'm a new title")



print 'GetWindowSize', glfw.GetWindowSize(window)
glfw.SetWindowSize(window,1024,768)
assert glfw.GetWindowSize(window) == (1024,768)

print 'GetWindowPos', glfw.GetWindowPos(window)
glfw.SetWindowPos(window,100,100)
assert glfw.GetWindowPos(window) == (100,100), glfw.GetWindowPos(window)

print 'FramebufferSize', glfw.GetFrambufferSize(window)

glfw.IconifyWindow(window)
glfw.RestoreWindow(window)

glfw.HideWindow(window)
glfw.ShowWindow(window)

glfw.SwapBuffers(window)

glfw.SetClipboardString(window, 'hello')
string = glfw.GetClipboardString(window)
assert string == 'hello'

for attrib in (
    'FOCUSED', 'ICONIFIED', 'VISIBLE', 'RESIZABLE', 'DECORATED',
    'CLIENT_API',
    'CONTEXT_VERSION_MAJOR', 'CONTEXT_VERSION_MINOR', 'CONTEXT_REVISION', 'CONTEXT_ROBUSTNESS',
    'OPENGL_FORWARD_COMPAT', 'OPENGL_DEBUG_CONTEXT', 'OPENGL_PROFILE',
):
    glfw_attrib = getattr(glfw, attrib)
    print attrib, glfw.GetWindowAttrib(window, glfw_attrib)

for joy in range(10):
    print 'Joystick', joy, glfw.GetJoystickName(joy)
    print 'present', glfw.JoystickPresent(joy)
    print 'axes', glfw.GetJoystickAxes(joy)


glfw.SetInputMode(window, glfw.STICKY_KEYS, GL_TRUE)

assert 0 == glfw.WindowShouldClose(window)
loop = 0
while not glfw.WindowShouldClose(window):

    glfw.SwapBuffers(window)
    glfw.SwapBuffers(window2)

    if glfw.GetKey(window, glfw.KEY_ESCAPE) == glfw.GLFW_PRESS:
        glfw.SetWindowShouldClose(window, 1)

    if loop >= 10:
        glfw.SetWindowShouldClose(window, 1)
    loop += 1
    time.sleep(1)


glfw.DestroyWindow(window)
glfw.DestroyWindow(window2)

glfw.Terminate()
