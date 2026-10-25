# Avançar Liberal

Static Portuguese-language website for Avançar Liberal, with official brand assets,
a Python tool for comparing personal income tax (IRS) scenarios, and supporting
policy documents.

- [Website and local preview](#website)
- [Python setup](#python-setup)
- [IRS comparison](#irs-comparison)
- [Land value tax proposal](#land-value-tax-proposal)

## Project Structure

```text
website/                 Deployable static website: HTML, CSS, JavaScript, assets
assets/                  Visual guide and original Instagram publication archive
logotipo/02.Logotipo/     Original logos, background variants, and media
Avançar Website modelo.pdf
                         Website copy and reference sitemap
data/comparar_irs.py      IRS comparison and graph export script
data/requirements.txt    Python dependencies
data/graphs/             Generated PNG and SVG charts
lvt/                     Land value tax proposal, summary, and comparisons
```

## Website

### Local Preview

Run this command from the repository root:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory website
```

Open <http://127.0.0.1:8000/>. If the port is occupied, choose another one.
Stop the server with `Ctrl+C`.

The website has **no build step, Node.js dependencies, or backend**. Python's
standard library is enough to preview it; the IRS tool's virtual environment
and Matplotlib are not needed. Serve it over HTTP rather than opening the HTML
with `file://`, because the publication archive is loaded with `fetch`.

To publish the site, serve the contents of [website/](website/) from a static
HTTP host, retaining the relative paths. Source PDFs, the original logo folder,
and the Python tooling are not required on the host.

### Pages and Navigation

The structure is based on page 7 of
[Avançar Website modelo.pdf](<Avançar Website modelo.pdf>), narrowed to the
**Comissão Executiva (CE)** candidature. CN, CJ and CF are not part of the
current website.

| Page | File | Purpose |
| --- | --- | --- |
| Início | [index.html](website/index.html) | Candidature introduction, Liberal Humanismo, three priorities, political positions, and three publication highlights |
| Liberal Humanismo | [liberal-humanismo.html](website/liberal-humanismo.html) | Principles and practical examples from the supplied model |
| CE Home | [ce.html](website/ce.html) | Commission candidature landing page |
| CE / Vídeos | [ce-videos.html](website/ce-videos.html) | Video publication space |
| CE / Candidato + Equipa | [ce-equipa.html](website/ce-equipa.html) | Candidate and team presentation space |
| CE / MEG | [ce-meg.html](website/ce-meg.html) | Official candidature document space |
| Contactos | [contactos.html](website/contactos.html) | Direct email and Instagram contact links |
| Doações | [doacoes.html](website/doacoes.html) | Donation information space |
| Publicações | [posts.html](website/posts.html) | Local archive of Instagram publications |

The existing [equipa.html](website/equipa.html),
[propostas.html](website/propostas.html), and
[junta-te.html](website/junta-te.html) addresses remain available for team
navigation, priorities, and participation. They are not primary menu items.

Shared header, footer, active-page indicators, CE subnavigation and mobile-menu
behavior live in [main.js](website/js/main.js). These shared elements and the
publication cards require JavaScript.

### Content Awaiting Publication

CE videos, candidate/team biographies, MEG documents, the Liberal Humanismo
presentation video, and donation details are explicitly marked **Em preparação**.
Replace those notices only when the corresponding official material is available.
No payment details, unconfirmed biographies, or placeholder member names are
published.

Contact and participation use direct links, not submission forms. The email link
opens the visitor's email application; the website does not collect or store
messages and does not claim to have delivered them.

### Visual Identity and Logos

[style.css](website/css/style.css) follows the Avançar palette in
[Cores-e-Letras.pdf](assets/Cores-e-Letras.pdf):

| Color | Hex |
| --- | --- |
| Cyan | `#00C3FF` |
| Navy | `#050487` |
| Pink | `#FF006B` |
| Yellow | `#FFE112` |
| Red | `#FF3C32` |
| Green | `#00F395` |

Bricolage Grotesque, Figtree and Urbanist are self-hosted in
[website/assets/fonts/](website/assets/fonts/), alongside their SIL Open Font
License notices. No external font service is contacted at runtime.

The website uses **unmodified original SVGs**, not recreated artwork or raster
crops from the PDF:

| Website asset | Source in `logotipo/02.Logotipo/` | Use |
| --- | --- | --- |
| [mainlogo.svg](website/assets/mainlogo.svg) | [Avançar_mainlogo.svg](<logotipo/02.Logotipo/Avançar_mainlogo.svg>) | Main symbol and favicon on every page |
| [logo.svg](website/assets/logo.svg) | [Avançar 2 - Logo.svg](<logotipo/02.Logotipo/Avançar 2 - Logo.svg>) | Full logo on the white header |
| [avancar-mark.svg](website/assets/avancar-mark.svg) | [Icon Variação A](<logotipo/02.Logotipo/Avançar 2 - Icon Variação A.svg>) | White/red symbol on the cyan hero |
| [logo-dark.svg](website/assets/logo-dark.svg) | [Logo Variação D](<logotipo/02.Logotipo/Avançar 2 - Logo Variação D.svg>) | White/pink logo on the navy footer |

Choose the supplied variant for the background; preserve the artwork, lettering,
colors and aspect ratio. Copy any replacement into the website assets so the
deployed site remains self-contained.

The hero's **two thin concentric rings** are CSS decorations, not part of the
logo. They are layered above the SVG's opaque background and below the yellow
label to keep the circles continuous without altering the official artwork.

### Local Publication Archive

[posts.js](website/js/posts.js) reads
[manifest.json](website/assets/posts/manifest.json) and renders local images from
[website/assets/posts/](website/assets/posts/). The homepage shows the three
newest archived posts; the publications page shows all 12, newest first.

This is a **partial archive from July to October 2026**, not a live Instagram
feed. Some captions are incomplete. The original downloads and metadata are
retained in [assets/avancarliberal/](assets/avancarliberal/).

To update the archive:

1. Copy the publication images into `website/assets/posts/`.
2. Update the published manifest with the shortcode, caption, publication
   timestamp, and local image filename. Follow the existing record format.
3. Keep `downloaded_media[0].file` consistent with the copied JPG filename;
   the current renderer displays the first image of each publication.
4. Check the homepage and publications page over HTTP. Update the archive
   description and counts if its coverage changes.

Images are lazy-loaded. Loading failures display an explicit message and an
Instagram link. Instagram is contacted only when a visitor follows an external
link; there are no Instagram embeds or automatic feed requests.

## Python Setup

Use Python 3.10 or newer. The script has been run with Python 3.14.
Run these commands from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r data/requirements.txt
```

Matplotlib is the only declared external dependency. Graphs are exported without
opening a graphical window. The virtual environment and Python caches are ignored
by Git; exported charts remain trackable.

## IRS Comparison

```bash
python data/comparar_irs.py --smn 970
```

`--smn` is the **monthly gross minimum wage**, not the annual amount.
By default, it is multiplied by 14 payments: `970 * 14 = 13580` EUR per year.
The value of 970 EUR is an example assumption, not a confirmed statutory value.

The proposed marginal rates are:

| Annual taxable income | Rate |
| --- | --- |
| Up to the taxable equivalent of the annual minimum wage | 0% |
| Above that exemption, up to 23,985 EUR | 15% |
| Above 23,985 EUR, up to 44,762 EUR | 28% |
| Above 44,762 EUR, up to 89,995 EUR | 35% |
| Above 89,995 EUR | 48% |

The exempt taxable threshold is the annual gross minimum wage after the specific
deduction: the larger of `8.54 * IAS` and employee social contributions.
For the default assumptions, this gives approximately 8,992.91 EUR of taxable
income from 13,580 EUR gross. Each rate applies only to its income band.

Compare selected annual taxable incomes or adjust the graph range:

```bash
python data/comparar_irs.py --smn 970 --rendimentos 23985 44762 89995
python data/comparar_irs.py --smn 970 --max-rendimento 60000
python data/comparar_irs.py --smn 970 --graphs-dir data/graphs
python data/comparar_irs.py --help
```

`--max-rendimento` is a taxable-income limit. The gross-income and labor-cost
charts convert that limit to the corresponding gross income and employer cost.

### Fiscal Assumptions

The reference brackets are transcribed from the supplied image, labeled as an
OE2027 proposal. The script uses its normal marginal rates; its rounded average
rates can yield small differences under the statutory calculation method.

The simulation assumes a single employee, without dependents or other income:

- IAS: 537.13 EUR per month, configurable with `--ias`.
- Minimum-existence reference: by default, the largest of 12,880 EUR, the annual
  gross minimum wage, and `21 * IAS`; configurable with `--minimo-existencia`.
- Employee social contributions: 11% of gross income.
- Employer TSU: 23.75% of gross income, configurable with `--taxa-tsu`.
- General family-expense deduction: 250 EUR in both alternatives, configurable
  from 0 to 250 with `--despesas-gerais`.

**The IAS and minimum-existence parameters for 2027 are configurable hypotheses,
not confirmed legislation.** The current Article 70 minimum-existence abatement
is applied to the reference table. The proposal instead uses its own 0% band.
Other deductions, joint taxation, the solidarity surcharge, special regimes,
and other employer costs are not included. This is a scenario comparison, not
a complete tax-return calculator or a certified national revenue estimate.

```bash
python data/comparar_irs.py --smn 970 --ias 537.13 --minimo-existencia 13580
python data/comparar_irs.py --smn 970 --despesas-gerais 0 --taxa-tsu 23.75
```

Official references: [CIRS Article 25](https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/codigos_tributarios/cirs_rep/Pages/irs25.aspx)
and [CIRS Article 70](https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/codigos_tributarios/cirs_rep/Pages/irs70.aspx).

### Revenue Comparison With CSV

Provide a UTF-8 CSV with these columns:

```csv
rendimento_coletavel,contribuintes
18530,100
30538,50
```

Each row represents a positive integer count of taxpayers at the same annual
taxable income, **before the minimum-existence abatement**, not gross wages.
All taxpayers are modeled with the same fiscal assumptions. Using income-band
averages makes the totals approximate. Semicolon-separated CSVs and decimal
commas are also accepted.

For a CSV placed at `data/distribuicao.csv`:

```bash
python data/comparar_irs.py --smn 970 --csv data/distribuicao.csv --limite-perda 1000000000
```

The script reports both totals and the revenue difference for the CSV population.
It tests whether the loss is strictly below `--limite-perda`, expressed in EUR.
`1000000` means one million; `1000000000` means one billion. No national revenue
claim can be checked without an appropriate taxpayer distribution.

### Graph Exports

Charts are written to [data/graphs](data/graphs) as PNG and SVG:

| File Stem | X Axis | Y Axis |
| --- | --- | --- |
| `comparacao_irs` | Annual taxable income before abatement | Effective IRS rate (%) |
| `poupanca_anual` | Annual taxable income before abatement | Reference IRS minus proposed IRS (EUR) |
| `taxas_irs` | Annual taxable income before abatement | Marginal table rates and effective IRS rates (%) |
| `irs_ss_trabalhador` | Annual gross income | `(IRS + employee SS) / gross` (%) |
| `imposto_sobre_trabalho` | Annual employer cost: gross + TSU | `(IRS + employee SS + employer TSU) / employer cost` (%) |
| `receita_total_csv` | Reference table and proposal | Total IRS for the CSV population (EUR; requires `--csv`) |

## Land Value Tax Proposal

[lvt/](lvt/) contains the Portuguese policy documents for a proposed land value
tax reform:

- [Full proposal](lvt/proposta.md)
- [Summary](lvt/proposta-resumo.md) and [PDF version](lvt/proposta-resumo.pdf)
- [Comparison](lvt/comparacao.md)

These documents describe proposals and illustrative scenarios, not enacted tax
rules or guaranteed individual savings.