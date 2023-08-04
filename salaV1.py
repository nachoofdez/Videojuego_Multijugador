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
DELTA = 30

Der = 0
Izq = 1
Arr = 2
Abj = 3

DELTA_BULLET = 5

class Player():
    def __init__(self, side):
        self.side = side
        
        if side == LEFT_PLAYER:
            self.pos = [20, SIZE[Y]//2]
            self.dir = Der
        else:
            self.pos = [SIZE[X] - 20, SIZE[Y]//2]
            self.dir = Izq

    def get_pos(self):
        return self.pos
    
    def get_dir(self):
        return self.dir

    def get_side(self):
        return self.side

    def moveDown(self):
        self.pos[Y] += DELTA
        self.dir = Abj
        if self.pos[Y] > SIZE[Y]:
            self.pos[Y] = SIZE[Y]
    
    def moveRight(self):
        self.pos[X] += DELTA
        self.dir = Der
        if self.pos[X] > SIZE[X]:
            self.pos[X] = SIZE[X]
            
    def moveUp(self):
        self.pos[Y] -= DELTA
        self.dir = Arr
        if self.pos[Y] < 0:
            self.pos[Y] = 0
    
    def moveLeft(self):
        self.pos[X] -= DELTA
        self.dir = Izq
        if self.pos[X] < 0:
            self.pos[X] = 0

    def __str__(self):
        return f"P<{SIDESSTR[self.side]}, {self.pos}>"

class Bullet():
    def __init__(self, player):
        self.pos=player.get_pos()
        self.direction = player.get_dir()

    def get_pos(self):
        return self.pos

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
        self.players = manager.list( [Player(LEFT_PLAYER), Player(RIGHT_PLAYER)] )
        self.bullets = manager.list( [  ] )
        self.score = manager.list( [0,0] )
        self.running = Value('i', 1) # 1 running
        self.lock = Lock()

    def get_player(self, side):
        return self.players[side]

    def get_bullets(self):
        return list(self.bullets)

    def get_score(self):
        return list(self.score)

    def is_running(self):
        return self.running.value == 1

    def stop(self):
        self.running.value = 0

    def moveUp(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveUp()
        self.players[player] = p
        self.lock.release()

    def moveDown(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveDown()
        self.players[player] = p
        self.lock.release()
    
    def moveLeft(self,player):
        self.lock.acquire()
        p = self.players[player]
        p.moveLeft()
        self.players[player] = p
        self.lock.release()
    
    def moveRight(self,player):
        self.lock.acquire()
        p = self.players[player]
        p.moveRight()
        self.players[player] = p
        self.lock.release()
        
    def createBullet(self, player):
        self.lock.acquire()
        self.bullets.append(Bullet(player))
        self.lock.release()

    def get_info(self):
        
        pos = []
        for x in self.bullets:
            pos.append(x.get_pos())
        info = {
            'pos_bullets': pos,
            'pos_left_player': self.players[LEFT_PLAYER].get_pos(),
            'pos_right_player': self.players[RIGHT_PLAYER].get_pos(),
            'score': list(self.score),
            'is_running': self.running.value == 1
        }
        
        
        return info

    def move_bullets(self):
        self.lock.acquire()
        for i in range(len(self.bullets)):
            bullet = self.bullets[i]
            bullet.update()
            self.bullets[i] = bullet
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
                elif command == "quit":
                    game.stop()
            if side == 1:
                game.move_bullets()
                
            #print(game.get_info()['pos_bullets']) Funciona
                
            conn.send(game.get_info())
            
            #print(len(game.bullets)) Sí se añaden correctamente a la lista de balas
            
            
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

