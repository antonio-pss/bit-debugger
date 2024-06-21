from settings import *
import os


class GameSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = vector()
        self.active = False

    def draw(self, target_pos, surface):
        self.offset.x = -(target_pos[0] - surface.get_width()/2)
        self.offset.y = -(target_pos[1] - surface.get_height()/2)

        for sprite in self:
            surface.blit(sprite.image, sprite.rect.topleft + self.offset)


class States(pygame.sprite.Group):
    def __init__(self, name):
        super().__init__()
        self.active = False
        self.name = name

    def setup(self, command):
        rows = sql_importer(command)

        for row in rows:
            if row['surf_path'] != '':
                Frame((WINDOW_WIDTH * row['pos_x'], WINDOW_HEIGHT * row['pos_y']), import_image(*row['surf_path'].split('|')),
                      row['text'], self)
            else:
                Frame((WINDOW_WIDTH * row['pos_x'], WINDOW_HEIGHT * row['pos_y']), pygame.Surface((200, 50)), row['text'], self)
