#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o site do guideline em site/: home, régua do app e régua do sacado."""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"
regua = json.loads((ROOT / "regua.json").read_text(encoding="utf-8"))

SAMPLE = {
 "first_name":"Rafael","rep_name":"Helena Prado","inviter_name":"Rafael Doria",
 "company_name":"ACME Distribuidora LTDA","code":"418302",
 "reset_url":"#","invite_url":"#","sign_url":"#","boleto_url":"#","app_url":"#",
 "preferences_url":"#","request_ip":"189.4.221.87","request_device":"iPhone 15 · Safari · Curitiba, BR",
 "changed_at":"08 set 2026, 11h04","submitted_at":"05 set 2026, 16h22",
 "doc_name":"Contrato social — última alteração","reject_reason":"A imagem está desfocada nas páginas 3 e 4, o que impede a leitura do quadro societário.",
 "credit_limit":"R$ 240.000,00","order_id":"#ANT-2026-1234",
 "gross_amount":"R$ 18.300,00","net_amount":"R$ 17.797,00","rate":"2,8% a.m.",
 "expires_at":"10 set 2026, 18h00","sacado_name":"Grupo Ferronorte S.A.",
 "sacado_contact":"financeiro@ferronorte.com.br","expected_payment":"09 set 2026",
 "paid_at":"08 set 2026, 14h37","bank_account":"ANTI · Ag 0001 · CC 88.421-6",
 "cancel_reason":"O sacado não confirmou a operação dentro do prazo de 48 horas.",
 "amount":"R$ 4.250,00","recipient_name":"Marina Coelho ME","recipient_doc":"41.882.907/0001-33",
 "tx_id":"E18236120260908TX9F4","due_date":"22 set 2026","payer_name":"Grupo Ferronorte S.A.",
 "fail_reason":"Saldo insuficiente na conta ANTI no momento da liquidação.",
 "company_legal_name":"ANTI Serviços Financeiros S.A. · CNPJ 55.402.118/0001-90",
 "company_address":"Rua Comendador Araújo, 143 · Curitiba, PR",
}

import base64
# A pagina publicada bloqueia imagem de host externo, entao o preview embute a
# marca como data URI. Os arquivos de dist/ seguem com a URL publica de verdade.
LOGO_SRC = "https://brandbook.sejaanti.com.br/assets/download/anti-icone-branco.png"
LOGO_DATA = "data:image/png;base64," + base64.b64encode(
    (ROOT / "assets" / "anti-icone-branco-2x.png").read_bytes()).decode()

def fill(t):
    t = t.replace(LOGO_SRC, LOGO_DATA)
    return re.sub(r"\{\{\{?\s*([a-z_]+)\s*\}?\}\}", lambda m: SAMPLE.get(m.group(1), m.group(0)), t)

GROUPS = [
 ("Autenticação", "Entrar, provar quem é, recuperar acesso.",
  "Disparo imediato, sem exceção. É o único grupo em que o email precisa chegar antes da notificação in-app — se o usuário está travado fora do app, o push não resolve."),
 ("KYC", "Abrir a conta e mantê-la habilitada.",
  "Aqui o email é o canal principal: o usuário fecha o app depois de enviar os documentos e só volta quando é chamado. Todo email deste grupo tem par exato na Central de Notificações."),
 ("Antecipação", "O ciclo da operação, da proposta à liquidação.",
  "Espelha o status do pedido nas telas OT2 → OT6. Um pedido nunca muda de estado sem um email correspondente, para que o histórico da caixa de entrada seja legível como rastro da operação."),
 ("Conta", "Movimento de dinheiro na conta digital.",
  "Comprovante e falha. São os emails que o cliente guarda, encaminha para o contador e usa como prova — por isso carregam o bloco de dados completo, com ID de transação."),
]

# nome curto da comunicacao (o que a gente usa para conversar sobre ela)
NAME = {
 "01-codigo-verificacao":"Código de acesso",
 "02-recuperar-senha":"Redefinição de senha",
 "03-senha-alterada":"Senha alterada",
 "04-boas-vindas":"Boas-vindas",
 "05-documentos-em-analise":"Documentos em análise",
 "06-documento-rejeitado":"Documento rejeitado",
 "07-conta-aprovada":"Conta aprovada",
 "08-convite-representante":"Convite ao representante",
 "09-proposta-disponivel":"Proposta disponível",
 "10-contrato-para-assinatura":"Contrato para assinatura",
 "11-pedido-em-analise":"Pedido em análise",
 "12-aguardando-sacado":"Aguardando sacado",
 "13-sacado-confirmou":"Sacado confirmou",
 "14-operacao-liquidada":"Operação liquidada",
 "15-pedido-cancelado":"Pedido cancelado",
 "16-transferencia-enviada":"Transferência enviada",
 "17-boleto-emitido":"Boleto emitido",
 "18-pagamento-falhou":"Pagamento recusado",
}

