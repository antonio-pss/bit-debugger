import pygame.sprite

from settings import *
from timer import Timer


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)


class AnimatedSprite(Sprite):
    def __init__(self, pos, frames, groups):
        self.frames = frames
        self.frame_index = 0
        self.animation_speed = 10
        super().__init__(pos, self.frames[self.frame_index], groups)

    def animate(self, delta):
        self.frame_index += self.animation_speed * delta
        self.image = self.frames[int(self.frame_index) % len(self.frames)]


class Player(AnimatedSprite):
    def __init__(self, pos, frames_walk, frames_jumping, groups, collision_sprites, enemy_sprites):
        super().__init__(pos, frames_walk, groups)
        self.flip = False

        # frames
        self.frames_jumping = frames_jumping
        self.frames_walk = frames_walk

        # movement & collision
        self.start_pos = pos
        self.collision_sprites = collision_sprites
        self.enemy_sprites = enemy_sprites
        self.direction = vector()
        self.speed = 300
        self.gravity = 50
        self.on_floor = False

        # timer

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = keys[pygame.K_d] - keys[pygame.K_a]
        if keys[pygame.K_SPACE] and self.on_floor:
            self.direction.y = -15

    def move(self, delta):
        # horizontal
        self.rect.x += self.direction.x * self.speed * delta
        self.collision('horizontal')

        # vertical
        self.direction.y += self.gravity * delta
        self.rect.y += self.direction.y
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.rect.right = sprite.rect.left
                    if self.direction.x < 0: self.rect.left = sprite.rect.right
                if direction == 'vertical':
                    if self.direction.y > 0: self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0: self.rect.top = sprite.rect.bottom
                    self.direction.y = 0

    def check_floor(self):
        bottom_rect = pygame.FRect((0, 0), (self.rect.width, 2)).move_to(midtop=self.rect.midbottom)
        self.on_floor = True if bottom_rect.collidelist([sprite.rect for sprite in self.collision_sprites]) >= 0 else False

    def animate(self, delta):
        # personagem virar quando andar
        if self.direction.x:
            self.frame_index += self.animation_speed * delta
            self.flip = self.direction.x < 0
        else:
            self.frame_index = 0

        # personagem pular
        self.frames = self.frames_walk if self.on_floor else self.frames_jumping

        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        self.image = pygame.transform.flip(self.image, self.flip, False)

    def check_enemy_collision(self):
        for enemy in self.enemy_sprites:
            if self.rect.colliderect(enemy.rect):
                if self.rect.bottom < enemy.rect.top + enemy.rect.height / 2 and self.direction.y > 0:
                    enemy.destroy()
                    self.direction.y = -10
                else:
                    self.rect.topleft = self.start_pos

    def update(self, delta):
        self.check_floor()
        self.input()
        self.move(delta)
        self.check_enemy_collision()
        self.animate(delta)


class Enemy(AnimatedSprite):
    def __init__(self, pos, frames_walk, frames_dead, groups):
        super().__init__(pos, frames_walk, groups)
        self.death_timer = Timer(2000, self.kill)

        self.frames_walk = frames_walk
        self.frames_dead = frames_dead

    def destroy(self):
        self.death_timer.activate()
        self.frames = self.frames_dead


class CI(Enemy):
    def __init__(self, rect, frames_walk, frames_dead, groups):
        super().__init__(rect.topleft, frames_walk, frames_dead, groups)
        self.rect.bottomleft = rect.bottomleft
        self.main_rect = rect

        # movement
        self.direction = 1
        self.speed = 100

    def move(self, delta):
        self.rect.x -= self.direction * self.speed * delta

    def constraint(self):
        if not self.main_rect.contains(self.rect):
            self.direction *= -1
            self.frames = [pygame.transform.flip(surf, True, False) for surf in self.frames]

    def update(self, delta):
        self.death_timer.update()
        if not self.death_timer:
            self.move(delta)
        self.animate(delta)
        self.constraint()


class Button(pygame.sprite.Sprite):
    def __init__(self, pos, surf, text, groups):
        super().__init__(groups)
        self.image = surf

        font = pygame.Font(None, 20)
        text_surf = font.render(text, True, 'White')
        text_rect = text_surf.get_frect(center=self.image.get_frect().center)

        self.text = text
        self.image.blit(text_surf, text_rect)
        self.rect = self.image.get_frect(center=pos)


class Question(Sprite):
    def __init__(self, pos, surf, number, groups):
        super().__init__(pos, surf, groups)


class Text(pygame.sprite.Sprite):
    def __init__(self, text, size, color, pos, groups):
        super().__init__(groups)
        self.font = pygame.font.Font(None, size)
        self.image = self.font.render(text, False, color)
        self.rect = self.image.get_frect(center=pos)

        self.timer = Timer(1000, self.kill, None, True)

    def update(self, _):
        self.timer.update()
