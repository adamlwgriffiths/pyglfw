# --------------------------------------------------------------------------
# Copyright 2012 Orson Peters. All rights reserved.
#
# Redistribution of this work, with or without modification, is permitted if
# Orson Peters is attributed as the original author or licensor of
# this work, but not in any way that suggests that Orson Peters endorses
# you or your use of the work.
#
# This work is provided by Orson Peters "as is" and any express or implied
# warranties are disclaimed. Orson Peters is not liable for any damage
# arising in any way out of the use of this work.
#
# Bindings updated to GLFW 3 by Adam Griffiths.
# --------------------------------------------------------------------------


__doc__ = """Python bindings for glfw 3 using ctypes.

These bindings are a thin layer over the raw ctypes bindings to the GLFW shared
library. No ctypes code is needed by the user, everything has a pure Python
interface.

Everything works as described in the GLFW reference manual, with a few changes:

 * All glfwFooBar functions should be accessed like glfw.FooBar. All
   GLFW_FOO_BAR constants should be accessed like glfw.FOO_BAR.
 * The functions glfwGetTime, glfwSetTime and glfwSleep are removed because they
   are unnecesarry in Python (use the `time` module).
 * The function glfwGetProcAddress returns the memory location as an integer.
 * Functions returning arguments by having types passed in as a pointer now
   return the values directly without accepting the argument. For example
   `void glfwGetVersion(int *major, int *minor, int *rev);` is wrapped as a
   function called glfw.GetVersion() taking no arguments and returning a tuple
   of 3 integers, respectively major, minor and rev. Similarly,
   glfw.GetWindowSize() returns a tuple of two integers giving the size of the
   window.
 * All of glfwGetVideoModes's arguments have been removed, and it simply returns
   a list of video modes.
 * The GLFWvidmode struct has been replaced with the class vidmode, who's
   member variables have the same names and meaning as GLFWvidmode's.
 * Type/value checking has been added to some functions, for example passing a
   negative size into glfw.OpenWindow raises a ValueError, and passing a list
   into glfw.SetWindowTitle results in a TypeError being raised. This is done
   because GLFW has no error messages, and thus this will ease debugging.
 * glfw.Init does not return an integer indicating the status, instead it
   always returns None and raises an InitError if the initialization failed. The
   same goes for glfw.OpenWindow, except it raises OpeningWindowError.
 * The callback function typedefs have been removed. Instead, callback functions
   can be passed regular Python functions taking the appropriate number of
   arguments.
 * GLFW_KEY_SPACE is removed.
 * The functions/callbacks taking/returning either a latin-1 character or an
   integer in C take and return either a unicode or an int in the wrapper. Any
   integer value < 256 gets converted to a one-character unicode. This is the
   reason why GLFW_KEY_SPACE is removed - for unambigous checking. Otherwise the
   comparison key == GLFW_KEY_SPACE will fail when key == u" ", which is a hard
   situation to debug.
 * The callback set with glfw.SetCharCallback always gets called with a
   one-character unicode string and never with an integer value.
 * glfw.GetJoystickAxes and glfw.GetJoystickButtons only take one parameter, the
   joystick id, and return a list of available data about respectively the axes
   positions and button states.
 * The UserPointer functions are not included.
   
Other than the above changes everything works exactly as in the GLFW reference
manual.
"""

import inspect as _inspect
import ctypes as _ctypes
from ctypes.util import find_library as _find_library

# Python cross-version support
# We support a minimum of version 2.5 - it's final release was in August 2006,
# at the time of this writing that's over 5 years ago. Any older versions are
# not of any interest (not to mention that ctypes was not built-in until 2.5.)

import sys

if sys.version_info.major == 3:
    _unichr = chr
else:
    _unichr = unichr

    
if sys.version_info.major == 2 and sys.version_info.minor < 6:
    def _is_int(obj):
        """Returns True if obj is an int, else False."""
        
        return isinstance(obj, int)


    def _is_real(obj):
        """Returns True if obj is an int or float, else False."""
        
        return isinstance(obj, int) or isinstance(obj, float)


    def _is_callable_nargs(obj, nargs):
        """Returns True if obj is a callable taking nargs positional arguments, False otherwise.
        
        For builtins only the check for callable is made, since builtins can't be inspected for
        the amount of arguments they take.
        """

        try:
            _inspect.getcallargs(obj, *[None for _ in range(nargs)])
        except TypeError:
            # we can't inspect builtins, thus we can't reject them now
            # however we can do a simple "is callable" check
            if not (_inspect.isbuiltin(obj) and callable(obj)):
                return False

        return True

else:
    import numbers as _numbers
    import collections as _collections

    def _is_int(obj):
        """Returns True if obj has numbers.Integral as ABC, else False."""
        
        return isinstance(obj, _numbers.Integral)


    def _is_real(obj):
        """Returns True if obj has numbers.Real as ABC, else False."""
        
        return isinstance(obj, _numbers.Real)


    def _is_callable_nargs(obj, nargs):
        """Returns True if obj is a callable taking nargs positional arguments, False otherwise.
        
        For builtins only the check for callable is made, since builtins can't be inspected for
        the amount of arguments they take.
        """

        try:
            _inspect.getcallargs(obj, *[None for _ in range(nargs)])
        except TypeError:
            if not (_inspect.isbuiltin(obj) and isinstance(obj, _collections.Callable)):
                return False

        return True

del sys


##################
# header defines #
##################

# version info
VERSION_MAJOR = 3
VERSION_MINOR = 0
VERSION_REVISION = 3

GLFW_RELEASE = 0
GLFW_PRESS = 1
GLFW_REPEAT = 2

