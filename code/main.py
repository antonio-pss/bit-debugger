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

        self.load_assets()
        self.setup()

    def load_assets(self):
        # graphics
        self.logo = import_image('..', 'images', 'logo_ex1')
        self.bit_frames_walk = import_folder('..', 'images', 'bit', 'bit-walk')
        self.bit_frames_jump = import_folder('..', 'images', 'bit', 'bit-jump')
        self.ci_frames_walk = import_folder('..', 'images', 'enemy', 'ci', 'ci-walk')
        self.ci_frames_dead = import_folder('..', 'images', 'enemy', 'ci', 'ci-dead')

    def setup(self):
        tmx_map = load_pygame(join('..', 'data', 'maps', 'level.tmx'))
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_height = tmx_map.height * TILE_SIZE

        for x, y, image in tmx_map.get_layer_by_name('Floor').tiles():
            Sprite((x*TILE_SIZE, y*TILE_SIZE), image, (self.all_sprites, self.collision_sprites))

        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(pos=(obj.x, obj.y),
                                     frames_walk=self.bit_frames_walk,
                                     frames_jumping=self.bit_frames_jump,
                                     groups=self.all_sprites,
                                     collision_sprites=self.collision_sprites)

    def out_border(self):
        if self.player.rect.y > self.level_height + 1000:
            self.player.rect.center = self.player.start_pos

    def run(self):
        while self.running:
            delta = self.clock.tick(FRAMERATE) / 1000
            # End
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Update
            self.all_sprites.update(delta)
            self.out_border()

            # Draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
