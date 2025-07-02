from logging import config
import pygame
import random
import numpy as np
import json
pygame.init()

with open('config.json', 'r') as file:
    config = json.load(file)


class Particula:
    def __init__(self, x, y, vx, vy, r):
        self.pos = np.array([float(x), float(y)]) 
        self.vel = np.array([vx, vy]) 
        self.raio = r
        self.cor = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )

    def atualizar_posicao(self, dt):
        self.pos += self.vel*dt

# Configurações da janela e de dados constantes
largura = config.get("largura", 800)
altura = config.get("altura", 600)
raio = config.get("raio", 40)
n_particulas = config.get("n_particulas", 90)
vel_min, vel_max = 10, 500.0
lista_particulas = []
print(f"Configurações: largura={largura}, altura={altura}, raio={raio}, n_particulas={n_particulas}")
# Define os atributos de cada partícula
for i in range(n_particulas):
    while True:
        x = random.uniform(raio, largura - raio)
        y = random.uniform(raio, altura - raio)
        while True:
            vx = random.uniform(-vel_max, vel_max)
            vy = random.uniform(-vel_max, vel_max)
            # Opcionalmente, garantir que a velocidade inicial não seja muito baixa
            if abs(vx) > vel_min or abs(vy) > vel_min:
                    break
        pos_ok = True
        for particula in lista_particulas:
            dist = np.linalg.norm(np.array([x, y]) - particula.pos)
            # Garantir que a nova partícula não está sobrepondo alguma partícula existente
            if dist < 2 * raio:
                pos_ok = False
                break
        if pos_ok:
            lista_particulas.append(Particula(x, y, vx, vy, raio))
            break
        
pygame.display.set_caption("Simulador de Partículas")
janela = pygame.display.set_mode((largura, altura))
FPS = 120
clock = pygame.time.Clock()
run = True 
while run:
    dt = clock.tick(FPS)/1000
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            run = False

    janela.fill((255, 255, 255))

    for particula in lista_particulas:
        particula.atualizar_posicao(dt)
        # Verifica colisão com as bordas da janela
        # Se isso acontecer, inverte a componente da velocidade da partícula no eixo normal ao contato, 
        # considerando que as bordas pesam muito mais que as partículas
        if particula.pos[0] - particula.raio <= 0:
            particula.pos[0] = particula.raio
            particula.vel[0] *= -1.0
        elif particula.pos[0] + particula.raio > largura:
            particula.pos[0] = largura - particula.raio
            particula.vel[0] *= -1.0

        if particula.pos[1] - particula.raio < 0:
            particula.pos[1] = particula.raio
            particula.vel[1] *= -1.0
        elif particula.pos[1] + particula.raio > altura:
            particula.pos[1] = altura - particula.raio
            particula.vel[1] *= -1.0

    # Desenha as partículas e seleciona aleatoriamente uma cor para cada uma
    for particula in lista_particulas:
        pygame.draw.circle(janela, particula.cor, 
            (int(particula.pos[0]), int(particula.pos[1])), int(particula.raio))

    # Colisões entre partículas
    for i in range(len(lista_particulas)):
        for j in range(i+1, len(lista_particulas)):
            particula1 = lista_particulas[i]
            particula2 = lista_particulas[j]
            n_direction = particula1.pos - particula2.pos
            dist = np.linalg.norm(n_direction)

            # Só calcula se as partículas estão "encostando" ou se sobrepondo
            # Calcula o versor normal e tangencial à direção entre as partículas
            if dist <= 2 * raio and dist != 0:
                n_uvector = n_direction / dist
                t_uvector = np.array([-n_uvector[1], n_uvector[0]])

                v1 = particula1.vel
                v2 = particula2.vel

                v1n = np.dot(v1, n_uvector)
                v1t = np.dot(v1, t_uvector)
                v2n = np.dot(v2, n_uvector)
                v2t = np.dot(v2, t_uvector)

                # Supondo que as partículas colidem elasticamente, conservando momento linear
                # e energia cinética, e possuem massas iguais:
                v1n_final = v2n
                v2n_final = v1n
                # A soma dos vetores é igual à velocidade resultante
                particula1.vel = v1n_final * n_uvector + v1t * t_uvector
                particula2.vel = v2n_final * n_uvector + v2t * t_uvector

                # Ajusta a posição para evitar sobreposição, erro bem sutil
                sobrepos = 2 * raio - dist
                particula1.pos += n_uvector * (sobrepos / 2)
                particula2.pos -= n_uvector * (sobrepos / 2)

    pygame.display.update()

pygame.quit()