# keyboard key definitions: 8-bit ISO-8859-1 (Latin 1) encoding is used
# for printable keys (such as A-Z, 0-9 etc), and values above 256
# represent special (non-printable) keys (e.g. F1, Page Up etc)
KEY_UNKNOWN = -1
# KEY_SPACE = 32 # this has been ommited to make all keycodes outside of latin 1
                 # range so we can safely translate all keys < 256 with chr()
                 # without having to worry about users checking for KEY_SPACE

# TODO: there are now new definitions
# ie GLFW_KEY_LEFT_BRACKET
# do we need to handle these a different way?

# function keys
KEY_ESCAPE = 256
KEY_ENTER = 257
KEY_TAB = 258
KEY_BACKSPACE = 259
KEY_INSERT = 260
KEY_DELETE = 261
KEY_RIGHT = 262
KEY_LEFT = 263
KEY_DOWN = 264
KEY_UP = 265
KEY_PAGE_UP = 266
KEY_PAGE_DOWN = 267
KEY_HOME = 268
KEY_END = 269
KEY_CAPS_LOCK = 280
KEY_SCROLL_LOCK = 281
KEY_NUM_LOCK = 282
KEY_PRINT_SCREEN = 283
KEY_PAUSE = 284
KEY_F1 = 290
KEY_F2 = 291
KEY_F3 = 292
KEY_F4 = 293
KEY_F5 = 294
KEY_F6 = 295
KEY_F7 = 296
KEY_F8 = 297
KEY_F9 = 298
KEY_F10 = 299
KEY_F11 = 300
KEY_F12 = 301
KEY_F13 = 302
KEY_F14 = 303
KEY_F15 = 304
KEY_F16 = 305
KEY_F17 = 306
KEY_F18 = 307
KEY_F19 = 308
KEY_F20 = 309
KEY_F21 = 310
KEY_F22 = 311
KEY_F23 = 312
KEY_F24 = 313
KEY_F25 = 314
KEY_KP_0 = 320
KEY_KP_1 = 321
KEY_KP_2 = 322
KEY_KP_3 = 323
KEY_KP_4 = 324
KEY_KP_5 = 325
KEY_KP_6 = 326
KEY_KP_7 = 327
KEY_KP_8 = 328
KEY_KP_9 = 329
KEY_KP_DECIMAL = 330
KEY_KP_DIVIDE = 331
KEY_KP_MULTIPLY = 332
KEY_KP_SUBTRACT = 333
KEY_KP_ADD = 334
KEY_KP_ENTER = 335
KEY_KP_EQUAL = 336
KEY_LEFT_SHIFT = 340
KEY_LEFT_CONTROL = 341
KEY_LEFT_ALT = 342
KEY_LEFT_SUPER = 343
KEY_RIGHT_SHIFT = 344
KEY_RIGHT_CONTROL = 345
KEY_RIGHT_ALT = 346
KEY_RIGHT_SUPER = 347
KEY_MENU = 348
KEY_LAST = KEY_MENU

# Modifier key flags
MOD_SHIFT = 0x0001
MOD_CONTROL = 0x0002
MOD_ALT = 0x0004
MOD_SUPER = 0x0008


# mouse button definitions
MOUSE_BUTTON_1 = 0
MOUSE_BUTTON_2 = 1
MOUSE_BUTTON_3 = 2
MOUSE_BUTTON_4 = 3
MOUSE_BUTTON_5 = 4
MOUSE_BUTTON_6 = 5
MOUSE_BUTTON_7 = 6
MOUSE_BUTTON_8 = 7
MOUSE_BUTTON_LAST = MOUSE_BUTTON_8

# mouse button aliases
MOUSE_BUTTON_LEFT = MOUSE_BUTTON_1
MOUSE_BUTTON_RIGHT = MOUSE_BUTTON_2
MOUSE_BUTTON_MIDDLE = MOUSE_BUTTON_3

# joystick identifiers
JOYSTICK_1 = 0
JOYSTICK_2 = 1
JOYSTICK_3 = 2
JOYSTICK_4 = 3
JOYSTICK_5 = 4
JOYSTICK_6 = 5
JOYSTICK_7 = 6
JOYSTICK_8 = 7
JOYSTICK_9 = 8
JOYSTICK_10 = 9
JOYSTICK_11 = 10
JOYSTICK_12 = 11
JOYSTICK_13 = 12
JOYSTICK_14 = 13
JOYSTICK_15 = 14
JOYSTICK_16 = 15
JOYSTICK_LAST = JOYSTICK_16

# error codes
NOT_INITIALIZED = 0x00010001
NO_CURRENT_CONTEXT = 0x00010002
INVALID_ENUM = 0x00010003
INVALID_VALUE = 0x00010004
OUT_OF_MEMORY = 0x00010005
API_UNAVAILABLE = 0x00010006
VERSION_UNAVAILABLE = 0x00010007
PLATFORM_ERROR = 0x00010008
FORMAT_UNAVAILABLE = 0x00010009

# window attributes
FOCUSED = 0x00020001
ICONIFIED = 0x00020002
RESIZABLE = 0x00020003
VISIBLE = 0x00020004
DECORATED = 0x00020005

RED_BITS = 0x00021001
GREEN_BITS = 0x00021002
BLUE_BITS = 0x00021003
ALPHA_BITS = 0x00021004
DEPTH_BITS = 0x00021005
STENCIL_BITS = 0x00021006
ACCUM_RED_BITS = 0x00021007
ACCUM_GREEN_BITS = 0x00021008
ACCUM_BLUE_BITS = 0x00021009
ACCUM_ALPHA_BITS = 0x0002100A
AUX_BUFFERS = 0x0002100B
STEREO = 0x0002100C
SAMPLES = 0x0002100D
SRGB_CAPABLE = 0x0002100E
REFRESH_RATE = 0x0002100F

