import pygame
import psycopg2
from os import walk
import tkinter as tk
from os.path import join
from pytmx import load_pygame
from pygame.math import Vector2 as vector

LEVEL = 1
WINDOW_WIDTH, WINDOW_HEIGHT = tk.Tk().winfo_screenwidth(), tk.Tk().winfo_screenheight()
FRAMERATE = 60
TILE_SIZE = 32

