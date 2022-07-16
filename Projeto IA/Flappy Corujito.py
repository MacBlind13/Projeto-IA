from cmath import pi
from msilib.schema import Patch
from pathlib import Path
#from locale import ABDAY_1
from re import T
from telnetlib import STATUS
import pygame
import neat
import time
import os
import random
pygame.font.init()

#aplica as medidas da tela do jogo
WIN_WIDTH = 600
WIN_HEIGHT = 800
CHAO = 730
DRAW_LINES = True

#define a tela do jogo
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Corujito")

#Aplica Imagens no jogo
LUZ_IMGS = (pygame.image.load(os.path.join("imgs", "LuzPP2.png"))),(pygame.image.load(os.path.join("imgs", "LuzPP1.png"))),(pygame.image.load(os.path.join("imgs", "LuzPP3.png")))
ARVORE_IMG = (pygame.image.load(os.path.join("imgs", "Pinheiro.png")))
CHAO_IMG =(pygame.image.load(os.path.join("imgs", "chao.png")))
BI_IMG = (pygame.image.load(os.path.join("imgs", "BoilingIsles.jpg")))
STAT_FONT = pygame.font.SysFont("papyrus", 50)
END_FONT = pygame.font.SysFont("papyrus", 70)

gen = 0

class Luz:#Programação Referente a Luz

    ANG_MAX = 25
    IMGS = LUZ_IMGS
    VEL_ANG = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):#Função para controlar a Luz
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def voo(self):#Função para controlar o Voo
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  #Controle da gravidade

        if displacement >= 16:#Velocidade terminal de queda
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:#Controle do algulo
            if self.tilt < self.ANG_MAX:
                self.tilt = self.ANG_MAX
        else:
            if self.tilt > -90:
                self.tilt -= self.VEL_ANG

    def draw(self, win):
        self.img_count += 1

        if self.img_count <= self.ANIMATION_TIME:#Animação da Luz mexendo
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:#Animação pra queda
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)#Rodar a Luz

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Arvore():#Programação Referente a Luz
    GAP = 280
    VEL = 5

    def __init__(self, x):#Define a copa e raiz da arvore, assim como
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0

        self.ARVORE_TOP = pygame.transform.flip(ARVORE_IMG, False, True)
        self.ARVORE_BOTTOM = ARVORE_IMG

        self.passed = False

        self.set_height()

    def set_height(self):#Define altura aleatoria para arvore
        self.height = random.randrange(50, 450)
        self.top = self.height - self.ARVORE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):#adiciona as arvores

        win.blit(self.ARVORE_TOP, (self.x, self.top))
        win.blit(self.ARVORE_BOTTOM, (self.x, self.bottom))


    def collide(self, luz, win):
        luz_mask = luz.get_mask()
        top_mask = pygame.mask.from_surface(self.ARVORE_TOP)
        bottom_mask = pygame.mask.from_surface(self.ARVORE_BOTTOM)
        top_offset = (self.x - luz.x, self.top - round(luz.y))
        bottom_offset = (self.x - luz.x, self.bottom - round(luz.y))

        b_point = luz_mask.overlap(bottom_mask, bottom_offset)
        t_point = luz_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