CLIENT_API = 0x00022001
CONTEXT_VERSION_MAJOR = 0x00022002
CONTEXT_VERSION_MINOR = 0x00022003
CONTEXT_REVISION = 0x00022004
CONTEXT_ROBUSTNESS = 0x00022005
OPENGL_FORWARD_COMPAT = 0x00022006
OPENGL_DEBUG_CONTEXT = 0x00022007
OPENGL_PROFILE = 0x00022008

OPENGL_API = 0x00030001
OPENGL_ES_API = 0x00030002

NO_ROBUSTNESS = 0
NO_RESET_NOTIFICATION = 0x00031001
LOSE_CONTEXT_ON_RESET = 0x00031002

OPENGL_ANY_PROFILE = 0
OPENGL_CORE_PROFILE = 0x00032001
OPENGL_COMPAT_PROFILE = 0x00032002

CURSOR = 0x00033001
STICKY_KEYS = 0x00033002
STICKY_MOUSE_BUTTONS = 0x00033003

CURSOR_NORMAL = 0x00034001
CURSOR_HIDDEN = 0x00034002
CURSOR_DISABLED = 0x00034003

CONNECTED = 0x00040001
DISCONNECTED = 0x00040002


# gl convenience definitions
GL_TRUE = 0x1
GL_FALSE = 0x0


##############
# structures #
##############

class vidmode(object):
    def __init__(self, width, height, redBits, greenBits, blueBits):
        self.width = width
        self.height = height
        self.redBits = redBits
        self.greenBits = greenBits
        self.blueBits = blueBits
    
    def __repr__(self):
        return "glfw.vidmode({}, {}, {}, {}, {})".format(self.width, self.height, self.redBits, self.greenBits, self.blueBits)
    
    # C vidmode struct
    class _struct(_ctypes.Structure):
        _fields_ = [
            ("width", _ctypes.c_int),
            ("height", _ctypes.c_int),
            ("redBits", _ctypes.c_int),
            ("blueBits", _ctypes.c_int),
            ("greenBits", _ctypes.c_int),
        ]

class gammaramp(object):
    def __init__(self, red, green, blue, size):
        self.red = red
        self.green = green
        self.blue = blue
        self.size = size
    
    def __repr__(self):
        return "glfw.gammaramp({}, {}, {}, {})".format(self.red, self.green, self.blue, self.size)
    
    # C vidmode struct
    class _struct(_ctypes.Structure):
        _fields_ = [
            ("red", _ctypes.POINTER(_ctypes.c_ushort)),
            ("green", _ctypes.POINTER(_ctypes.c_ushort)),
            ("blue", _ctypes.POINTER(_ctypes.c_ushort)),
            ("size", _ctypes.c_int),
        ]


#############
# functions #
#############

# First we define all the appropriate ctypes function definitions, then we write
# Python wrappers for all functions. We write wrapper functions for all
# ctypes functions, regardless if it's necessary or not, to give everything
# a Python feel (call overhead is pretty much irrelevant for a windowing
# library like GLFW.)

import os
import warnings

# load the GLFW shared library
if os.name == "nt":
    try:
        _glfwdll = _ctypes.windll.LoadLibrary(os.path.join(os.path.dirname(os.path.abspath(__file__)), "glfw.dll"))
    except:
        # make dll searching a bit more like windows does it
        # save path
        old_path = os.environ["PATH"]
        
        # add the directory containing the main script to path, if any
        import __main__
        if hasattr(__main__, "__file__") and __main__.__file__:
            os.environ["PATH"] = os.path.dirname(os.path.abspath(__main__.__file__)) + os.pathsep + os.environ["PATH"]
        del __main__
        
        # add cwd to path
        os.environ["PATH"] = os.path.abspath(".") + os.pathsep + os.environ["PATH"]
        
        # try to find the library
        glfw_loc = _find_library("glfw")
        
        # restore old path
        os.environ["PATH"] = old_path
        del old_path
        
        if glfw_loc is None:
            raise RuntimeError("no GLFW shared library found")
        else:
            warnings.warn("no GLFW shared library found in the module directory, using the system's library", RuntimeWarning)
            _glfwdll = _ctypes.windll.LoadLibrary(glfw_loc)
        
        del glfw_loc
else:
    try:
        _glfwdll = _ctypes.cdll.LoadLibrary(os.path.abspath(os.path.join(os.path.dirname(__file__), "libglfw.so")))
    except:
        try:
            _glfwdll = _ctypes.cdll.LoadLibrary(os.path.abspath(os.path.join(os.path.dirname(__file__), "libglfw.dylib")))
        except:
            glfw_loc = _find_library("glfw")
            
            if glfw_loc is None:
                raise RuntimeError("no GLFW shared library found")
            else:
                warnings.warn("no GLFW shared library found in the module directory, using the system's library", RuntimeWarning)
                _glfwdll = _ctypes.cdll.LoadLibrary(glfw_loc)
                
            del glfw_loc
    
# helper function for typedefs
# these are different thanks to different calling conventions
if os.name == "nt":
    func_typedef = _ctypes.WINFUNCTYPE
else:
    func_typedef = _ctypes.CFUNCTYPE
    
del warnings
del os


# helper function for function declarations
# restype before the function, like in C declarations
def func_def(restype, func, *argtypes):
    func.restype = restype
    func.argtypes = list(argtypes)
    
    return func
    
    
