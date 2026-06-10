import pygame
from pathlib import Path
import sys


IS_WEB = sys.platform == 'emscripten'


def _base_path():
    return Path(__file__).resolve().parents[1]


BASE_PATH = _base_path()


def resource_path(*parts):
    clean_parts = [part for part in parts if part not in ('..', '.')]
    return str(BASE_PATH.joinpath(*clean_parts))


def get_screen_size():
    if not pygame.display.get_init():
        pygame.display.init()

    display_info = pygame.display.Info()
    width = display_info.current_w or 1280
    height = display_info.current_h or 720
    return width, height

LEVEL = 1
QUESTIONS = 0
WINDOW_WIDTH, WINDOW_HEIGHT = (1280, 720) if IS_WEB else get_screen_size()
FRAMERATE = 60
MAX_DELTA = 1 / 20
PHYSICS_STEP = 1 / 120
TILE_SIZE = 32

