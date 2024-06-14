from settings import *


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
    def __init__(self, pos, frames_walk, frames_jumping, groups, collision_sprites):
        super().__init__(pos, frames_walk, groups)
        self.flip = False

        # frames
        self.frames_jumping = frames_jumping
        self.frames_walk = frames_walk

        # movement & collision
        self.collision_sprites = collision_sprites
        self.direction = vector()
        self.speed = 400
        self.gravity = 50
        self.on_floor = False

        # timer

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = keys[pygame.K_d] - keys[pygame.K_a]
        if keys[pygame.K_SPACE] and self.on_floor:
            self.direction.y = -20

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
            if sprite.rect.collidrect(self.rect):
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
        # lógica para o personagem virar quando andar
        if self.direction.x:
            self.frame_index += self.animation_speed * delta
            self.flip = self.direction.x < 0
        else:
            self.frame_index = 0

        # lógica para quando o personagem pular
        self.frames = self.frames_walk if self.on_floor else self.frames_jumping

        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        self.image = pygame.transform.flip(self.image, self.flip, False)

    def update(self, delta):
        self.check_floor()
        self.input()
        self.move(delta)
        self.animate(delta)
