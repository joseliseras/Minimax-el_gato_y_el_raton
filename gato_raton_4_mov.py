import pygame
import random

class JuegoGatoRaton:
    def __init__(self, size): # diferencia entre lista y tuplas
        self.size = size
        self.tablero = [[0 for _ in range(size)] for _ in range(size)]
        self.pos_raton = self.generar_posicion_aleatoria()
        self.pos_gato = self.generar_posicion_aleatoria(exclude=[self.pos_raton])
        self.madriguera = self.generar_posicion_mas_alejada(self.pos_raton)

        self.movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Movimientos solo arriba, abajo, izquierda y derecha

        self.tablero[self.pos_raton[0]][self.pos_raton[1]] = 1
        self.tablero[self.pos_gato[0]][self.pos_gato[1]] = 2
        self.tablero[self.madriguera[0]][self.madriguera[1]] = 3

    def generar_posicion_aleatoria(self, exclude=[]):
        while True:
            pos = (random.randint(0, self.size - 1), random.randint(0, self.size - 1))
            if pos not in exclude:
                return pos

    def generar_posicion_mas_alejada(self, referencia):
        return max(((fila, col) for fila in range(self.size) for col in range(self.size) if (fila, col) != referencia),
                   key=lambda pos: self.distancia(pos, referencia))

    def mover_raton(self, nueva_pos):
        if nueva_pos == self.madriguera:
            self.tablero[self.pos_raton[0]][self.pos_raton[1]] = 0
            self.pos_raton = nueva_pos
            self.tablero[self.pos_raton[0]][self.pos_raton[1]] = 1
            print("¡El ratón ha llegado a la madriguera y ha ganado!")
            return True  # Indica que el ratón ha ganado
        else:
            self.tablero[self.pos_raton[0]][self.pos_raton[1]] = 0
            self.pos_raton = nueva_pos
            self.tablero[self.pos_raton[0]][self.pos_raton[1]] = 1
            return False  # Indica que el juego continúa

    def mover_gato(self):
        movimientos_posibles = self.movimientos_posibles(self.pos_gato, es_raton=False)
        if movimientos_posibles:
            mejor_movimiento = min(movimientos_posibles, key=lambda pos: self.distancia(pos, self.pos_raton))
            if mejor_movimiento == self.pos_raton:
                self.pos_raton = None
            self.tablero[self.pos_gato[0]][self.pos_gato[1]] = -1  # Marcar la casilla anterior del gato como inutilizada (trampa_raton)
            self.pos_gato = mejor_movimiento
            self.tablero[self.pos_gato[0]][self.pos_gato[1]] = 2

    def es_valido(self, pos, es_raton=True):
        fila, columna = pos
        if not (0 <= fila < self.size and 0 <= columna < self.size):
            return False
        if es_raton:
            return self.tablero[fila][columna] in {0, 3}
        return self.tablero[fila][columna] in {0, 1}

    def distancia(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def movimientos_posibles(self, pos, es_raton=True):
        return [(pos[0] + mov[0], pos[1] + mov[1]) for mov in self.movimientos if self.es_valido((pos[0] + mov[0], pos[1] + mov[1]), es_raton)]

    def evaluar_estado(self, pos_raton, pos_gato):
        return self.distancia(pos_raton, pos_gato) - self.distancia(pos_raton, self.madriguera)

    def minimax(self, profundidad, maximizando, pos_raton, pos_gato):
        if self.distancia(pos_raton, pos_gato) == 0:
            return -100 if maximizando else 100
        if profundidad == 0:
            return self.evaluar_estado(pos_raton, pos_gato)

        if maximizando:
            posibles_movimientos = self.movimientos_posibles(pos_raton)
            if not posibles_movimientos:
                return self.evaluar_estado(pos_raton, pos_gato)
            return max(self.minimax(profundidad - 1, False, mov, pos_gato) for mov in posibles_movimientos)
        else:
            posibles_movimientos = self.movimientos_posibles(pos_gato, False)
            if not posibles_movimientos:
                return self.evaluar_estado(pos_raton, pos_gato)
            return min(self.minimax(profundidad - 
                                    1, True, pos_raton, mov) for mov in posibles_movimientos)

    def mejor_movimiento_raton(self):
        movimientos_posibles = self.movimientos_posibles(self.pos_raton)
        if not movimientos_posibles:
            return None
        movimientos_a_madriguera = [mov for mov in movimientos_posibles if mov == self.madriguera]
        if movimientos_a_madriguera:
            return movimientos_a_madriguera[0]
        else:
            return max(movimientos_posibles, key=lambda mov: self.minimax(3, False, mov, self.pos_gato))

def jugar():
    pygame.init()
    size = 8
    ancho_celda = 100
    pantalla = pygame.display.set_mode((size * ancho_celda, size * ancho_celda))
    pygame.display.set_caption("Juego Gato y Ratón")
    reloj = pygame.time.Clock()

    juego = JuegoGatoRaton(size)

    # Ruta para cargar las imágenes y ajustarlas al tamaño de las celdas
    imagen_raton = pygame.image.load('G:/Mi unidad/Penguin Academy/CODEPRO/El gato y el raton/raton.png')
    imagen_raton = pygame.transform.scale(imagen_raton, (ancho_celda, ancho_celda))
    imagen_gato = pygame.image.load('G:/Mi unidad/Penguin Academy/CODEPRO/El gato y el raton/gato.png')
    imagen_gato = pygame.transform.scale(imagen_gato, (ancho_celda, ancho_celda))
    imagen_madriguera = pygame.image.load('G:/Mi unidad/Penguin Academy/CODEPRO/El gato y el raton/madriguera.png')
    imagen_madriguera = pygame.transform.scale(imagen_madriguera, (ancho_celda, ancho_celda))
    imagen_trampa = pygame.image.load('G:/Mi unidad/Penguin Academy/CODEPRO/El gato y el raton/trampa_raton.png')
    imagen_trampa = pygame.transform.scale(imagen_trampa, (ancho_celda, ancho_celda))

    def dibujar_tablero():
        pantalla.fill((255, 255, 255))
        for fila in range(size):
            for col in range(size):
                rect = pygame.Rect(col * ancho_celda, fila * ancho_celda, ancho_celda, ancho_celda)
                pygame.draw.rect(pantalla, (0, 0, 0), rect, 1)
                if juego.tablero[fila][col] == 1:
                    pantalla.blit(imagen_raton, rect.topleft)
                elif juego.tablero[fila][col] == 2:
                    pantalla.blit(imagen_gato, rect.topleft)
                elif juego.tablero[fila][col] == -1:
                    pantalla.blit(imagen_trampa, rect.topleft)
                elif juego.tablero[fila][col] == 3:
                    pantalla.blit(imagen_madriguera, rect.topleft)

    turno_raton = True
    contador_movimientos = 0
    max_movimientos = 50

    while contador_movimientos < max_movimientos:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                

        if turno_raton and juego.pos_raton:
            mejor_movimiento = juego.mejor_movimiento_raton()
            if mejor_movimiento:
                if juego.mover_raton(mejor_movimiento):
                    return contador_movimientos + 1  # El ratón gano
        else:
            juego.mover_gato()
            if juego.pos_raton is None:
                print(f"El gato atrapó al ratón en {contador_movimientos + 1} movimientos!")
                return contador_movimientos + 1

        dibujar_tablero()
        pygame.display.flip()
        reloj.tick(1)

        turno_raton = not turno_raton
        contador_movimientos += 1

    print("El juego ha terminado después de 50 movimientos sin un ganador.")
    pygame.quit()
    return contador_movimientos

movimientos_para_atrapar = jugar()
print(f"Movimientos realizados: {movimientos_para_atrapar}")
