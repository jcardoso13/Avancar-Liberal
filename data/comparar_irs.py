"""Compara o IRS da imagem, com minimo de existencia, com cinco escaloes propostos.

Exemplos (970 EUR e apenas uma hipotese de SMN mensal):
    python3 data/comparar_irs.py --smn 970
    python3 data/comparar_irs.py --smn 970 --rendimentos 18530 30538 89995
    python3 data/comparar_irs.py --smn 970 --csv distribuicao.csv --limite-perda 1000000000
    python3 data/comparar_irs.py --smn 970 --max-rendimento 60000 --graphs-dir data/graphs
    python3 data/comparar_irs.py --smn 970 --ias 537.13 --minimo-existencia 13580
    python3 data/comparar_irs.py --smn 970 --taxa-tsu 23.75

Exporta graficos PNG e SVG para data/graphs, independentemente da pasta atual.
Inclui IRS + SS trabalhador sobre bruto e IRS + SS + TSU sobre custo do trabalho.
Taxas gerais assumidas: SS trabalhador 11%; TSU empregador 23,75%, configuravel.
Custo do trabalho = bruto + TSU; exclui outros custos do empregador.
Nos novos graficos, o bruto maximo corresponde ao maximo coletavel selecionado.
Dependencia: python3 -m pip install -r data/requirements.txt

CSV: rendimento_coletavel,contribuintes
     18530,100
     30538,50
Cada linha representa contribuintes com o mesmo rendimento coletavel anual,
antes do abatimento por minimo de existencia, nao salario bruto.
Se forem medias de intervalos, os totais sao aproximacoes.
Tambem aceita CSV separado por ponto e virgula e valores como 18530,50.

Fonte da tabela: imagem fornecida, identificada como proposta OE2027/art. 68.
Usa as taxas normais marginais. As taxas medias arredondadas da imagem nao
sao taxas adicionais; a sua utilizacao legal pode gerar pequenas diferencas.
Minimo de existencia: art. 70 do CIRS, com as formulas atualmente publicadas:
https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/codigos_tributarios/cirs_rep/Pages/irs70.aspx
Deducao especifica: art. 25 do CIRS (maximo entre 8,54 IAS e contribuicoes SS):
https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/codigos_tributarios/cirs_rep/Pages/irs25.aspx
Cenario: trabalhador dependente, solteiro, sem dependentes nem outros rendimentos,
SS de 11%. O bruto e estimado invertendo a deducao especifica da categoria A.
A isencao da proposta corresponde ao SMN bruto anual depois da deducao especifica.
IAS e referencia para 2027 sao hipoteses configuraveis, nao legislacao confirmada.
Referencia por omissao: maximo entre 12880 EUR, SMN anualizado e 21 IAS.
Aplica despesas gerais familiares (por omissao, 250 EUR) nas duas alternativas.
Nao aplica o abatimento do art. 70 a proposta, que tem o seu proprio escalao 0%.
Nao inclui outras deducoes, quociente conjugal, solidariedade nem regimes especiais.
Nao estima receita nacional sem dados; CSV assume o mesmo cenario por contribuinte.
"""

import argparse
import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


ZERO = Decimal("0")
CENTIMO = Decimal("0.01")
Escalao = tuple[Decimal | None, Decimal]
TABELA_IMAGEM: tuple[Escalao, ...] = (
    (Decimal("8666"), Decimal("12.20")),
    (Decimal("13075"), Decimal("15.20")),
    (Decimal("18530"), Decimal("20.70")),
    (Decimal("23985"), Decimal("23.60")),
    (Decimal("30538"), Decimal("30.60")),
    (Decimal("44762"), Decimal("34.60")),
    (Decimal("48373"), Decimal("43.10")),
    (Decimal("89995"), Decimal("44.60")),
    (None, Decimal("48.00")),
)


