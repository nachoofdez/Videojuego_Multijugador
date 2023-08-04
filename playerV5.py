from multiprocessing.connection import Client
import traceback
import pygame
import sys

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


#Direcciones hacia donde miran los jugadores
Der = 0
Izq = 1
Arr = 2
Abj = 3


FPS = 30


SIDES = ["left", "right"]
SIDESSTR = ["left", "right"]

class Player():
    def __init__(self, side):
        self.side = side        #Lado del jugador
        self.pos = [None, None]
        self.dir = None         #Ultima direccion del jugador

    def get_pos(self):
        return self.pos
	
    def get_dir(self):
        return self.dir
		
    def get_side(self):
        return self.side

    def set_pos(self, pos):
        self.pos = pos
	
    def set_dir(self,dir):
        self.dir=dir
		
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
        self.bullets_izq = []  #Balas que lanza jugador izq
        self.bullets_dr = []   #Balas que lanza jugador dr
        self.score = [0,0]
        self.running = True

    def get_player(self, side):
        return self.players[side]

    def set_pos_player(self, side, pos): #Actualiza las posiciones de los jugadores
        self.players[side].set_pos(pos)
        
    def set_dir_player(self,side,dir):   #Actualiza las direcciones de los jugadores
        self.players[side].set_dir(dir)
		
    def get_bullets(self):
        return self.bullets

    def set_bullets_pos_izq(self, pos):  #Actualiza las balas del jugador de la izquierda, toma como entrada pos que es la lista de posiciones de las balas
        result = []
        for i in range(len(pos)):
            bala = Bullet()
            bala.set_pos(pos[i])
            result.append(bala)
        self.bullets_izq = result
    
    def set_bullets_pos_dr(self, pos):   #Actualiza las balas del jugador de la derecha
        result = []
        for i in range(len(pos)):
            bala = Bullet()
            bala.set_pos(pos[i])
            result.append(bala)
        self.bullets_dr = result

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score


    def update(self, gameinfo):
        self.set_pos_player(LEFT_PLAYER, gameinfo['pos_left_player']) 
        self.set_pos_player(RIGHT_PLAYER, gameinfo['pos_right_player']) 
        self.set_dir_player(LEFT_PLAYER, gameinfo['dir_left_player']) 
        self.set_dir_player(RIGHT_PLAYER, gameinfo['dir_right_player'])    
        self.set_bullets_pos_izq(gameinfo['pos_bullets_izq']) #Se reciben las posiciones de las balas
        self.set_bullets_pos_dr(gameinfo['pos_bullets_dr'])
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball}>"


class Nave(pygame.sprite.Sprite):
    def __init__(self, player):
      super().__init__()
      #Creamos las distintas imagenes de la nave rotadas
      self.imagen_l = pygame.image.load('nave.png')
      self.imagen_down = pygame.transform.rotate(self.imagen_l,90)
      self.imagen_r = pygame.transform.rotate(self.imagen_l,180)
      self.imagen_up = pygame.transform.rotate(self.imagen_l,270)
      
      self.player = player
      #Se configura la orientacion inicial de la nave en funcion del lado
      if self.player.side == LEFT_PLAYER:
          self.image = self.imagen_r
      else:
          self.image=self.imagen_l
      self.rect = self.image.get_rect()
      self.update()

    def update(self):  #Actualizamos la imagen de la nave segun su direccion y posicion
        pos = self.player.get_pos()
        direc = self.player.get_dir()
        if direc == Der:
            self.image = self.imagen_r
        elif direc == Izq:
            self.image=self.imagen_l
        elif direc == Abj:
            self.image=self.imagen_down
        elif direc == Arr:
            self.image=self.imagen_up
        self.rect.centerx, self.rect.centery = pos

    def __str__(self):
        return f"S<{self.player}>"


