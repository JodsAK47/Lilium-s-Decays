"""Menu inicial e seleção das plantas disponíveis."""
import pygame

from assets import PERSONAGENS, carregar_frames, carregar_imagem
from config import LARGURA, ALTURA


class MenuInicial:
    def __init__(self):
        self.personagens = list(PERSONAGENS)
        self.selecionado = 0
        self.tela_atual = "inicio"
        conceito = carregar_imagem("Concept Estrutura/Menu Concept layoult - Copia.png")
        self.fundo_inicio = pygame.transform.scale(conceito, (LARGURA, ALTURA))
        # Usa o cenário do conceito, sem os botões desenhados na própria imagem.
        cenario = conceito.subsurface((0, 0, conceito.get_width(), 340))
        self.fundo = pygame.transform.scale(cenario, (LARGURA, ALTURA))
        sombra = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        sombra.fill((12, 15, 20, 160))
        self.fundo.blit(sombra, (0, 0))
        self.fonte_titulo = pygame.font.SysFont(None, 76)
        self.fonte = pygame.font.SysFont(None, 32)
        self.fonte_pequena = pygame.font.SysFont(None, 25)
        self.fonte_detalhe = pygame.font.SysFont(None, 22)
        self.fonte_rotulo = pygame.font.SysFont(None, 18)
        self.cards = [pygame.Rect(LARGURA // 2 - 410 + i * 280, 235, 260, 310) for i in range(3)]
        # Áreas dos botões na imagem original, convertidas à resolução do jogo.
        def area(x, y, largura, altura):
            return pygame.Rect(
                round(x * LARGURA / conceito.get_width()),
                round(y * ALTURA / conceito.get_height()),
                round(largura * LARGURA / conceito.get_width()),
                round(altura * ALTURA / conceito.get_height()),
            )

        self.botao_jogar_inicio = area(94, 348, 102, 44)
        self.botao_config = area(207, 348, 101, 44)
        self.botao_sair_inicio = area(319, 348, 101, 44)
        self.botao_iniciar_partida = pygame.Rect(LARGURA // 2 - 160, 555, 320, 58)
        self.botao_voltar = pygame.Rect(LARGURA // 2 - 160, 630, 320, 48)

    @property
    def botao_sair(self):
        return self.botao_sair_inicio if self.tela_atual == "inicio" else self.botao_voltar

    @property
    def botao_jogar(self):
        if self.tela_atual == "inicio":
            return self.botao_jogar_inicio
        return self.botao_iniciar_partida

    @property
    def personagem(self):
        return self.personagens[self.selecionado]

    def confirmar(self):
        if self.tela_atual == "config":
            return "alternar_tela"
        if self.tela_atual == "inicio":
            self.tela_atual = "selecao"
            return None
        self.tela_atual = "inicio"
        return "jogar"

    def voltar(self):
        if self.tela_atual != "inicio":
            self.tela_atual = "inicio"
            return None
        return "sair"

    def processar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.confirmar()
            if evento.key == pygame.K_ESCAPE:
                return self.voltar()
            if self.tela_atual == "selecao":
                if evento.key in (pygame.K_LEFT, pygame.K_a):
                    self.selecionado = (self.selecionado - 1) % len(self.personagens)
                elif evento.key in (pygame.K_RIGHT, pygame.K_d):
                    self.selecionado = (self.selecionado + 1) % len(self.personagens)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.tela_atual == "inicio" and self.botao_config.collidepoint(evento.pos):
                self.tela_atual = "config"
                return None
            if self.tela_atual == "selecao":
                for i, card in enumerate(self.cards):
                    if card.collidepoint(evento.pos):
                        self.selecionado = i
            if self.botao_jogar.collidepoint(evento.pos):
                return self.confirmar()
            if self.botao_sair.collidepoint(evento.pos):
                return self.voltar()
        return None

    def texto(self, tela, texto, centro, fonte=None, cor=(245, 237, 214)):
        imagem = (fonte or self.fonte).render(texto, True, cor)
        tela.blit(imagem, imagem.get_rect(center=centro))

    def desenhar(self, tela):
        if self.tela_atual == "inicio":
            # Os botões já fazem parte da arte: apenas suas áreas recebem cliques.
            tela.blit(self.fundo_inicio, (0, 0))
            return
        tela.blit(self.fundo, (0, 0))
        self.texto(tela, "LILIUM'S DECAY", (LARGURA // 2, 125), self.fonte_titulo)
        if self.tela_atual == "selecao":
            self.desenhar_selecao(tela)
        mouse = pygame.mouse.get_pos()
        botoes = ((self.botao_jogar, "JOGAR"), (self.botao_sair, "SAIR"))
        dica = "Clique em PLAY para jogar ou pressione Enter"
        if self.tela_atual == "selecao":
            botoes = ((self.botao_jogar, "INICIAR PARTIDA"), (self.botao_sair, "VOLTAR"))
            dica = "Escolha com o mouse ou A/D e confirme com Enter"
        if self.tela_atual == "config":
            self.texto(tela, "CONFIGURAÇÕES", (LARGURA // 2, 260))
            cheia = bool(tela.get_flags() & pygame.FULLSCREEN)
            modo = "Tela cheia" if cheia else "Janela"
            self.texto(tela, "Modo atual: " + modo, (LARGURA // 2, 360))
            self.texto(tela, "WASD: mover | Disparo automático", (LARGURA // 2, 420))
            botoes = ((self.botao_jogar, "ALTERNAR TELA"), (self.botao_sair, "VOLTAR"))
            dica = "Enter: alternar modo de tela | ESC: voltar"
        for rect, rotulo in botoes:
            pygame.draw.rect(tela, (88, 120, 55) if rect.collidepoint(mouse) else (52, 77, 42), rect, border_radius=8)
            self.texto(tela, rotulo, rect.center)
        self.texto(tela, dica, (LARGURA // 2, 722), self.fonte_pequena)
        if self.tela_atual != "selecao":
            self.texto(tela, "WASD: mover  |  Tiro automático  |  ESC: voltar ao menu (reinicia a partida)", (LARGURA // 2, 758), self.fonte_pequena)

    def desenhar_selecao(self, tela):
        self.texto(tela, "Escolha seu estilo de jogo", (LARGURA // 2, 210))
        for i, (personagem, card) in enumerate(zip(self.personagens, self.cards)):
            selecionado = i == self.selecionado
            pygame.draw.rect(tela, (40, 58, 44) if selecionado else (30, 32, 37), card, border_radius=12)
            pygame.draw.rect(tela, (194, 229, 112) if selecionado else (67, 77, 68), card, 2 if selecionado else 1, border_radius=12)
            frames = carregar_frames(personagem, 96)
            frame = frames[(pygame.time.get_ticks() // 140) % len(frames)]
            tela.blit(frame, frame.get_rect(center=(card.centerx, card.y + 57)))
            self.texto(tela, PERSONAGENS[personagem]["nome"], (card.centerx, card.y + 120))
            perfil = PERSONAGENS[personagem]
            self.texto(tela, perfil["perfil"], (card.centerx, card.y + 149), self.fonte_pequena, (194, 229, 112))
            for rotulo, chave, y, cor in (
                ("VANTAGEM", "vantagem", 184, (194, 229, 167)),
                ("EM TROCA", "limite", 244, (178, 183, 175)),
            ):
                self.texto(tela, rotulo, (card.centerx, card.y + y), self.fonte_rotulo, cor)
                palavras = perfil[chave].split()
                linhas = [""]
                for palavra in palavras:
                    candidata = (linhas[-1] + " " + palavra).strip()
                    if self.fonte_detalhe.size(candidata)[0] > card.width - 40:
                        linhas.append(palavra)
                    else:
                        linhas[-1] = candidata
                for n, linha in enumerate(linhas):
                    self.texto(tela, linha, (card.centerx, card.y + y + 23 + n * 22), self.fonte_detalhe, cor)
            if selecionado:
                centro = (card.right - 20, card.y + 20)
                pygame.draw.circle(tela, (194, 229, 112), centro, 9)
                pygame.draw.lines(tela, (40, 58, 44), False,
                                  [(centro[0]-4, centro[1]), (centro[0]-1, centro[1]+3), (centro[0]+4, centro[1]-3)], 2)
