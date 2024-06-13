from settings import *


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector()

    def draw(self):
        for sprite in self:
            self.display_surface.blit(sprite.image, sprite.rect)