# persiste como card na Central de Notificacoes do app (ADV5)?
# nao persiste o que e efemero ou de seguranca, e o que vai para destinatario sem conta.
PERSIST = {
 "01-codigo-verificacao":(False,"Efêmero. Expira em 10 min e não deve virar histórico."),
 "02-recuperar-senha":(False,"Link de uso único. Guardar em lista de notificação é risco."),
 "03-senha-alterada":(True,"Registro de segurança. Precisa ficar auditável na conta."),
 "04-boas-vindas":(True,"Já existe como card “Welcome to ANTI” na Central."),
 "05-documentos-em-analise":(True,"É o status corrente do KYC enquanto durar a análise."),
 "06-documento-rejeitado":(True,"Card acionável: leva de volta para o reenvio."),
 "07-conta-aprovada":(True,"Marco da conta. Card “Empresa verificada”."),
 "08-convite-representante":(False,"Destinatário externo, ainda sem conta no app."),
 "09-proposta-disponivel":(True,"Card acionável com prazo de validade."),
 "10-contrato-para-assinatura":(True,"Pendência ativa até a assinatura."),
 "11-pedido-em-analise":(True,"Primeiro estado do pedido na timeline."),
 "12-aguardando-sacado":(True,"Estado do pedido; some quando o sacado confirma."),
 "13-sacado-confirmou":(True,"Mudança de estado do pedido."),
 "14-operacao-liquidada":(True,"Marco financeiro. Fica no histórico e no extrato."),
 "15-pedido-cancelado":(True,"Encerramento do pedido, com motivo."),
 "16-transferencia-enviada":(True,"Comprovante. Espelha o lançamento no extrato."),
 "17-boleto-emitido":(True,"Pendência de recebimento até o pagamento."),
 "18-pagamento-falhou":(True,"Card acionável para nova tentativa."),
}

# (implementada em dev, em producao) — nada implementado ainda
STATUS = {k:(False,False) for k in NAME}

TONE = {"Autenticação":"auth","KYC":"kyc","Antecipação":"ant","Conta":"conta"}

ANATOMY = [
 ("Cabeçalho", "22px 40px · fundo ink #171717", "Faixa preta com o wordmark e uma etiqueta de contexto em mono (Proposta, Segurança, Acao necessária). A etiqueta é o que o usuário lê antes do assunto no preview do cliente de email."),
 ("Sobretítulo", "IBM Plex Mono 10px · caps · 0.12em", "Classifica o email em duas palavras. Mesma taxonomia dos cards da Central de Notificações."),
 ("Título", "IBM Plex Sans 700 · 26px · -0.5px", "Uma frase, sujeito e verbo, no indicativo. Nunca uma pergunta."),
 ("Corpo", "Inter 15px · 1.65 · #52525b", "Um parágrafo. Diz o que aconteceu e o que muda para o usuário."),
 ("Bloco de dados", "Mono 11px caps / Plex Sans 700 14px", "Pares rótulo/valor separados por hairline. É o que substitui o print da tela: valor, pedido, sacado, prazo."),
 ("Destaque", "Fundo zinc + barra 3px semântica", "Só aparece quando existe motivo, risco ou aviso. Vermelho para rejeição e falha, âmbar para prazo e cancelamento."),
 ("Botão", "Pílula amarela #e9fc00 · ink 700 13px", "Um único CTA por email, sempre levando para a tela correspondente no app."),
 ("Rodapé", "Mono 9–11px · #8a8a90", "Assinatura ANTI · uma empresa DUX, canal de suporte, o aviso antifraude e os dados legais da emissora."),
]

def card(e):
    raw = (DIST / f'{e["id"]}.html').read_text(encoding="utf-8")
    doc = html.escape(fill(raw), quote=True)
    vars_html = "".join(f'<code>{{{{{v}}}}}</code>' for v in e["vars"])
    return f"""<article class="mail" id="{e['id']}">
  <header class="mail-head">
    <div class="mail-id">{e['id'].split('-')[0]}</div>
    <div class="mail-meta">
      <h3>{html.escape(e['subject'])}</h3>
      <p class="mail-trigger">{html.escape(e['trigger'])}</p>
      <div class="mail-tags">
        <span class="tag tag-{TONE[e['group']]}">{e['group']}</span>
        <span class="tag tag-screen">{html.escape(e['screen'])}</span>
      </div>
      <p class="mail-pre"><b>Preheader</b> {html.escape(e['preheader'])}</p>
      <div class="vars">{vars_html}</div>
    </div>
  </header>
  <div class="viewport"><iframe loading="lazy" title="Preview: {html.escape(e['subject'])}" srcdoc="{doc}"></iframe></div>
</article>"""

by_group = {}
for e in regua:
    by_group.setdefault(e["group"], []).append(e)

sections = []
for i, (g, sub, note) in enumerate(GROUPS, 1):
    items = by_group.get(g, [])
    chips = "".join(
      f'<a class="chip" href="#{e["id"]}">{html.escape(NAME[e["id"]])}</a>' for e in items)
    sections.append(f"""<section class="stage">
  <div class="stage-head">
    <span class="stage-n">Etapa {i}</span>
    <h3>{g}</h3>
    <p class="stage-sub">{sub}</p>
    <span class="stage-count">{len(items)} emails</span>
  </div>
  <div class="stage-body">
    <p class="stage-note">{note}</p>
    <div class="chips">{chips}</div>
  </div>
</section>""")

anatomy_rows = "".join(
  f"<li><span class='an-name'>{n}</span><span class='an-spec'>{s}</span><span class='an-why'>{w}</span></li>"
  for n, s, w in ANATOMY)

# ---------- tabela-guia ----------
def status_cell(ok):
    return ('<td class="st"><span class="mark yes">&#10003;</span></td>' if ok
            else '<td class="st"><span class="mark no">&#10005;</span></td>')

guide_rows = []
for gi, (g, gsub, _n) in enumerate(GROUPS, 1):
    items = by_group.get(g, [])
    done = sum(1 for e in items if STATUS[e["id"]][0])
    guide_rows.append(
      f'<tr class="grow grow-{TONE[g]}"><th colspan="6">'
      f'<span class="grow-n">Seção {gi}</span><span class="grow-name">{g}</span>'
      f'<span class="grow-sub">{gsub}</span>'
      f'<span class="grow-count">{done}/{len(items)}</span></th></tr>')
    for e in items:
        pv, pwhy = PERSIST[e["id"]]
        dev, prod = STATUS[e["id"]]
        guide_rows.append(
          f'<tr>'
          f'<td class="g-name"><span class="g-num">{e["id"].split("-")[0]}</span>{html.escape(NAME[e["id"]])}'
          f'<span class="g-sub">{html.escape(e["subject"])}</span></td>'
          f'<td class="g-trig">{html.escape(e["trigger"])}<span class="g-scr">{html.escape(e["screen"])}</span></td>'
          f'<td class="g-pers"><span class="pers {"p-yes" if pv else "p-no"}">{"Sim" if pv else "Não"}</span>'
          f'<span class="pers-why">{html.escape(pwhy)}</span></td>'
          f'<td class="g-link"><a href="#{e["id"]}">ver layout &rarr;</a></td>'
          f'{status_cell(dev)}{status_cell(prod)}'
          f'</tr>')

