import pygame
from entities.base import Entidade
from assets import carregar_tiro, carregar_poder
from config import TIRO_VELOCIDADE, TIRO_TAMANHO, TIRO_DANO, LARGURA, ALTURA


class Tiro(Entidade):
    def __init__(self, x, y, direcao, personagem="cacto", dano=TIRO_DANO, perfuracoes=0):
        super().__init__(x, y, TIRO_TAMANHO, TIRO_VELOCIDADE)
        self.direcao = pygame.Vector2(direcao)
        angulo = self.direcao.angle_to(pygame.Vector2(1, 0)) if self.direcao.length_squared() else 0
        self.image = pygame.transform.rotate(carregar_tiro(personagem), angulo)
        self.rect = self.image.get_rect(center=(x, y))
        self.posicao = pygame.Vector2(x, y)
        self.dano = dano
        self.acertos_restantes = 1 + perfuracoes
        self.inimigos_atingidos = set()

    def atingir(self, inimigo):
        if self.acertos_restantes <= 0 or inimigo in self.inimigos_atingidos:
            return False
        self.inimigos_atingidos.add(inimigo)
        inimigo.tomar_dano(self.dano)
        self.acertos_restantes -= 1
        if self.acertos_restantes == 0:
            self.kill()
        return True

    def update(self):
        self.posicao += self.direcao * self.velocidade
        self.rect.center = (round(self.posicao.x), round(self.posicao.y))
        if (self.rect.right < 0 or self.rect.left > LARGURA or
                self.rect.bottom < 0 or self.rect.top > ALTURA):
            self.kill()


class PoderInimigo(pygame.sprite.Sprite):
    """Magia direcionada, animada e removida ao sair da arena."""

    def __init__(self, x, y, direcao, tipo):
        super().__init__()
        self.direcao = pygame.Vector2(direcao)
        if self.direcao.length_squared():
            self.direcao.normalize_ip()
        self.velocidade = 4 if tipo == "lich" else 3
        self.dano = 1
        self.posicao = pygame.Vector2(x, y)
        angulo = self.direcao.angle_to(pygame.Vector2(1, 0)) if self.direcao.length_squared() else 0
        self.frames = tuple(pygame.transform.rotate(frame, angulo) for frame in carregar_poder(tipo))
        self.idade = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=self.posicao)

    def update(self):
        self.idade += 1
        self.posicao += self.direcao * self.velocidade
        self.image = self.frames[(self.idade // 8) % len(self.frames)]
        self.rect = self.image.get_rect(center=(round(self.posicao.x), round(self.posicao.y)))
        if (self.idade > 360 or self.rect.right < 0 or self.rect.left > LARGURA or
                self.rect.bottom < 0 or self.rect.top > ALTURA):
            self.kill()
