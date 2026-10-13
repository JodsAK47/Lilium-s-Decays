# 🌱 lilium's Decay

Um jogo de sobrevivência inspirado em **Brotato**, onde plantas guerreiras enfrentam hordas intermináveis de zumbis para proteger o jardim.

---

## 📖 Sobre o Jogo

**Garden Survivors** é um jogo de ação e sobrevivência em arena desenvolvido com **Python** e **Pygame**.

O jogador controla uma planta armada que deve sobreviver a ondas cada vez mais difíceis de zumbis. Durante a partida, é possível coletar recursos, evoluir atributos e desbloquear novas habilidades para enfrentar inimigos mais poderosos.

A proposta combina a progressão rápida e frenética de Brotato com um universo de plantas e mortos-vivos.

---

## 🎮 Gameplay

* Movimentação livre pelo mapa.
* Ataques automáticos.
* Ondas progressivas de inimigos.
* Sistema de evolução entre rodadas.
* Diferentes plantas jogáveis.
* Diversos tipos de zumbis.
* Chefes especiais.
* inimigos que surgem em maior quantidade e mais rapido a cada rodada que passa(Usando contadores e quantidades de inimigos)

---

## 🌿 Plantas Disponíveis

### 🟢 Ervilheiro

* Alta velocidade de ataque.
* Dano moderado.

### 🌵 Cacto

* Alto dano por disparo.
* Menor velocidade de movimento.

### 🌻 Girassol Guerreiro

* Regeneração de vida.
* Atributos equilibrados.

### 🦷 Planta Carnívora

* Especialista em combate corpo a corpo.
* Grande resistência.

---

## 🧟 Inimigos

| Inimigo | Arte | Comportamento | Aparece |
| --- | --- | --- | --- |
| Zumbi Comum | Verde | Persegue a planta; 3 de vida | Rodada 1 |
| Zumbi Corredor | Amarelo | Mais rápido; 1 de vida | Rodada 1 |
| Zumbi Tanque | Azul | Lento e resistente; 8 de vida | A partir da rodada 2 |
| Zumbi Roxo | Roxo | Dispara um poder à distância; 4 de vida | A partir da rodada 3 |
| Lich | `Litch.png` | Chefe com 35 de vida, barra de vida e rajadas de três magias | Um nas rodadas 5, 10, 15… |

O Lich concede 15 XP ao ser derrotado e não desaparece ao encostar no jogador.
Após receber dano, a planta ganha um segundo de proteção, indicado por um círculo.

---

## ⭐ Sistema de Melhorias

Ao subir de nível, o jogo pausa e oferece três habilidades diferentes sorteadas
entre as cinco abaixo. Clique em um cartão ou pressione **1, 2 ou 3** para escolher.

| Habilidade | Efeito por escolha |
| --- | --- |
| Adubo potente | +20% de dano nos próximos tiros |
| Fotossíntese acelerada | +15% de velocidade de ataque |
| Casca resistente | +1 de vida máxima e recupera 1 de vida |
| Raízes coletoras | +30% de alcance de atração do XP |
| Espinhos perfurantes | Cada tiro pode atingir mais 1 inimigo |

As melhorias se acumulam durante a partida; os percentuais são aplicados sobre
o valor atual. Cada projétil causa dano apenas uma vez em cada inimigo.
Se uma coleta render vários níveis, cada nível concede uma escolha, em sequência.
Uma nova partida reinicia todos os atributos.

A tela de evolução compara o valor atual do atributo com o valor após a escolha.
O painel **Suas melhorias** mostra quantas vezes cada habilidade foi adquirida,
o bônus acumulado e o atributo atual. A quantidade de escolhas pendentes também
fica visível; o jogo permanece pausado até terminar todas as escolhas.

### Experiência e progressão

O XP aparece como cristais com facetas e brilho animado: verde para 1 XP,
azul para recompensas de 2 a 9 XP e roxo para 10 XP ou mais (como o Lich).
A barra da partida mostra o XP coletado e o custo do próximo nível.

