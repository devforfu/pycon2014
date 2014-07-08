import pygame
import tmx

class Animation:
    def __init__(self, *names):
        self.next_frame = 0
        self.frames = [pygame.image.load(image_name) for image_name in names]

    def next(self):
        self.next_frame += 1
        if self.next_frame == len(self.frames):
            self.next_frame = 0
        return self.frames[self.next_frame]


class Player(pygame.sprite.Sprite):
    def __init__(self, location, *groups):
        super(Player, self).__init__(*groups)
        self.image_left = pygame.image.load('guy-left.png')
        self.image_right = pygame.image.load('guy-right.png')
        self.image = self.image_right
        self.step = 300
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.resting = False
        self.is_dead = False
        self.gun_cooldown = 0
        self.dy = 0
        self.direction = 1

        self.go_left_animation = Animation('left-step1.png', 'guy-left.png', 'left-step2.png')
        self.go_right_animation = Animation('right-step1.png', 'guy-right.png', 'right-step2.png')

    def handle_input(self, dt, game):
        key = pygame.key.get_pressed()
        h = self.step * dt
        not_moving = True
        if key[pygame.K_LEFT]:
            self.direction = -1
            self.rect.x -= h
            # self.image = self.image_left
            self.image = self.go_left_animation.next()
            not_moving = False
        if key[pygame.K_RIGHT]:
            self.direction = 1
            self.rect.x += h
            # self.image = self.image_right
            self.image = self.go_right_animation.next()
            not_moving = False
        if key[pygame.K_SPACE] and self.resting:
            game.jump.play()
            self.dy = -500
        if key[pygame.K_LSHIFT] and not self.gun_cooldown:
            if self.direction > 0:
                Bullet(self.rect.midright, 1, game.sprites)
            else:
                Bullet(self.rect.midleft, -1, game.sprites)
            self.gun_cooldown = 1
            game.shoot.play()

        if not_moving and self.direction == -1:
            self.image = self.image_left
        if not_moving and self.direction == 1:
            self.image = self.image_right
        self.gun_cooldown = max(0, self.gun_cooldown - dt)
        self.dy = min(400, self.dy + 40)
        self.rect.y += self.dy * dt

    def update(self, dt, game):
        last = self.rect.copy()
        self.handle_input(dt, game)
        new = self.rect
        self.resting = False
        # for cell in pygame.sprite.spritecollide(self, game.walls, False):
        for cell in game.tilemap.layers['triggers'].collide(new, 'blockers'):
            blockers = cell['blockers']
            if 'l' in blockers and last.right <= cell.left and new.right > cell.left:
                new.right = cell.left
            if 'r' in blockers and last.left >= cell.right and new.left < cell.right:
                new.left = cell.right
            if 't' in blockers and last.bottom <= cell.top and new.bottom > cell.top:
                self.resting = True
                new.bottom = cell.top
                self.dy = 0
            if 'b' in blockers and last.top >= cell.bottom and new.top < cell.bottom:
                new.top = cell.bottom
                self.dy = 0

        # set the camera to put the player in the middle of the screen
        game.tilemap.set_focus(new.x, new.y)


class Enemy(pygame.sprite.Sprite):
    image = pygame.image.load('enemy.png')
    def __init__(self, location, *groups):
        super(Enemy, self).__init__(*groups)
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.direction = 1

    def update(self, dt, game):
        self.rect.x += self.direction * 100 * dt
        for cell in game.tilemap.layers['triggers'].collide(self.rect, 'reverse'):
            if self.direction > 0:
                self.rect.right = cell.left
            else:
                self.rect.left = cell.right
            self.direction *= -1
            break
        if self.rect.colliderect(game.player.rect):
            game.player.is_dead = True


class Bullet(pygame.sprite.Sprite):
    image = pygame.image.load('bullet.png')
    def __init__(self, location, direction, *groups):
        super(Bullet, self).__init__(*groups)
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.direction = direction
        self.lifespan = 1

    def update(self, dt, game):
        self.lifespan -= 0.5 * dt
        if self.lifespan < 0:
            self.kill()
            return
        self.rect.x += self.direction * 400 * dt

        if pygame.sprite.spritecollide(self, game.enemies, True):
            game.explosion.play()
            self.kill()


class Game(object):
    def main(self, screen):
        clock = pygame.time.Clock()
        background = pygame.image.load('background.png')

        self.tilemap = tmx.load('map-enemies.tmx', screen.get_size())
        self.jump = pygame.mixer.Sound('jump.wav')
        self.shoot = pygame.mixer.Sound('shoot.wav')
        self.explosion = pygame.mixer.Sound('explosion.wav')
        self.sprites = tmx.SpriteLayer()
        self.enemies = tmx.SpriteLayer()
        for enemy in self.tilemap.layers['triggers'].find('enemy'):
            Enemy((enemy.px, enemy.py), self.enemies)
        self.tilemap.layers.append(self.enemies)
        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        self.player = Player((start_cell.px, start_cell.py), self.sprites)
        self.tilemap.layers.append(self.sprites)

        while True:
            dt = clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            self.tilemap.update(dt / 1000., self)
            screen.blit(background, (0, 0))
            self.tilemap.draw(screen)
            pygame.display.flip()

            if self.player.is_dead:
                print('- YOU DIED -')
                return


class ScrolledGroup(pygame.sprite.Group):
    def draw(self, surface):
        for sprite in self.sprites():
            surface.blit(sprite.image,
                (sprite.rect.x - self.camera_x, sprite.rect.y))


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    Game().main(screen)