total = len(regua)
done_dev = sum(1 for e in regua if STATUS[e["id"]][0])
done_prod = sum(1 for e in regua if STATUS[e["id"]][1])
persist_n = sum(1 for e in regua if PERSIST[e["id"]][0])

guide_table = f"""<div class="block" id="guia">
  <h2 class="sec">Guia das comunicações do aplicativo</h2>
  <p class="lede" style="margin:0 0 26px;">Uma linha por comunicação, agrupada pela seção da jornada. <b>Persistência</b> responde se aquele aviso também fica como card na Central de Notificações do app — o que é efêmero ou de segurança não deve virar histórico. As duas últimas colunas são o placar: hoje nenhuma das dezoito está construída.</p>
  <div class="tablewrap">
  <table class="guide">
    <thead><tr>
      <th>Comunicação</th><th>Gatilho</th><th>Persistência</th><th>Layout</th>
      <th class="st">Implementada</th><th class="st">Em produção</th>
    </tr></thead>
    <tbody>{"".join(guide_rows)}</tbody>
    <tfoot><tr>
      <th colspan="2">Total</th>
      <th>{persist_n} de {total} persistem no app</th>
      <th></th>
      <th class="st">{done_dev}/{total}</th>
      <th class="st">{done_prod}/{total}</th>
    </tr></tfoot>
  </table>
  </div>
  <p class="legend"><span class="mark no">&#10005;</span> não construída &nbsp;·&nbsp; <span class="mark yes">&#10003;</span> pronta &nbsp;·&nbsp; para atualizar o placar, edite <code>STATUS</code> em <code>make_preview.py</code> e rode o script.</p>
</div>"""

# ---------- workflow ----------
FLUXO = [
 ("Solicitação", "Dux",
  "O pedido da comunicação, com a etapa da jornada em que ela entra e o que precisa dizer."),
 ("Materialização no Figma", "Claude",
  "Vira layout em dois estados: com as variáveis à mostra e com dados de teste preenchidos."),
 ("Revisão do texto", "Dux",
  "O time aprova o copy contra a etapa da jornada. É o passo que libera a comunicação."),
 ("Exportação", "Dux",
  "O HTML sai do repositório e vira um Dynamic Template, com <code>template_id</code> próprio."),
 ("Disparo", "Backend",
  "No evento, a Mail Send API é chamada com o template e os parâmetros da comunicação."),
]

flow_steps = ('<div class="fm-arrow" aria-hidden="true">→</div>').join(
  f'<li class="fm-step"><div class="fm-top"><span class="fm-n">{i}</span>'
  f'<span class="fm-owner">{who}</span></div>'
  f'<h4>{t}</h4><p>{d}</p></li>'
  for i, (t, who, d) in enumerate(FLUXO, 1))

workflow_block = f"""<div class="block" id="workflow">
  <h2 class="sec">O workflow</h2>
  <p class="lede" style="margin:0 0 30px;">São duas réguas, com públicos e responsabilidades diferentes, e as duas seguem o mesmo caminho de produção: cinco passos, com dono definido em cada um. O desenho existe para que nenhuma comunicação chegue ao destinatário sem ter passado pela revisão de texto, e para que o HTML tenha uma origem só.</p>
  <div class="tablewrap"><table class="duas">
    <thead><tr><th>Régua</th><th>Quem recebe</th><th>O que cobre</th><th>Status</th></tr></thead>
    <tbody>
      <tr>
        <td class="d-name"><a href="regua-app.html">Régua do app</a></td>
        <td>O cedente — quem tem conta no ANTI</td>
        <td>As dezoito comunicações deste documento, da criação da conta à liquidação da operação</td>
        <td><span class="pill-wip">Em revisão</span><span class="d-note">18 desenhadas, nenhuma implementada</span></td>
      </tr>
      <tr>
        <td class="d-name"><a href="regua-sacado.html">Régua do sacado</a></td>
        <td>O fornecedor e o parceiro, que é o sacado</td>
        <td>Cadastro do fornecedor, análise da operação e caminho do dinheiro, nas duas pontas</td>
        <td><span class="pill-wip">In progress</span><span class="d-note">15 comunicações, template IDs criados</span></td>
      </tr>
    </tbody>
  </table></div>

  <h3 class="flow-title">Os cinco passos</h3>
  <div class="flowwrap"><ol class="flowmap">{flow_steps}</ol></div>
  <div class="note" style="border-left-color:var(--conta);"><b>Onde isso tudo mora</b><p>As comunicações vivem num repositório próprio no GitHub, separado do código do aplicativo — só o copy, o gerador, os layouts e os dados de teste. O passo 2 acontece primeiro em arquivo: o Claude gera os layouts localmente, e é esse material que depois vai para o Figma, para revisão, e para o SendGrid, para envio. Versionar é o que tira as comunicações da máquina de uma pessoa só: qualquer um do time abre o repositório, lê o texto aprovado, vê o HTML exato que está no ar e acompanha no histórico o que mudou em cada template a cada revisão de copy.</p></div>
  <div class="note" style="border-left-color:var(--ant);"><b>A via de volta</b><p>A chamada de API é a ida: o sistema pede ao SendGrid que envie. A volta é o <i>Event Webhook</i>, que o SendGrid chama de volta no nosso endpoint a cada entrega, abertura, bounce ou marcação de spam. É essa via que diz se a régua está funcionando de verdade — e é dela que sai o número de implementadas que aparece na página de cada régua.</p></div>
</div>

"""

