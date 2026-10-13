"""Execute com .venv/bin/python -m unittest discover -s tests -v."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import unittest
from pathlib import Path
from unittest.mock import patch

import pygame
import assets
from entities.projectile import PoderInimigo, Tiro
from game import Game
from inimigos1 import Lich, ZumbiComum, ZumbiCorredor, ZumbiRoxo, ZumbiTanque


class IntegracaoArtes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jogo = Game()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.jogo.iniciar_partida()

    def adicionar(self, inimigo):
        self.jogo.inimigos.add(inimigo)
        self.jogo.todos_sprites.add(inimigo)
        return inimigo

    def test_todas_as_artes_sao_carregadas(self):
        for funcao in (assets.carregar_imagem, assets.carregar_frames, assets.carregar_faixa,
                       assets.carregar_arma, assets.carregar_tiro, assets.carregar_poder):
            funcao.cache_clear()
        with patch.object(pygame.image, "load", wraps=pygame.image.load) as carregar:
            assets.criar_mapa((1200, 800))
            for personagem in assets.PERSONAGENS:
                self.assertEqual(len(assets.carregar_frames(personagem, 50)), 6)
                for esquerda in (False, True):
                    self.assertGreater(assets.carregar_arma(personagem, esquerda=esquerda).get_width(), 0)
                assets.carregar_tiro(personagem)
            for arquivo, quantidade, altura in assets.INIMIGOS.values():
                frames = assets.carregar_faixa(arquivo, quantidade, altura)
                self.assertEqual(len(frames), quantidade)
                self.assertTrue(all(frame.get_bounding_rect().width > 0 for frame in frames))
            assets.carregar_poder("lich")
            assets.carregar_poder("roxo")
        usados = {Path(chamada.args[0]).name for chamada in carregar.call_args_list}
        existentes = {p.name for p in (assets.RAIZ / "ARTES").glob("*.png")}
        self.assertEqual(usados, existentes)

    def test_rodadas_introduzem_inimigos_e_um_chefe(self):
        for rodada, tipo in ((2, ZumbiTanque), (3, ZumbiRoxo), (5, Lich), (10, Lich)):
            self.jogo.iniciar_partida()
            self.jogo.rodada = rodada
            self.jogo.spawnar_inimigo()
            self.assertIsInstance(next(iter(self.jogo.inimigos)), tipo)
            for i in range(1, 20):
                self.jogo.inimigos_spawnados = i
                self.jogo.spawnar_inimigo()
            self.assertEqual(sum(isinstance(i, Lich) for i in self.jogo.inimigos), int(rodada % 5 == 0))

    def test_conjuradores_disparam_e_respeitam_intervalo(self):
        for tipo, quantidade in ((ZumbiRoxo, 1), (Lich, 3)):
            inimigo = tipo(600, 450)
            inimigo.tempo_ataque = 0
            poderes = inimigo.atacar(self.jogo.jogador)
            self.assertEqual(len(poderes), quantidade)
            self.assertFalse(inimigo.atacar(self.jogo.jogador))
            for poder in poderes:
                antes = poder.posicao.copy()
                poder.update()
                self.assertGreater(poder.posicao.distance_to(antes), 0)

    def test_conjurador_fora_da_arena_continua_entrando(self):
        inimigo = Lich(600, 840)
        for _ in range(160):
            inimigo.update(self.jogo.jogador)
        self.assertLessEqual(inimigo.rect.bottom, 800)

    def test_magia_causa_dano_com_protecao_temporaria(self):
        vida = self.jogo.jogador.vida
        for _ in range(2):
            poder = PoderInimigo(*self.jogo.jogador.rect.center, (1, 0), "roxo")
            self.jogo.poderes_inimigos.add(poder)
            self.jogo.todos_sprites.add(poder)
            self.jogo.verificar_colisoes()
            self.assertFalse(poder.alive())
        self.assertEqual(self.jogo.jogador.vida, vida - 1)

    def test_chefe_sobrevive_contato_e_morte_concede_xp_uma_vez(self):
        chefe = self.adicionar(Lich(*self.jogo.jogador.rect.center))
        self.jogo.verificar_colisoes()
        self.assertTrue(chefe.alive())
        tiro = Tiro(*chefe.rect.center, (1, 0), dano=35, perfuracoes=1)
        self.jogo.tiros.add(tiro)
        self.jogo.jogador.rect.center = (100, 100)
        self.jogo.verificar_colisoes()
        self.jogo.verificar_colisoes()
        self.assertFalse(chefe.alive())
        self.assertEqual(self.jogo.pontos, 1)
        self.assertEqual(sum(xp.quantidade for xp in self.jogo.xps), 15)

    def test_poder_expira_e_reinicio_limpa_ataques(self):
        poder = PoderInimigo(600, 400, (0, 0), "lich")
        self.jogo.poderes_inimigos.add(poder)
        self.jogo.todos_sprites.add(poder)
        for _ in range(361):
            poder.update()
        self.assertFalse(poder.alive())
        self.jogo.poderes_inimigos.add(PoderInimigo(600, 400, (1, 0), "roxo"))
        self.jogo.iniciar_partida()
        self.assertFalse(self.jogo.poderes_inimigos)
        self.assertEqual(self.jogo.tempo_invulneravel, 0)

    def test_renderizacao_de_todas_as_plantas_e_animacoes(self):
        for indice in range(3):
            self.jogo.menu.selecionado = indice
            self.jogo.menu.tela_atual = "selecao"
            self.jogo.menu.desenhar(self.jogo.tela)
            self.jogo.iniciar_partida()
            for i, tipo in enumerate((ZumbiComum, ZumbiCorredor, ZumbiTanque, ZumbiRoxo, Lich)):
                self.adicionar(tipo(200 + i * 170, 250))
            for frame in range(180):
                self.jogo.atualizar()
                if frame % 20 == 0:
                    self.jogo.disparar_tiro()
                self.jogo.desenhar()
            self.assertEqual(self.jogo.estado, "jogo")
        self.jogo.menu.selecionado = 0


if __name__ == "__main__":
    unittest.main()