# GLFW initialization, termination and version querying
func_def(_ctypes.c_int, _glfwdll.glfwInit)
func_def(None, _glfwdll.glfwTerminate)
func_def(None, _glfwdll.glfwGetVersion, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int))
func_def(_ctypes.c_char_p, _glfwdll.glfwGetVersionString)
func_def(_ctypes.c_void_p, _glfwdll.glfwSetErrorCallback, _ctypes.c_void_p)

# monitors
func_def(_ctypes.POINTER(_ctypes.POINTER(_ctypes.c_int)), _glfwdll.glfwGetMonitors, _ctypes.POINTER(_ctypes.c_int))
func_def(_ctypes.POINTER(_ctypes.c_int), _glfwdll.glfwGetPrimaryMonitor)
func_def(None, _glfwdll.glfwGetMonitorPos, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int))
func_def(None, _glfwdll.glfwGetMonitorPhysicalSize, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int))
func_def(_ctypes.c_char_p, _glfwdll.glfwGetMonitorName, _ctypes.POINTER(_ctypes.c_int))
func_def(_ctypes.c_void_p, _glfwdll.glfwSetMonitorCallback, _ctypes.c_void_p)

# video mode functions
func_def(_ctypes.POINTER(vidmode._struct), _glfwdll.glfwGetVideoModes, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int));
func_def(_ctypes.POINTER(vidmode._struct), _glfwdll.glfwGetVideoMode, _ctypes.POINTER(_ctypes.c_int));

# gamma
func_def(None, _glfwdll.glfwSetGamma, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_float)
func_def(_ctypes.POINTER(gammaramp._struct), _glfwdll.glfwGetGammaRamp, _ctypes.POINTER(_ctypes.c_int))
func_def(None, _glfwdll.glfwSetGammaRamp, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(gammaramp._struct))

# window handling
func_def(None, _glfwdll.glfwDefaultWindowHints)
func_def(None, _glfwdll.glfwWindowHint, _ctypes.c_int, _ctypes.c_int)
func_def(_ctypes.POINTER(_ctypes.c_int), _glfwdll.glfwCreateWindow, _ctypes.c_int, _ctypes.c_int, _ctypes.c_char_p, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int))
func_def(None, _glfwdll.glfwDestroyWindow, _ctypes.POINTER(_ctypes.c_int))
func_def(_ctypes.c_int, _glfwdll.glfwWindowShouldClose, _ctypes.POINTER(_ctypes.c_int))
func_def(None, _glfwdll.glfwSetWindowShouldClose, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int)

func_def(None, _glfwdll.glfwSetWindowTitle, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_char_p)
func_def(None, _glfwdll.glfwGetWindowPos, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int))
func_def(None, _glfwdll.glfwSetWindowPos, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int, _ctypes.c_int)
func_def(None, _glfwdll.glfwGetWindowSize, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int))
func_def(None, _glfwdll.glfwSetWindowSize, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int, _ctypes.c_int)

func_def(None, _glfwdll.glfwGetFramebufferSize, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_int))

func_def(None, _glfwdll.glfwIconifyWindow, _ctypes.POINTER(_ctypes.c_int))
func_def(None, _glfwdll.glfwRestoreWindow, _ctypes.POINTER(_ctypes.c_int))
func_def(None, _glfwdll.glfwShowWindow, _ctypes.POINTER(_ctypes.c_int))
func_def(None, _glfwdll.glfwHideWindow, _ctypes.POINTER(_ctypes.c_int))

func_def(_ctypes.POINTER(_ctypes.c_int), _glfwdll.glfwGetWindowMonitor, _ctypes.POINTER(_ctypes.c_int))
func_def(_ctypes.c_int, _glfwdll.glfwGetWindowAttrib, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int)

#func_def(None, _glfwdll.glfwSetWindowUserPointer, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_void_p)
#func_def(_ctypes.c_void_p, _glfwdll.glfwGetWindowUserPointer, _ctypes.POINTER(_ctypes.c_int))

# we pass callback functions as void pointers because the prototypes are defined at the wrapper functions themselves
func_def(_ctypes.c_void_p, _glfwdll.glfwSetWindowPosCallback, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_void_p)
func_def(_ctypes.c_void_p, _glfwdll.glfwSetWindowSizeCallback, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_void_p)
func_def(_ctypes.c_void_p, _glfwdll.glfwSetWindowCloseCallback, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_void_p)
func_def(_ctypes.c_void_p, _glfwdll.glfwSetWindowRefreshCallback, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_void_p)
func_def(_ctypes.c_void_p, _glfwdll.glfwSetWindowFocusCallback, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_void_p)
func_def(_ctypes.c_void_p, _glfwdll.glfwSetWindowIconifyCallback, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_void_p)
func_def(_ctypes.c_void_p, _glfwdll.glfwSetFramebufferSizeCallback, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_void_p)

# input
func_def(None, _glfwdll.glfwPollEvents)
func_def(None, _glfwdll.glfwWaitEvents)
func_def(_ctypes.c_int, _glfwdll.glfwGetInputMode, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int)
func_def(None, _glfwdll.glfwSetInputMode, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int, _ctypes.c_int)

func_def(_ctypes.c_int, _glfwdll.glfwGetKey, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int)
func_def(_ctypes.c_int, _glfwdll.glfwGetMouseButton, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int)
func_def(None, _glfwdll.glfwGetCursorPos, _ctypes.POINTER(_ctypes.c_int), _ctypes.POINTER(_ctypes.c_double), _ctypes.POINTER(_ctypes.c_double))
func_def(None, _glfwdll.glfwSetCursorPos, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_double, _ctypes.c_double)

