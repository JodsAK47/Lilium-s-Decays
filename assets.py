"""Artes compartilhadas, carregadas a partir da pasta do projeto."""
from functools import lru_cache
from pathlib import Path

import pygame

RAIZ = Path(__file__).resolve().parent
PERSONAGENS = {
    "cacto": {"nome": "Cacto", "sprite": "cacto.png", "tiro": "tiro do cacto.png", "arma": "Armacacto.png"},
    "ervilheiro": {"nome": "Ervilheiro", "sprite": "ervilheiro.png", "tiro": "tiro ervilheiro.png", "arma": "armaervilheiro.png"},
    "lirio": {"nome": "Lírio", "sprite": "lirio.png", "tiro": "tiro do lirio.png", "arma": "Armalirio.png"},
}

# As faixas têm células retangulares e resoluções diferentes.
INIMIGOS = {
    "verde": ("zumbi_verde.png", 24, 54),
    "amarelo": ("zumbi_amarelo.png", 24, 50),
    "azul": ("Zumbi_Azul.png", 24, 72),
    "roxo": ("zumbi_roxo.png", 48, 58),
    "lich": ("Litch.png", 4, 110),
}


@lru_cache(maxsize=None)
def carregar_imagem(caminho):
    return pygame.image.load(str(RAIZ / caminho)).convert_alpha()


@lru_cache(maxsize=None)
def carregar_faixa(arquivo, quantidade, altura):
    sheet = carregar_imagem("ARTES/" + arquivo)
    largura = sheet.get_width() // quantidade
    tamanho = (round(largura * altura / sheet.get_height()), altura)
    return tuple(
        pygame.transform.scale(sheet.subsurface((i * largura, 0, largura, sheet.get_height())), tamanho)
        for i in range(quantidade)
    )


@lru_cache(maxsize=None)
def carregar_arma(personagem, largura=42, esquerda=False):
    sheet = carregar_imagem("ARTES/" + PERSONAGENS[personagem]["arma"])
    metade = sheet.get_width() // 2
    sprite = sheet.subsurface((metade if esquerda else 0, 0, metade, sheet.get_height()))
    sprite = sprite.subsurface(sprite.get_bounding_rect())
    return pygame.transform.scale(sprite, (largura, round(sprite.get_height() * largura / sprite.get_width())))


@lru_cache(maxsize=None)
def carregar_poder(tipo):
    if tipo == "lich":
        return carregar_faixa("poderlicth.png", 4, 24)[:2]
    if tipo == "roxo":
        return carregar_faixa("poder_zumbi_roxo.png", 2, 18)[:1]
    raise ValueError("Poder desconhecido: " + tipo)


@lru_cache(maxsize=None)
def carregar_frames(personagem, tamanho):
    sheet = carregar_imagem("ARTES/" + PERSONAGENS[personagem]["sprite"])
    lado = sheet.get_height()
    return tuple(
        pygame.transform.scale(sheet.subsurface((x, 0, lado, lado)), (tamanho, tamanho))
        for x in range(0, sheet.get_width(), lado)
    )


@lru_cache(maxsize=None)
def carregar_tiro(personagem):
    sheet = carregar_imagem("ARTES/" + PERSONAGENS[personagem]["tiro"])
    # As artes contêm duas orientações; a metade direita aponta para a direita.
    largura = sheet.get_width() // 2
    sprite = sheet.subsurface((largura, 0, largura, sheet.get_height()))
    return pygame.transform.scale(sprite, (largura * 2, sheet.get_height() * 2))


def criar_mapa(tamanho):
    piso = carregar_imagem("ARTES/deserto.png")
    mapa = pygame.Surface(tamanho)
    for y in range(0, tamanho[1], piso.get_height()):
        for x in range(0, tamanho[0], piso.get_width()):
            mapa.blit(piso, (x, y))
    return mapa
