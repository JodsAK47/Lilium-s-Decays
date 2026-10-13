from dataclasses import dataclass


def xp_para_proximo_nivel(nivel):
    """Crescimento gradual: 10, 14, 19, 24, 30… sem salto exponencial."""
    progresso = max(0, nivel - 1)
    return 10 + 4 * progresso + progresso * progresso // 4


@dataclass(frozen=True)
class Habilidade:
    nome: str
    descricao: str
    atributo: str
    multiplicador: float = 1
    acrescimo: int = 0

    def prever(self, jogador):
        valor = getattr(jogador, self.atributo)
        return valor * self.multiplicador + self.acrescimo

    def formatar_valor(self, valor):
        if self.atributo == "intervalo_tiro":
            texto = f"{1000 / valor:.2f} tiros/s"
        elif self.atributo == "dano_tiro":
            texto = f"{valor:.2f} de dano"
        elif self.atributo == "vida_maxima":
            texto = f"{valor:g} de vida máxima"
        elif self.atributo == "raio_atracao_xp":
            texto = f"{valor:.0f} px de alcance"
        else:
            texto = f"{int(valor) + 1} alvos por tiro"
        return texto.replace(".", ",")

    def efeito_acumulado(self, quantidade):
        if not quantidade:
            return "Ainda não adquirida"
        if self.atributo == "vida_maxima":
            return f"+{quantidade} de vida máxima"
        if self.atributo == "perfuracoes":
            return f"+{quantidade} alvos por tiro"
        fator = 1 / self.multiplicador if self.atributo == "intervalo_tiro" else self.multiplicador
        bonus = (fator ** quantidade - 1) * 100
        unidade = {"dano_tiro": "dano", "intervalo_tiro": "cadência", "raio_atracao_xp": "alcance"}[self.atributo]
        return f"+{bonus:.1f}% de {unidade}".replace(".", ",")

    def aplicar(self, jogador):
        setattr(jogador, self.atributo, self.prever(jogador))
        if self.atributo == "vida_maxima":
            jogador.vida = min(jogador.vida + 1, jogador.vida_maxima)


HABILIDADES = (
    Habilidade("Adubo potente", "+20% de dano nos próximos tiros.", "dano_tiro", 1.2),
    Habilidade("Fotossíntese acelerada", "+15% de velocidade de ataque.", "intervalo_tiro", 1 / 1.15),
    Habilidade("Casca resistente", "+1 de vida máxima e recupera 1 de vida.", "vida_maxima", acrescimo=1),
    Habilidade("Raízes coletoras", "+30% de alcance para atrair XP.", "raio_atracao_xp", 1.3),
    Habilidade("Espinhos perfurantes", "Cada tiro pode atingir mais 1 inimigo.", "perfuracoes", acrescimo=1),
)