cards = "".join(card(e) for e in regua)

# ============================================================ o site

SITE = ROOT / "site"

FIGMA_RS = "https://www.figma.com/design/XIT0diYFNoRLVEBR02XrAx/Risco-Sacado?node-id=24-7"

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500;700'
         '&family=Inter:wght@400;500;600&display=swap">')

PAGINAS = [
    ("index.html",        "Guideline",        ""),
    ("regua-app.html",    "Régua do app",     "Em revisão"),
    ("regua-sacado.html", "Régua do sacado",  "In progress"),
]

def nav(atual):
    itens = []
    for arquivo, nome, status in PAGINAS:
        cls = "nav-link atual" if arquivo == atual else "nav-link"
        st = f'<span class="nav-st">{status}</span>' if status else ""
        itens.append(f'<a class="{cls}" href="{arquivo}">{nome}{st}</a>')
    return f'''<nav class="topnav">
  <a class="nav-brand" href="index.html">ANTI<span>·</span>Comunicação</a>
  <div class="nav-links">{"".join(itens)}</div>
</nav>'''

def pagina(arquivo, titulo, corpo):
    return f'''<title>{titulo}</title>
{FONTS}
<link rel="stylesheet" href="style.css">
<div class="shell">
{nav(arquivo)}
{corpo}
<footer class="end">ANTI &middot; uma empresa DUX &middot; guideline das réguas de comunicação</footer>
</div>
'''

def parte(nome):
    return (ROOT / "parts" / f"{nome}.html").read_text(encoding="utf-8")

# ------------------------------------------------------------ home
LINKS = [
  ("Repositório", "As comunicações, o gerador e os HTML de produção",
   "github.com/&lt;org&gt;/anti-comunicacoes", "#"),
  ("Figma dos emails", "Os layouts, com variáveis e com dados de teste",
   "figma.com/design/CDkBtKsfa2uuRdEYVUDfeM",
   "https://www.figma.com/design/CDkBtKsfa2uuRdEYVUDfeM"),
  ("Figma do Risco Sacado", "O fluxo do parceiro e do fornecedor no Portal ANTI",
   "figma.com/design/XIT0diYFNoRLVEBR02XrAx", FIGMA_RS),
  ("Brandbook", "A marca, os ativos e o uso correto do ícone",
   "brandbook.sejaanti.com.br", "https://brandbook.sejaanti.com.br/"),
  ("SendGrid", "Onde os templates vivem e de onde os emails saem",
   "Email API › Dynamic Templates", "https://app.sendgrid.com/"),
]

links_html = "".join(
  f'<a class="link-card" href="{url}"{" target=_blank rel=noopener" if url != "#" else ""}>'
  f'<span class="link-name">{n}</span><span class="link-what">{w}</span>'
  f'<span class="link-url">{u}</span></a>' for n, w, u, url in LINKS)

home = f'''<header class="hero">
  <div class="kicker">ANTI &middot; Guideline &middot; v1 &middot; set 2026</div>
  <h1>Guideline das<br><em>réguas de comunicação</em>.</h1>
  <p class="lede">De qual domínio sai cada mensagem, por qual caminho ela é aprovada e como ela é construída. Este documento é o centralizador: as regras que valem para toda comunicação de email do ANTI moram aqui, e cada régua tem a sua própria página.</p>
  <div class="facts">
    <div class="fact"><b>2</b><span>réguas</span></div>
    <div class="fact"><b>3</b><span>domínios de envio</span></div>
    <div class="fact"><b>5</b><span>passos até o disparo</span></div>
    <div class="fact"><b>8</b><span>blocos de layout</span></div>
    <div class="fact"><b>600px</b><span>largura &middot; tabelas</span></div>
  </div>
</header>

{parte("dominios")}

{workflow_block}

<div class="block">
  <h2 class="sec">O layout</h2>
  <p class="lede" style="margin:0 0 30px;">Um único template serve todas as comunicações. São oito blocos, cada um com uma função — e a disciplina é usar só os que a mensagem precisa, nunca todos.</p>
  <div class="anatomy">
    <div class="viewport" style="height:640px;border:1px solid var(--line);border-radius:14px;border-top:1px solid var(--line);">
      <iframe title="Anatomia do template" srcdoc="{html.escape(fill((DIST / '09-proposta-disponivel.html').read_text(encoding='utf-8')), quote=True)}"></iframe>
    </div>
    <ol>{anatomy_rows}</ol>
  </div>
</div>

<div class="block">
  <h2 class="sec">Onde está o resto</h2>
  <p class="lede" style="margin:0 0 30px;">As duas réguas, e as ferramentas que sustentam as duas.</p>
  <div class="link-grid">{links_html}</div>
</div>
'''