func_def(_ctypes.c_void_p, _glfwdll.glfwSetKeyCallback, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_void_p)
func_def(_ctypes.c_void_p, _glfwdll.glfwSetCharCallback, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_void_p)
func_def(_ctypes.c_void_p, _glfwdll.glfwSetMouseButtonCallback, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_void_p)
func_def(_ctypes.c_void_p, _glfwdll.glfwSetCursorPosCallback, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_void_p)
func_def(_ctypes.c_void_p, _glfwdll.glfwSetCursorEnterCallback, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_void_p)
func_def(_ctypes.c_void_p, _glfwdll.glfwSetScrollCallback, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_void_p)

# joystick input
func_def(_ctypes.c_int, _glfwdll.glfwJoystickPresent, _ctypes.c_int)
func_def(_ctypes.POINTER(_ctypes.c_float), _glfwdll.glfwGetJoystickAxes, _ctypes.c_int, _ctypes.POINTER(_ctypes.c_int))
func_def(_ctypes.POINTER(_ctypes.c_ubyte), _glfwdll.glfwGetJoystickButtons, _ctypes.c_int, _ctypes.POINTER(_ctypes.c_int))
func_def(_ctypes.c_char_p, _glfwdll.glfwGetJoystickName, _ctypes.c_int)

# clipboard functions
func_def(None, _glfwdll.glfwSetClipboardString, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_char_p)
func_def(_ctypes.c_char_p, _glfwdll.glfwGetClipboardString, _ctypes.POINTER(_ctypes.c_int))

# context functions
func_def(None, _glfwdll.glfwMakeContextCurrent, _ctypes.POINTER(_ctypes.c_int))
func_def(_ctypes.POINTER(_ctypes.c_int), _glfwdll.glfwGetCurrentContext)
func_def(None, _glfwdll.glfwSwapBuffers, _ctypes.POINTER(_ctypes.c_int))
func_def(None, _glfwdll.glfwSwapInterval, _ctypes.c_int)

# extension support
func_def(_ctypes.c_int, _glfwdll.glfwExtensionSupported, _ctypes.c_char_p)
func_def(_ctypes.c_void_p, _glfwdll.glfwGetProcAddress, _ctypes.c_char_p)



# Normally argument checking is a no-go in Python (duck typing), but we're dealing 
# with a C library here - even worse - one that has no error messages at all, so
# any checking we can do before passing things to C and possibly failing is a must.
# So we accept any real number for sizes, integers where only integers make sense
# (such as channel depths) and only the appropriate integer flags where asked for.


# TODO: replace error checking with glfwSetErrorCallback


# error for failed init
class InitError(Exception):
    pass

# error for failed opening window
class OpeningWindowError(Exception):
    pass


def Init():
    if not _glfwdll.glfwInit():
        raise InitError("couldn't initialize GLFW")

def Terminate():
    _glfwdll.glfwTerminate()

def GetVersionString():
    version = _glfwdll.GetVersionString()
    return str(version.value)

def GetVersion():
    major, minor, rev = _ctypes.c_int(), _ctypes.c_int(), _ctypes.c_int()
    
    _glfwdll.glfwGetVersion(_ctypes.byref(major), _ctypes.byref(minor), _ctypes.byref(rev))
    
    return (major.value, minor.value, rev.value)

def DefaultWindowHints():
    _glfwdll.glfwDefaultWindowHints()

def WindowHint(target, hint):
    if not _is_int(target) or not _is_int(hint):
        raise TypeError("target and hint must be numbers")

    if target not in (
        RESIZABLE, VISIBLE, DECORATED,
        RED_BITS, GREEN_BITS, BLUE_BITS, ALPHA_BITS, DEPTH_BITS, STENCIL_BITS,
        ACCUM_RED_BITS, ACCUM_GREEN_BITS, ACCUM_BLUE_BITS, ACCUM_ALPHA_BITS,
        AUX_BUFFERS, STEREO, SAMPLES, SRGB_CAPABLE, REFRESH_RATE,
        CLIENT_API, OPENGL_FORWARD_COMPAT, OPENGL_PROFILE, OPENGL_DEBUG_CONTEXT,
        CONTEXT_VERSION_MAJOR, CONTEXT_VERSION_MINOR, CONTEXT_ROBUSTNESS,
        ):
        raise ValueError("invalid target parameter")

    _glfwdll.glfwWindowHint(target, hint)

def GetWindowAttrib(window, param):
    if not _is_int(param):
        raise TypeError("param must be a integer")
    
    if not param in (
        FOCUSED, ICONIFIED,
        RESIZABLE, VISIBLE, DECORATED,
        SAMPLES, SRGB_CAPABLE,
        CLIENT_API, OPENGL_FORWARD_COMPAT, OPENGL_PROFILE, OPENGL_DEBUG_CONTEXT,
        CONTEXT_VERSION_MAJOR, CONTEXT_VERSION_MINOR, CONTEXT_ROBUSTNESS,
        CONTEXT_REVISION,
    ):
        raise ValueError("invalid requested parameter")

    return _glfwdll.glfwGetWindowAttrib(window, param)

def CreateWindow(width, height, title, monitor=None, window=None):
    if not _is_real(width) or not _is_real(height):
        raise TypeError("width and height must be numbers")
        
    if width < 0  or height < 0:
        raise ValueError("width and height must be non-negative")
    
    opened = _glfwdll.glfwCreateWindow(int(width), int(height), title, None, None)
    
    if not opened:
        raise OpeningWindowError("couldn't open GLFW window")

    return opened

def DestroyWindow(window):
    _glfwdll.glfwDestroyWindow(window)

def SetWindowTitle(window, title):
    title = title.encode("latin-1")
    
    _glfwdll.glfwSetWindowTitle(window, title)

