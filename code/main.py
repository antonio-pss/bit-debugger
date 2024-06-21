from groups import *
from sprites import *
from support import *
from settings import *


class Game:
    def __init__(self):
        # Setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption('Bit Debugger')
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'main_menu'
        self.questions = 0

        # Groups
        self.states = {
            'main_menu': States('main_menu'),
            'menu': States('menu'),
            'questions': States('questions'),
            'tips': States('tips')}

        self.groups = {
            'game': GameSprites(),
            'collision': pygame.sprite.Group(),
            'enemy': pygame.sprite.Group(),
            'locations': Locations()}

        # Zoom
        self.zoom_scale = 2
        self.internal_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

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
        #self.states['main_menu'].active = True
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
                Sprite(pos=(obj.x, obj.y),
                       surf=pygame.Surface((obj.width, obj.height)),
                       groups=self.groups['locations'],
                       number=obj.number,
                       name='question' if obj.name == 'Question' else 'tip')

    def check_menu(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_button = pygame.mouse.get_pressed()[0]

        for state in self.states.values():
            if state.active:
                for sprite in state:
                    if sprite.rect.collidepoint(mouse_pos) and mouse_button:
                        if state.name == 'main_menu':
                            if sprite.text == 'Start': state.active = False
                            if sprite.text == 'About':
                                pass
                            if sprite.text == 'Quit': self.running = False
                        elif state.name == 'menu':
                            if sprite.text == 'Resume':
                                state.active = False
                            if sprite.text == 'Restart':
                                self.player.rect.center = self.player.start_pos
                                state.active = False
                            if sprite.text == 'Quit':
                                state.active = False
                                self.states['main_menu'].active = True
                        elif state.name == 'questions':
                            if not sprite.answer:
                                self.player.rect.center = self.player.start_pos
                            else:
                                self.questions += 1
                        elif state.name == 'tips': pass

    def check_state(self):
        for state in self.states.values():
            if state.active: self.state = state.name

    def pause(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]: self.states['menu'].active = not self.states['menu'].active

    def run(self):
        while self.running:
            delta = self.clock.tick(FRAMERATE) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.states[self.state].active:
                if self.state == 'main_menu':
                    self.display_surface.fill('#87ceeb')
                self.states[self.state].update()
                self.states[self.state].draw(self.display_surface)
            else:
                self.groups['game'].update(delta, self.level_height)
                self.groups['enemy'].update(delta, self.level_height)
                self.groups['locations'].update(self.player, self.states['tips'], self.states['questions'], self.questions)
                self.pause()

                self.internal_surf.fill('#87ceeb')
                self.groups['game'].draw(self.player.rect.center, self.internal_surf)

                # Zoom
                scaled_surf = pygame.transform.scale(self.internal_surf, vector((WINDOW_WIDTH, WINDOW_HEIGHT)) * self.zoom_scale)
                scaled_rect = scaled_surf.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                self.display_surface.blit(scaled_surf, scaled_rect)

            self.check_menu()
            self.check_state()
            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
