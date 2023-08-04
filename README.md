# Videojuego_Multijugador

Los archivos de Python salaV5.py y playerV5.py consisten en un videojuego multijugador distribuido hecho con las librerías pygame y Multiprocessing. Es importante que las imágenes que se adjuntan estén en la misma carpeta que los archivos Python para poder ejecutar los perogramas.

Para ejecutar los programas, se crea la sala del videojuego en la terminal de un dispositivo de la forma 'python salaV5.py ip_sala', donde ip_sala es la ip del dispositivo donde se ejecuta la sala. Y desde otros dos dispositivos nos conectamos a la sala de la forma 'python playerV5.py ip_sala'.

SOBRE EL VIDEOJUEGO:

Es un juego de dos jugadores.
Cada uno controla una nave que se mueve pulsando las flechas del teclado.
Consiste en impactar al contrincante con una bala que es disparada con la tecla 'espacio' en la dirección en la que te estás moviendo.
Cada vez que un jugador impacta al otro, las posiciones se reinician y sube en una unidad el marcador del jugador correspondiente.
Termina cuando uno de los dos jugadores logra 4 impactos.

SOBRE LOS ARCHIVOS:

salaV5.py se debe ejecutar en una terminal que hará de sala. Esta realizará todas las operaciones aritméticas en función de los eventos que le lleguen de los otros jugadores. De esta forma, la sala lleva toda la información importante acerca del juego.

playerV5.py se ejecuta en la terminal del jugador y toma como argumento la dirección ip de la sala para poder conectarse a ella. Cuando solo se ha conectado un jugador, le aparece una pantalla de carga que pone: 'Esperando al contrincante'. Cuando se conecta el otro jugador el juego comienza inmediatamente. Este programa se encarga de recibir la información.

playerv1.py y salaV1.py son una primera versión del juego sin colisiones de las balas. Tampoco está implementada la eliminación de una bala si sale de rango por lo que con esta versión podría dar problemas de memoria si se dispara.

Las imágenes PNG son para el fondo de pantalla, el proyectil y la nave del jugador.