Cada nível exige mais experiência. Os primeiros custos são **10, 14, 19, 24 e
30 XP**. Para um nível atual `n`, o custo é
`10 + 4 * (n - 1) + (n - 1) ** 2 // 4`: crescimento gradual, sem multiplicação
exponencial. O XP excedente é preservado; uma coleta grande pode conceder vários
níveis, cada um com uma escolha de melhoria. A nova partida reinicia nível,
experiência, atributos e histórico de habilidades.


---

## 🎯 Objetivo

Sobreviver ao maior número possível de ondas e derrotar os chefes que surgem durante a partida.

---

## 🎮 Controles

| Tecla | Função              |
| ----- | ------------------- |
| W     | Mover para cima     |
| A     | Mover para esquerda |
| S     | Mover para baixo    |
| D     | Mover para direita  |
| ESC   | Voltar ao menu e encerrar a partida atual |

---

### Menu e sprites implementados

No menu inicial, clique em **Jogar** ou pressione Enter/Espaço para abrir a seleção.
Depois, selecione **Cacto**, **Ervilheiro** ou **Lírio** com o mouse, A/D ou as setas.
Clique em **Iniciar partida** ou pressione Enter/Espaço para começar.
Na seleção, **Voltar** ou ESC retorna ao menu inicial.
Cada planta usa sua animação e seu projétil; os atributos de combate continuam iguais.
A seleção mostra apenas as plantas. As três armas aparecem durante a partida, acompanhando a mira automática.
O cenário da partida usa a textura `ARTES/deserto.png` repetida pelo mapa.

Todos os 17 PNGs de `ARTES` são utilizados: as três plantas, suas três armas e
três projéteis, os quatro zumbis, o Lich, os poderes do zumbi roxo e do Lich e o deserto.
As folhas de sprites são recortadas conforme a quantidade de quadros de cada arte,
preservando suas proporções. O Cacto usa `cacto.png`.

ESC durante a partida retorna ao menu; ao jogar novamente, a partida começa do zero.
Ao perder toda a vida, o jogo também retorna ao menu inicial. ESC no menu ou **Sair** fecha o jogo.

## 🛠️ Tecnologias Utilizadas

* Python 3
* Pygame

---

## 🚀 Instalação

Clone o repositório:

```bash
git clone https://github.com/seu-usuario/garden-survivors.git
```

Acesse a pasta do projeto:

```bash
cd garden-survivors
```

Instale as dependências:

```bash
pip install pygame
```

Execute o jogo:

```bash
python main.py
```

Para verificar carregamento de todas as artes, animações, ataques, colisões e rodadas
sem abrir uma janela:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

---

## 📂 Estrutura do Projeto

```text
garden-survivors/
│
├── assets/
│   ├── sprites/
│   ├── sounds/
│   └── backgrounds/
│
├── src/
│   ├── player.py
│   ├── enemy.py
│   ├── projectile.py
│   ├── wave_manager.py
│   └── game.py
│
├── main.py
├── requirements.txt
└── README.md
```

---

## 📸 Screenshots

Adicione imagens do jogo aqui:

```markdown
![Gameplay](assets/screenshots/gameplay.png)
```

---

## 🔮 Funcionalidades Futuras

* Sistema de loja permanente
* Novas plantas jogáveis
* Mais tipos de zumbis
* Habilidades únicas
* Sistema de conquistas
* Salvamento de progresso
* Multiplayer local

---

## 🤝 Contribuição

Contribuições são bem-vindas!

1. Faça um Fork do projeto
2. Crie uma branch para sua feature

```bash
git checkout -b minha-feature
```

3. Commit suas alterações

```bash
git commit -m "Adiciona nova funcionalidade"
```

4. Envie para o GitHub

```bash
git push origin minha-feature
```

5. Abra um Pull Request

---

## 📜 Licença

Este projeto está sob a licença MIT.

---

Desenvolvido com ❤️ utilizando Python e Pygame.
