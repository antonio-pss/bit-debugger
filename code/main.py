from settings import *
from sprites import *
from groups import *


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

    def setup(self):
        pass

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
            self.all_sprites.draw(self.player)
            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()