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
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption('Bit Debugger')
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'main_menu'

        # Groups
        self.states = {
            'main_menu': States('main_menu'),
            'menu': States('menu'),
            'questions': States('questions'),
            'tip': States('tip')
        }
        self.groups = {
            'game': GameSprites(),
            'collision': pygame.sprite.Group(),
            'enemy': pygame.sprite.Group(),
            'questions_locations': pygame.sprite.Group(),
            'tip_locations': pygame.sprite.Group()
        }

        # Zoom
        self.zoom_scale = 2
        self.internal_surf_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.internal_surf = pygame.Surface(self.internal_surf_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.internal_surf_size_vector = vector(self.internal_surf_size)

        self.gray_background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.gray_background.fill((0, 0, 0, 128))

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
        self.states['main_menu'].setup("select * from frame f inner join display d on f.id_display = d.id where d.name = 'Main Menu'")
        self.states['main_menu'].active = True
        self.states['menu'].setup("select * from frame f inner join display d on f.id_display = d.id where d.name = 'Menu'")

        tmx_map = load_pygame(join('..', 'data', 'maps', 'level.tmx'))
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_height = tmx_map.height * TILE_SIZE

        for x, y, image in tmx_map.get_layer_by_name('Floor').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.groups['game'], self.groups['collision']))

        for x, y, image in tmx_map.get_layer_by_name('Props').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.groups['game'])

        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(pos=(obj.x, obj.y),
                                     frames_walk=self.bit_frames_walk,
                                     frames_jumping=self.bit_frames_jump,
                                     groups=self.groups['game'],
                                     collision_sprites=self.groups['collision'],
                                     enemy_sprites=self.groups['enemy'])
            if obj.name == 'Enemy':
                self.enemy = CI(rect=pygame.FRect(obj.x, obj.y, obj.width, obj.height),
                                frames_walk=self.ci_frames_walk,
                                frames_dead=self.ci_frames_dead,
                                groups=(self.groups['game'], self.groups['enemy']))
            if obj.name == 'Question' or obj.name == 'Tip':
                Question(pos=(obj.x, obj.y),
                         surf=pygame.Surface((obj.width, obj.height)),
                         number=obj.number,
                         groups=self.groups['questions_locations'] if obj.name == 'Question' else self.groups['tip_locations'])

    def check_question(self):
        keys = pygame.key.get_pressed()
        for sprite in self.groups['questions_locations']:
            if sprite.rect.colliderect(self.player.rect):
                Text('Press E to start', 16, 'white', sprite.rect.midtop, self.groups['game'])
                if keys[pygame.K_e]:
                    self.question = True
                    self.setup_questions()

    def check_tip(self):
        keys = pygame.key.get_pressed()
        for sprite in self.groups['tip_locations']:
            if sprite.rect.colliderect(self.player.rect):
                Text('Press E to learn', 16, 'white', sprite.rect.midtop, self.groups['game'])
                if keys[pygame.K_e]:
                    self.tip = True
                    self.setup_tips()

    def setup_questions(self):
        self.question_sprites.empty()
        buttons_text = ['1', '2', '3', '4', 'Return']
        buttons_pos = [(WINDOW_WIDTH * 0.25, WINDOW_HEIGHT * 0.65), (WINDOW_WIDTH * 0.25, WINDOW_HEIGHT * 0.75),
                       (WINDOW_WIDTH * 0.75, WINDOW_HEIGHT * 0.65), (WINDOW_WIDTH * 0.75, WINDOW_HEIGHT * 0.75),
                       (WINDOW_WIDTH * 0.1, WINDOW_HEIGHT * 0.1)]

        for i, button in enumerate(buttons_text):
            Frame(buttons_pos[i], pygame.Surface((200, 50)), button, self.question_sprites)

    def setup_tips(self):
        self.tip_sprites.empty()
        Frame((WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2), pygame.Surface((500, 500)), '', self.tip_sprites)

    def out_border(self):
        if self.player.rect.y > self.level_height + 1000:
            self.player.rect.center = self.player.start_pos

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

    def check_click_tips(self):
        mouse_click = pygame.mouse.get_pressed()[0]
        if mouse_click:
            self.tip = False

    def check(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_button = pygame.mouse.get_pressed()[0]

        for state in self.states.values():
            if state.active:
                for sprite in state:
                    if sprite.rect.collidepoint(mouse_pos) and mouse_button:
                        if state.name == 'main_menu':
                            if sprite.text == 'Start':
                                state.active = False
                            if sprite.text == 'Options':
                                pass
                            if sprite.text == 'Quit':
                                self.running = False
                        elif state.name == 'menu':
                            if sprite.text == 'Resume':
                                state.active = False
                            if sprite.text == 'Restart':
                                self.player.rect.center = self.player.start_pos
                                state.active = False
                            if sprite.text == 'Quit':
                                state.active = False
                                self.states['main_menu'].active = True
                        elif state.name == 'question':
                            if not sprite.answer:
                                self.player.rect.center = self.player.start_pos

    def check_state(self):
        for state in self.states.values():
            if state.active: self.state = state.name

    def pause(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.states['menu'].active = not self.states['menu'].active
            self.display_surface.blit(self.gray_background, (0, 0))

    def run(self):
        while self.running:
            delta = self.clock.tick(FRAMERATE) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.states[self.state].active:
                if self.states[self.state].name == 'main_menu':
                    self.display_surface.fill('#87ceeb')
                self.states[self.state].draw(self.display_surface)
                self.check()
            else:
                self.groups['game'].update(delta)
                self.groups['enemy'].update(delta)
                self.groups['questions_locations'].update(self.player)
                self.out_border()
                self.check_question()
                self.check_tip()
                self.pause()

                self.internal_surf.fill('#87ceeb')
                self.groups['game'].draw(self.player.rect.center, self.internal_surf)

                # Zoom
                scaled_surf = pygame.transform.scale(self.internal_surf, self.internal_surf_size_vector * self.zoom_scale)
                scaled_rect = scaled_surf.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                self.display_surface.blit(scaled_surf, scaled_rect)

            self.check_state()
            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
