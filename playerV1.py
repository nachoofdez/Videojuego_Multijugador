from multiprocessing.connection import Client
import traceback
import pygame
import sys, os

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)
X = 0
Y = 1
SIZE = (700, 525)

LEFT_PLAYER = 0
RIGHT_PLAYER = 1
PLAYER_COLOR = [GREEN, YELLOW]
PLAYER_HEIGHT = 20
PLAYER_WIDTH = 20

BALL_COLOR = WHITE
BALL_SIZE = 10
FPS = 30


SIDES = ["left", "right"]
SIDESSTR = ["left", "right"]

class Player():
    def __init__(self, side):
        self.side = side
        self.pos = [None, None]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

class Bullet():
    def __init__(self):
        self.pos=[ None, None ]

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"B<{self.pos}>"


class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.bullets = []
        self.score = [0,0]
        self.running = True

    def get_player(self, side):
        return self.players[side]

    def set_pos_player(self, side, pos):
        self.players[side].set_pos(pos)


    def get_bullets(self):
        return self.bullets

    def set_bullets_pos(self, pos):
        result = []
        for i in range(len(pos)):
            bala = Bullet()
            bala.set_pos(pos[i])
            result.append(bala)
        self.bullets = result

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score


    def update(self, gameinfo):
        self.set_pos_player(LEFT_PLAYER, gameinfo['pos_left_player'])
        self.set_pos_player(RIGHT_PLAYER, gameinfo['pos_right_player'])
        self.set_bullets_pos(gameinfo['pos_bullets'])
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball}>"


class Paddle(pygame.sprite.Sprite):
    def __init__(self, player):
      super().__init__()
      self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
      self.image.fill(BLACK)
      self.image.set_colorkey(BLACK)#drawing the paddle
      self.player = player
      color = PLAYER_COLOR[self.player.get_side()]
      pygame.draw.rect(self.image, color, [0,0,PLAYER_WIDTH, PLAYER_HEIGHT])
      self.rect = self.image.get_rect()
      self.update()

    def update(self):
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos

    def __str__(self):
        return f"S<{self.player}>"


class BulletSprite(pygame.sprite.Sprite):
    def __init__(self, bullet):
        super().__init__()
        
        self.image = pygame.Surface([BALL_SIZE, BALL_SIZE])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        self.bullet = bullet
        pygame.draw.rect(self.image, BALL_COLOR, [0, 0, BALL_SIZE, BALL_SIZE])
        self.rect = self.image.get_rect()
        #self.update()
        pos = self.bullet.get_pos()
        self.rect.centerx, self.rect.centery = pos
        
    
    def update(self):
        pos = self.bullet.get_pos()
        self.rect.centerx, self.rect.centery = pos
    


class Display():
    def __init__(self, game):
        self.game = game
        self.paddles = [Paddle(self.game.get_player(i)) for i in range(2)]
        
        self.all_sprites = pygame.sprite.Group()
        self.paddle_group = pygame.sprite.Group()
        for paddle  in self.paddles:
            self.all_sprites.add(paddle)
            self.paddle_group.add(paddle)
        for bull in game.bullets:
            self.all_sprites.add(BulletSprite(bull))

        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.background = pygame.image.load('background2.png')
        pygame.init()

    def analyze_events(self, side):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
                elif event.key == pygame.K_UP:
                    events.append("up")
                elif event.key == pygame.K_DOWN:
                    events.append("down")
                elif event.key == pygame.K_RIGHT:
                    events.append("right")
                elif event.key == pygame.K_LEFT:
                    events.append("left")
                elif event.key == pygame.K_SPACE:
                    events.append("space")
            elif event.type == pygame.QUIT:
                events.append("quit")
                
        return events


    def refresh(self, game):
        
        self.game = game
        self.paddles = [Paddle(self.game.get_player(i)) for i in range(2)]
        
        all_aux = pygame.sprite.Group()
        paddle_aux = pygame.sprite.Group()
        
        for paddle  in self.paddles:
            all_aux.add(paddle)
            paddle_aux.add(paddle)
        
        for bullet in self.game.bullets:
            bull=BulletSprite(bullet)
            all_aux.add(bull)
            
        self.all_sprites=all_aux
        self.paddles = paddle_aux
        self.screen.blit(self.background, (0, 0))
        score = self.game.get_score()
        font = pygame.font.Font(None, 74)
        text = font.render(f"{score[LEFT_PLAYER]}", 1, WHITE)
        self.screen.blit(text, (250, 10))
        text = font.render(f"{score[RIGHT_PLAYER]}", 1, WHITE)
        self.screen.blit(text, (SIZE[X]-250, 10))
        self.all_sprites.draw(self.screen)
        
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()


def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game()
            side,gameinfo = conn.recv()
            
            print(f"I am playing {SIDESSTR[side]}")
            game.update(gameinfo)
            display = Display(game)
            while game.is_running():
                events = display.analyze_events(side)
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()
                
                #print(gameinfo['pos_bullets']) Correcto
                
                game.update(gameinfo)
                
                #print(len(game.bullets)) Correcto
                
                display.refresh(game)
                display.tick()
                
                
                
                    
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)