# ------------------------------------------------------------ régua do app
app = f'''<header class="hero pagehero">
  <div class="kicker">Régua 1 de 2 &middot; destinatário: o cedente</div>
  <h1>Régua do <em>app</em>.<span class="hero-st">Em revisão</span></h1>
  <p class="lede">Dezoito emails de serviço, um para cada mudança de estado que o aplicativo já comunica na Central de Notificações. Mesmo gatilho, mesma taxonomia, mesmo texto: o email é a versão do aviso que sobrevive fora do app, na caixa de entrada do cedente.</p>
  <div class="facts">
    <div class="fact"><b>18</b><span>comunicações</span></div>
    <div class="fact"><b>4</b><span>etapas da jornada</span></div>
    <div class="fact"><b>16</b><span>persistem no app</span></div>
    <div class="fact"><b>0</b><span>implementadas</span></div>
  </div>
</header>

<div class="block">
  <h2 class="sec">Os tipos de comunicação</h2>
  <p class="lede" style="margin:0 0 30px;">Quatro etapas da jornada do cedente, da criação da conta à movimentação de dinheiro.</p>
  {"".join(sections)}
</div>

{guide_table}

<div class="block">
  <h2 class="sec">Os dezoito emails</h2>
  <p class="lede" style="margin:0 0 30px;">Renderizados com dados de exemplo — é assim que cada um chega na caixa de entrada.</p>
  <div class="mails">{cards}</div>
</div>

{parte("sendgrid")}
'''

# ------------------------------------------------------------ régua do sacado

# As 15 comunicacoes do Risco Sacado, com o template_id que ja existe no SendGrid.
# fluxo: FRS = cadastro do fornecedor · PFS = operacao no portal · RS = cadastro em duas etapas
# quem: F = fornecedor (vende a nota) · P = parceiro, que e o sacado (analisa e paga)
# As 13 comunicações do Risco Sacado, aprovadas no Figma e criadas no SendGrid.
# fluxo: FRS = cadastro do fornecedor · PFS = operação no portal
# quem: F = fornecedor (vende a nota) · P = parceiro (analisa e paga, é o sacado)
# node = id do card no Figma (Risco-Sacado); png = arquivo em assets/previews/
SACADO = [
 dict(cod="FRS1",   nome="Convite", fluxo="FRS", quem="F",
      tid="d-df076170993449039a972802cde7bbf5",
      quando="O parceiro inclui o CNPJ do fornecedor na carteira dele — cadastro avulso ou importação por planilha — e o fornecedor ainda não tem conta no portal",
      vars=["cnpj","link_cta","nome_parceira","razao_social","rotulo_papel","rotulo_papel_plural"],
      node="30:6", png="FRS1-convite.png"),
 dict(cod="FRS1",   nome="Cadastro em análise", fluxo="FRS", quem="F",
      tid="d-68534294d64145d1bc45ef348d7cfba0",
      quando="O fornecedor conclui o cadastro num único formulário — CNPJ, dados do representante e os quatro documentos — e ele entra em conferência",
      vars=["data_envio","link_cta","nome_parceira","razao_social"],
      node="30:10", png="FRS1-cadastro-em-analise.png"),
 dict(cod="FRS2",   nome="Cadastro aprovado", fluxo="FRS", quem="F",
      tid="d-48eafcac67b94c5a87b51646caa9c1ff",
      quando="A equipe Anti aprova os documentos e o parceiro confirma o vínculo — a conta do fornecedor passa a ATIVA",
      vars=["data_aprovacao","link_cta","nome_parceira","razao_social"],
      node="30:14", png="FRS2-cadastro-aprovado.png"),
 dict(cod="FRS3",   nome="Cadastro negado", fluxo="FRS", quem="F",
      tid="d-7a59f96e6e3f4ae4ab3bd0a4f6f5f4e0",
      quando="O cadastro do fornecedor é reprovado na conferência de documentos",
      vars=["data_analise","link_cta","nome_parceira","razao_social"],
      node="30:18", png="FRS3-cadastro-negado.png"),
 dict(cod="FRS2-P", nome="Cadastro aprovado (parceiro)", fluxo="FRS", quem="P",
      tid="d-e87f58eec2b04bc0baf5c91e4f8964ef",
      quando="Mesmo evento do FRS2, do lado do parceiro — o fornecedor que ele colocou na carteira está liberado para operar",
      vars=["cnpj","data_aprovacao","link_cta","razao_social"],
      node="91:2", png="FRS2P-parceiro-cadastro-aprovado.png"),
 dict(cod="FRS3-P", nome="Cadastro negado (parceiro)", fluxo="FRS", quem="P",
      tid="d-afbd77eabc4d478ca385f149c59f2c12",
      quando="Mesmo evento do FRS3, do lado do parceiro",
      vars=["cnpj","data_analise","link_cta","motivo_recusa","razao_social"],
      node="91:6", png="FRS3P-parceiro-cadastro-negado.png"),
 dict(cod="PFS1",   nome="Solicitação enviada", fluxo="PFS", quem="F",
      tid="d-dd5d687573bd48a38339e77470225c4f",
      quando="O fornecedor anexa a nota, confere os dados extraídos e confirma o envio — etapa 3 de 3 do assistente de nova antecipação",
      vars=["link_cta","nome_parceira","order_id","valor_nota","vencimento"],
      node="41:2", png="PFS1-solicitacao-enviada.png"),
 dict(cod="PFS1-P", nome="Nova solicitação (parceiro)", fluxo="PFS", quem="P",
      tid="d-2e9435d081214a13a6f9fa25315c4cf9",
      quando="Mesmo envio, do lado do parceiro — a nota cai na fila “Para analisar” do Portal do Parceiro",
      vars=["cnpj_cedente","descricao","link_cta","nome_cedente","order_id","valor_nota","vencimento"],
      node="41:14", png="PFS1-parceiro-nova-solicitacao.png"),
 dict(cod="PFS2",   nome="Solicitação aprovada", fluxo="PFS", quem="F",
      tid="d-84f758f7f7dc4c5eb8681cd34905c7f0",
      quando="A dupla aprovação fecha: o parceiro aprova a nota (APROVAÇÃO PARCEIRO) e a Anti aprova o crédito (APROVAÇÃO ANTI) — contrato gerado",
      vars=["desagio","link_cta","nome_parceira","order_id","valor_liquido","valor_nota"],
      node="41:6", png="PFS2-solicitacao-aprovada.png"),
 dict(cod="PFS3",   nome="Solicitação recusada", fluxo="PFS", quem="F",
      tid="d-e9b5379872e64b55972589430d7cdca3",
      quando="A operação é recusada — pelo parceiro ou pela Anti, na tela de detalhe da operação",
      vars=["link_cta","nome_parceira","order_id","valor_nota"],
      node="41:10", png="PFS3-solicitacao-recusada.png"),
 dict(cod="PFS4",   nome="Contrato assinado", fluxo="PFS", quem="F",
      tid="d-5b598cf937164a07b8bcaaf0453ef957",
      quando="O contrato da cessão é assinado digitalmente por todas as partes",
      vars=["conta_destino","link_cta","nome_parceira","order_id","previsao_credito","valor_liquido"],
      node="91:12", png="PFS4-contrato-assinado.png"),
 dict(cod="PFS5",   nome="Valor creditado", fluxo="PFS", quem="F",
      tid="d-72de6fe3e58145db9d90ae63f21815da",
      quando="O depósito do valor líquido é efetivado na conta do fornecedor — liquidação da operação",
      vars=["conta_destino","data_credito","desagio","link_cta","nome_parceira","order_id","valor_liquido","valor_nota"],
      node="91:16", png="PFS5-valor-creditado.png"),
 dict(cod="PFS6",   nome="Falha no depósito", fluxo="PFS", quem="F",
      tid="d-0bab21d89b5a4a4e898318e371b39490",
      quando="O depósito não se conclui — dados bancários divergentes, conta encerrada ou saldo insuficiente do lado da Anti",
      vars=["id_tentativa","link_cta","motivo_falha","order_id","valor_liquido"],
      node="91:20", png="PFS6-falha-no-deposito.png"),
 dict(cod="PFS7",   nome="Pendência na solicitação", fluxo="PFS", quem="F", novo=True,
      tid="d-b50b009d7eb54c168e509b3f03a10f10",
      quando="A equipe Anti revisa a solicitação e falta algo — documento ou informação — para seguir com a análise (sem tela mapeada: descoberto no SendGrid em 25/09/2026, sem passar pelo Figma)",
      vars=["link_cta","nome_parceira","order_id","pendencias","pendencias_frase","valor_nota","vencimento"],
      node="145:3", png="PFS7-pendencia-na-solicitacao.png"),
 dict(cod="PRS1",   nome="Convite parceira", fluxo="PRS", quem="P", novo=True,
      tid="d-113bdd4dfd044dcd9370de4bd2b9301f",
      quando="A equipe Anti cadastra o responsável por uma nova empresa parceira, que ainda não tem acesso ao Portal do Parceiro (sem tela mapeada: descoberto no SendGrid em 25/09/2026, sem passar pelo Figma)",
      vars=["email","link_cta","nome_parceira","senha_minima","validade"],
      node="145:9", png="PRS1-convite-parceira.png"),
]



