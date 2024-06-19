import pygame
from pytmx import load_pygame
from pygame.math import Vector2 as vector
from os.path import join
from os import walk
import tkinter as tk

LEVEL = 0
WINDOW_WIDTH, WINDOW_HEIGHT = tk.Tk().winfo_screenwidth(), tk.Tk().winfo_screenheight()
FRAMERATE = 60
TILE_SIZE = 32

