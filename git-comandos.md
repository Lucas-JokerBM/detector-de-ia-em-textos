# Guia Completo de Comandos Git

Referência prática com a **funcionalidade** de cada comando e um **exemplo de uso no dia a dia**.

## Sumário

1. [Configuração](#1-configuração)
2. [Criar e obter repositórios](#2-criar-e-obter-repositórios)
3. [Ciclo básico: status, add, commit](#3-ciclo-básico-status-add-commit)
4. [Inspeção e histórico](#4-inspeção-e-histórico)
5. [Branches](#5-branches)
6. [Merge e Rebase](#6-merge-e-rebase)
7. [Repositórios remotos](#7-repositórios-remotos)
8. [Desfazer alterações](#8-desfazer-alterações)
9. [Stash](#9-stash)
10. [Tags](#10-tags)
11. [Ferramentas avançadas](#11-ferramentas-avançadas)
12. [Submodules e Worktrees](#12-submodules-e-worktrees)
13. [Manutenção e diagnóstico](#13-manutenção-e-diagnóstico)
14. [Boas práticas](#14-boas-práticas)
15. [Fluxo de trabalho diário](#15-fluxo-de-trabalho-diário)

---

## 1. Configuração

### `git config`
**Funcionalidade:** Define configurações do Git em três níveis: `--system` (máquina), `--global` (usuário) e `--local` (repositório).

```bash
# Identidade (obrigatório antes do primeiro commit)
git config --global user.name "Seu Nome"
git config --global user.email "voce@empresa.com"

# Editor padrão e branch inicial
git config --global core.editor "code --wait"
git config --global init.defaultBranch main

# Evita merge commits desnecessários ao fazer pull
git config --global pull.rebase true

# Aliases para ganhar produtividade
git config --global alias.st "status -sb"
git config --global alias.lg "log --oneline --graph --decorate --all"

# Listar configurações e ver a origem de cada uma
git config --list --show-origin
```

**Dia a dia:** Configure uma vez por máquina. Use `--local` quando trabalhar com e-mail diferente em um projeto específico (ex.: projeto pessoal vs. empresa).

### `git help`
**Funcionalidade:** Exibe a documentação de qualquer comando.

```bash
git help rebase
git commit --help
```

---

## 2. Criar e obter repositórios

### `git init`
**Funcionalidade:** Cria um novo repositório Git na pasta atual.

```bash
mkdir meu-projeto && cd meu-projeto
git init
```

**Dia a dia:** Ao iniciar um projeto do zero na sua máquina.

### `git clone`
**Funcionalidade:** Copia um repositório remoto (com todo o histórico) para a sua máquina.

```bash
git clone https://github.com/empresa/projeto.git
git clone git@github.com:empresa/projeto.git meu-diretorio
git clone --depth 1 https://github.com/empresa/projeto.git   # só o último commit (mais rápido)
git clone --branch develop https://github.com/empresa/projeto.git
```

**Dia a dia:** Primeiro passo ao entrar em um projeto existente. Use `--depth 1` em pipelines de CI para economizar tempo.

---

## 3. Ciclo básico: status, add, commit

### `git status`
**Funcionalidade:** Mostra o estado do working directory e da staging area (arquivos modificados, novos, preparados).

```bash
git status
git status -sb    # formato curto, com info da branch
```

**Dia a dia:** O comando mais usado. Rode antes de qualquer `add`/`commit` para saber o que está prestes a registrar.

### `git add`
**Funcionalidade:** Move alterações para a staging area (o que entrará no próximo commit).

```bash
git add arquivo.js          # um arquivo
git add src/                # uma pasta
git add .                   # tudo na pasta atual
git add -p                  # escolhe trechos (hunks) interativamente
git add -u                  # só arquivos já rastreados (inclui deleções)
```

**Dia a dia:** Prefira `git add -p` para revisar o que está commitando e manter commits pequenos e focados.

### `git commit`
**Funcionalidade:** Registra um snapshot da staging area no histórico.

```bash
git commit -m "feat: adiciona login com Google"
git commit -am "fix: corrige validação de CPF"     # add + commit (só rastreados)
git commit --amend                                  # altera o último commit
git commit --amend --no-edit                        # inclui arquivos esquecidos, mantém a mensagem
```

**Dia a dia:** Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`). Só use `--amend` em commits que **ainda não foram enviados** ao remoto.

### `git rm`
**Funcionalidade:** Remove arquivos do working directory e do índice.

```bash
git rm arquivo.txt
git rm --cached .env          # para de rastrear, mas mantém o arquivo no disco
git rm -r pasta/
```

**Dia a dia:** Use `--cached` quando commitou algo por engano (ex.: `.env`) e quer parar de versionar. Depois adicione ao `.gitignore`.

### `git mv`
**Funcionalidade:** Move ou renomeia arquivos, registrando a mudança.

```bash
git mv antigo.js novo.js
git mv utils.js src/utils.js
```

### `.gitignore`
**Funcionalidade:** Arquivo que lista padrões que o Git deve ignorar.

```gitignore
node_modules/
.env
*.log
dist/
.DS_Store
```

---

## 4. Inspeção e histórico

### `git log`
**Funcionalidade:** Exibe o histórico de commits.

```bash
git log
git log --oneline
git log --oneline --graph --decorate --all     # visão em árvore
git log -5                                     # últimos 5
git log --author="Maria"
git log --since="2 weeks ago"
git log --grep="login"                         # busca na mensagem
git log -p arquivo.js                          # histórico de um arquivo com diffs
git log -S"minhaFuncao"                        # commits que adicionaram/removeram o termo
git log main..feature                          # commits em feature que não estão em main
```

**Dia a dia:** Para entender quando e por que algo mudou.

### `git diff`
**Funcionalidade:** Mostra diferenças entre estados do código.

```bash
git diff                       # working dir vs. staging
git diff --staged              # staging vs. último commit
git diff main..feature         # entre branches
git diff HEAD~3 HEAD           # entre commits
git diff --stat                # resumo
```

**Dia a dia:** Rode `git diff --staged` antes de commitar para uma última revisão.

### `git show`
**Funcionalidade:** Mostra detalhes de um commit, tag ou objeto.

```bash
git show                  # último commit
git show a1b2c3d
git show HEAD~2:src/app.js    # arquivo como estava 2 commits atrás
```

### `git blame`
**Funcionalidade:** Mostra quem alterou cada linha de um arquivo e em qual commit.

```bash
git blame src/app.js
git blame -L 10,30 src/app.js      # só linhas 10 a 30
```

**Dia a dia:** Para descobrir o contexto de uma linha estranha (e perguntar a quem a escreveu, sem culpar).

### `git shortlog`
**Funcionalidade:** Resume commits por autor.

```bash
git shortlog -sn           # ranking de contribuições
```

### `git reflog`
**Funcionalidade:** Registro local de todos os movimentos do `HEAD`. Salva-vidas para recuperar commits "perdidos".

```bash
git reflog
git reset --hard HEAD@{3}      # volta ao estado de 3 movimentos atrás
```

**Dia a dia:** Fez um `reset --hard` e se arrependeu? O `reflog` provavelmente ainda tem o commit.

### `git grep`
**Funcionalidade:** Busca texto nos arquivos rastreados.

```bash
git grep "TODO"
git grep -n "minhaFuncao" -- "*.js"
```

### `git bisect`
**Funcionalidade:** Busca binária no histórico para achar o commit que introduziu um bug.

```bash
git bisect start
git bisect bad                  # versão atual está com bug
git bisect good v1.2.0          # versão que funcionava
# Git faz checkout no meio; teste e marque:
git bisect good    # ou: git bisect bad
# ...repita até achar o commit culpado
git bisect reset
```

**Dia a dia:** Quando "funcionava semana passada" e há dezenas de commits no meio.

---

## 5. Branches

### `git branch`
**Funcionalidade:** Lista, cria, renomeia e apaga branches.

```bash
git branch                       # locais
git branch -a                    # locais + remotas
git branch -vv                   # com upstream e último commit
git branch feature/login         # cria (sem trocar)
git branch -m nome-antigo novo   # renomeia
git branch -d feature/login      # apaga (se já mergeada)
git branch -D feature/login      # apaga à força
git branch --merged main         # branches já integradas
```

### `git switch`
**Funcionalidade:** Troca de branch (comando moderno, mais claro que `checkout`).

```bash
git switch main
git switch -c feature/carrinho       # cria e troca
git switch -                         # volta para a branch anterior
```

### `git checkout`
**Funcionalidade:** Comando legado multiuso: troca de branch ou restaura arquivos.

```bash
git checkout feature/login
git checkout -b feature/novo
git checkout a1b2c3d              # "detached HEAD" em um commit
```

**Dia a dia:** Prefira `git switch` (branches) e `git restore` (arquivos).

### Convenção de nomes (boa prática)
```
feature/nome-da-funcionalidade
fix/descricao-do-bug
hotfix/problema-em-producao
chore/atualiza-dependencias
```

---

## 6. Merge e Rebase

### `git merge`
**Funcionalidade:** Integra o histórico de outra branch na atual.

```bash
git switch main
git merge feature/login            # merge normal
git merge --no-ff feature/login    # sempre cria merge commit
git merge --squash feature/login   # junta tudo em um único commit (você commita depois)
git merge --abort                  # cancela um merge com conflito
```

**Resolvendo conflitos:**
```bash
git merge feature/login
# CONFLICT em src/app.js → edite o arquivo, remova os marcadores <<<<<<< ======= >>>>>>>
git add src/app.js
git commit
```

### `git rebase`
**Funcionalidade:** Reaplica seus commits sobre outra base, gerando histórico linear.

```bash
git switch feature/login
git rebase main                    # atualiza sua branch com as novidades da main
git rebase --continue              # após resolver conflito
git rebase --abort
git rebase -i HEAD~4               # interativo: reordenar, juntar (squash), editar, apagar commits
```

**Dia a dia:** Limpe seus commits locais com `rebase -i` antes de abrir o Pull Request.

> ⚠️ **Regra de ouro:** nunca faça rebase de commits que já foram publicados e são usados por outras pessoas.

### `git cherry-pick`
**Funcionalidade:** Copia um commit específico para a branch atual.

```bash
git cherry-pick a1b2c3d
git cherry-pick a1b2c3d..f4e5d6c      # intervalo
```

**Dia a dia:** Levar um hotfix da `main` para uma branch de release.

### `git rerere`
**Funcionalidade:** "Reuse recorded resolution": memoriza como você resolveu um conflito e reaplica automaticamente.

```bash
git config --global rerere.enabled true
```

---

## 7. Repositórios remotos

### `git remote`
**Funcionalidade:** Gerencia os endereços de repositórios remotos.

```bash
git remote -v
git remote add origin git@github.com:empresa/projeto.git
git remote add upstream git@github.com:original/projeto.git    # fork
git remote set-url origin git@github.com:empresa/novo.git
git remote remove upstream
git remote prune origin       # remove referências a branches apagadas no remoto
```

### `git fetch`
**Funcionalidade:** Baixa novidades do remoto **sem** alterar seus arquivos.

```bash
git fetch
git fetch --all --prune
```

**Dia a dia:** Use para ver o que mudou antes de integrar.

### `git pull`
**Funcionalidade:** `fetch` + integração (merge ou rebase) na branch atual.

```bash
git pull
git pull --rebase origin main
git pull --ff-only          # falha se não for fast-forward (mais seguro)
```

### `git push`
**Funcionalidade:** Envia seus commits ao remoto.

```bash
git push
git push -u origin feature/login        # primeiro push: define upstream
git push --force-with-lease             # force push SEGURO (após rebase na sua branch)
git push origin --delete feature/login  # apaga branch remota
git push --tags
```

> ⚠️ **Nunca** use `git push --force` em `main`/`develop`. Se precisar forçar na sua branch, prefira `--force-with-lease`.

---

## 8. Desfazer alterações

### `git restore`
**Funcionalidade:** Restaura arquivos (comando moderno).

```bash
git restore arquivo.js                    # descarta mudanças no working dir
git restore --staged arquivo.js           # tira da staging (mantém a edição)
git restore --source=HEAD~2 arquivo.js    # restaura versão de 2 commits atrás
```

### `git reset`
**Funcionalidade:** Move o `HEAD` (e opcionalmente staging/working dir) para outro commit.

```bash
git reset --soft HEAD~1     # desfaz o commit, mantém tudo na staging
git reset --mixed HEAD~1    # (padrão) desfaz o commit, mantém as edições sem staging
git reset --hard HEAD~1     # desfaz o commit E DESCARTA as edições ⚠️
git reset --hard origin/main   # iguala sua branch ao remoto (descarta o local)
```

**Dia a dia:** `--soft` é ótimo para "commitei errado a mensagem/escopo, quero refazer".

### `git revert`
**Funcionalidade:** Cria um **novo commit** que desfaz outro, sem reescrever o histórico.

```bash
git revert a1b2c3d
git revert HEAD
git revert -m 1 <merge-commit>      # reverte um merge commit
```

**Dia a dia:** Use `revert` em branches compartilhadas; use `reset` apenas em commits locais.

### `git clean`
**Funcionalidade:** Remove arquivos não rastreados.

```bash
git clean -n         # simulação (dry-run), SEMPRE rode antes
git clean -fd        # remove arquivos e pastas não rastreados
git clean -fdx       # inclui os ignorados (ex.: node_modules) ⚠️
```

### Resumo: qual usar?

| Situação | Comando |
|---|---|
| Descartar edição não commitada | `git restore arquivo` |
| Tirar arquivo da staging | `git restore --staged arquivo` |
| Refazer último commit (local) | `git reset --soft HEAD~1` |
| Desfazer commit já publicado | `git revert <hash>` |
| Corrigir mensagem do último commit | `git commit --amend` |
| Recuperar commit "perdido" | `git reflog` + `git reset` |

---

## 9. Stash

### `git stash`
**Funcionalidade:** Guarda temporariamente alterações não commitadas, deixando o working dir limpo.

```bash
git stash                          # guarda
git stash push -m "wip: formulário"   # com descrição
git stash -u                       # inclui arquivos não rastreados
git stash list
git stash show -p stash@{0}        # vê o conteúdo
git stash pop                      # aplica e remove da lista
git stash apply stash@{1}          # aplica e mantém na lista
git stash drop stash@{0}
git stash clear
git stash branch feature/nova      # cria branch a partir do stash
```

**Dia a dia:** Está no meio de uma tarefa e surge um bug urgente? `git stash` → troca de branch → corrige → volta → `git stash pop`.

---

## 10. Tags

### `git tag`
**Funcionalidade:** Marca pontos importantes do histórico (normalmente versões).

```bash
git tag                              # lista
git tag v1.0.0                       # leve
git tag -a v1.0.0 -m "Versão 1.0.0"  # anotada (recomendada)
git tag -a v0.9.0 a1b2c3d            # em commit antigo
git push origin v1.0.0               # envia uma tag
git push --tags                      # envia todas
git tag -d v1.0.0                    # apaga local
git push origin --delete v1.0.0      # apaga remota
```

**Dia a dia:** Use [Versionamento Semântico](https://semver.org/lang/pt-BR/) (`MAJOR.MINOR.PATCH`) para releases.

---

## 11. Ferramentas avançadas

### `git commit --fixup` + `git rebase --autosquash`
**Funcionalidade:** Cria commits de correção que são automaticamente fundidos ao commit original.

```bash
git commit --fixup a1b2c3d
git rebase -i --autosquash main
```

### `git patch` (`format-patch` / `apply` / `am`)
**Funcionalidade:** Exporta e importa mudanças como arquivos de patch.

```bash
git format-patch -3                  # gera 3 patches
git apply correcao.patch             # aplica sem commitar
git am 0001-correcao.patch           # aplica e cria o commit
```

### `git archive`
**Funcionalidade:** Exporta o código (sem a pasta `.git`) em `.zip` ou `.tar`.

```bash
git archive --format=zip --output=release.zip v1.0.0
```

### `git notes`
**Funcionalidade:** Anexa anotações a commits sem alterá-los.

```bash
git notes add -m "Validado pelo QA" a1b2c3d
```

### `git hooks` (pasta `.git/hooks`)
**Funcionalidade:** Scripts executados automaticamente em eventos (`pre-commit`, `commit-msg`, `pre-push`).

```bash
# Exemplo: .git/hooks/pre-commit
#!/bin/sh
npm run lint || exit 1
```

**Dia a dia:** Use com ferramentas como **Husky** ou **pre-commit** para padronizar lint, testes e mensagens de commit na equipe.

### `git sparse-checkout`
**Funcionalidade:** Baixa apenas algumas pastas de um repositório grande (monorepo).

```bash
git sparse-checkout set apps/web packages/ui
```

### `git restore -p` / `git checkout -p`
**Funcionalidade:** Descarta trechos específicos de mudanças interativamente.

---

## 12. Submodules e Worktrees

### `git submodule`
**Funcionalidade:** Inclui outro repositório dentro do seu, em uma versão específica.

```bash
git submodule add https://github.com/lib/exemplo.git libs/exemplo
git submodule update --init --recursive
git clone --recurse-submodules https://github.com/empresa/projeto.git
git submodule update --remote
```

### `git worktree`
**Funcionalidade:** Permite ter várias branches abertas em pastas diferentes ao mesmo tempo, sem clonar de novo.

```bash
git worktree add ../projeto-hotfix hotfix/pagamento
git worktree list
git worktree remove ../projeto-hotfix
```

**Dia a dia:** Revisar um PR ou corrigir um hotfix sem mexer na branch em que você está trabalhando (alternativa ao `stash`).

---

## 13. Manutenção e diagnóstico

### `git gc`
**Funcionalidade:** Limpa e otimiza o repositório (compacta objetos).

```bash
git gc --aggressive --prune=now
```

### `git fsck`
**Funcionalidade:** Verifica a integridade do banco de objetos.

```bash
git fsck --full
```

### `git count-objects`
**Funcionalidade:** Mostra o tamanho do repositório.

```bash
git count-objects -vH
```

### `git ls-files`
**Funcionalidade:** Lista arquivos rastreados.

```bash
git ls-files
git ls-files --others --ignored --exclude-standard    # arquivos ignorados
```

### `git rev-parse`
**Funcionalidade:** Resolve referências e retorna informações do repositório (útil em scripts).

```bash
git rev-parse HEAD                    # hash completo do commit atual
git rev-parse --abbrev-ref HEAD       # nome da branch atual
git rev-parse --show-toplevel         # raiz do repositório
```

### `git describe`
**Funcionalidade:** Gera um nome legível para o commit com base na tag mais próxima.

```bash
git describe --tags      # ex.: v1.2.0-5-ga1b2c3d
```

### `git version`
```bash
git --version
```

---

## 14. Boas práticas

### Commits
- **Pequenos e atômicos:** cada commit faz *uma* coisa.
- **Mensagem no imperativo e clara:** `fix: corrige cálculo de frete` e não `arrumei umas coisas`.
- Siga **Conventional Commits**:
  ```
  feat: nova funcionalidade
  fix: correção de bug
  docs: documentação
  style: formatação (sem mudança de lógica)
  refactor: refatoração
  test: testes
  chore: tarefas de build/dependências
  ```
- Corpo do commit explica o **porquê**, não o *como*.

### Branches
- Nunca commite direto na `main`; use branches curtas + Pull Request.
- Apague branches já mergeadas.
- Mantenha a branch atualizada com `git pull --rebase` ou `git rebase main`.

### Segurança
- **Nunca** commite senhas, tokens ou `.env`. Use `.gitignore` e secrets managers.
- Se vazar um segredo: **revogue-o imediatamente** (remover do histórico não basta).
- Ative assinatura de commits (GPG/SSH) em projetos críticos:
  ```bash
  git config --global commit.gpgsign true
  ```

### Histórico
- Não reescreva histórico público (`rebase`/`reset`/`push --force`).
- Em branches compartilhadas, prefira `revert`.
- Antes de abrir o PR: `git fetch && git rebase origin/main` e `git rebase -i` para organizar commits.

### Hábitos
- Rode `git status` e `git diff --staged` antes de cada commit.
- Faça `git pull` antes de começar a trabalhar.
- Faça push com frequência (backup + visibilidade).

---

## 15. Fluxo de trabalho diário

### Começando o dia
```bash
git switch main
git pull --ff-only
git switch -c feature/relatorio-vendas
```

### Durante o desenvolvimento
```bash
# ...edita arquivos...
git status -sb
git add -p
git diff --staged
git commit -m "feat(relatorios): adiciona filtro por período"
```

### Atualizando sua branch com a main
```bash
git fetch origin
git rebase origin/main
# resolve conflitos se houver, depois:
git add .
git rebase --continue
```

### Enviando e abrindo o Pull Request
```bash
git push -u origin feature/relatorio-vendas
# (após rebase) git push --force-with-lease
```

### Interrupção urgente (bug em produção)
```bash
git stash push -u -m "wip relatório"
git switch -c hotfix/erro-pagamento origin/main
# ...corrige...
git commit -am "fix(pagamento): trata timeout do gateway"
git push -u origin hotfix/erro-pagamento
git switch feature/relatorio-vendas
git stash pop
```

### Depois do merge do PR
```bash
git switch main
git pull --ff-only
git branch -d feature/relatorio-vendas
git fetch --prune
```

### Cenário de socorro: "me ajuda, deu ruim!"
```bash
git reflog                       # encontre o estado anterior
git reset --hard HEAD@{2}        # volte a ele
```

---

## Cola rápida (Cheat Sheet)

| Objetivo | Comando |
|---|---|
| Ver estado | `git status -sb` |
| Preparar tudo | `git add .` |
| Commitar | `git commit -m "tipo: mensagem"` |
| Histórico bonito | `git log --oneline --graph --decorate --all` |
| Nova branch | `git switch -c nome` |
| Atualizar do remoto | `git pull --rebase` |
| Enviar | `git push -u origin nome` |
| Guardar WIP | `git stash push -u -m "msg"` |
| Desfazer último commit (local) | `git reset --soft HEAD~1` |
| Desfazer commit publicado | `git revert <hash>` |
| Corrigir último commit | `git commit --amend` |
| Achar bug no histórico | `git bisect` |
| Recuperar o "perdido" | `git reflog` |

---

*Dica final:* configure aliases (`git config --global alias.xx ...`) para os comandos que você mais usa. Com o tempo, o Git deixa de ser uma barreira e vira uma rede de segurança.
