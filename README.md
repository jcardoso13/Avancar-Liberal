# Avancar Liberal

Static website for the Avancar Liberal movement and a Python tool for comparing
Portuguese personal income tax (IRS) scenarios, including social contributions.

## Project Structure

```text
website/                 Static HTML pages, CSS, JavaScript, and assets
data/comparar_irs.py      IRS comparison and graph export script
data/requirements.txt    Python dependencies
data/graphs/             Generated PNG and SVG charts
```

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

## Website Preview

The [website/index.html](website/index.html) entry point is a static site with no
build step or Node.js dependencies. To preview it locally:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory website
```

Open <http://127.0.0.1:8000/>. Use another port if 8000 is occupied.
### Website Structure and Content

The primary navigation is based on page 7 of `Avançar Website modelo.pdf`,
restricted to the Comissão Executiva candidature:

- Homepage: `website/index.html`
- Liberal Humanismo: `website/liberal-humanismo.html`
- Contactos: `website/contactos.html`
- Doações: `website/doacoes.html`
- CE: `website/ce.html`, with separate `ce-videos.html`, `ce-equipa.html`
  and `ce-meg.html` pages.

The homepage and Liberal Humanismo copy are based on the supplied website model.
Videos, candidates/teams, MEG documents and donation details are explicitly marked
as in preparation until official material is supplied. No payment details or
unconfirmed team biographies are fabricated. The existing team, proposals and
participation URLs remain available, but are no longer primary navigation items.
Contact and participation now use direct contact links, not browser-only form
storage that could misleadingly report a message as delivered.

`website/css/style.css` uses the Avançar palette from pages 1–4 of
`assets/Cores-e-Letras.pdf`: cyan `#00C3FF`, navy `#050487`, pink `#FF006B`,
yellow `#FFE112`, red `#FF3C32` and green `#00F395`. Bricolage Grotesque,
Figtree and Urbanist are self-hosted in `website/assets/fonts/`, with their
SIL Open Font License notices. No font service is contacted at runtime.

Website logos are unmodified SVG copies from `logotipo/02.Logotipo/`:

| Website asset | Original artwork | Use |
| --- | --- | --- |
| `website/assets/mainlogo.svg` | `Avançar_mainlogo.svg` | Main symbol / favicon on every page |
| `website/assets/logo.svg` | `Avançar 2 - Logo.svg` | Original full wordmark on the white header |
| `website/assets/avancar-mark.svg` | `Avançar 2 - Icon Variação A.svg` | White/red symbol on the cyan homepage hero |
| `website/assets/logo-dark.svg` | `Avançar 2 - Logo Variação D.svg` | White/pink wordmark on the navy footer |

Keep the original artwork, lettering, colors and aspect ratios unchanged.
These vector assets replace the recreated logos; no PDF raster crops are used.
The two thin concentric rings around the homepage hero are CSS decorations,
layered above the SVG background and below the yellow label. They do not modify
the official artwork.

`website/posts.html` and the homepage display local images from
`website/assets/posts/`, copied from `assets/avancarliberal/`. The accompanying
`manifest.json` is the source for publication dates, captions and filenames.
This is a partial archive of 12 posts, not a live Instagram feed; captions may be
incomplete. To refresh it, copy the new images and update the published manifest
together. The original download manifest is retained in the source assets.
Instagram is contacted only when a visitor follows an external link.

Serve the site over HTTP using the command above: the local publication manifest
is loaded with `fetch`, which browsers may block on `file://` URLs.