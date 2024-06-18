import pygame.sprite

from settings import *
from support import *
from sprites import *
from groups import *
from timer import Timer


class Game:
    def __init__(self):
        # Setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Bit Debugger')
        self.clock = pygame.time.Clock()
        self.running = True
        self.menu = False
        self.question = False

        # Groups
        # Game
        self.game_sprites = GameSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # Menu
        self.menu_sprites = pygame.sprite.Group()

        # Questions
        self.question_locations = pygame.sprite.Group()
        self.question_sprites = pygame.sprite.Group()

        # Tips
        self.tip_locations = pygame.sprite.Group()
        self.tip_sprites = pygame.sprite.Group()

        # Zoom
        self.zoom_scale = 1.60
        self.internal_surf_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.internal_surf = pygame.Surface(self.internal_surf_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_frect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        self.internal_surf_size_vector = vector(self.internal_surf_size)

        self.load_assets()
        self.setup()
        self.setup_menu()

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

        n_question = 0
        n_tip = 0

        for x, y, image in tmx_map.get_layer_by_name('Floor').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.game_sprites, self.collision_sprites))

        for x, y, image in tmx_map.get_layer_by_name('Props').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.game_sprites)

        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(pos=(obj.x, obj.y),
                                     frames_walk=self.bit_frames_walk,
                                     frames_jumping=self.bit_frames_jump,
                                     groups=self.game_sprites,
                                     collision_sprites=self.collision_sprites,
                                     enemy_sprites=self.enemy_sprites)
            if obj.name == 'Enemy':
                self.enemy = CI(rect=pygame.FRect(obj.x, obj.y, obj.width, obj.height),
                                frames_walk=self.ci_frames_walk,
                                frames_dead=self.ci_frames_dead,
                                groups=(self.game_sprites, self.enemy_sprites))
            if obj.name == 'Question' or obj.name == 'Tip':
                Question(pos=(obj.x, obj.y),
                         surf=pygame.Surface((obj.width, obj.height)),
                         number=n_question if obj.name == 'Question' else n_tip,
                         groups=self.question_locations if obj.name == 'Question' else self.tip_locations)
                n_question += 1 if obj.name == 'Question' else n_question
                n_tip += 1 if obj.name == 'Tip' else n_tip

    def setup_menu(self):
        buttons = ['Resume', 'Restart', 'Quit']
        Button((WINDOW_WIDTH/2, WINDOW_HEIGHT/2-150), self.logo, '', self.menu_sprites)

        for i, button in enumerate(buttons):
            Button((WINDOW_WIDTH/2, (WINDOW_HEIGHT/2)+50+i*100), pygame.Surface((200, 50)), button, self.menu_sprites)

        self.gray_background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.gray_background.fill((0, 0, 0, 128))

    def setup_questions(self):
        self.question_sprites.empty()
        buttons_text = ['1', '2', '3', '4', 'Return']
        buttons_pos = [(WINDOW_WIDTH*0.25, WINDOW_HEIGHT*0.65), (WINDOW_WIDTH*0.25, WINDOW_HEIGHT*0.75),
                       (WINDOW_WIDTH*0.75, WINDOW_HEIGHT*0.65), (WINDOW_WIDTH*0.75, WINDOW_HEIGHT*0.75),
                       (WINDOW_WIDTH*0.1, WINDOW_HEIGHT*0.1)]

        for i, button in enumerate(buttons_text):
            Button(buttons_pos[i], pygame.Surface((200, 50)), button, self.question_sprites)

    def out_border(self):
        if self.player.rect.y > self.level_height + 1000:
            self.player.rect.center = self.player.start_pos

    def check_click_menu(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_button = pygame.mouse.get_pressed()[0]

        for sprite in self.menu_sprites:
            if sprite.rect.collidepoint(mouse_pos) and mouse_button:
                if sprite.text == 'Resume':
                    self.menu = False
                elif sprite.text == 'Restart':
                    self.player.rect.center = self.player.start_pos
                    self.menu = False
                elif sprite.text == 'Quit':
                    self.running = False

    def check_click_question(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_button = pygame.mouse.get_pressed()[0]

        for sprite in self.question_sprites:
            if sprite.rect.collidepoint(mouse_pos) and mouse_button:
                if sprite.text == 'Restart':
                    self.player.rect.center = self.player.start_pos
                    self.menu = False
                elif sprite.text == 'Return':
                    self.question = False

    def check_question(self):
        keys = pygame.key.get_pressed()
        for sprite in self.question_locations:
            if sprite.rect.colliderect(self.player.rect):
                Text('Press E to start', 16, 'white', sprite.rect.midtop, self.game_sprites)
                if keys[pygame.K_e]:
                    self.question = True
                    self.setup_questions()

    def check_tip(self):
        keys = pygame.key.get_pressed()
        for sprite in self.tip_locations:
            if sprite.rect.colliderect(self.player.rect):
                Text('Press E to learn', 16, 'white', sprite.rect.midtop, self.game_sprites)

    def pause(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.menu = not self.menu
            self.display_surface.blit(self.gray_background, (0, 0))

    def run(self):
        while self.running:
            delta = self.clock.tick(FRAMERATE) / 1000
            # End
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.menu:
                self.menu_sprites.update()
                self.menu_sprites.draw(self.display_surface)
                self.check_click_menu()
            elif self.question:
                self.question_sprites.update()
                self.question_sprites.draw(self.display_surface)
                self.check_click_question()
            else:
                # Update
                self.game_sprites.update(delta)
                self.enemy_sprites.update(delta)
                self.question_locations.update(self.player)
                self.out_border()
                self.check_question()
                self.check_tip()
                self.pause()

                # Draw
                self.internal_surf.fill('#87ceeb')
                self.game_sprites.draw(self.player.rect.center, self.internal_surf)

                # Zoom
                scaled_surf = pygame.transform.scale(self.internal_surf, self.internal_surf_size_vector * self.zoom_scale)
                scaled_rect = scaled_surf.get_frect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                self.display_surface.blit(scaled_surf, scaled_rect)

            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