@dataclass(frozen=True)
class MinimoExistencia:
    ias: Decimal
    referencia: Decimal
    despesas_gerais: Decimal = Decimal("250")
    taxa_ss: Decimal = Decimal("0.11")

    def __post_init__(self) -> None:
        valores = (self.ias, self.referencia, self.despesas_gerais, self.taxa_ss)
        if any(not valor.is_finite() or valor < ZERO for valor in valores):
            raise ValueError("Os parametros fiscais devem ser finitos e nao negativos.")
        if self.ias <= ZERO or self.referencia <= ZERO or self.taxa_ss >= 1:
            raise ValueError("IAS e referencia devem ser positivos; a taxa SS deve ser inferior a 1.")

    def bruto_estimado(self, coletavel: Decimal) -> Decimal:
        if not coletavel.is_finite() or coletavel < ZERO:
            raise ValueError("O rendimento deve ser finito e nao negativo.")
        if coletavel == ZERO:
            return ZERO
        deducao = Decimal("8.54") * self.ias
        return max(coletavel + deducao, coletavel / (1 - self.taxa_ss))

    def coletavel_de_bruto(self, bruto: Decimal) -> Decimal:
        if not bruto.is_finite() or bruto < ZERO:
            raise ValueError("O rendimento bruto deve ser finito e nao negativo.")
        deducao = max(Decimal("8.54") * self.ias, bruto * self.taxa_ss)
        return max(ZERO, bruto - deducao)

    def abatimento(self, coletavel: Decimal) -> Decimal:
        bruto = self.bruto_estimado(coletavel)
        if bruto > Decimal("2.2") * 14 * self.ias:
            return ZERO
        deducao = bruto - coletavel
        primeiro_limite, primeira_taxa = TABELA_IMAGEM[0]
        assert primeiro_limite is not None
        credito_em_rendimento = self.despesas_gerais / (primeira_taxa / 100)
        limite_transicao = self.referencia + (primeiro_limite - credito_em_rendimento) / Decimal("3.60")
        if bruto <= self.referencia:
            valor = self.referencia - deducao - credito_em_rendimento
        elif bruto <= limite_transicao:
            valor = self.referencia - Decimal("2.60") * (bruto - self.referencia) - deducao - credito_em_rendimento
        else:
            valor = limite_transicao - primeiro_limite - Decimal("1.35") * (bruto - limite_transicao) - deducao
        return min(coletavel, max(ZERO, valor))


def numero_nao_negativo(texto: str) -> Decimal:
    try:
        valor = Decimal(texto.strip().replace(",", "."))
    except InvalidOperation as erro:
        raise argparse.ArgumentTypeError(f"Numero invalido: {texto!r}") from erro
    if not valor.is_finite() or valor < ZERO:
        raise argparse.ArgumentTypeError("O valor deve ser finito e nao negativo.")
    return valor


def tabela_proposta(limite_isento: Decimal) -> tuple[Escalao, ...]:
    if not ZERO < limite_isento < Decimal("23985"):
        raise ValueError("O SMN anualizado deve ser maior que 0 e menor que 23985 EUR.")
    return (
        (limite_isento, ZERO),
        (Decimal("23985"), Decimal("15")),
        (Decimal("44762"), Decimal("28")),
        (Decimal("89995"), Decimal("35")),
        (None, Decimal("48")),
    )


def coleta(rendimento: Decimal, tabela: tuple[Escalao, ...]) -> Decimal:
    if not rendimento.is_finite() or rendimento < ZERO:
        raise ValueError("O rendimento deve ser finito e nao negativo.")
    imposto = ZERO
    limite_anterior = ZERO
    for limite, taxa in tabela:
        topo = rendimento if limite is None else min(rendimento, limite)
        imposto += max(ZERO, topo - limite_anterior) * taxa / Decimal("100")
        if limite is None or rendimento <= limite:
            break
        limite_anterior = limite
    return imposto.quantize(CENTIMO, rounding=ROUND_HALF_UP)


def impostos_comparados(
    rendimento: Decimal, proposta: tuple[Escalao, ...], minimo: MinimoExistencia | None = None
) -> tuple[Decimal, Decimal]:
    abatimento = minimo.abatimento(rendimento) if minimo is not None else ZERO
    despesas = minimo.despesas_gerais if minimo is not None else ZERO
    atual = max(ZERO, coleta(rendimento - abatimento, TABELA_IMAGEM) - despesas)
    novo = max(ZERO, coleta(rendimento, proposta) - despesas)
    return atual, novo


def euros(valor: Decimal) -> str:
    return f"{valor:,.2f}".translate(str.maketrans({",": " ", ".": ","}))


