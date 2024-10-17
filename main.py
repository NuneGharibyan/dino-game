import math
import os
import random
import sys

import pygame

WIDTH = 623
HEIGHT = 250

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
pygame.display.set_caption('Dino')

class BG:

    def __init__(self, x):
        self.width = WIDTH
        self.height = HEIGHT
        self.x = x
        self.y = 0
        self.set_texture()
        self.show()

    def update(self, dx):
        self.x += dx
        if self.x <= -WIDTH:
            self.x = WIDTH

    def show(self):
        screen.blit(self.texture, (self.x, self.y))

    def set_texture(self):
        path = os.path.join('assets/images/bg.png')
        self.texture = pygame.image.load(path)
        self.texture = pygame.transform.scale(self.texture, (self.width, self.height))

class Dino:

    def __init__(self):
        self.width = 100
        self.height = 90
        self.x = 10
        self.y = 110
        self.current_frame = 0
        self.frames = []
        self.dy = 3
        self.gravity = 1
        self.onground = True
        self.jumping = False
        self.jump_stop = 10
        self.falling = False
        self.fall_stop = self.y
        self.load_sprites()  
        self.show()

    def load_sprites(self):
        path = os.path.join('assets/images/dino3.png')  
        sprite_sheet = pygame.image.load(path).convert_alpha()

        for i in range(3):
            frame = sprite_sheet.subsurface((i * self.width, 0, self.width, self.height))
            self.frames.append(frame)

    def update(self, loops):
        if self.jumping:
            self.y -= self.dy
            if self.y <= self.jump_stop:
                self.fall()
            self.current_frame = 1  
        elif self.falling:
            self.y += self.gravity * self.dy
            if self.y >= self.fall_stop:
                self.stop()
            self.current_frame = 2  
        elif self.onground and loops % 4 == 0:
            self.current_frame = (self.current_frame + 1) % 3  

    def show(self):
        screen.blit(self.frames[self.current_frame], (self.x, self.y))

    def jump(self):
        self.jumping = True
        self.onground = False

    def fall(self):
        self.jumping = False
        self.falling = True

    def stop(self):
        self.falling = False
        self.onground = True

class Cactus:

    def __init__(self, x):
        self.width = 55
        self.height = 90
        self.x = x
        self.y = 120
        self.set_texture()
        self.show()

    def update(self, dx):
        self.x += dx

    def show(self):
        screen.blit(self.texture, (self.x, self.y))

    def set_texture(self):
        path = os.path.join('assets/images/rockTall.png')
        self.texture = pygame.image.load(path)
        self.texture = pygame.transform.scale(self.texture, (self.width, self.height))

class Collision:

    def between(self, obj1, obj2):
        distance = math.sqrt((obj1.x - obj2.x)**2 + (obj1.y - obj2.y)**2)
        return distance < 35

class Score:

    def __init__(self, hs):
        self.hs = hs
        self.act = 0
        self.font = pygame.font.SysFont('monospace', 18)
        self.color = (0, 0, 0)
        self.show()

    def update(self, loops):
        self.act = loops 
        self.check_hs()

    def show(self):
        self.lbl = self.font.render(f'HI {self.hs} {self.act}', 1, self.color)
        lbl_width = self.lbl.get_rect().width
        screen.blit(self.lbl, (WIDTH - lbl_width - 10, 10))


    def check_hs(self):
        if self.act >= self.hs:
            self.hs = self.act

class Game:

    def __init__(self, hs=0):
        self.bg = [BG(x=0), BG(x=WIDTH)]
        self.dino = Dino()
        self.obstacles = []
        self.collision = Collision()
        self.score = Score(hs)
        self.speed = 3
        self.playing = False
        self.set_labels()
        self.spawn_cactus()

    def set_labels(self):
        big_font = pygame.font.SysFont('monospace', 24, bold=True)
        small_font = pygame.font.SysFont('monospace', 18)
        self.big_lbl = big_font.render(f'G A M E  O V E R', 1, (0, 0, 0))
        self.small_lbl = small_font.render(f'press r to restart', 1, (0, 0, 0))

    def start(self):
        self.playing = True

    def over(self):
        screen.blit(self.big_lbl, (WIDTH // 2 - self.big_lbl.get_width() // 2, HEIGHT // 4))
        screen.blit(self.small_lbl, (WIDTH // 2 - self.small_lbl.get_width() // 2, HEIGHT // 2))
        self.playing = False

    def tospawn(self, loops):
        return loops % 100 == 0

    def spawn_cactus(self):
        if len(self.obstacles) > 0:
            prev_cactus = self.obstacles[-1]
            x = random.randint(prev_cactus.x + self.dino.width + 84, WIDTH + prev_cactus.x + self.dino.width + 84)

        else:
            x = random.randint(WIDTH + 100, 1000)

        cactus = Cactus(x)
        self.obstacles.append(cactus)

    def restart(self):
        self.__init__(hs=self.score.hs)

def main():

    game = Game()
    dino = game.dino

    clock = pygame.time.Clock()
    loops = 0
    over = False

    while True:

        if game.playing:

            loops += 1

            for bg in game.bg:
                bg.update(-game.speed)
                bg.show()

            dino.update(loops)
            dino.show()

            if game.tospawn(loops):
                game.spawn_cactus()

            for cactus in game.obstacles:
                cactus.update(-game.speed)
                cactus.show()

                if game.collision.between(dino, cactus):
                   over = True
            
            if over:
                game.over()

            game.score.update(loops)
            game.score.show()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not over:
                        if dino.onground:
                            dino.jump()

                        if not game.playing:
                            game.start()

                if event.key == pygame.K_r:
                    game.restart()
                    dino = game.dino
                    loops = 0
                    over = False

        clock.tick(80)
        pygame.display.update()

main()