class BulletSprite(pygame.sprite.Sprite):
    def __init__(self, bullet):
        super().__init__()
        imagen = pygame.image.load('bala.png')
        self.image = imagen
        self.bullet = bullet
        self.rect = self.image.get_rect()
        pos = self.bullet.get_pos()
        self.rect.centerx, self.rect.centery = pos
        
    
    def update(self):
        pos = self.bullet.get_pos()
        self.rect.centerx, self.rect.centery = pos
    


class Display():
    def __init__(self, game):
        self.game = game
        self.naves = [Nave(self.game.get_player(i)) for i in range(2)]
        #Cremos los distintos grupos de sprites que necesitamos para los collides y para dibujarlos
        self.all_sprites = pygame.sprite.Group()
        self.nave_group = pygame.sprite.Group()
        self.bulls_izq_group = pygame.sprite.Group()
        self.bulls_dr_group = pygame.sprite.Group()
        
        for nave  in self.naves:
            self.all_sprites.add(nave)
            self.nave_group.add(nave)
            
        for bull in game.bullets_izq:
            self.all_sprites.add(BulletSprite(bull))
            self.bulls_izq_group.add(BulletSprite(bull))
        
        for bull in game.bullets_dr:
            self.all_sprites.add(BulletSprite(bull))
            self.bulls_dr_group.add(BulletSprite(bull))

        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.background = pygame.image.load('background2.png')  #Configuramos el fondo de pantalla
        
        

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
        if side==0: #Choque balas derecha con nave izquierda
            if pygame.sprite.spritecollide(self.naves[side],self.bulls_dr_group,True):
                events.append("collide")
        if side==1: #Choque balas izquierda con nave derecha
            if pygame.sprite.spritecollide(self.naves[side],self.bulls_izq_group,True):
                events.append("collide")
                
        return events


    def refresh(self, game):
        
        self.game = game
        self.naves = [Nave(self.game.get_player(i)) for i in range(2)]
        
        # Como solución al problema de crear una bala cuando un jugador dispare o que esta se elimine
        # cuando sale de rango o choca con la roca, el refresh toma como parámetro game y los sprites
        # se vuelven a crear desde cero a partir de game.
        
        all_aux = pygame.sprite.Group() #Grupo de todos los sprites
        nave_aux = pygame.sprite.Group() #Grupo de sprites de la nave
        izq_aux = pygame.sprite.Group() #Grupo de sprites balas izq
        dr_aux = pygame.sprite.Group() #Grupo de sprites balas dr
        
        for nave  in self.naves:
            all_aux.add(nave)
            nave_aux.add(nave)
        
        for bullet in self.game.bullets_izq:
            bull=BulletSprite(bullet)
            all_aux.add(bull)
            izq_aux.add(bull)
        
        for bullet in self.game.bullets_dr:
            bull=BulletSprite(bullet)
            all_aux.add(bull)
            dr_aux.add(bull)
        
        self.bulls_izq_group = izq_aux
        self.bulls_dr_group = dr_aux
        self.all_sprites=all_aux
        self.nave_group = nave_aux
        
        
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
    
    screen = pygame.display.set_mode(SIZE)
    pygame.init() #Iniciamos el juego
    
    #Creamos una pantalla de carga que aparecerá hasta que se conecte el otro jugador
    screen.fill(BLACK) 
    font = pygame.font.Font(None, 36) 
    texto = font.render("Esperando al jugador rival", True, GREEN) 
    background_carga = pygame.image.load('background2.png')
    screen.blit(background_carga, (0, 0))
    screen.blit(texto, (screen.get_width()/2 - texto.get_width()/2, screen.get_height()/2 - texto.get_height()/2 -100))

    pygame.display.flip()

    
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
                game.update(gameinfo)               
                display.refresh(game)
                display.tick()
            score=game.get_score()
            if score[0]>score[1]:
                print('Ganador: Jugador izquierda')
            else:
                print('Ganador:Jugador Derecha')
                    
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