FLUXO_NOME = {"FRS": "Cadastro do fornecedor", "PFS": "Operação no portal", "PRS": "Acesso do parceiro"}
QUEM_NOME = {"F": "Fornecedor", "P": "Parceiro"}

import re as _re
def _slug(t):
    return _re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")

def status_pill(x):
    if x.get("novo"):
        return '<span class="pill-new">Novo · sem tela</span>'
    return '<span class="pill-wip">In progress</span>'

sacado_rows = ""
_fluxo_atual = None
for x in SACADO:
    if x["fluxo"] != _fluxo_atual:
        _fluxo_atual = x["fluxo"]
        n = sum(1 for y in SACADO if y["fluxo"] == _fluxo_atual)
        sacado_rows += (f'<tr class="grow"><th colspan="6">'
                        f'<span class="grow-n">{_fluxo_atual}</span>'
                        f'<span class="grow-name">{FLUXO_NOME[_fluxo_atual]}</span>'
                        f'<span class="grow-count">{n} comunicações</span></th></tr>')
    sacado_rows += (
      f'<tr>'
      f'<td class="s-name"><a href="#pv-{x["cod"].lower()}-{_slug(x["nome"])}">'
      f'<span class="g-num">{x["cod"]}</span>{html.escape(x["nome"])}</a></td>'
      f'<td class="s-quem"><span class="quem quem-{x["quem"]}">{QUEM_NOME[x["quem"]]}</span></td>'
      f'<td class="s-when">{html.escape(x["quando"])}</td>'
      f'<td class="s-vars">{"".join(f"<code>{{{{{v}}}}}</code>" for v in x["vars"])}</td>'
      f'<td class="s-tid"><code class="tid">{x["tid"]}</code></td>'
      f'<td class="st">{status_pill(x)}</td>'
      f'</tr>')