class Chao:
    VEL = 5
    WIDTH = CHAO_IMG.get_width()
    IMG = CHAO_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, luzes, arvores, chao, pontos, gen, arvore_ind):
    if gen == 0:
        gen = 1
    win.blit(BI_IMG, (0,0))

    for arvore in arvores:
        arvore.draw(win)

    chao.draw(win)
    for luz in luzes:

        if DRAW_LINES:#adiciona linha que representam o calculo da IA
            try:
                pygame.draw.line(win, (255,0,0), (luz.x+luz.img.get_width()/2, luz.y + luz.img.get_height()/2), (arvores[arvore_ind].x + arvores[arvore_ind].ARVORE_TOP.get_width()/2, arvores[arvore_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (luz.x+luz.img.get_width()/2, luz.y + luz.img.get_height()/2), (arvores[arvore_ind].x + arvores[arvore_ind].ARVORE_BOTTOM.get_width()/2, arvores[arvore_ind].bottom), 5)
            except:
                pass

        luz.draw(win)#adiciiona a Luz

    # texto para pontuação
    pontos_label = STAT_FONT.render("Pontos: " + str(pontos),1,(255,255,255))
    win.blit(pontos_label, (WIN_WIDTH - pontos_label.get_width() - 15, 10))

    # texto para geração atual
    pontos_label = STAT_FONT.render("Geração: " + str(gen-1),1,(255,255,255))
    win.blit(pontos_label, (10, 10))

    #texto para individuos vivos
    pontos_label = STAT_FONT.render("Vivos: " + str(len(luzes)),1,(255,255,255))
    win.blit(pontos_label, (10, 50))

    pygame.display.update()


def eval_genomes(genomes, config):#aplica a lista de genomas utilizados, e armazena informação das gerações
    global WIN, gen
    win = WIN
    gen += 1
    nets = []
    luzes = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        luzes.append(Luz(230,350))
        ge.append(genome)

    chao = Chao(CHAO)
    arvores = [Arvore(700)]
    pontos = 0

    clock = pygame.time.Clock()

    run = True
    while run and len(luzes) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        arvore_ind = 0
        if len(luzes) > 0:
            if len(arvores) > 0.1 and luzes[0].x > arvores[0].x + arvores[0].ARVORE_BOTTOM.get_width():  #escolhe qual dos canos na tela mirar a IA
                arvore_ind = 1                                                                

        for x, luz in enumerate(luzes): #recompensa o passaro com melhor desempenho
            ge[x].fitness += 0.1
            luz.move()

            output = nets[luzes.index(luz)].activate((luz.y, abs(luz.y - arvores[arvore_ind].height), abs(luz.y - arvores[arvore_ind].bottom)))#calcula a posição da Luz para saber a hora certa de pular

            if output[0] > 0.5:
                luz.voo()

        chao.move()

        rem = []
        add_arvore = False

        for arvore in arvores:#Função para avaliar colisão entra Luz e Arvores
            arvore.move()
            for luz in luzes:
                if arvore.collide(luz, win):
                    ge[luzes.index(luz)].fitness -= 1
                    nets.pop(luzes.index(luz))
                    ge.pop(luzes.index(luz))
                    luzes.pop(luzes.index(luz))

            if arvore.x + arvore.ARVORE_TOP.get_width() < 0:
                rem.append(arvore)

            if not arvore.passed and arvore.x < luz.x:
                arvore.passed = True
                add_arvore = True

        if add_arvore:#Função que recompensa melhor desempenho
            pontos += 1
            for genome in ge:
                genome.fitness += 5
            arvores.append(Arvore(WIN_WIDTH))

        for r in rem:#Remove arvores que passaram
            arvores.remove(r)

        for luz in luzes:#Aplica IA para a Luz permanecer no centro
            if luz.y + luz.img.get_height() - 10 >= CHAO or luz.y < -50:
                nets.pop(luzes.index(luz))
                ge.pop(luzes.index(luz))
                luzes.pop(luzes.index(luz))

        draw_window(WIN, luzes, arvores, chao, pontos, gen, arvore_ind)#Adiciona grafico dos objetos

def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)#chama a função que direciona para configurações do NEAT

    p = neat.Population(config)#gera uma população de indiividuos

    winner = p.run(eval_genomes, 30)

    print('\nBest genome:\n{!s}'.format(winner))#mostra melhor genoma


if __name__ == '__main__':#Essa função direciona o arquivo de configurações do NEAT
    local_dir = Path(__file__).parent
    config_path = os.path.join(local_dir, 'config-feedfoward.txt')
    run(config_path)