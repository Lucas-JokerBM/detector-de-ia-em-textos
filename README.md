# Detector de I.A. em documentos .docx

Avalia a probabilidade de um `.docx` ter sido escrito por I.A. e aponta **o que alterar**, frase por frase.
Um único núcleo, três formas de uso: **web**, **desktop** e **linha de comando**.

> Análise heurística (estilo + estatística). Indica probabilidade, **não prova autoria**.
> Textos formais, técnicos ou em segunda língua podem gerar falsos positivos. Pesos ainda não calibrados com dados reais.

## Arquitetura

```
src/detector_ia/
  core/            domínio puro (sem framework): leitura segura, analisadores, motor, relatório
    analyzers/     Strategy + Registry: 1 classe = 1 indicador (statistical.py, stylistic.py)
    lexicon.py     dados (clichês/conectivos) separados da lógica
  service.py       casos de uso (usado por CLI, API e desktop local)
  config.py        configuração por variáveis de ambiente (12-factor)
  api/             FastAPI: /api/v1/health, /api/v1/analyze + segurança + interface estática
  web/static/      UI única (HTML/CSS/JS) usada no navegador E no desktop
  desktop/         janela nativa (pywebview) -> modo local ou remoto
  cli.py           `detector-ia arquivo.docx [--json]`
```

Escalabilidade: API **stateless** (nenhum arquivo é gravado), análise CPU-bound fora do event loop,
vários *workers* (`DETECTOR_WORKERS`) e réplicas atrás de balanceador (`docker compose up --scale`).
Novos indicadores entram sem alterar o motor (veja abaixo).

## Executar

```bash
pip install -e ".[api,desktop,dev]"

detector-ia contrato.docx                 # CLI
detector-ia-server                        # web em http://127.0.0.1:8000
detector-ia-desktop --mode local          # janela desktop com servidor embutido
detector-ia-desktop --mode remote --url https://seu-servidor   # janela desktop -> servidor hospedado

python -m pytest                          # (ou: cd tests && PYTHONPATH=../src:. python -m unittest)
docker compose up --build                 # produção (copie .env.example para .env)
```

## Proteção contra cópia — o que realmente funciona

Nenhum código distribuído ao usuário é 100% à prova de cópia; a defesa é em camadas:

1. **Arquitetura (a mais forte):** a análise roda **no servidor**. Navegador e app desktop em modo `remote`
   nunca recebem o motor nem o léxico. Use este modo para a versão comercial.
2. **Compilação:** `scripts/build_desktop.py` gera binário nativo via Nuitka (dificulta muito a engenharia reversa,
   mas não a impede). Use `--mode local` somente se precisar de funcionamento offline.
3. **Acesso controlado:** chave de API (`X-API-Key`, comparação em tempo constante), rate limit, tamanho máximo
   de upload, CSP e cabeçalhos de segurança; sem armazenamento de documentos nem de conteúdo em logs.
4. **Jurídico:** `LICENSE` proprietária (preencha titular/ano), termos de uso e registro de direitos autorais.
5. **Operacional:** repositório e imagem Docker **privados**; segredos só em variáveis de ambiente.

## Segurança do upload

Limite de tamanho, assinatura ZIP, limite de descompactação e razão de compressão (zip-bomb),
`defusedxml` (XXE / billion laughs), extensão validada, parsing em *thread pool*.
Atrás de proxy reverso, configure também `client_max_body_size` (nginx) ou equivalente e TLS.

## Como adicionar um indicador

```python
from detector_ia.core.analyzers.base import Analyzer, AnalyzerOutput, FlagHit, register

@register
class MeuIndicador(Analyzer):
    id, name, default_weight = "meu_indicador", "Meu indicador", 0.05
    def analyze(self, doc):
        ...  # doc.sentences, doc.tokens, doc.text, doc.per_1000(n)
        return AnalyzerOutput(self.metric("valor", 0.7, "explicação", "o que fazer"), [FlagHit(0, "motivo", "sugestão")])
```
Pesos podem ser ajustados sem código: `DETECTOR_WEIGHTS='{"phrases":0.3}'`.

## Próximos passos sugeridos

Calibrar pesos com um conjunto rotulado (textos humanos × I.A.), cache de resultados por hash, fila de jobs
(Celery/RQ) para arquivos grandes, rate limit em Redis, métricas (Prometheus), CI (ruff + mypy + testes).