def ler_distribuicao(caminho: Path) -> list[tuple[Decimal, int]]:
    linhas = []
    with caminho.open(encoding="utf-8-sig", newline="") as ficheiro:
        amostra = ficheiro.read(4096)
        ficheiro.seek(0)
        try:
            formato = csv.Sniffer().sniff(amostra, delimiters=",;")
        except csv.Error as erro:
            raise ValueError("CSV invalido: use virgula ou ponto e virgula.") from erro
        leitor = csv.DictReader(ficheiro, dialect=formato)
        obrigatorias = {"rendimento_coletavel", "contribuintes"}
        if not obrigatorias.issubset(leitor.fieldnames or []):
            raise ValueError("O CSV deve ter as colunas rendimento_coletavel,contribuintes.")
        for linha in leitor:
            try:
                rendimento = numero_nao_negativo(linha["rendimento_coletavel"])
                contribuintes = int(linha["contribuintes"])
                if contribuintes <= 0:
                    raise ValueError("A contagem de contribuintes deve ser positiva.")
            except (ValueError, TypeError, AttributeError, argparse.ArgumentTypeError) as erro:
                raise ValueError(f"Linha {leitor.line_num} do CSV: {erro}") from erro
            linhas.append((rendimento, contribuintes))
    if not linhas:
        raise ValueError("O CSV nao contem contribuinte algum.")
    return linhas


def totais(
    distribuicao: list[tuple[Decimal, int]], proposta: tuple[Escalao, ...],
    minimo: MinimoExistencia | None = None,
) -> tuple[Decimal, Decimal]:
    imagem = novo = ZERO
    for rendimento, quantidade in distribuicao:
        imposto_imagem, imposto_proposta = impostos_comparados(rendimento, proposta, minimo)
        imagem += imposto_imagem * quantidade
        novo += imposto_proposta * quantidade
    return imagem, novo


def mostrar_comparacao(
    rendimentos: list[Decimal], proposta: tuple[Escalao, ...], minimo: MinimoExistencia | None = None
) -> None:
    print("\nValores anuais em EUR; coletavel antes do minimo de existencia; reducao relativa ao IRS da imagem.")
    print(f"{'Rend. coletavel':>17} {'IRS imagem':>15} {'IRS proposta':>15} {'Poupanca':>15} {'Reducao':>10}")
    for rendimento in sorted(set(rendimentos)):
        atual, novo = impostos_comparados(rendimento, proposta, minimo)
        poupanca = atual - novo
        percentagem = f"{100 * poupanca / atual:.2f}%" if atual else "n/a"
        print(f"{euros(rendimento):>17} {euros(atual):>15} {euros(novo):>15} {euros(poupanca):>15} {percentagem:>10}")