BACKEND = [
 ("Template ID em configuração, nunca no código",
  "Os treze <code>template_id</code> já existem no SendGrid e estão na tabela acima, conferidos contra a conta. Eles pertencem ao ambiente, não ao código: sandbox e produção têm ids diferentes, e um id fixo no fonte é o erro que só aparece no dia do go-live."),
 ("Um evento, dois destinatários",
  "A dupla aprovação faz cada mudança de estado render duas comunicações — o par FRS2/FRS2-P e o par PFS1/PFS1-P. São dois <code>template_id</code> e duas chamadas, não um email com dois destinatários em cópia: o que o fornecedor precisa ler não é o que o parceiro precisa ler."),
 ("O convite vai para quem ainda não tem conta",
  "FRS1 · Convite sai depois da inclusão do CNPJ na carteira do parceiro, para um endereço que nunca se autenticou. O <code>link_cta</code> desse template carrega um link de convite válido por 7 dias — a cópia já avisa o fornecedor disso, o valor exato não é uma variável."),
 ("Bounce do convite volta para o parceiro",
  "O endereço do fornecedor vem da planilha ou do cadastro avulso que o parceiro fez, então erro de digitação é caso comum. O Event Webhook precisa devolver o bounce de FRS1 para a tela de Fornecedores, e não falhar em silêncio — senão o fornecedor fica em AGUARDANDO para sempre."),
 ("Idempotência por evento",
  "Retry de fila não pode virar segundo email. A chave combina o id da operação (ou do cadastro) com o código da comunicação — <code>PFS5:op_12345</code>."),
 ("Motivo da recusa: só o parceiro vê",
  "FRS3 e PFS3 (fornecedor) não carregam <code>motivo_recusa</code> — o email manda o fornecedor falar com o suporte. Já FRS3-P (parceiro) carrega o motivo, porque foi ele quem recusou. Enviar o motivo também ao fornecedor é mudança de produto, não só de template — decidir antes de alterar."),
 ("Uma inconsistência de nome, ainda aberta",
  "Ao descrever o fornecedor numa mensagem para o parceiro, PFS1-P usa <code>nome_cedente</code>/<code>cnpj_cedente</code>, enquanto FRS2-P/FRS3-P usam <code>razao_social</code>/<code>cnpj</code> sem prefixo. Não foi decisão deliberada — as duas rodadas de geração divergiram. Antes de versionar 1.0, escolher um padrão só e republicar os três templates."),
 ("Dois templates fora deste escopo",
  "<code>RS1</code> e <code>RS2</code> existem no SendGrid — vieram de uma proposta de melhoria ao cadastro (página Melhoria, no Figma), que reorganiza o formulário em dois passos. A proposta não foi aprovada nem decidida, então ficou fora deste documento. Não usar esses dois nos testes de disparo: eles não correspondem a nenhuma tela do fluxo atual do portal."),
 ("Os números vêm de um lugar só",
  "Valor da nota, deságio e valor líquido aparecem no email e na tela de detalhe da operação. Eles têm que sair do mesmo cálculo: divergência entre o que o email diz e o que o portal mostra vira chamado no suporte e desconfiança na conta."),
]

backend_html = "".join(
  f'<div class="bk"><h4>{t}</h4><p>{d}</p></div>' for t, d in BACKEND)

sacado_ctx = parte("sacado-contexto").replace(
  '<h2 class="sec">Régua do sacado</h2>', '<h2 class="sec">Por que o sacado recebe email</h2>')

FIGMA_CADASTRO = "https://www.figma.com/design/XIT0diYFNoRLVEBR02XrAx/Risco-Sacado?node-id=0-1"
FIGMA_LOGADO   = "https://www.figma.com/design/XIT0diYFNoRLVEBR02XrAx/Risco-Sacado?node-id=22-7"

def _figma_card(node):
    return f"https://www.figma.com/design/XIT0diYFNoRLVEBR02XrAx/Risco-Sacado?node-id={node.replace(':', '-')}"

preview_html = ""
_fluxo_prev = None
for x in SACADO:
    if x["fluxo"] != _fluxo_prev:
        _fluxo_prev = x["fluxo"]
        if preview_html:
            preview_html += "</div>"
        preview_html += (f'<h3 class="prev-group"><span class="grow-n">{_fluxo_prev}</span>'
                          f'<span class="grow-name">{FLUXO_NOME[_fluxo_prev]}</span></h3><div class="mails">')
    anchor = f'pv-{x["cod"].lower()}-{_slug(x["nome"])}'
    preview_html += (
      f'<article class="mail" id="{anchor}">'
      f'<header class="mail-head"><div class="mail-id">{x["cod"]}</div><div class="mail-meta">'
      f'<h3>{html.escape(x["nome"])}</h3><p class="mail-trigger">{html.escape(x["quando"])}</p>'
      f'<div class="mail-tags"><span class="quem quem-{x["quem"]}">{QUEM_NOME[x["quem"]]}</span></div>'
      f'<p class="mail-pre"><b>Template ID</b><code class="tid">{x["tid"]}</code></p>'
      f'</div></header>'
      f'<a class="mail-shot" href="previews/{x["png"]}" target="_blank" rel="noopener">'
      f'<img src="previews/{x["png"]}" alt="Preview do email {x["cod"]} · {html.escape(x["nome"])}" loading="lazy"></a>'
      f'<div class="mail-foot"><a class="chip" href="{_figma_card(x["node"])}" target="_blank" rel="noopener">'
      f'Ver este card no Figma &rarr;</a></div>'
      f'</article>')
preview_html += "</div>"

FIGMA_PARCEIRO = "https://www.figma.com/design/XIT0diYFNoRLVEBR02XrAx/Risco-Sacado?node-id=24-7"

