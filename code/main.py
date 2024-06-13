import pygame.sprite

from settings import *
from support import *
from sprites import *
from groups import *
from timer import Timer


class Game:
    def __init__(self):
        # Setup
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Bit Debugger')
        self.clock = pygame.time.Clock()
        self.running = True

        # Sprites
        self.player = None

        # Groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

        self.setup()

    def setup(self):
        tmx_map = load_pygame(join('..', 'data', 'maps', 'level.tmx'))

        for x, y, image in tmx_map.get_layer_by_name('Floor').tiles():
            Sprite((x*TILE_SIZE, y*TILE_SIZE), image, (self.all_sprites, self.collision_sprites))

        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                pass
                # self.player = Player((obj.x, obj.y), surf=, self.all_sprites, self.collision_sprites)


    def run(self):
        delta = self.clock.tick(FRAMERATE) / 1000
        while self.running:
            # End
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Update
            self.all_sprites.update(delta)

            # Draw
            self.all_sprites.draw()
            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