def exportar_graficos(
    rendimentos: list[Decimal],
    proposta: tuple[Escalao, ...],
    pasta: Path,
    max_rendimento: Decimal,
    distribuicao: list[tuple[Decimal, int]] | None = None,
    minimo: MinimoExistencia | None = None,
    taxa_tsu: Decimal = Decimal("0.2375"),
) -> list[Path]:
    if not taxa_tsu.is_finite() or taxa_tsu < ZERO:
        raise ValueError("A taxa TSU deve ser finita e nao negativa.")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    pasta.mkdir(parents=True, exist_ok=True)
    pontos = {max_rendimento * Decimal(indice) / Decimal("800") for indice in range(801)}
    pontos.update(rendimento for rendimento in rendimentos if rendimento <= max_rendimento)
    pontos.update(
        limite for limite, _ in (*TABELA_IMAGEM, *proposta)
        if limite is not None and limite <= max_rendimento
    )
    if minimo is not None:
        primeiro_limite, primeira_taxa = TABELA_IMAGEM[0]
        assert primeiro_limite is not None
        transicao = minimo.referencia + (
            primeiro_limite - minimo.despesas_gerais / (primeira_taxa / 100)
        ) / Decimal("3.60")
        for bruto in (minimo.referencia, transicao, Decimal("2.2") * 14 * minimo.ias):
            deducao = min(bruto, max(Decimal("8.54") * minimo.ias, bruto * minimo.taxa_ss))
            coletavel = bruto - deducao
            pontos.update(valor for valor in (coletavel, coletavel + CENTIMO) if ZERO <= valor <= max_rendimento)
    amostra = sorted(pontos)
    eixo = [float(rendimento) for rendimento in amostra]
    impostos = [impostos_comparados(rendimento, proposta, minimo) for rendimento in amostra]
    imposto_imagem = [atual for atual, _ in impostos]
    imposto_proposta = [novo for _, novo in impostos]
    poupancas = [atual - novo for atual, novo in zip(imposto_imagem, imposto_proposta)]
    formatador_euros = FuncFormatter(lambda valor, _: f"{valor:,.0f}".replace(",", " "))
    formatador_taxas = FuncFormatter(lambda valor, _: f"{valor:g}%")
    cores = ("#007c91", "#d35400")
    ficheiros = []
    limite_isento = proposta[0][0]
    rodape = (
        f"Limite coletavel isento na proposta: {euros(limite_isento)} EUR. "
        "Rendimento coletavel, nao salario bruto.\n"
        "Simulacao sem deducoes, minimo de existencia, quociente conjugal ou solidariedade."
    )
    if minimo is not None:
        rodape = (
            "Categoria A, solteiro, sem outros rendimentos; bruto estimado a partir do coletavel.\n"
            f"Hipoteses: IAS {euros(minimo.ias)} EUR; minimo {euros(minimo.referencia)} EUR brutos; "
            f"despesas gerais {euros(minimo.despesas_gerais)} EUR.\n"
            f"Proposta: 0% ate {euros(limite_isento)} EUR coletaveis. Sem outras deducoes ou solidariedade."
        )

    with plt.rc_context({
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titleweight": "bold", "figure.facecolor": "white",
        "axes.labelcolor": "#303030", "text.color": "#303030",
        "svg.fonttype": "none",
    }):
        def preparar(eixos, titulo, unidade):
            eixos.set_title(titulo, loc="left", pad=16)
            eixos.set_xlabel("Rendimento coletavel anual antes do minimo de existencia (EUR)")
            eixos.set_ylabel(unidade)
            eixos.set_xlim(0, float(max_rendimento))
            eixos.xaxis.set_major_formatter(formatador_euros)
            eixos.grid(axis="y", alpha=0.2)
            eixos.set_axisbelow(True)

        def guardar(figura, nome, nota=None):
            figura.text(0.08, 0.025, rodape if nota is None else nota, fontsize=8, color="#555555", va="bottom")
            figura.tight_layout(rect=(0.02, 0.16 if nota is None else 0.18, 0.98, 0.98))
            try:
                for formato in ("png", "svg"):
                    caminho = pasta / f"{nome}.{formato}"
                    figura.savefig(caminho, dpi=180, facecolor="white")
                    ficheiros.append(caminho)
            finally:
                plt.close(figura)

        figura, eixos = plt.subplots(figsize=(11, 6))
        preparar(eixos, "Taxa efetiva de IRS: imagem OE2027 vs. proposta", "Coleta / rendimento coletavel (%)")
        for impostos, cor, legenda in (
            (imposto_imagem, cores[0], "Imagem OE2027"),
            (imposto_proposta, cores[1], "Proposta"),
        ):
            efetivas = [float(100 * imposto / rendimento) if rendimento else 0 for rendimento, imposto in zip(amostra, impostos)]
            eixos.plot(eixo, efetivas, color=cor, label=legenda, linewidth=2.3)
        eixos.yaxis.set_major_formatter(formatador_taxas)
        eixos.set_ylim(bottom=0)
        eixos.legend(frameon=False)
        guardar(figura, "comparacao_irs")

        figura, eixos = plt.subplots(figsize=(11, 6))
        preparar(eixos, "Poupanca anual com a proposta", "IRS imagem - IRS proposta (EUR)")
        valores_poupanca = [float(valor) for valor in poupancas]
        eixos.plot(eixo, valores_poupanca, color=cores[0], linewidth=2.3)
        eixos.fill_between(eixo, valores_poupanca, 0, where=[valor >= 0 for valor in poupancas], color=cores[0], alpha=0.12, interpolate=True)
        eixos.fill_between(eixo, valores_poupanca, 0, where=[valor < 0 for valor in poupancas], color=cores[1], alpha=0.2, interpolate=True)
        eixos.axhline(0, color="#555555", linewidth=0.8)
        eixos.yaxis.set_major_formatter(formatador_euros)
        guardar(figura, "poupanca_anual")

        figura, paineis = plt.subplots(2, 1, figsize=(11, 9), sharex=True)
        for tabela, impostos, cor, legenda in (
            (TABELA_IMAGEM, imposto_imagem, cores[0], "Imagem OE2027"),
            (proposta, imposto_proposta, cores[1], "Proposta"),
        ):
            marginais = [
                float(next(taxa for limite, taxa in tabela if limite is None or rendimento < limite))
                for rendimento in amostra
            ]
            efetivas = [float(100 * imposto / rendimento) if rendimento else 0 for rendimento, imposto in zip(amostra, impostos)]
            paineis[0].step(eixo, marginais, where="post", color=cor, label=legenda, linewidth=2)
            paineis[1].plot(eixo, efetivas, color=cor, label=legenda, linewidth=2)
        for eixos, titulo in zip(paineis, ("Taxas marginais da tabela (antes do minimo de existencia)", "Taxa efetiva: IRS / rendimento coletavel")):
            preparar(eixos, titulo, "Taxa (%)")
            eixos.yaxis.set_major_formatter(formatador_taxas)
            eixos.set_ylim(bottom=0)
            eixos.legend(frameon=False)
        guardar(figura, "taxas_irs")

        if minimo is not None:
            max_bruto = minimo.bruto_estimado(max_rendimento)
            brutos = {max_bruto * Decimal(indice) / Decimal("800") for indice in range(1, 801)}
            brutos.update(minimo.bruto_estimado(valor) for valor in amostra if valor > ZERO)
            brutos.add(min(CENTIMO, max_bruto))
            amostra_bruta = sorted(brutos)
            impostos_brutos = [
                impostos_comparados(minimo.coletavel_de_bruto(bruto), proposta, minimo)
                for bruto in amostra_bruta
            ]
            nota_trabalho = (
                "Categoria A, solteiro, sem outros rendimentos; deducao especifica de 8,54 IAS ou SS.\n"
                f"Hipoteses: IAS {euros(minimo.ias)} EUR; minimo {euros(minimo.referencia)} EUR brutos; "
                f"despesas gerais {euros(minimo.despesas_gerais)} EUR.\n"
                f"SS trabalhador: {100 * minimo.taxa_ss:g}%; TSU empregador: {100 * taxa_tsu:g}%. "
                f"Proposta: 0% ate {euros(limite_isento)} EUR coletaveis.\n"
                "Custo do trabalho = bruto + TSU. Sem outras deducoes, solidariedade ou custos do empregador."
            )
            for incluir_tsu, nome, titulo, legenda_x, legenda_y in (
                (
                    False, "irs_ss_trabalhador", "IRS + SS do trabalhador: imagem OE2027 vs. proposta",
                    "Rendimento bruto anual (EUR)", "(IRS + SS trabalhador) / bruto (%)",
                ),
                (
                    True, "imposto_sobre_trabalho", "Carga total sobre o trabalho: imagem OE2027 vs. proposta",
                    "Custo anual do trabalho: bruto + TSU (EUR)", "(IRS + SS + TSU) / custo do trabalho (%)",
                ),
            ):
                bases = [bruto * (1 + taxa_tsu) if incluir_tsu else bruto for bruto in amostra_bruta]
                contribuicoes = [
                    bruto * (minimo.taxa_ss + taxa_tsu if incluir_tsu else minimo.taxa_ss)
                    for bruto in amostra_bruta
                ]
                figura, eixos = plt.subplots(figsize=(11, 6))
                preparar(eixos, titulo, legenda_y)
                eixos.set_xlabel(legenda_x)
                eixos.set_xlim(0, float(bases[-1]))
                for indice, cor, legenda in ((0, cores[0], "Imagem OE2027"), (1, cores[1], "Proposta")):
                    taxas = [
                        float(100 * (impostos[indice] + contribuicao) / base)
                        for impostos, contribuicao, base in zip(impostos_brutos, contribuicoes, bases)
                    ]
                    eixos.plot([float(base) for base in bases], taxas, color=cor, label=legenda, linewidth=2.3)
                eixos.yaxis.set_major_formatter(formatador_taxas)
                eixos.set_ylim(bottom=0)
                eixos.legend(frameon=False)
                guardar(figura, nome, nota_trabalho)

        if distribuicao is not None:
            atual, novo = totais(distribuicao, proposta, minimo)
            quantidade = sum(contagem for _, contagem in distribuicao)
            figura, eixos = plt.subplots(figsize=(9, 6))
            barras = eixos.bar(["Imagem OE2027", "Proposta"], [float(atual), float(novo)], color=cores, width=0.5)
            eixos.bar_label(barras, labels=[f"{euros(valor)} EUR" for valor in (atual, novo)], padding=8)
            eixos.set_title(
                f"IRS total do CSV: {quantidade:,} contribuintes\n"
                f"Perda de receita: {euros(atual - novo)} EUR",
                loc="left", pad=16,
            )
            eixos.set_ylabel("IRS total (EUR)")
            eixos.yaxis.set_major_formatter(formatador_euros)
            eixos.set_ylim(0, float(max(atual, novo)) * 1.2 if max(atual, novo) else 1)
            eixos.grid(axis="y", alpha=0.2)
            eixos.set_axisbelow(True)
            rodape += "\nUniverso do CSV, nao necessariamente nacional; medias de intervalos dao totais aproximados."
            guardar(figura, "receita_total_csv")
    return ficheiros


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--smn", type=numero_nao_negativo, required=True, help="SMN mensal assumido, em EUR.")
    parser.add_argument("--pagamentos", type=int, default=14, help="Meses para anualizar o SMN (por omissao: 14).")
    parser.add_argument("--rendimentos", type=numero_nao_negativo, nargs="+", help="Rendimentos coletaveis anuais a comparar.")
    parser.add_argument("--csv", type=Path, help="Distribuicao de rendimentos e contagens de contribuintes.")
    parser.add_argument("--limite-perda", type=numero_nao_negativo, help="Limite anual em EUR: 1000000 = 1 milhao; 1000000000 = 1 mil milhoes.")
    parser.add_argument("--graphs-dir", type=Path, default=Path(__file__).resolve().parent / "graphs", help="Pasta de exportacao dos graficos (por omissao: data/graphs).")
    parser.add_argument("--max-rendimento", type=numero_nao_negativo, help="Rendimento maximo nos graficos (por omissao: pelo menos 120000 EUR, incluindo os dados fornecidos).")
    parser.add_argument("--ias", type=numero_nao_negativo, default=Decimal("537.13"), help="IAS mensal assumido (por omissao: 537.13 EUR; hipotese, nao valor confirmado de 2027).")
    parser.add_argument("--minimo-existencia", type=numero_nao_negativo, help="Referencia anual bruta assumida (por omissao: maximo entre 12880 EUR, SMN anualizado e 21 IAS).")
    parser.add_argument("--despesas-gerais", type=numero_nao_negativo, default=Decimal("250"), help="Deducao anual de despesas gerais nas duas alternativas, entre 0 e 250 EUR.")
    parser.add_argument("--taxa-tsu", type=numero_nao_negativo, default=Decimal("23.75"), help="Taxa percentual de TSU do empregador (por omissao: 23.75).")
    args = parser.parse_args()
    if args.pagamentos <= 0:
        parser.error("--pagamentos deve ser positivo.")
    if args.max_rendimento == ZERO:
        parser.error("--max-rendimento deve ser positivo.")
    if args.despesas_gerais > Decimal("250"):
        parser.error("--despesas-gerais nao pode exceder 250 EUR neste cenario.")
    if args.limite_perda is not None and args.csv is None:
        parser.error("--limite-perda exige --csv; exemplos isolados nao estimam receita total.")
    smn_anual_bruto = args.smn * args.pagamentos
    try:
        referencia = args.minimo_existencia if args.minimo_existencia is not None else max(
            Decimal("12880"), smn_anual_bruto, 21 * args.ias
        )
        minimo = MinimoExistencia(args.ias, referencia, args.despesas_gerais)
        limite_isento = minimo.coletavel_de_bruto(smn_anual_bruto)
        proposta = tabela_proposta(limite_isento)
        distribuicao = ler_distribuicao(args.csv) if args.csv else None
    except (OSError, ValueError, csv.Error) as erro:
        parser.error(str(erro))

    print("Comparacao de IRS simulado: imagem OE2027 com minimo de existencia vs. proposta")
    print(f"Hipotese: SMN mensal {euros(args.smn)} EUR x {args.pagamentos} = {euros(smn_anual_bruto)} EUR brutos anuais.")
    print(f"Limite isento coletavel: {euros(smn_anual_bruto)} - {euros(smn_anual_bruto - limite_isento)} de deducao especifica = {euros(limite_isento)} EUR.")
    print("A isencao da proposta incide sobre rendimento coletavel, nao salario bruto.")
    print("Taxas marginais da proposta: 0% / 15% / 28% / 35% / 48%.")
    print("Cenario: categoria A, solteiro, sem dependentes nem outros rendimentos; SS 11%.")
    print("O bruto e estimado a partir do coletavel anterior ao abatimento (deducao especifica: maximo de 8.54 IAS e SS).")
    print(f"Hipoteses nao confirmadas para 2027: IAS {euros(minimo.ias)} EUR; minimo de existencia {euros(minimo.referencia)} EUR brutos.")
    print(f"Despesas gerais deduzidas nas duas alternativas: {euros(minimo.despesas_gerais)} EUR.")
    print(f"Novos graficos: SS trabalhador {100 * minimo.taxa_ss:g}%; TSU empregador {args.taxa_tsu:g}%.")
    print("Art. 70 aplicado apenas a imagem; proposta com escalao 0%. Sem outras deducoes ou solidariedade.")
    print("Imagem calculada pelas taxas normais; as medias arredondadas podem dar pequenas diferencas.")
    rendimentos = args.rendimentos or [
        ZERO, Decimal("8666"), Decimal("13075"), limite_isento,
        Decimal("18530"), Decimal("23985"), Decimal("30538"),
        Decimal("44762"), Decimal("48373"), Decimal("60000"),
        Decimal("89995"), Decimal("120000"),
    ]
    mostrar_comparacao(rendimentos, proposta, minimo)
    max_rendimento = args.max_rendimento or max(
        [Decimal("120000"), *rendimentos, *(rendimento for rendimento, _ in distribuicao or [])]
    )
    try:
        ficheiros = exportar_graficos(
            rendimentos, proposta, args.graphs_dir, max_rendimento, distribuicao, minimo, args.taxa_tsu / 100
        )
    except ImportError:
        parser.error("Matplotlib em falta. Instale com: python3 -m pip install -r data/requirements.txt")
    except OSError as erro:
        parser.error(f"Nao foi possivel exportar os graficos: {erro}")
    print("\nGraficos exportados:")
    for caminho in ficheiros:
        print(f"  {caminho}")
    if distribuicao is None:
        print("\nSem distribuicao de rendimentos, nao e possivel estimar a perda total de receita.")
        print("Use --csv e --limite-perda para testar a afirmacao; explicite o valor de '1MM'.")
        return

    atual, novo = totais(distribuicao, proposta, minimo)
    perda = atual - novo
    quantidade = sum(contagem for _, contagem in distribuicao)
    print(f"\nUniverso do CSV: {quantidade:,} contribuintes (nao necessariamente nacional).")
    print("Se as linhas forem medias de intervalos, estes totais sao apenas aproximacoes.")
    print("Todos os contribuintes do CSV sao simulados com as mesmas hipoteses de categoria A.")
    print(f"Coleta da imagem:  {euros(atual)} EUR")
    print(f"Coleta proposta:   {euros(novo)} EUR")
    print(f"Perda de receita:  {euros(perda)} EUR (negativa = aumento)")
    print(f"Poupanca media:    {euros(perda / quantidade)} EUR/contribuinte")
    if atual:
        print(f"Reducao da coleta: {100 * perda / atual:.2f}%")
    if args.limite_perda is not None:
        resultado = "SIM" if perda < args.limite_perda else "NAO"
        print(f"Perda inferior a {euros(args.limite_perda)} EUR neste universo? {resultado}")


if __name__ == "__main__":
    main()