sacado = f'''<header class="hero pagehero">
  <div class="kicker">Régua 2 de 2 &middot; Portal ANTI &middot; produto Risco Sacado</div>
  <h1>Régua do <em>risco sacado</em>.<span class="hero-st">In progress</span></h1>
  <p class="lede">Quinze comunicações que cobrem o cadastro do fornecedor, a análise da operação e o caminho do dinheiro — treze com tela mapeada no Figma, e duas descobertas direto no SendGrid, sem passar por lá ainda. Diferente da régua do app, aqui há dois destinatários: o fornecedor, que vende a nota, e o parceiro, que a paga.</p>
  <div class="facts">
    <div class="fact"><b>15</b><span>comunicações</span></div>
    <div class="fact"><b>3</b><span>fluxos</span></div>
    <div class="fact"><b>2</b><span>destinatários</span></div>
    <div class="fact"><b>15</b><span>template IDs verificados</span></div>
    <div class="fact"><b>2</b><span>sem tela mapeada</span></div>
  </div>
</header>

{sacado_ctx}

<div class="block">
  <h2 class="sec">As comunicações</h2>
  <p class="lede" style="margin:0 0 20px;">Agrupadas pelo fluxo a que pertencem. Cada linha traz quem recebe, o gatilho, as variáveis reais que o template espera em <code>dynamic_template_data</code> e o <code>template_id</code> do SendGrid. Clique no nome da comunicação para ver a cara dela na seção Preview, logo abaixo.</p>
  <p class="aviso"><b>Template ID e variáveis conferidos contra a conta real do SendGrid, um a um, em 28/09/2026.</b> Este documento é espelho do fluxo desenhado nas páginas <a href="{FIGMA_CADASTRO}" target="_blank" rel="noopener">Cadastro Fornecedor</a>, <a href="{FIGMA_LOGADO}" target="_blank" rel="noopener">Fluxo logado</a> e <a href="{FIGMA_PARCEIRO}" target="_blank" rel="noopener">Fluxo do Parceiro</a> — nenhuma proposta ainda não decidida entra aqui (RS1/RS2 seguem fora, ver nota no backend). As variáveis são exatamente os <code>{{{{token}}}}</code> que aparecem no HTML de cada versão ativa. Uma convenção vale para as quinze: o botão de ação é sempre <code>{{{{link_cta}}}}</code>, em todo template — nunca um nome específico como <code>contrato_url</code> ou <code>portal_url</code>.</p>
  <div class="note" style="border-left-color:var(--auth);"><b>Ressincronizado depois de uma edição direta no SendGrid</b><p>Em 25/09/2026, quem implementou o backend editou os treze templates originais direto no Code Editor do SendGrid — sem passar pelo Figma nem por este repositório. A mudança real: <code>{{{{nome_parceira}}}}</code> passou a substituir "Mynd" cravado no texto (o portal tem mais parceiros, como o Banco do Brasil), e <code>PFS1-P</code> trocou a linha "Nota" por "Serviço" (<code>{{{{descricao}}}}</code> no lugar de <code>{{{{numero_nota}}}}</code>), alinhando com o que <code>PFS1</code> já mostrava do lado do fornecedor. A mesma pessoa também criou dois templates novos direto no SendGrid — <b>PFS7</b> e <b>PRS1</b>, marcados abaixo como &ldquo;Novo &middot; sem tela&rdquo; — que preenchem lacunas reais do fluxo (uma pendência na análise, o primeiro acesso de um parceiro novo) mas ainda não têm uma tela do portal mapeada aqui. Este documento, o Figma e o gerador em <code>emails/</code> foram todos ressincronizados a partir do SendGrid nesta data.</p></div>
  <div class="tablewrap"><table class="sacado">
    <thead><tr>
      <th>Comunicação</th><th>Quem recebe</th><th>Gatilho</th>
      <th>Variáveis</th><th>Template ID &middot; SendGrid</th><th>Status</th>
    </tr></thead>
    <tbody>{sacado_rows}</tbody>
  </table></div>
</div>

<div class="block" id="preview">
  <h2 class="sec">Preview</h2>
  <p class="lede" style="margin:0 0 12px;">A cara real de cada uma das quinze comunicações, na mesma ordem e com os mesmos códigos da tabela acima — são capturas do HTML publicado, não um mockup à parte. Clique numa imagem para abrir em tamanho real, ou em &ldquo;Ver no Figma&rdquo; para abrir o card correspondente no arquivo <a href="https://www.figma.com/design/XIT0diYFNoRLVEBR02XrAx/Risco-Sacado" target="_blank" rel="noopener">Risco Sacado</a>.</p>
  <p class="lede" style="margin:0 0 30px;">O Figma é a referência para contexto, não só para o visual: a maioria dos cards fica ao lado do print da tela do Portal ANTI que dispara aquela comunicação, ligado por uma seta — a página <a href="{FIGMA_CADASTRO}" target="_blank" rel="noopener">Cadastro Fornecedor</a> tem o FRS1/FRS2/FRS3, e a <a href="{FIGMA_LOGADO}" target="_blank" rel="noopener">Fluxo logado</a> tem o PFS1&ndash;PFS6. PFS7 e PRS1 são exceção: entraram no Figma nesta ressincronização, com borda tracejada roxa, sem seta para nenhuma tela — porque nenhuma foi mapeada ainda.</p>
  {preview_html}
</div>

<div class="block">
  <h2 class="sec">Para a implementação no backend</h2>
  <p class="lede" style="margin:0 0 30px;">O que muda em relação à régua do app, onde o destinatário é um usuário autenticado.</p>
  <div class="bk-grid">{backend_html}</div>
</div>
'''

# ------------------------------------------------------------ escreve
SITE.mkdir(exist_ok=True)
(SITE / "index.html").write_text(pagina("index.html", "Guideline das Réguas de Comunicação", home), encoding="utf-8")
(SITE / "regua-app.html").write_text(pagina("regua-app.html", "Régua do App — Guideline ANTI", app), encoding="utf-8")
(SITE / "regua-sacado.html").write_text(pagina("regua-sacado.html", "Régua do Sacado — Guideline ANTI", sacado), encoding="utf-8")
(SITE / "style.css").write_text((ROOT / "style.css").read_text(encoding="utf-8"), encoding="utf-8")

# previews reais das 13 comunicações do Risco Sacado (screenshots do HTML no
# SendGrid), usados na seção Preview de regua-sacado.html
import shutil
PREV_SRC = ROOT / "assets" / "previews"
PREV_OUT = SITE / "previews"
PREV_OUT.mkdir(exist_ok=True)
for x in SACADO:
    shutil.copyfile(PREV_SRC / x["png"], PREV_OUT / x["png"])

print("site/ gerado:", sorted(p.name for p in SITE.iterdir()))
print("previews copiados:", len(list(PREV_OUT.iterdir())))
