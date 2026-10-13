import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest
from unittest.mock import patch

import pygame
from game import Game
from habilidades import HABILIDADES, xp_para_proximo_nivel
from inimigos1 import XP, ZumbiComum


class Evolucao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jogo = Game()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.jogo.iniciar_partida()

    def coletar(self, quantidade):
        cristal = XP(*self.jogo.jogador.rect.center, quantidade)
        self.jogo.xps.add(cristal)
        self.jogo.todos_sprites.add(cristal)
        self.jogo.verificar_colisoes()

    def test_perfis_aplicados_aos_tiros_melhorias_e_reinicio(self):
        esperados = {"cacto": (5, 1.0, 4, 300), "ervilheiro": (4, 0.4, 6, 120),
                     "lirio": (7, 0.5, 5, 200)}
        for indice, personagem in enumerate(self.jogo.menu.personagens):
            self.jogo.menu.selecionado = indice
            self.jogo.iniciar_partida()
            jogador = self.jogo.jogador
            vida, dano, velocidade, intervalo = esperados[personagem]
            self.assertEqual((jogador.vida, jogador.vida_maxima, jogador.dano_tiro,
                              jogador.velocidade, jogador.intervalo_tiro),
                             (vida, vida, dano, velocidade, intervalo))
            alvo = ZumbiComum(600, 300)
            self.jogo.inimigos.add(alvo)
            HABILIDADES[0].aplicar(jogador)
            HABILIDADES[1].aplicar(jogador)
            HABILIDADES[2].aplicar(jogador)
            self.jogo.disparar_tiro()
            tiro = next(iter(self.jogo.tiros))
            self.assertAlmostEqual(tiro.dano, dano * 1.2)
            self.assertAlmostEqual(jogador.intervalo_tiro, intervalo / 1.15)
            self.assertEqual(jogador.vida, vida + 1)
            self.jogo.iniciar_partida()
            self.assertEqual(self.jogo.jogador.dano_tiro, dano)
            self.assertEqual(self.jogo.jogador.vida, vida)
        self.jogo.menu.selecionado = 0

    def test_custos_crescem_gradualmente(self):
        custos = [xp_para_proximo_nivel(n) for n in range(1, 101)]
        self.assertEqual(custos[:5], [10, 14, 19, 24, 30])
        self.assertTrue(all(a < b <= a * 1.4 for a, b in zip(custos, custos[1:])))

    def test_coleta_preserva_excedente_e_concede_escolha_por_nivel(self):
        self.coletar(50)
        self.assertEqual((self.jogo.nivel, self.jogo.xp, self.jogo.xp_maximo), (4, 7, 24))
        self.assertEqual(self.jogo.melhorias_pendentes, 3)
        for restante in (2, 1, 0):
            self.jogo.escolher_habilidade(0)
            self.assertEqual(self.jogo.melhorias_pendentes, restante)
            self.assertEqual(self.jogo.menu_upgrade_ativo, restante > 0)
        self.assertEqual(sum(self.jogo.habilidades_adquiridas.values()), 3)

    def test_custo_exato_nao_pula_nivel_extra(self):
        self.coletar(10)
        self.assertEqual((self.jogo.nivel, self.jogo.xp, self.jogo.xp_maximo), (2, 0, 14))
        self.jogo.escolher_habilidade(0)
        self.coletar(13)
        self.assertEqual(self.jogo.nivel, 2)
        self.assertFalse(self.jogo.menu_upgrade_ativo)
        self.coletar(1)
        self.assertEqual((self.jogo.nivel, self.jogo.xp, self.jogo.xp_maximo), (3, 0, 19))

    def test_previa_historico_e_bonus_correspondem_aos_atributos(self):
        for habilidade in HABILIDADES:
            self.jogo.melhorias_pendentes = 2
            for _ in range(2):
                self.jogo.abrir_escolha_habilidade()
                self.jogo.opcoes_habilidades[0] = habilidade
                antes = getattr(self.jogo.jogador, habilidade.atributo)
                previsto = habilidade.prever(self.jogo.jogador)
                self.assertEqual(getattr(self.jogo.jogador, habilidade.atributo), antes)
                self.jogo.escolher_habilidade(0)
                self.assertAlmostEqual(getattr(self.jogo.jogador, habilidade.atributo), previsto)
            self.assertEqual(self.jogo.habilidades_adquiridas[habilidade.atributo], 2)
        self.assertEqual(HABILIDADES[0].efeito_acumulado(2), "+44,0% de dano")
        self.assertEqual(HABILIDADES[3].efeito_acumulado(2), "+69,0% de alcance")
        self.assertEqual(HABILIDADES[4].formatar_valor(self.jogo.jogador.perfuracoes), "3 alvos por tiro")
        self.jogo.escolher_habilidade(0)  # Uma escolha fechada não aplica de novo.
        self.assertEqual(sum(self.jogo.habilidades_adquiridas.values()), 10)

    def test_upgrade_pausa_mundo_e_aceita_mouse_e_teclado(self):
        inimigo = ZumbiComum(100, 100)
        self.jogo.inimigos.add(inimigo)
        self.coletar(24)
        antes = inimigo.rect.copy()
        self.jogo.atualizar()
        self.assertEqual(inimigo.rect, antes)
        clique = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=self.jogo.rects_opcoes[1].center)
        tecla = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_3)
        for evento in (clique, tecla):
            with patch.object(pygame.event, "get", return_value=[evento]):
                self.jogo.processar_eventos()
        self.assertFalse(self.jogo.menu_upgrade_ativo)
        self.assertEqual(sum(self.jogo.habilidades_adquiridas.values()), 2)

    def test_reinicio_limpa_historico_e_progressao(self):
        self.coletar(50)
        self.jogo.escolher_habilidade(0)
        self.jogo.iniciar_partida()
        self.assertEqual((self.jogo.nivel, self.jogo.xp, self.jogo.xp_maximo), (1, 0, 10))
        self.assertFalse(self.jogo.habilidades_adquiridas)
        self.assertFalse(self.jogo.menu_upgrade_ativo)
        self.assertEqual(self.jogo.melhorias_pendentes, 0)

    def test_cristal_tem_transparencia_animacao_e_atracao_sem_ultrapassar(self):
        jogador = self.jogo.jogador
        for quantidade in (1, 3, 15):
            cristal = XP(jogador.rect.centerx + 3, jogador.rect.centery, quantidade)
            self.assertEqual(cristal.image.get_at((0, 0)).a, 0)
            self.assertGreater(cristal.image.get_at((18, 18)).a, 0)
            self.assertNotEqual(pygame.image.tobytes(cristal.frames[0], "RGBA"),
                                pygame.image.tobytes(cristal.frames[1], "RGBA"))
            cristal.update(jogador)
            self.assertEqual(cristal.rect.center, jogador.rect.center)
            self.assertEqual(cristal.quantidade, quantidade)

    def test_tela_mostra_todas_as_opcoes_sem_alterar_atributos(self):
        self.coletar(10)
        antes = vars(self.jogo.jogador).copy()
        for i in range(len(HABILIDADES)):
            self.jogo.opcoes_habilidades = [HABILIDADES[(i+k) % len(HABILIDADES)] for k in range(3)]
            self.jogo.desenhar()
        self.assertEqual(vars(self.jogo.jogador), antes)
        self.assertFalse(self.jogo.habilidades_adquiridas)


if __name__ == "__main__":
    unittest.main()