def GetWindowSize(window):
    width, height = _ctypes.c_int(), _ctypes.c_int()
    
    _glfwdll.glfwGetWindowSize(window, _ctypes.byref(width), _ctypes.byref(height))
    
    return width.value, height.value

def SetWindowSize(window, width, height):
    if not _is_real(width) or not _is_real(height):
        raise TypeError("width and height must be numbers")
    
    if width < 0 or height < 0:
        raise ValueError("width and height must be non-negative")
        
    _glfwdll.glfwSetWindowSize(window, int(width), int(height))

def GetWindowPos(window):
    x, y = _ctypes.c_int(), _ctypes.c_int()
    
    _glfwdll.glfwGetWindowPos(window, _ctypes.byref(x), _ctypes.byref(y))
    
    return x.value, y.value

def SetWindowPos(window, x, y):
    if not _is_real(x) or not _is_real(y):
        raise ValueError("x and y must be numbers")
    
    _glfwdll.glfwSetWindowPos(window, int(x), int(y))

def IconifyWindow(window):
    _glfwdll.glfwIconifyWindow(window)

def RestoreWindow(window):
    _glfwdll.glfwRestoreWindow(window)

def ShowWindow(window):
    _glfwdll.glfwShowWindow(window)

def HideWindow(window):
    _glfwdll.glfwHideWindow(window)

def SwapBuffers(window):
    _glfwdll.glfwSwapBuffers(window)
    
def SwapInterval(interval):
    if not _is_int(interval):
        raise TypeError("interval must be an integer")
        
    if interval < 0:
        raise ValueError("interval must be non-negative")
        
    _glfwdll.glfwSwapInterval(interval)

def MakeContextCurrent(window):
    _glfwdll.glfwMakeContextCurrent(window)

def GetCurrentContext():
    return _glfwdll.glfwGetCurrentContext()

def WindowShouldClose(window):
    return _glfwdll.glfwWindowShouldClose(window)

def SetWindowShouldClose(window, value):
    if not _is_int(value):
        raise TypeError("value must be an integer")

    _glfwdll.glfwSetWindowShouldClose(window, value)

def GetFrambufferSize(window):
    width, height = _ctypes.c_int(), _ctypes.c_int()

    _glfwdll.glfwGetFramebufferSize(window, _ctypes.byref(width), _ctypes.byref(height))

    return int(width.value), int(height.value)

def SetWindowPosCallback(window, func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 3):
            raise TypeError("incompatible callback (a callable taking three arguments is required)")
            
        callback = SetWindowPosCallback._callbacktype(func)
    
    # we must keep a reference
    SetWindowPosCallback._callback = callback
    _glfwdll.glfwSetWindowPosCallback(window, _ctypes.cast(callback, _ctypes.c_void_p))

def SetWindowSizeCallback(window, func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 3):
            raise TypeError("incompatible callback (a callable taking three arguments is required)")
            
        callback = SetWindowSizeCallback._callbacktype(func)
    
    # we must keep a reference
    SetWindowSizeCallback._callback = callback
    _glfwdll.glfwSetWindowSizeCallback(window, _ctypes.cast(callback, _ctypes.c_void_p))
    

def SetWindowCloseCallback(window, func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 1):
            raise TypeError("incompatible callback (a callable taking one argument is required)")
            
        callback = SetWindowCloseCallback._callbacktype(lambda: bool(func()))
        
    SetWindowCloseCallback._callback = callback
    _glfwdll.glfwSetWindowCloseCallback(window, _ctypes.cast(callback, _ctypes.c_void_p))


def SetWindowRefreshCallback(window, func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 1):
            raise TypeError("incompatible callback (a callable taking one argument is required)")
        
        callback = SetWindowRefreshCallback._callbacktype(func)
        
    SetWindowRefreshCallback._callback = callback
    _glfwdll.glfwSetWindowRefreshCallback(window, _ctypes.cast(callback, _ctypes.c_void_p))

def SetWindowFocusCallback(window, func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 2):
            raise TypeError("incompatible callback (a callable taking two arguments is required)")
        
        callback = SetWindowFocusCallback._callbacktype(func)
        
    SetWindowFocusCallback._callback = callback
    _glfwdll.glfwSetWindowFocusCallback(window, _ctypes.cast(callback, _ctypes.c_void_p))

def SetWindowIconifyCallback(window, func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 2):
            raise TypeError("incompatible callback (a callable taking two arguments is required)")
        
        callback = SetWindowIconifyCallback._callbacktype(func)
        
    SetWindowIconifyCallback._callback = callback
    _glfwdll.glfwSetWindowIconifyCallback(window, _ctypes.cast(callback, _ctypes.c_void_p))

def SetFramebufferSizeCallback(window, func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 3):
            raise TypeError("incompatible callback (a callable taking three arguments is required)")
        
        callback = SetFramebufferSizeCallback._callbacktype(func)
        
    SetFramebufferSizeCallback._callback = callback
    _glfwdll.glfwSetFramebufferSizeCallback(window, _ctypes.cast(callback, _ctypes.c_void_p))

def SetErrorCallback(func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 2):
            raise TypeError("incompatible callback (a callable taking two arguments is required)")
        
        callback = SetErrorCallback._callbacktype(func)
        
    SetErrorCallback._callback = callback
    _glfwdll.glfwSetErrorCallback(_ctypes.cast(callback, _ctypes.c_void_p))

def SetMonitorCallback(func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 2):
            raise TypeError("incompatible callback (a callable taking two arguments is required)")
        
        callback = SetMonitorCallback._callbacktype(func)
        
    SetMonitorCallback._callback = callback
    _glfwdll.glfwSetMonitorCallback(_ctypes.cast(callback, _ctypes.c_void_p))

