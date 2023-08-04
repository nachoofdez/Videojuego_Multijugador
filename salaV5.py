from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys

LEFT_PLAYER = 0
RIGHT_PLAYER = 1
SIDESSTR = ["left", "right"]
SIZE = (700, 525)
X=0
Y=1
DELTA = 20 #Desplazamiento de los jugadores

#Límites de la roca
roca_up = 165
roca_down = 320
roca_r = 425
roca_l = 240

#Direcciones hacia donde miran los jugadores
Der = 0
Izq = 1
Arr = 2
Abj = 3

DELTA_BULLET = 15 #Desplazamiento de la bala

class Player():
    def __init__(self, side):
        self.side = side
        #Inicializamos jugadores
        if side == LEFT_PLAYER:
            self.pos = [20, SIZE[Y]//2]
            self.dir = Der
        else:
            self.pos = [SIZE[X] - 20, SIZE[Y]//2]
            self.dir = Izq

    def get_pos(self):
        return self.pos
    
    def set_pos(self, posicion): #Para actualizar la posición de los jugadores
        self.pos = posicion
    
    def get_dir(self): #Para obtener la dirección hacia donde miran los jugadores
        return self.dir
    
    def set_dir(self,direccion):
        self.dir = direccion
        

    def get_side(self):
        return self.side
    
    #Movimiento jugadores sin que se salgan de los bordes ni entren en la roca
    def moveDown(self):
        self.pos[Y] += DELTA
        self.dir = Abj
        if self.pos[Y] > SIZE[Y]:
            self.pos[Y] = SIZE[Y]
        if self.pos[Y] > roca_up and self.pos[X] < roca_r and self.pos[X] > roca_l and self.pos[Y] < roca_down: #Si está dentro de la roca
            self.pos[Y] = roca_up
    
    def moveRight(self):
        self.pos[X] += DELTA
        self.dir = Der
        if self.pos[X] > SIZE[X]:
            self.pos[X] = SIZE[X]
        if self.pos[X] > roca_l and self.pos[Y] < roca_down and self.pos[Y] > roca_up and self.pos[X] < roca_r:
            self.pos[X] = roca_l 
            
    def moveUp(self):
        self.pos[Y] -= DELTA
        self.dir = Arr
        if self.pos[Y] < 0:
            self.pos[Y] = 0
        if self.pos[Y] < roca_down and self.pos[X] < roca_r and self.pos[X] > roca_l and self.pos[Y] > roca_up:
            self.pos[Y] = roca_down
    
    def moveLeft(self):
        self.pos[X] -= DELTA
        self.dir = Izq
        if self.pos[X] < 0:
            self.pos[X] = 0
        if self.pos[X] < roca_r and self.pos[Y] < roca_down and self.pos[Y] > roca_up and self.pos[X] > roca_l:
            self.pos[X] = roca_r
	
    def __str__(self):
        return f"P<{SIDESSTR[self.side]}, {self.pos}>"

class Bullet():
    def __init__(self, player):
        #Inicializamos bala con posicion y direccion del jugador que dispara
        self.pos=player.get_pos()
        self.direction = player.get_dir()

    def get_pos(self):
        return self.pos
    
    #Movimiento bala en funcion de su direccion
    def update(self):
        if self.direction == Der:
            self.pos[X] += DELTA_BULLET
        elif self.direction == Izq:
            self.pos[X] -= DELTA_BULLET
        elif self.direction == Abj:
            self.pos[Y] += DELTA_BULLET
        else:
            self.pos[Y] -= DELTA_BULLET
        

    def __str__(self):
        return f"B<{self.pos, self.direction}>"

class Game():
    def __init__(self, manager):
        #Inicializamos el juego
        self.players = manager.list( [Player(LEFT_PLAYER), Player(RIGHT_PLAYER)] )
        self.bullets_izq = manager.list( [  ] )
        self.bullets_dr = manager.list( [ ] )
        self.score = manager.list( [0,0] )
        self.running = Value('i', 1) # 1 running
        self.lock = Lock()

    def get_player(self, side):
        return self.players[side]

    def get_bullets_izq(self):
        return list(self.bullets_izq)
    
    def get_bullets_dr(self):
        return list(self.bullets_dr)

    def get_score(self):
        return list(self.score)

    def is_running(self):
        return self.running.value == 1

    def stop(self):
        self.running.value = 0
        
        #Movimiento jugadores 
    def moveUp(self, player):
        self.lock.acquire()
        
        ###SECCIÓN CRÍTICA
        p = self.players[player]
        p.moveUp()
        self.players[player] = p
        ##################
        
        self.lock.release()

    def moveDown(self, player):
        self.lock.acquire()
        
        ###SECCIÓN CRÍTICA
        p = self.players[player]
        p.moveDown()
        self.players[player] = p
        ##################
        
        self.lock.release()
    
    def moveLeft(self,player):
        self.lock.acquire()
        
        ###SECCIÓN CRÍTICA
        p = self.players[player]
        p.moveLeft()
        self.players[player] = p
        #################
        
        self.lock.release()
    
    def moveRight(self,player):
        self.lock.acquire()
        
        ###SECCIÓN CRÍTICA
        p = self.players[player]
        p.moveRight()
        self.players[player] = p
        ##################
        
        self.lock.release()
     
    #Se anade una bala al disparar un jugador a su lado correspondiente
    def createBullet(self, player):
        self.lock.acquire()
        
        ###SECCIÓN CRÍTICA
        if player.side == 1:
            self.bullets_dr.append(Bullet(player))
        if player.side == 0:
            self.bullets_izq.append(Bullet(player))
        ##################
            
        self.lock.release()
    
    #Depende de la colision, se suma 1 a un lado del marcador, y se reinicia el juego al principio
    def bull_collide(self, player):
        self.lock.acquire()
        
        ###SECCIÓN CRÍTICA
        if player.side == 0:
            self.score[RIGHT_PLAYER] += 1
        else:
            self.score[LEFT_PLAYER] += 1
            
        if self.score[RIGHT_PLAYER] >3 or self.score[LEFT_PLAYER]>3: #Cuando llegue a 4 el marcador, se termina el juego
        	self.stop()
            
        p = self.players[0]
        p.set_pos([20, SIZE[Y]//2])
        p.set_dir(Der)
        self.players[0] = p
        
        p = self.players[1]
        p.set_pos([SIZE[X] - 20, SIZE[Y]//2])
        p.set_dir(Izq)
        self.players[1] = p
        
        self.bullets_izq[:] = [] #Reiniciamos el conjunto de balas a lista vacía
        self.bullets_dr[:] = []
        ################
        
        self.lock.release()

    def get_info(self):
        self.lock.acquire()
        
        ###SECCIÓN CRÍTICA <- Estamos accediendo a memoria compartida
        #Guardamos las posiciones de balas izq y balas dr en 2 listas, para enviar la informacion
        pos_izq = []
        for x in self.bullets_izq:
            pos_izq.append(x.get_pos())
        pos_dr = []
        for x in self.bullets_dr:
            pos_dr.append(x.get_pos())
        #Informacion que mandamos    
        info = {
            'pos_bullets_izq': pos_izq,
            'pos_bullets_dr': pos_dr,
            'pos_left_player': self.players[LEFT_PLAYER].get_pos(),
            'pos_right_player': self.players[RIGHT_PLAYER].get_pos(),
            'dir_left_player': self.players[LEFT_PLAYER].get_dir(),
            'dir_right_player': self.players[RIGHT_PLAYER].get_dir(),
            'score': list(self.score),
            'is_running': self.running.value == 1
        }
        ################
        
        self.lock.release()
        return info
    
    
    def move_bullets(self):
        self.lock.acquire()
        
        ###SECCIÓN CRÍTICA
        #Si al moverse, se salen de la pantalla o entran en la roca las eliminamos
        for i in reversed(range(len(self.bullets_izq))): #Para las balas izquierda
            bullet = self.bullets_izq[i]
            bullet.update()
            if bullet.pos[X] > roca_l and bullet.pos[Y] < roca_down and bullet.pos[Y] > roca_up and bullet.pos[X] < roca_r: #Si está dentro de la roca
            	del self.bullets_izq[i]
            elif bullet.pos[X] > SIZE[X] or bullet.pos[X] < 0 or bullet.pos[Y] > SIZE[Y] or bullet.pos[Y] < 0: #Si se sale del límite de pantalla borramos la bala para no ocupar memoria de más
                del self.bullets_izq[i]
            else:
                self.bullets_izq[i] = bullet
                
        for i in reversed(range(len(self.bullets_dr))): #Para las balas derecha
            bullet = self.bullets_dr[i]
            bullet.update()
            
            if bullet.pos[X] > roca_l and bullet.pos[Y] < roca_down and bullet.pos[Y] > roca_up and bullet.pos[X] < roca_r:
            	del self.bullets_dr[i]
            elif bullet.pos[X] > SIZE[X] or bullet.pos[X] < 0 or bullet.pos[Y] > SIZE[Y] or bullet.pos[Y] < 0:
                del self.bullets_dr[i]
            
            else:
                self.bullets_dr[i] = bullet
        #################
        
        self.lock.release()


    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.running.value}>"

def player(side, conn, game):
    try:
        print(f"starting player {SIDESSTR[side]}:{game.get_info()}")
        conn.send( (side, game.get_info()) )
        while game.is_running():
            
            
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "up":
                    game.moveUp(side)
                elif command == "down":
                    game.moveDown(side)
                elif command == "right":
                    game.moveRight(side)
                elif command == "left":
                    game.moveLeft(side)
                elif command == "space":
                    game.createBullet(game.players[side])
                elif command == "collide":
                    game.bull_collide(game.players[side])
                elif command == "quit":
                    game.stop()
            if side == 1:
                game.move_bullets()
                
            conn.send(game.get_info())
            
            
            
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")


def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                
                
                if n_player == 2:
                    players[0].start()
                    players[1].start()
                    n_player = 0
                    players = [None, None]
                    game = Game(manager)

    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]

    main(ip_address)

