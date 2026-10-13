import pygame
import random
from assets import criar_mapa
from menu import MenuInicial
from habilidades import HABILIDADES
from entities.player import Jogador
from inimigos1 import XP
from entities.projectile import Tiro
from inimigos1 import ZumbiComum, ZumbiCorredor, ZumbiTanque, ZumbiRoxo, Lich
from config import (
    LARGURA, ALTURA, FPS, COR_TEXTO,
    SPAWN_INTERVALO, TAXA_ZUMBI_COMUM,
    INIMIGOS_RODADA_INICIAL,
    AUMENTO_INIMIGOS_POR_RODADA,
    TEMPO_ENTRE_RODADAS, TELA_CHEIA,MENSAGEM_DURACAO,COR_MENSAGEM
)


class Game:
    #classe do loop principal
    def __init__(self):
        pygame.init()
        flags = pygame.SCALED | (pygame.FULLSCREEN if TELA_CHEIA else 0)
        self.tela = pygame.display.set_mode((LARGURA, ALTURA), flags)
        pygame.display.set_caption("Lilium's Decay")
        self.clock = pygame.time.Clock()
        self.fonte = pygame.font.SysFont(None, 30)
        self.fonte_cards = pygame.font.SysFont(None, 28)
        self.mapa = criar_mapa((LARGURA, ALTURA))
        self.menu = MenuInicial()
        self.estado = "menu"
        self.rodando = True

    def iniciar_partida(self):
        self.estado = "jogo"
        # Sprites groups
        self.todos_sprites = pygame.sprite.Group()
        self.inimigos = pygame.sprite.Group()
        self.tiros = pygame.sprite.Group()      
        self.poderes_inimigos = pygame.sprite.Group()
        self.xps = pygame.sprite.Group()
        self.tempo_invulneravel = 0
        
        # Criar jogador
        self.jogador = Jogador(LARGURA // 2, ALTURA - 60, self.menu.personagem)
        self.todos_sprites.add(self.jogador)
        #variaveis
        self.pontos = 0
        self.xp = 0
        self.nivel = 1
        self.tempo_inicio = pygame.time.get_ticks()
        self.tempo_final = None
        
        self.xp_maximo = 10
        self.spawn_timer = 0
        self.rodando = True
        self.tempo_ultimo_tiro = 0
        #rodadas
        self.rodada = 1
        self.inimigos_para_spawnar = INIMIGOS_RODADA_INICIAL
        self.inimigos_spawnados = 0
        self.tempo_entre_rodadas = 0
        self.aguardando_proxima_rodada = False
        self.mensagens = []
        #estado de upgrade
        self.menu_upgrade_ativo = False
        self.rects_opcoes = []
        self.opcoes_habilidades = []
        self.melhorias_pendentes = 0

    def abrir_escolha_habilidade(self):
        self.opcoes_habilidades = random.sample(HABILIDADES, 3)
        self.rects_opcoes = [pygame.Rect(140 + i * 320, 260, 280, 280) for i in range(3)]
        self.menu_upgrade_ativo = True

    def escolher_habilidade(self, indice):
        if not self.menu_upgrade_ativo or not 0 <= indice < len(self.opcoes_habilidades):
            return
        habilidade = self.opcoes_habilidades[indice]
        habilidade.aplicar(self.jogador)
        self.mostrar_mensagem(habilidade.nome + " adquirida!")
        self.melhorias_pendentes -= 1
        if self.melhorias_pendentes > 0:
            self.abrir_escolha_habilidade()
        else:
            self.menu_upgrade_ativo = False
            self.opcoes_habilidades = []
            self.rects_opcoes = []

    def mostrar_mensagem(self, texto, duracao=None):
        self.mensagens.append({
            "texto": texto,
            "tempo": duracao if duracao else MENSAGEM_DURACAO
        })



    def buscar_inimigo_mais_proximo(self):
        if not self.inimigos:
            return None

        inimigo_mais_proximo = None
        menor_distancia = float("inf")

        jogador_pos = pygame.math.Vector2(self.jogador.rect.center)

        for inimigo in self.inimigos:
            inimigo_pos = pygame.math.Vector2(inimigo.rect.center)
            distancia = jogador_pos.distance_to(inimigo_pos)

            if distancia < menor_distancia:
                menor_distancia = distancia
                inimigo_mais_proximo = inimigo

        return inimigo_mais_proximo

    def processar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
                return
            if self.estado == "menu":
                acao = self.menu.processar_evento(event)
                if acao == "jogar":
                    self.iniciar_partida()
                elif acao == "alternar_tela":
                    cheia = bool(self.tela.get_flags() & pygame.FULLSCREEN)
                    flags = pygame.SCALED | (0 if cheia else pygame.FULLSCREEN)
                    self.tela = pygame.display.set_mode((LARGURA, ALTURA), flags)
                elif acao == "sair":
                    self.rodando = False
                    return
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.estado = "menu"
                return
            if self.menu_upgrade_ativo:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, rect in enumerate(self.rects_opcoes):
                        if rect.collidepoint(event.pos):
                            self.escolher_habilidade(i)
                            return
                elif event.type == pygame.KEYDOWN and event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    self.escolher_habilidade(event.key - pygame.K_1)
                    return

        # Se o jogo estiver pausado no upgrade  ignor os tiro
        if self.estado != "jogo" or self.menu_upgrade_ativo:
            return




        agora = pygame.time.get_ticks()

        if agora - self.tempo_ultimo_tiro >= self.jogador.intervalo_tiro:
            self.disparar_tiro()
            self.tempo_ultimo_tiro = agora

    def disparar_tiro(self):
        alvo = self.buscar_inimigo_mais_proximo()
        if alvo is None:
            return  # sem inimigo na tela, não atira

        self.jogador.mirar(alvo.rect.center)
        jogador_pos = self.jogador.posicao_arma
        alvo_pos = pygame.math.Vector2(alvo.rect.center)

        direcao = alvo_pos - jogador_pos
        if direcao.length() > 0:
            direcao = direcao.normalize()

        tiro = Tiro(
            *jogador_pos, direcao, self.jogador.personagem,
            dano=self.jogador.dano_tiro, perfuracoes=self.jogador.perfuracoes,
        )
        self.todos_sprites.add(tiro)
        self.tiros.add(tiro)

    def spawnar_inimigo(self):
        lado = random.randint(0, 3)
        
        if lado == 0:  # Topo
            x = random.randint(-40, LARGURA + 40)
            y = -40
        elif lado == 1:  # Baixo
            x = random.randint(-40, LARGURA + 40)
            y = ALTURA + 40
        elif lado == 2:  # Esquerda
            x = -40
            y = random.randint(-40, ALTURA + 40)
        else:  # Direita
            x = LARGURA + 40
            y = random.randint(-40, ALTURA + 40)

        # Um chefe garantido a cada cinco rodadas, dentro da cota da onda.
        if self.rodada % 5 == 0 and self.inimigos_spawnados == 0:
            novo_inimigo = Lich(x, y)
            self.mostrar_mensagem("O Lich chegou!")
        elif self.rodada == 2 and self.inimigos_spawnados == 0:
            novo_inimigo = ZumbiTanque(x, y)
        elif self.rodada == 3 and self.inimigos_spawnados == 0:
            novo_inimigo = ZumbiRoxo(x, y)
        else:
            tipos = [ZumbiComum, ZumbiCorredor]
            pesos = [TAXA_ZUMBI_COMUM, 1 - TAXA_ZUMBI_COMUM]
            if self.rodada >= 2:
                tipos.append(ZumbiTanque)
                pesos.append(0.2)
            if self.rodada >= 3:
                tipos.append(ZumbiRoxo)
                pesos.append(0.2)
            novo_inimigo = random.choices(tipos, weights=pesos, k=1)[0](x, y)

        self.todos_sprites.add(novo_inimigo)
        self.inimigos.add(novo_inimigo)

    def verificar_colisoes(self):
       
        # Processa cada projétil até consumir seus acertos, sem repetir dano ou XP.
        for tiro in list(self.tiros):
            for zumbi in pygame.sprite.spritecollide(tiro, self.inimigos, False):
                if not tiro.atingir(zumbi):
                    continue
                if zumbi.vida <= 0:
                    self.pontos += 1
                    xp = XP(*zumbi.rect.center, zumbi.xp)
                    self.todos_sprites.add(xp)
                    self.xps.add(xp)
                if tiro.acertos_restantes == 0:
                    break
        xps_coletados = pygame.sprite.spritecollide(
            self.jogador,
            self.xps,
            True
            )

        for xp in xps_coletados:
            self.xp += xp.quantidade
        while self.xp >= self.xp_maximo:
            self.xp -= self.xp_maximo
            self.nivel += 1
            self.melhorias_pendentes += 1
            self.mostrar_mensagem(f"LEVEL UP! Nível {self.nivel}")
        if self.melhorias_pendentes and not self.menu_upgrade_ativo:
            self.abrir_escolha_habilidade()

        contatos = pygame.sprite.spritecollide(self.jogador, self.inimigos, False)
        poderes = pygame.sprite.spritecollide(self.jogador, self.poderes_inimigos, True)
        if (contatos or poderes) and not self.tempo_invulneravel:
            # O chefe precisa ser derrotado com tiros, inclusive após encostar.
            for inimigo in contatos:
                if not inimigo.chefe:
                    inimigo.kill()
            self.tempo_invulneravel = 60
            dano = max((poder.dano for poder in poderes), default=1)
            if self.jogador.tomar_dano(dano):
                self.mostrar_mensagem("GAME OVER!", duracao=999999)
                self.tempo_final = pygame.time.get_ticks()
                self.estado = "menu"

    def atualizar(self):

        # menu de habilidade ativo pauso o jogo   
        if self.estado != "jogo" or self.menu_upgrade_ativo:
            return
        self.tempo_invulneravel = max(0, self.tempo_invulneravel - 1)
        
         # Atualiza o tempo de vida das mensagens na tela
        for mensagem in self.mensagens[:]:
            mensagem["tempo"] -= 1
            if mensagem["tempo"] <= 0:
                self.mensagens.remove(mensagem)

    # Timer de spawn
        if not self.aguardando_proxima_rodada:

            if self.inimigos_spawnados < self.inimigos_para_spawnar:

                self.spawn_timer += 1

                if self.spawn_timer >= SPAWN_INTERVALO:
                    self.spawnar_inimigo()
                    self.inimigos_spawnados += 1
                    self.spawn_timer = 0

    # quando morrer todo mundo e rodada acabar
            elif len(self.inimigos) == 0:
                self.aguardando_proxima_rodada = True
                self.tempo_entre_rodadas = TEMPO_ENTRE_RODADAS

        else:
    #contagem para próxima rodada
            self.tempo_entre_rodadas -= 1
            if self.tempo_entre_rodadas <= 0:
                self.iniciar_proxima_rodada()

        self.jogador.update()
        self.tiros.update()
        self.poderes_inimigos.update()

        for inimigo in self.inimigos:
            inimigo.update(self.jogador)
            poderes = inimigo.atacar(self.jogador)
            self.poderes_inimigos.add(*poderes)
            self.todos_sprites.add(*poderes)

        alvo = self.buscar_inimigo_mais_proximo()
        if alvo is not None:
            self.jogador.mirar(alvo.rect.center)

        for xp in self.xps:
            xp.update(self.jogador)

        self.verificar_colisoes()

    def iniciar_proxima_rodada(self):
        self.rodada += 1
    # Aumenta quantidade de inimigos
        self.inimigos_para_spawnar = (
            INIMIGOS_RODADA_INICIAL +
            (self.rodada - 1) * AUMENTO_INIMIGOS_POR_RODADA
    )
        self.inimigos_spawnados = 0
        self.spawn_timer = 0
        self.aguardando_proxima_rodada = False
        self.mostrar_mensagem(f"Rodada {self.rodada}")

    def desenhar_menu_upgrade(self):
        # Fundo escuro semi-transparente
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.tela.blit(overlay, (0, 0))

        titulo = self.fonte.render("ESCOLHA UMA HABILIDADE", True, (255, 255, 255))
        self.tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 205)))
        pos_mouse = pygame.mouse.get_pos()
        for i, (habilidade, rect) in enumerate(zip(self.opcoes_habilidades, self.rects_opcoes)):
            hover = rect.collidepoint(pos_mouse)
            pygame.draw.rect(self.tela, (60, 60, 80) if hover else (40, 40, 50), rect, border_radius=12)
            pygame.draw.rect(self.tela, (255, 215, 0) if hover else (150, 150, 150), rect, 3, border_radius=12)
            y = rect.y + 35
            for texto, cor in ((habilidade.nome, (194, 229, 112)), (habilidade.descricao, COR_TEXTO)):
                linhas = []
                linha = ""
                for palavra in texto.split():
                    candidata = (linha + " " + palavra).strip()
                    if linha and self.fonte_cards.size(candidata)[0] > rect.width - 32:
                        linhas.append(linha)
                        linha = palavra
                    else:
                        linha = candidata
                linhas.append(linha)
                for linha in linhas:
                    imagem = self.fonte_cards.render(linha, True, cor)
                    self.tela.blit(imagem, imagem.get_rect(midtop=(rect.centerx, y)))
                    y += 30
                y += 25
            tecla = self.fonte_cards.render(f"[{i + 1}] Escolher", True, COR_TEXTO)
            self.tela.blit(tecla, tecla.get_rect(center=(rect.centerx, rect.bottom - 30)))
        dica = self.fonte_cards.render("Clique em uma opção ou pressione 1, 2 ou 3", True, COR_TEXTO)
        self.tela.blit(dica, dica.get_rect(center=(LARGURA // 2, 590)))

    def desenhar(self):
        if self.estado == "menu":
            self.menu.desenhar(self.tela)
            pygame.display.flip()
            return
        self.tela.blit(self.mapa, (0, 0))
        self.todos_sprites.draw(self.tela)
        self.jogador.desenhar_arma(self.tela)
        if self.tempo_invulneravel:
            pygame.draw.circle(self.tela, (235, 240, 180), self.jogador.rect.center, 30, 2)
        for inimigo in self.inimigos:
            if inimigo.chefe:
                barra = pygame.Rect(inimigo.rect.centerx - 45, inimigo.rect.top - 12, 90, 7)
                pygame.draw.rect(self.tela, (40, 20, 45), barra)
                pygame.draw.rect(self.tela, (191, 75, 235), (barra.x, barra.y, round(barra.width * max(0, inimigo.vida) / inimigo.vida_maxima), barra.height))
        pygame.draw.rect(self.tela, (30, 40, 30), (0, 0, LARGURA, 42))

    #Relógio
        if self.tempo_final is None:
            tempo_atual = pygame.time.get_ticks()
            tempo = (tempo_atual - self.tempo_inicio) // 1000
        else:
            tempo = (self.tempo_final - self.tempo_inicio) // 1000

    #HUD
        texto = self.fonte.render(
            f"Rodada: {self.rodada} | Vida: {self.jogador.vida}/{self.jogador.vida_maxima} | "
            f"Pontos: {self.pontos} | Nível: {self.nivel} | "
            f"Tempo: {tempo}",
            True,
            COR_TEXTO
        )

        self.tela.blit(texto, (10, 10))

    #Barra de XP
        largura_barra = 400
        altura_barra = 22

        x_barra = (LARGURA - largura_barra) // 2
        y_barra = ALTURA - 25

        # Fundo da barra
        pygame.draw.rect(
            self.tela,
            (50, 50, 50),
            (x_barra, y_barra, largura_barra, altura_barra)
        )

        # Progresso
        progresso = self.xp / self.xp_maximo

        pygame.draw.rect(
            self.tela,
            (0, 255, 100),
            (
                x_barra,
                y_barra,
                largura_barra * progresso,
                altura_barra
            )
        )
        y_mensagem = 100
        for mensagem in self.mensagens:
            texto_renderizado = self.fonte.render(mensagem["texto"], True, COR_MENSAGEM)
            rect_texto = texto_renderizado.get_rect(center=(LARGURA // 2, y_mensagem))
            self.tela.blit(texto_renderizado, rect_texto)
            y_mensagem += 40
        if self.menu_upgrade_ativo:
            self.desenhar_menu_upgrade()

        pygame.display.flip()

    def executar(self):

        #loop principal

        while self.rodando:
            self.clock.tick(FPS)
            self.processar_eventos()
            if not self.rodando:
                break
            self.atualizar()
            self.desenhar()

        pygame.quit()