def GetMonitors():
    num_monitors = _ctypes.c_int()

    monitors = _glfwdll.glfwGetMonitors(_ctypes.byref(num_monitors))

    return [monitors[i] for i in range(num_monitors.value)]

def GetPrimaryMonitor():
    monitor = _glfwdll.glfwGetPrimaryMonitor()
    return monitor

def GetMonitorPos(monitor):
    x, y = _ctypes.c_int(), _ctypes.c_int()

    _glfwdll.glfwGetMonitorPos(monitor, _ctypes.byref(x), _ctypes.byref(y))

    return int(x.value), int(y.value)

def GetMonitorPhysicalSize(monitor):
    width, height = _ctypes.c_int(), _ctypes.c_int()

    _glfwdll.glfwGetMonitorPhysicalSize(monitor, _ctypes.byref(width), _ctypes.byref(height))

    return int(width.value), int(height.value)

def GetMonitorName(monitor):
    return _glfwdll.glfwGetMonitorName(monitor)

def GetWindowMonitor(window):
    return _glfwdll.glfwGetWindowMonitor(window)

def GetVideoModes(monitor):
    num_modes = _ctypes.c_int()

    video_modes = _glfwdll.glfwGetVideoModes(monitor, _ctypes.byref(num_modes))

    result = []
    for i in range(num_modes.value):
        video_mode = video_modes[i]
        result.append(vidmode(video_mode.width, video_mode.height, video_mode.redBits, video_mode.greenBits, video_mode.blueBits))

    return result

def GetVideoMode(monitor):
    video_mode = _glfwdll.glfwGetVideoMode(monitor)

    if bool(video_mode):
        video_mode = video_mode[0]
        return vidmode(video_mode.width, video_mode.height, video_mode.redBits, video_mode.greenBits, video_mode.blueBits)
    return None

def SetGamma(monitor, gamma):
    _glfwdll.glfwSetGamma(monitor, _ctypes.c_float(gamma))

def GetGammaRamp(monitor):
    gamma = _glfwdll.glfwGetGammaRamp(monitor)

    if bool(gamma):
        gamma = gamma[0]
        return gammaramp(gamma.red[0], gamma.green[0], gamma.blue[0], gamma.size)
    return None

def SetGammaRamp(monitor, gamma):
    _glfwdll.glfwSetGammaRamp(monitor, _ctypes.byref(gamma._struct))

def PollEvents():
    _glfwdll.glfwPollEvents()

def WaitEvents():
    _glfwdll.glfwWaitEvents()

def GetKey(window, key):
    try:
        # passed a string?
        key = ord(key.encode("latin-1").upper())
    except:
        # must be an integer, no?
        if not key in GetKey._legal_keycodes:
            raise ValueError("key must be one of the keycodes or a one-character latin-1 string")
    print key
    result = _glfwdll.glfwGetKey(window, key)
    print result
    return result
    #return _glfwdll.glfwGetKey(window, key)

# too tedious to repeat here, use locals()
GetKey._legal_keycodes = set([code for var, code in list(globals().items()) if var.startswith("KEY_") or var.startswith("MOD_")])
GetKey._legal_keycodes.remove(KEY_UNKNOWN)
try:
	del var, code
except NameError: # not in all versions these "leak"
	pass

def GetMouseButton(window, button):
    if not _is_int(button):
        raise TypeError("button must be a integer")
        
    if not button in (MOUSE_BUTTON_1, MOUSE_BUTTON_2, MOUSE_BUTTON_3, MOUSE_BUTTON_4,
                      MOUSE_BUTTON_5, MOUSE_BUTTON_6, MOUSE_BUTTON_7, MOUSE_BUTTON_8):
        raise ValueError("button must be one of the button codes")
    
    return _glfwdll.glfwGetMouseButton(window, button)

def GetCursorPos(window):
    x, y = _ctypes.c_double(), _ctypes.c_double()
    
    _glfwdll.glfwGetCursorPos(window, _ctypes.byref(x), _ctypes.byref(y))
    
    return int(x.value), int(y.value)

def SetCursorPos(window, x, y):
    if not _is_real(x) or not _is_real(y):
        raise TypeError("x and y should be numbers")
    x, y = _ctypes.c_double(x), _ctypes.c_double(y)
    
    _glfwdll.glfwSetCursorPos(window, x, y)

def SetKeyCallback(window, func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 5):
            raise TypeError("incompatible callback (a callable taking five arguments is required)")
        
        callback = SetKeyCallback._callbacktype(
            lambda key, scancode, action, mods: func(chr(key) if key < 256 else key, scancode, action, mods)
        )
        
    SetKeyCallback._callback = callback
    _glfwdll.glfwSetKeyCallback(window, _ctypes.cast(callback, _ctypes.c_void_p))

def SetCharCallback(window, func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 3):
            raise TypeError("incompatible callback (a callable taking three arguments is required)")
        
        callback = SetCharCallback._callbacktype(lambda char, action: func(chr(char), action))
        
    SetCharCallback._callback = callback
    _glfwdll.glfwSetCharCallback(window, _ctypes.cast(callback, _ctypes.c_void_p))

def SetMouseButtonCallback(window, func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 4):
            raise TypeError("incompatible callback (a callable taking four arguments is required)")
        
        callback = SetMouseButtonCallback._callbacktype(func)
        
    SetMouseButtonCallback._callback = callback
    _glfwdll.glfwSetMouseButtonCallback(window, _ctypes.cast(callback, _ctypes.c_void_p))

