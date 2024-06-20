from settings import *


class GameSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = vector()

    def draw(self, target_pos, surface):
        self.offset.x = -(target_pos[0] - surface.get_width()/2)
        self.offset.y = -(target_pos[1] - surface.get_height()/2)

        for sprite in self:
            surface.blit(sprite.image, sprite.rect.topleft + self.offset)


class States(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.active = False

    def setup(self):
        pass
