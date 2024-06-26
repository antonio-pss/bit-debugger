import pygame

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

        # PlaceHolder
        self.enemy = list()

        # Groups
        self.states = {
            'main_menu': States('main_menu'),
            'menu': States('menu'),
            'victory': States('victory'),
            'game_over': States('game_over'),
            'choose': States('choose'),
            'tips': States('tips'),
            'questions': States('questions'),
        }

        self.groups = {
            'game': GameSprites(),
            'collision': pygame.sprite.Group(),
            'enemy': pygame.sprite.Group(),
            'locations': Locations(),
            'damage': pygame.sprite.Group(),
            'coffee': pygame.sprite.Group()}

        # Zoom
        self.zoom_scale = 2
        self.internal_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        self.load_assets()
        self.setup()

    def load_assets(self):
        # graphics
        self.logo = import_image('..', 'images', 'displays', 'logos', '0')
        self.bit_frames_walk = import_folder('..', 'images', 'bit', 'bit-walk')
        self.bit_frames_jump = import_folder('..', 'images', 'bit', 'bit-jump')
        self.ci_frames_walk = import_folder('..', 'images', 'enemy', 'ci-walk')
        self.ci_frames_dead = import_folder('..', 'images', 'enemy', 'ci-dead')
        self.background = import_image('..', 'data', 'maps', 'background')
        self.btn_small = import_folder('..', 'images', 'displays', 'btn_small')
        self.btn_large = import_folder('..', 'images', 'displays', 'btn_large')
        self.spike = import_image('..', 'images', 'spike')
        self.coins = import_folder('..', 'images', 'coins')
        self.coffee = import_folder('..', 'images', 'coffee')

    def setup(self):
        self.states['main_menu'].setup("select * from frame f inner join display d on f.id_display = d.id where d.name = 'Main Menu'")
        self.states['main_menu'].active = True
        self.states['menu'].setup("select * from frame f inner join display d on f.id_display = d.id where d.name = 'Menu'")
        self.states['victory'].setup("select * from frame f inner join display d on f.id_display = d.id where d.name = 'Victory'")
        self.states['game_over'].setup("select * from frame f inner join display d on f.id_display = d.id where d.name = 'Game Over'")
        self.states['choose'].setup("select * from frame f inner join display d on f.id_display = d.id where d.name = 'Choose'")

        self.grayback = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.grayback.fill((0, 0, 0, 128))
        self.map_movement = 0
        self.map_vector = -1

        tmx_map = load_pygame(join('..', 'data', 'maps', 'map-bitdebugger_2.tmx'))
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_height = tmx_map.height * TILE_SIZE

        for x, y, image in tmx_map.get_layer_by_name('blocos').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((32, 32), pygame.SRCALPHA), (self.groups['game'], self.groups['collision']))

        for x, y, image in tmx_map.get_layer_by_name('damage').tiles():
            Sprite((x * TILE_SIZE + 6, y * TILE_SIZE + 17), self.spike, (self.groups['game'], self.groups['damage']))

        Sprite((0, 0), self.background, self.groups['game'])

        for obj in tmx_map.get_layer_by_name('entities'):
            if obj.name == 'Player':
                self.player = Player(pos=(obj.x, obj.y),
                                     frames_walk=self.bit_frames_walk,
                                     frames_jumping=self.bit_frames_jump,
                                     groups=self.groups['game'],
                                     collision_sprites=self.groups['collision'],
                                     enemy_sprites=self.groups['enemy'],
                                     damage_sprites=self.groups['damage'])
            elif obj.name == 'Enemy':
                self.enemy.append(CI(rect=pygame.FRect(obj.x, obj.y, obj.width, obj.height),
                                frames_walk=self.ci_frames_walk,
                                frames_dead=self.ci_frames_dead,
                                groups=(self.groups['game'], self.groups['enemy'])))
            elif obj.name == 'Question' or obj.name == 'Tip':
                Sprite(pos=(obj.x, obj.y),
                       surf=pygame.Surface((obj.width, obj.height)),
                       groups=self.groups['locations'],
                       number=obj.number,
                       name='question' if obj.name == 'Question' else 'tip')
            elif obj.name == 'Coin':
                Coin(pos=(obj.x, obj.y), frames=self.coins, groups=self.groups['game'])
            elif obj.name == 'Coffee':
                CoffeeLife(pos=(obj.x, obj.y), surf=import_image('..', 'images', 'coffee'), groups=self.groups['game'], player=self.player)

        for i in range(self.player.hearts):
            Coffee((i*55, 0), self.coffee, self.groups['coffee'], i)

    def restart(self):
        self.player.rect.center = self.player.start_pos
        self.player.check_pos = self.player.start_pos
        self.questions = 0
        for sprite in self.enemy:
            sprite.kill()
        self.enemy.clear()

        self.states['victory'].setup(
            "select * from frame f inner join display d on f.id_display = d.id where d.name = 'Victory'")
        self.states['game_over'].setup(
            "select * from frame f inner join display d on f.id_display = d.id where d.name = 'Game Over'")

        tmx_map = load_pygame(join('..', 'data', 'maps', 'map-bitdebugger_2.tmx'))
        for obj in tmx_map.get_layer_by_name('entities'):
            if obj.name == 'Enemy':
                self.enemy.append(CI(rect=pygame.FRect(obj.x, obj.y, obj.width, obj.height),
                                frames_walk=self.ci_frames_walk,
                                frames_dead=self.ci_frames_dead,
                                groups=(self.groups['game'], self.groups['enemy'])))

    def check_menu(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_button = pygame.mouse.get_pressed()[0]
        keys = pygame.key.get_just_pressed()

        for state in self.states.values():
            if state.active:
                if (state.name == 'game_over' or state.name == 'victory') and keys[pygame.K_ESCAPE]:
                    self.questions = 0
                    self.player.hearts = 5
                    state.active = False
                    self.states['main_menu'].active = True
                for sprite in state:
                    if sprite.rect.collidepoint(mouse_pos) and mouse_button:

                        # Main Menu
                        if state.name == 'main_menu':
                            if sprite.text == 'Começar':
                                state.active = False
                                self.restart()
                            if sprite.text == 'Sair': self.running = False

                        # Menu
                        elif state.name == 'menu':
                            if sprite.text == 'Voltar':
                                state.active = False
                            if sprite.text == 'Reiniciar':
                                self.player.rect.center = self.player.start_pos
                                state.active = False
                            if sprite.text == 'Sair':
                                state.active = False
                                self.states['choose'].active = True

                        # Choose
                        elif state.name == 'choose':
                            if sprite.text == 'Sim':
                                state.active = False
                                self.states['main_menu'].active = True
                            if sprite.text == 'Não':
                                state.active = False
                                self.states['menu'].active = True

                        # Questões
                        elif state.name == 'questions':
                            if sprite.name == 'Frame':
                                if not sprite.answer:
                                    self.player.rect.center = self.player.check_pos
                                    state.active = False
                                    self.player.hearts -= 1
                                else:
                                    self.player.check_pos = self.player.rect.center
                                    self.player.hearts = 5
                                    state.active = False
                                    self.questions += 1

    def check_state(self):
        for state in self.states.values():
            if state.active: self.state = state.name

        if self.player.hearts == 0:
            self.states['game_over'].active = True

        if self.questions == 2:
            self.states['victory'].active = True

    def pause(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]: self.states['menu'].active = not self.states['menu'].active

    def run(self):
        while self.running:
            delta = self.clock.tick(FRAMERATE) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            scaled_surf = pygame.transform.scale(self.internal_surf, vector((WINDOW_WIDTH, WINDOW_HEIGHT)) * self.zoom_scale)
            scaled_rect = scaled_surf.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

            if self.states[self.state].active:
                if self.state == 'main_menu':
                    self.map_movement += self.map_vector
                    if self.map_movement < -(self.level_width-WINDOW_WIDTH) or self.map_movement >= 0:
                        self.map_vector *= -1
                    self.display_surface.blit(self.background, (self.map_movement, -210))
                    self.display_surface.blit(self.grayback, (0, 0))
                else:
                    self.groups['game'].draw(self.player.rect.center, self.internal_surf)
                    self.display_surface.blit(scaled_surf, scaled_rect)
                    self.display_surface.blit(self.grayback, (0, 0))

                self.states[self.state].update(delta, self.states[self.state])
                self.states[self.state].draw(self.display_surface)
                self.check_menu()
            else:
                self.internal_surf.fill('black')
                self.groups['game'].draw(self.player.rect.center, self.internal_surf)
                self.display_surface.blit(scaled_surf, scaled_rect)
                self.groups['coffee'].draw(self.display_surface)

                self.groups['game'].update(delta, self.level_height)
                self.groups['enemy'].update(delta, self.level_height)
                self.groups['coffee'].update(self.player.hearts)
                self.groups['locations'].update(self.player, self.states['tips'], self.states['questions'], self.questions, self.groups['game'])
                self.pause()

            self.check_state()
            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
