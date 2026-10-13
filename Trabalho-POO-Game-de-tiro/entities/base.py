import pygame

class Entidade(pygame.sprite.Sprite):
    def __init__(self, x,y,tamanho, velocidade):
        super().__init__()


        self.image = pygame.Surface((tamanho, tamanho))
        self.rect = self.image.get_rect(center=(x, y))

  
        self.x = x 
        self.y =y 
        self.tamanho = tamanho
        self.velocidade = velocidade