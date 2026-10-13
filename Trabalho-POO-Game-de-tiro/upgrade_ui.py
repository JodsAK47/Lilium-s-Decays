"""Tela de evolução: escolhas, comparação de atributos e melhorias da partida."""
import pygame
from habilidades import HABILIDADES


TEXTO = (238, 244, 231)
SUAVE = (159, 179, 168)


class TelaUpgrade:
    def __init__(self):
        self.fontes = {n: pygame.font.SysFont(None, n) for n in (19, 21, 23, 27, 36)}
        self.cards = [pygame.Rect(56 + i * 258, 230, 242, 310) for i in range(3)]
        self.overlay = pygame.Surface((1200, 800), pygame.SRCALPHA)
        self.overlay.fill((4, 12, 14, 218))

    def texto(self, tela, texto, pos, tamanho=23, cor=TEXTO):
        tela.blit(self.fontes[tamanho].render(texto, True, cor), pos)

    def paragrafo(self, tela, texto, pos, largura, tamanho=23, cor=TEXTO):
        fonte = self.fontes[tamanho]
        linha = ""
        x, y = pos
        for palavra in texto.split():
            candidata = (linha + " " + palavra).strip()
            if linha and fonte.size(candidata)[0] > largura:
                self.texto(tela, linha, (x, y), tamanho, cor)
                y += tamanho
                linha = palavra
            else:
                linha = candidata
        self.texto(tela, linha, (x, y), tamanho, cor)
        return y + tamanho

    def desenhar(self, tela, jogo):
        tela.blit(self.overlay, (0, 0))
        pygame.draw.rect(tela, (13, 25, 27), (28, 120, 1144, 560), border_radius=18)
        self.texto(tela, "Escolha uma habilidade", (56, 158), 36)
        mouse = pygame.mouse.get_pos()
        destaque = (158, 216, 174)
        for i, (habilidade, rect) in enumerate(zip(jogo.opcoes_habilidades, self.cards)):
            hover = rect.collidepoint(mouse)
            pygame.draw.rect(tela, (29, 46, 41) if hover else (21, 34, 34), rect, border_radius=10)
            if hover:
                pygame.draw.rect(tela, destaque, rect, 1, border_radius=10)
            x, y = rect.x + 18, rect.y
            self.paragrafo(tela, habilidade.nome, (x, y+24), rect.width-36, 27)
            self.paragrafo(tela, habilidade.descricao, (x, y+94), rect.width-36, 21, SUAVE)
            atual = habilidade.formatar_valor(getattr(jogo.jogador, habilidade.atributo))
            depois = habilidade.formatar_valor(habilidade.prever(jogo.jogador))
            self.texto(tela, "Atual: " + atual, (x, y+184), 19, SUAVE)
            self.texto(tela, "Após: " + depois, (x, y+209), 21, destaque)
            pygame.draw.line(tela, (45, 62, 53), (x, y+251), (rect.right-18, y+251))
            self.texto(tela, f"[{i+1}]  Escolher", (x, y+272), 21, destaque if hover else TEXTO)

        pygame.draw.line(tela, (42, 59, 51), (835, 230), (835, 610))
        self.texto(tela, "Adquiridas", (860, 234), 23)
        adquiridas = [h for h in HABILIDADES if jogo.habilidades_adquiridas.get(h.atributo, 0)]
        if not adquiridas:
            self.paragrafo(tela, "Suas melhorias aparecerão aqui após a primeira escolha.", (860, 282), 265, 21, SUAVE)
        for i, habilidade in enumerate(adquiridas):
            y = 280 + i * 66
            quantidade = jogo.habilidades_adquiridas[habilidade.atributo]
            self.texto(tela, habilidade.nome, (860, y), 21)
            self.texto(tela, f"{quantidade}x", (1108, y), 21, destaque)
            self.texto(tela, habilidade.efeito_acumulado(quantidade), (860, y+25), 19, SUAVE)

        if jogo.melhorias_pendentes > 1:
            self.texto(tela, f"{jogo.melhorias_pendentes} escolhas restantes", (56, 566), 21, destaque)
        self.texto(tela, "Clique em uma opção ou pressione 1, 2 ou 3", (56, 630), 19, SUAVE)
