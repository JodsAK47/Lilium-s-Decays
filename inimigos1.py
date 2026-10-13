"""Inimigos animados, ataques e experiência coletável."""
import pygame
from assets import INIMIGOS, carregar_faixa, carregar_cristal_xp
from entities.projectile import PoderInimigo
from config import XP_VELOCIDADE_ATRACAO, LARGURA, ALTURA


class InimigoBase(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade, vida_maxima, xp, arte):
        super().__init__()
        self.velocidade = velocidade
        self.vida = self.vida_maxima = vida_maxima
        self.xp = xp
        self.arte = arte
        self.frames = carregar_faixa(*INIMIGOS[arte])
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.posicao = pygame.Vector2(x, y)
        self.tempo_animacao = 0
        self.esquerda = False
        self.intervalo_ataque = 0
        self.tempo_ataque = 0
        self.alcance_ataque = 0
        self.chefe = False

    def update(self, jogador):
        direcao = pygame.Vector2(jogador.rect.center) - self.posicao
        distancia = direcao.length()
        if direcao.x:
            self.esquerda = direcao.x < 0
        # Conjuradores param a uma distância que permite desviar dos poderes.
        dentro_da_arena = pygame.Rect(0, 42, LARGURA, ALTURA - 42).contains(self.rect)
        distancia_minima = self.alcance_ataque * 0.7 if self.intervalo_ataque and dentro_da_arena else 0
        if distancia > distancia_minima:
            self.posicao += direcao.normalize() * min(self.velocidade, distancia)
        self.tempo_animacao += 1
        metade = len(self.frames) // 2
        indice = (self.tempo_animacao // 7) % metade
        self.image = self.frames[indice + (metade if self.esquerda else 0)]
        self.rect = self.image.get_rect(center=(round(self.posicao.x), round(self.posicao.y)))
        if self.intervalo_ataque:
            self.tempo_ataque = max(0, self.tempo_ataque - 1)

    def atacar(self, jogador):
        if not self.intervalo_ataque or self.tempo_ataque:
            return ()
        # Só dispara depois de entrar na arena.
        if not pygame.Rect(0, 42, LARGURA, ALTURA - 42).collidepoint(self.rect.center):
            return ()
        direcao = pygame.Vector2(jogador.rect.center) - self.rect.center
        if not 0 < direcao.length() <= self.alcance_ataque:
            return ()
        self.tempo_ataque = self.intervalo_ataque
        angulos = (-18, 0, 18) if self.chefe else (0,)
        return tuple(PoderInimigo(*self.rect.center, direcao.rotate(angulo), self.arte)
                     for angulo in angulos)

    def tomar_dano(self, dano):
        self.vida -= dano
        if self.vida <= 0:
            self.kill()


class ZumbiComum(InimigoBase):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=2, vida_maxima=3, xp=1, arte="verde")


class ZumbiCorredor(InimigoBase):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=4, vida_maxima=1, xp=2, arte="amarelo")


class ZumbiTanque(InimigoBase):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=1.2, vida_maxima=8, xp=3, arte="azul")


class ZumbiRoxo(InimigoBase):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=1.5, vida_maxima=4, xp=3, arte="roxo")
        self.intervalo_ataque = 150
        self.tempo_ataque = 90
        self.alcance_ataque = 420


class Lich(InimigoBase):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=1, vida_maxima=35, xp=15, arte="lich")
        self.chefe = True
        self.intervalo_ataque = 110
        self.tempo_ataque = 90
        self.alcance_ataque = 600


class XP(pygame.sprite.Sprite):

    def __init__(self, x, y, quantidade):
        super().__init__()

        self.quantidade = quantidade
        self.velocidade = XP_VELOCIDADE_ATRACAO


        tipo = "chefe" if quantidade >= 10 else "raro" if quantidade >= 2 else "comum"
        self.frames = carregar_cristal_xp(tipo)
        self.tempo_animacao = (x + y) % 40
        self.image = self.frames[0]
        self.posicao = pygame.Vector2(x, y)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self,jogador):
        self.tempo_animacao += 1
        self.image = self.frames[(self.tempo_animacao // 10) % len(self.frames)]
        xp_pos = self.posicao
        jogador_pos = pygame.math.Vector2(jogador.rect.center)

        distancia = xp_pos.distance_to(jogador_pos)

        # só se move se estiver dentro do raio de atração
        if distancia <= jogador.raio_atracao_xp and distancia > 0:
            direcao = (jogador_pos - xp_pos).normalize()
            self.posicao += direcao * min(self.velocidade, distancia)
            self.rect.center = (round(self.posicao.x), round(self.posicao.y))
