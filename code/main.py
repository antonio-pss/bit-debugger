import asyncio

import pygame
from pygame.math import Vector2 as vector
from pytmx import load_pygame

from groups import GameSprites, Locations, States
from settings import (
    FRAMERATE,
    IS_WEB,
    MAX_DELTA,
    TILE_SIZE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    resource_path,
)
from sprites import CI, Coffee, CoffeeLife, Coin, Player, Sprite
from support import import_folder, import_image


class Game:
    def __init__(self):
        # Setup
        pygame.init()
        flags = 0 if IS_WEB else pygame.FULLSCREEN
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
        pygame.display.set_caption('Bit Debugger')
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'main_menu'
        self.questions = 0

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
        self.internal_size = (
            WINDOW_WIDTH // self.zoom_scale,
            WINDOW_HEIGHT // self.zoom_scale,
        )
        self.internal_surf = pygame.Surface(self.internal_size)

        self.load_assets()
        self.setup()

    def load_assets(self):
        # graphics
        self.bit_frames_walk = import_folder('..', 'images', 'bit', 'bit-walk')
        self.bit_frames_jump = import_folder('..', 'images', 'bit', 'bit-jump')
        self.ci_frames_walk = import_folder('..', 'images', 'enemy', 'ci-walk')
        self.ci_frames_dead = import_folder('..', 'images', 'enemy', 'ci-dead')
        self.background = import_image('..', 'data', 'maps', 'background')
        self.spike = import_image('..', 'images', 'spike')
        self.coins = import_folder('..', 'images', 'coins')
        self.coffee = import_folder('..', 'images', 'coffee')

    def setup(self):
        self.states['main_menu'].setup()
        self.states['main_menu'].active = True
        self.states['menu'].setup()
        self.states['victory'].setup()
        self.states['game_over'].setup()
        self.states['choose'].setup()

        self.grayback = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.grayback.fill((0, 0, 0, 128))
        self.map_movement = 0
        self.map_speed = 60
        self.map_direction = -1

        self.tmx_map = load_pygame(resource_path('data', 'maps', 'map-bitdebugger_2.tmx'))
        self.level_width = self.tmx_map.width * TILE_SIZE
        self.level_height = self.tmx_map.height * TILE_SIZE

        for x, y, _ in self.tmx_map.get_layer_by_name('blocos').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((32, 32), pygame.SRCALPHA), (self.groups['game'], self.groups['collision']))

        for x, y, _ in self.tmx_map.get_layer_by_name('damage').tiles():
            Sprite((x * TILE_SIZE + 6, y * TILE_SIZE + 17), self.spike, (self.groups['game'], self.groups['damage']))

        Sprite((0, 0), self.background, self.groups['game'])

        entities = self.tmx_map.get_layer_by_name('entities')
        for obj in entities:
            if obj.name == 'Player':
                self.player = Player(pos=(obj.x, obj.y),
                                     frames_walk=self.bit_frames_walk,
                                     frames_jumping=self.bit_frames_jump,
                                     groups=self.groups['game'],
                                     collision_sprites=self.groups['collision'],
                                     enemy_sprites=self.groups['enemy'],
                                     damage_sprites=self.groups['damage'])
            elif obj.name in ('Question', 'Tip'):
                Sprite(pos=(obj.x, obj.y),
                       surf=pygame.Surface((obj.width, obj.height)),
                       groups=self.groups['locations'],
                       number=obj.number,
                       name='question' if obj.name == 'Question' else 'tip')

        self.spawn_dynamic_entities()

        for i in range(self.player.hearts):
            Coffee((i*55, 0), self.coffee, self.groups['coffee'], i)

    def spawn_dynamic_entities(self):
        for obj in self.tmx_map.get_layer_by_name('entities'):
            if obj.name == 'Enemy':
                CI(
                    rect=pygame.FRect(obj.x, obj.y, obj.width, obj.height),
                    frames_walk=self.ci_frames_walk,
                    frames_dead=self.ci_frames_dead,
                    groups=(self.groups['game'], self.groups['enemy']),
                )
            elif obj.name == 'Coin':
                Coin((obj.x, obj.y), self.coins, self.groups['game'])
            elif obj.name == 'Coffee':
                CoffeeLife(
                    (obj.x, obj.y),
                    import_image('..', 'images', 'coffee'),
                    self.groups['game'],
                    self.player,
                )

    def restart(self):
        for state in self.states.values():
            state.active = False

        for sprite in list(self.groups['game']):
            if isinstance(sprite, (CI, Coin, CoffeeLife)):
                sprite.kill()

        self.groups['enemy'].empty()
        self.spawn_dynamic_entities()

        self.player.hearts = 5
        self.player.respawn(self.player.start_pos)
        self.player.check_pos = vector(self.player.start_pos)
        self.questions = 0

        for name in ('victory', 'game_over', 'tips', 'questions'):
            self.states[name].empty()

        self.states['victory'].setup()
        self.states['game_over'].setup()

    def check_menu(self, click_pos, escape_pressed):
        for state in self.states.values():
            if state.active:
                if state.name in ('game_over', 'victory') and escape_pressed:
                    self.restart()
                    self.states['main_menu'].active = True
                    return
                if click_pos is None:
                    continue
                for sprite in state:
                    if sprite.rect.collidepoint(click_pos):
                        if state.name == 'main_menu':
                            if sprite.text == 'Começar':
                                state.active = False
                                self.restart()
                            elif sprite.text == 'Sair':
                                self.running = False
                        elif state.name == 'menu':
                            if sprite.text == 'Voltar':
                                state.active = False
                            elif sprite.text == 'Reiniciar':
                                self.restart()
                            elif sprite.text == 'Sair':
                                state.active = False
                                self.states['choose'].active = True
                        elif state.name == 'choose':
                            if sprite.text == 'Sim':
                                state.active = False
                                self.states['main_menu'].active = True
                            elif sprite.text == 'Não':
                                state.active = False
                                self.states['menu'].active = True
                        elif state.name == 'questions':
                            if sprite.name == 'Frame':
                                if not sprite.answer:
                                    self.player.respawn(self.player.check_pos)
                                    state.active = False
                                    self.player.hearts -= 1
                                else:
                                    self.player.check_pos = self.player.rect.center
                                    self.player.hearts = 5
                                    state.active = False
                                    self.questions += 1
                        return

    def check_state(self):
        for state in self.states.values():
            if state.active: self.state = state.name

        if self.player.hearts <= 0:
            self.states['game_over'].active = True

        if self.questions >= 2:
            self.states['victory'].active = True

    def pause(self, escape_pressed):
        if escape_pressed:
            self.states['menu'].active = not self.states['menu'].active

    def draw_game(self):
        self.internal_surf.fill('black')
        self.groups['game'].draw(self.player.rect.center, self.internal_surf)
        pygame.transform.scale(
            self.internal_surf,
            self.display_surface.get_size(),
            self.display_surface,
        )

    async def run(self):
        while self.running:
            delta = min(self.clock.tick(FRAMERATE) / 1000, MAX_DELTA)
            await asyncio.sleep(0)

            click_pos = None
            escape_pressed = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click_pos = event.pos
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    escape_pressed = True

            if self.states[self.state].active:
                if self.state == 'main_menu':
                    self.map_movement += self.map_direction * self.map_speed * delta
                    if self.map_movement < -(self.level_width-WINDOW_WIDTH) or self.map_movement >= 0:
                        self.map_direction *= -1
                        self.map_movement = max(
                            -(self.level_width - WINDOW_WIDTH),
                            min(0, self.map_movement),
                        )
                    self.display_surface.blit(self.background, (self.map_movement, -210))
                    self.display_surface.blit(self.grayback, (0, 0))
                else:
                    self.draw_game()
                    self.display_surface.blit(self.grayback, (0, 0))

                self.states[self.state].update(delta, self.states[self.state])
                self.states[self.state].draw(self.display_surface)
                self.check_menu(click_pos, escape_pressed)
            else:
                self.draw_game()
                self.groups['coffee'].draw(self.display_surface)

                self.groups['game'].update(delta, self.level_height)
                self.groups['enemy'].update(delta, self.level_height)
                self.groups['coffee'].update(self.player.hearts)
                self.groups['locations'].update(self.player, self.states['tips'], self.states['questions'], self.questions, self.groups['game'])
                self.pause(escape_pressed)

            self.check_state()
            pygame.display.update()

        pygame.quit()


async def main():
    game = Game()
    await game.run()


if __name__ == '__main__':
    asyncio.run(main())
