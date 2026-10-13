"""Tela de evolução: escolhas, comparação de atributos e melhorias da partida."""
import pygame
from habilidades import HABILIDADES


ESTILOS = {
    "dano_tiro": ("DANO", (244, 177, 100)),
    "intervalo_tiro": ("CADÊNCIA", (110, 205, 240)),
    "vida_maxima": ("DEFESA", (241, 140, 154)),
    "raio_atracao_xp": ("COLETA", (128, 219, 167)),
    "perfuracoes": ("PERFURAÇÃO", (185, 158, 244)),
}
TEXTO = (238, 244, 231)
SUAVE = (159, 179, 168)


class TelaUpgrade:
    def __init__(self):
        self.fontes = {n: pygame.font.SysFont(None, n) for n in (19, 21, 23, 27, 46)}
        self.cards = [pygame.Rect(56 + i * 258, 210, 242, 354) for i in range(3)]
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

    def icone(self, tela, atributo, x, y, cor):
        pygame.draw.rect(tela, (25, 43, 41), (x, y, 44, 44), border_radius=12)
        if atributo == "dano_tiro":
            pygame.draw.polygon(tela, cor, [(x+9,y+27),(x+21,y+9),(x+35,y+9),(x+35,y+23),(x+17,y+35)])
            pygame.draw.line(tela, TEXTO, (x+15,y+29), (x+29,y+15), 2)
        elif atributo == "intervalo_tiro":
            pygame.draw.polygon(tela, cor, [(x+25,y+6),(x+11,y+25),(x+21,y+25),(x+18,y+38),(x+34,y+18),(x+24,y+18)])
        elif atributo == "vida_maxima":
            pygame.draw.polygon(tela, cor, [(x+10,y+10),(x+22,y+6),(x+34,y+10),(x+32,y+28),(x+22,y+38),(x+12,y+28)], 3)
            pygame.draw.line(tela, TEXTO, (x+22,y+15), (x+22,y+28), 3)
            pygame.draw.line(tela, TEXTO, (x+16,y+21), (x+28,y+21), 3)
        elif atributo == "raio_atracao_xp":
            pygame.draw.circle(tela, cor, (x+22,y+22), 15, 2)
            pygame.draw.circle(tela, cor, (x+22,y+22), 9, 1)
            pygame.draw.polygon(tela, TEXTO, [(x+22,y+15),(x+27,y+22),(x+22,y+29),(x+17,y+22)])
        else:
            for offset in (0, 9, 18):
                pygame.draw.line(tela, cor, (x+9+offset,y+32), (x+17+offset,y+12), 3)
                pygame.draw.polygon(tela, cor, [(x+17+offset,y+9),(x+10+offset,y+16),(x+20+offset,y+19)])

    def desenhar(self, tela, jogo):
        tela.blit(self.overlay, (0, 0))
        pygame.draw.rect(tela, (13, 25, 27), (28, 36, 1144, 728), border_radius=22)
        pygame.draw.rect(tela, (66, 91, 78), (28, 36, 1144, 728), 1, border_radius=22)
        self.texto(tela, "EVOLUÇÃO  /  JOGO PAUSADO", (56, 58), 19, (163, 218, 151))
        self.texto(tela, "Sua planta está mais forte", (56, 88), 46)
        self.texto(tela, "Escolha uma melhoria. Os efeitos se acumulam durante esta partida.", (56, 140), 23, SUAVE)
        pygame.draw.rect(tela, (37, 60, 43), (1000, 69, 146, 48), border_radius=12)
        self.texto(tela, f"NÍVEL {jogo.nivel}", (1020, 83), 27, (185, 234, 157))
        self.texto(tela, "ESCOLHA SEU PRÓXIMO PASSO", (56, 181), 19, SUAVE)
        mouse = pygame.mouse.get_pos()
        for i, (habilidade, rect) in enumerate(zip(jogo.opcoes_habilidades, self.cards)):
            categoria, cor = ESTILOS[habilidade.atributo]
            quantidade = jogo.habilidades_adquiridas.get(habilidade.atributo, 0)
            hover = rect.collidepoint(mouse)
            pygame.draw.rect(tela, (29, 48, 45) if hover else (21, 36, 37), rect, border_radius=14)
            pygame.draw.rect(tela, cor if hover else (58, 80, 71), rect, 2 if hover else 1, border_radius=14)
            pygame.draw.rect(tela, cor, (rect.x+20, rect.y, 45, 3), border_radius=1)
            x, y = rect.x + 18, rect.y
            self.icone(tela, habilidade.atributo, x, y+22, cor)
            self.texto(tela, categoria, (x+56, y+26), 19, cor)
            self.texto(tela, f"Adquirida {quantidade}x" if quantidade else "Nova habilidade", (x+56, y+48), 19, SUAVE)
            self.paragrafo(tela, habilidade.nome, (x, y+88), rect.width-36, 27)
            self.paragrafo(tela, habilidade.descricao, (x, y+150), rect.width-36, 21, SUAVE)
            pygame.draw.line(tela, (57, 76, 69), (x, y+231), (rect.right-18, y+231))
            atual = habilidade.formatar_valor(getattr(jogo.jogador, habilidade.atributo))
            depois = habilidade.formatar_valor(habilidade.prever(jogo.jogador))
            self.texto(tela, "Atual: " + atual, (x, y+245), 19, SUAVE)
            self.texto(tela, "Após: " + depois, (x, y+269), 21, cor)
            botao = pygame.Rect(x, y+307, rect.width-36, 32)
            pygame.draw.rect(tela, cor if hover else (41, 62, 54), botao, border_radius=7)
            self.texto(tela, f"[{i+1}]  Escolher melhoria", (x+14, y+315), 21, (15, 28, 29) if hover else TEXTO)

        pygame.draw.rect(tela, (18, 32, 33), (842, 176, 304, 544), border_radius=14)
        self.texto(tela, "SUAS MELHORIAS", (860, 196), 27)
        total = sum(jogo.habilidades_adquiridas.values())
        self.texto(tela, f"{total} escolhas aplicadas nesta partida", (860, 228), 19, SUAVE)
        for i, habilidade in enumerate(HABILIDADES):
            y = 258 + i * 86
            quantidade = jogo.habilidades_adquiridas.get(habilidade.atributo, 0)
            cor = ESTILOS[habilidade.atributo][1] if quantidade else SUAVE
            pygame.draw.line(tela, (42, 61, 54), (860, y-6), (1128, y-6))
            self.texto(tela, habilidade.nome, (860, y+3), 21, TEXTO if quantidade else SUAVE)
            self.texto(tela, f"{quantidade}x", (1105, y+3), 21, cor)
            self.texto(tela, habilidade.efeito_acumulado(quantidade), (860, y+29), 19, cor)
            atual = habilidade.formatar_valor(getattr(jogo.jogador, habilidade.atributo))
            self.texto(tela, "Atual: " + atual, (860, y+51), 19, SUAVE)

        pygame.draw.rect(tela, (18, 32, 33), (56, 584, 758, 136), border_radius=14)
        self.texto(tela, f"Próximo nível: {jogo.nivel+1}", (76, 603), 23)
        self.texto(tela, f"{jogo.xp} / {jogo.xp_maximo} XP", (652, 604), 21, (133, 221, 175))
        pygame.draw.rect(tela, (36, 57, 50), (76, 638, 716, 7), border_radius=3)
        largura = round(716 * min(1, jogo.xp / jogo.xp_maximo))
        if largura:
            pygame.draw.rect(tela, (111, 211, 159), (76, 638, largura, 7), border_radius=3)
        pendentes = jogo.melhorias_pendentes
        dica = f"{pendentes} escolhas pendentes. Escolha uma melhoria por vez." if pendentes > 1 else "Esta escolha conclui sua evolução. Prepare-se para voltar à arena."
        self.texto(tela, dica, (76, 672), 21, SUAVE)
        self.texto(tela, "Clique em um cartão ou use 1, 2 ou 3 para escolher", (56, 739), 19, SUAVE)
