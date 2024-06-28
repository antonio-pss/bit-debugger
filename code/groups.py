import pygame

from settings import *
from support import *
from sprites import *


class GameSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = vector()
        self.active = False

    def draw(self, target_pos, surface):
        self.offset.x = -(target_pos[0] - surface.get_width() / 2)
        self.offset.y = -(target_pos[1] - surface.get_height() / 2)

        for sprite in self:
            surface.blit(sprite.image, sprite.rect.topleft + self.offset)


class States(pygame.sprite.Group):
    def __init__(self, name):
        super().__init__()
        self.active = False
        self.name = name

    def setup(self, command):
        rows = sql_importer(command)

        if self.name == 'tips':
            Sprite((0, 0), pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA), self)

        for row in rows:
            if self.name == 'tips':
                self.dialog = Dialog(row['text'], 16*3, import_image(*row['surf_path'].split('|')), row['color'], (WINDOW_WIDTH * row['pos_x'], WINDOW_HEIGHT * row['pos_y']), self)
                self.dialog.rect.midbottom = (WINDOW_WIDTH*0.4, WINDOW_HEIGHT)
                Sprite(self.dialog.rect.bottomleft, import_image('..', 'images', 'senior-update', 'senior-dica-update'), self)
            elif self.name == 'questions':
                if row['pos_x'] == 0.5:
                    self.dialog = Dialog(row['text'], 16 * 3, import_image(*row['surf_path'].split('|')), row['color'],(WINDOW_WIDTH * row['pos_x'], WINDOW_HEIGHT * row['pos_y']), self)
                else:
                    Frame((WINDOW_WIDTH * row['pos_x'], WINDOW_HEIGHT * row['pos_y']), import_folder(*row['surf_path'].split('|')), row['text'], self, row['answer'], row['size'])
            else:
                Frame((WINDOW_WIDTH * row['pos_x'], WINDOW_HEIGHT * row['pos_y']), import_folder(*row['surf_path'].split('|')), row['text'], self, None, row['size'])


class Locations(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.timer = Timer(1000)

    def update(self, player, tip, question, questions, game):
        self.timer.update()
        key = pygame.key.get_just_pressed()[pygame.K_e]

        for sprite in self:
            if player.rect.colliderect(sprite.rect):
                if sprite.text == 'tip' and not self.timer:
                    self.timer.activate()
                    PressText('Aperte E para ver a dica.', 16, 'white', sprite.rect.midtop, game)
                if sprite.text == 'tip' and key:
                    tip.empty()
                    tip.setup(f"select * from frame f inner join display d on f.id_display = d.id "
                              f"where d.name = 'Tip' and d.level = {LEVEL} and d.number = {sprite.number}")
                    tip.active = True
                elif sprite.text == 'question' and questions < sprite.number:
                    question.empty()
                    question.setup(f"select * from frame f inner join display d on f.id_display = d.id "
                                   f"where d.name = 'Question' and d.level = {LEVEL} and d.number = {sprite.number}")
                    question.active = True