def SetCursorPosCallback(window, func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 3):
            raise TypeError("incompatible callback (a callable taking three arguments is required)")
        
        callback = SetCursorPosCallback._callbacktype(func)
        
    SetCursorPosCallback._callback = callback
    _glfwdll.glfwSetCursorPosCallback(window, _ctypes.cast(callback, _ctypes.c_void_p))

def SetCursorEnterCallback(window, func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 2):
            raise TypeError("incompatible callback (a callable taking two arguments is required)")
        
        callback = SetCursorEnterCallback._callbacktype(func)
        
    SetCursorEnterCallback._callback = callback
    _glfwdll.glfwSetCursorEnterCallback(window, _ctypes.cast(callback, _ctypes.c_void_p))

def SetScrollCallback(window, func):
    if func is None:
        callback = None
    else:
        if not _is_callable_nargs(func, 3):
            raise TypeError("incompatible callback (a callable taking three arguments is required)")
        
        callback = SetScrollCallback._callbacktype(func)
        
    SetScrollCallback._callback = callback
    _glfwdll.glfwSetScrollCallback(window, _ctypes.cast(callback, _ctypes.c_void_p))

def SetClipboardString(window, string):
    s = _ctypes.c_char_p()
    s.value = string

    _glfwdll.glfwSetClipboardString(window, s)

def GetClipboardString(window):
    return _glfwdll.glfwGetClipboardString(window)

def ExtensionSupported(extension):
    return _glfwdll.glfwExtensionSupported(extension.encode("latin-1")) == GL_TRUE

def GetProcAddress(procname):
    return _glfwdll.glfwGetProcAddress(procname.encode("latin-1"))

def JoystickPresent(joy):
    if not _is_int(joy):
        raise TypeError("joystick must be int")
    
    if not joy in set(range(16)):
        raise ValueError("joy must be one of the glfw.JOYSTICK_n constants")

    return _glfwdll.glfwJoystickPresent(joy)

def GetJoystickAxes(joy):
    if not _is_int(joy):
        raise TypeError("joystick must be int")
    
    if not joy in set(range(16)):
        raise ValueError("joy must be one of the glfw.JOYSTICK_n constants")

    num_axes = _ctypes.c_int()

    axes = _glfwdll.glfwGetJoystickAxes(joy, _ctypes.byref(num_axes))

    return [axes[i].value for i in range(num_axes.value)]

def GetJoystickButtons(joy):
    if not _is_int(joy):
        raise TypeError("joystick must be int")
    
    if not joy in set(range(16)):
        raise ValueError("joy must be one of the glfw.JOYSTICK_n constants")

    num_buttons = _ctypes.c_int()

    buttons = _glfwdll.glfwGetJoystickButtons(joy, _ctypes.byref(num_buttons))

    return [buttons[i].value for i in range(num_buttons.value)]

def GetJoystickName(joy):
    if not _is_int(joy):
        raise TypeError("joystick must be int")
    
    if not joy in set(range(16)):
        raise ValueError("joy must be one of the glfw.JOYSTICK_n constants")

    name = _glfwdll.glfwGetJoystickName(joy)
    if not bool(name):
        return None
    return str(name.value)

def SetInputMode(window, mode, value):
    if mode not in (CURSOR, STICKY_KEYS, STICKY_MOUSE_BUTTONS,):
        raise TypeError("mode is not valid")

    if mode == CURSOR:
        if value not in (CURSOR_NORMAL, CURSOR_HIDDEN, CURSOR_DISABLED,):
            raise ValueError("invalid value for mode")
    elif mode in (STICKY_KEYS, STICKY_MOUSE_BUTTONS):
        # must be GL_TRUE or GL_FALSE
        if value not in (0x0, 0x1):
            raise ValueError("value must be GL_TRUE or GL_FALSE")
    
    _glfwdll.glfwSetInputMode(window, mode, value)

def GetInputMode(window, mode):
    if mode not in (CURSOR, STICKY_KEYS, STICKY_MOUSE_BUTTONS):
        raise TypeError("mode is not valid")

    result = _glfwdll.glfwGetInputMode(window, mode)
    return int(result.value)


#####################
# function typedefs #
#####################

SetWindowPosCallback._callbacktype = func_typedef(None, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int, _ctypes.c_int)
SetWindowSizeCallback._callbacktype = func_typedef(None, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int, _ctypes.c_int)
SetWindowCloseCallback._callbacktype = func_typedef(None, _ctypes.POINTER(_ctypes.c_int))
SetWindowRefreshCallback._callbacktype = func_typedef(None, _ctypes.POINTER(_ctypes.c_int))
SetWindowFocusCallback._callbacktype = func_typedef(None, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int)
SetWindowIconifyCallback._callbacktype = func_typedef(None, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int)
SetFramebufferSizeCallback._callbacktype = func_typedef(None, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int, _ctypes.c_int)

SetMonitorCallback._callbacktype = func_typedef(None, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int)

SetKeyCallback._callbacktype = func_typedef(None, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int, _ctypes.c_int, _ctypes.c_int, _ctypes.c_int)
SetCharCallback._callbacktype = func_typedef(None, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int, _ctypes.c_int)

SetMouseButtonCallback._callbacktype = func_typedef(None, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int, _ctypes.c_int)
SetCursorPosCallback._callbacktype = func_typedef(None, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_double, _ctypes.c_double)
SetCursorEnterCallback._callbacktype = func_typedef(None, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_int)
SetScrollCallback._callbacktype = func_typedef(None, _ctypes.POINTER(_ctypes.c_int), _ctypes.c_double, _ctypes.c_double)

SetErrorCallback._callbacktype = func_typedef(None, _ctypes.c_int, _ctypes.c_char_p)


# delete no longer needed helper functions
del func_def
del func_typedef

# load submodules
import glfw.ext
