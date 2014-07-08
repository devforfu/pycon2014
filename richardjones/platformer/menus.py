import pygame
import kezmenu

from platformer import Game


class Menu(object):
    running = True

    def main(self, screen):
        clock = pygame.time.Clock()
        background = pygame.image.load('background.png')
        menu = kezmenu.KezMenu(
            ['Play!', lambda: Game().main(screen)],
            ['Quit', lambda: setattr(self, 'running', False)],
        )
        menu.x = 200
        menu.y = 100

        while self.running:
            menu.update(pygame.event.get(), clock.tick(30)/1000)
            screen.blit(background, (0, 0))
            menu.draw(screen)
            pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    Menu().main(screen)