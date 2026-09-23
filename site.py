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
        <td><span class="pill-wip">Em construção</span><span class="d-note">desenhadas, nenhuma implementada</span></td>
      </tr>
      <tr>
        <td class="d-name"><a href="regua-sacado.html">Régua do sacado</a></td>
        <td>O sacado — o devedor da nota, sem conta no app</td>
        <td>Confirmação da operação, notificação da cessão, vencimento e pagamento</td>
        <td><span class="pill-wip">Em construção</span><span class="d-note">6 previstas, a validar</span></td>
      </tr>
    </tbody>
  </table></div>

  <h3 class="flow-title">Os cinco passos</h3>
  <div class="flowwrap"><ol class="flowmap">{flow_steps}</ol></div>
  <div class="note" style="border-left-color:var(--conta);"><b>Onde isso tudo mora</b><p>As comunicações vivem num repositório próprio no GitHub, separado do código do aplicativo — só o copy, o gerador, os layouts e os dados de teste. O passo 2 acontece primeiro em arquivo: o Claude gera os layouts localmente, e é esse material que depois vai para o Figma, para revisão, e para o SendGrid, para envio. Versionar é o que tira as comunicações da máquina de uma pessoa só: qualquer um do time abre o repositório, lê o texto aprovado, vê o HTML exato que está no ar e acompanha no histórico o que mudou em cada template a cada revisão de copy.</p></div>
  <div class="note" style="border-left-color:var(--ant);"><b>A via de volta</b><p>A chamada de API é a ida: o sistema pede ao SendGrid que envie. A volta é o <i>Event Webhook</i>, que o SendGrid chama de volta no nosso endpoint a cada entrega, abertura, bounce ou marcação de spam. É essa via que diz se a régua está funcionando de verdade — e é dela que sai o número que preenche as duas últimas colunas da tabela adiante.</p></div>
</div>

"""

cards = "".join(card(e) for e in regua)

# ============================================================ o site

SITE = ROOT / "site"

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
SACADO = [
 dict(nome="Confirmação da operação", quando="O cedente informa o sacado e envia a solicitação (telas de informar sacado e solicitação enviada; pedido em OT3)",
      para="Contato financeiro do sacado", acao="Confirmar a nota e o valor",
      vars=["sacado_name","sacado_contact","cedente_name","order_id","invoice_number","gross_amount","due_date","confirm_url","expires_at"]),
 dict(nome="Lembrete de confirmação", quando="O prazo de confirmação está acabando e o sacado não respondeu",
      para="Contato financeiro do sacado", acao="Confirmar antes do prazo",
      vars=["sacado_name","cedente_name","order_id","confirm_url","hours_left"]),
 dict(nome="Notificação da cessão", quando="Contrato assinado — o crédito muda de titular",
      para="Contato financeiro e jurídico do sacado", acao="Registrar o novo domicílio de pagamento",
      vars=["sacado_name","cedente_name","invoice_number","gross_amount","due_date","escrow_account","assignment_date"]),
 dict(nome="Lembrete de vencimento", quando="Alguns dias antes da data de vencimento da nota",
      para="Contato financeiro do sacado", acao="Pagar no domicílio correto",
      vars=["sacado_name","invoice_number","amount","due_date","escrow_account","boleto_url"]),
 dict(nome="Confirmação de pagamento", quando="O pagamento é identificado na conta escrow",
      para="Contato financeiro do sacado", acao="Nenhuma — é recibo",
      vars=["sacado_name","invoice_number","amount","paid_at","receipt_url"]),
 dict(nome="Operação encerrada sem efeito", quando="A operação é cancelada depois de o sacado já ter sido contatado",
      para="Contato financeiro do sacado", acao="Nenhuma — desfaz a instrução anterior",
      vars=["sacado_name","cedente_name","order_id","cancel_reason"]),
]

sacado_rows = "".join(
  f'<tr>'
  f'<td class="s-name"><span class="g-num">{i:02d}</span>{html.escape(x["nome"])}</td>'
  f'<td class="s-when">{html.escape(x["quando"])}<span class="s-para">{html.escape(x["para"])}</span></td>'
  f'<td class="s-acao">{html.escape(x["acao"])}</td>'
  f'<td class="s-vars">{"".join(f"<code>{{{{{v}}}}}</code>" for v in x["vars"])}</td>'
  f'<td class="s-tid"><span class="tid-vazio">a preencher</span></td>'
  f'<td class="st"><span class="pill-wip">In progress</span></td>'
  f'</tr>' for i, x in enumerate(SACADO, 1))

BACKEND = [
 ("O link precisa ser um token assinado",
  "O sacado não tem conta, então a confirmação acontece fora de sessão. O <code>confirm_url</code> carrega um token de uso único, com expiração curta e vínculo ao pedido — não um id sequencial adivinhável."),
 ("Sem persistência in-app",
  "Nenhuma dessas comunicações vira card na Central de Notificações: o destinatário não tem onde vê-la. O email é o canal inteiro, e o registro fica no log de eventos da operação."),
 ("Bounce volta para o cedente",
  "O endereço do sacado é digitado pelo cedente, então erro de digitação é o caso comum, não a exceção. O Event Webhook precisa tratar o bounce dessas comunicações avisando o cedente no app, e não silenciosamente."),
 ("Idempotência por evento",
  "Retry de fila não pode virar segundo email. A chave de idempotência combina o id da operação com o tipo de comunicação."),
 ("O que não pode ir no corpo",
  "Dados do cedente além do necessário para o sacado reconhecer a nota. A relação comercial é dele com o cedente; a ANTI entra como cessionária, não como parte da negociação."),
 ("Remetente e domínio",
  "Decisão em aberto: se sai do mesmo domínio transacional do app ou de um subdomínio próprio. O público é outro e o volume é outro, o que pesa a favor de separar."),
]

backend_html = "".join(
  f'<div class="bk"><h4>{t}</h4><p>{d}</p></div>' for t, d in BACKEND)

sacado_ctx = parte("sacado-contexto").replace(
  '<h2 class="sec">Régua do sacado</h2>', '<h2 class="sec">Por que o sacado recebe email</h2>')

sacado = f'''<header class="hero pagehero">
  <div class="kicker">Régua 2 de 2 &middot; destinatário: o sacado</div>
  <h1>Régua do <em>sacado</em>.<span class="hero-st">In progress</span></h1>
  <p class="lede">Risco sacado é o modelo padrão da operação: a decisão de crédito olha para quem vai pagar a nota. Essas são as comunicações que saem para ele — outro público, outro tom e outro peso jurídico que os da régua do app.</p>
  <div class="facts">
    <div class="fact"><b>6</b><span>comunicações previstas</span></div>
    <div class="fact"><b>0</b><span>implementadas</span></div>
    <div class="fact"><b>0</b><span>persistem no app</span></div>
    <div class="fact"><b>95%</b><span>das operações com escrow</span></div>
  </div>
</header>

{sacado_ctx}

<div class="block">
  <h2 class="sec">As comunicações</h2>
  <p class="lede" style="margin:0 0 20px;">Cada linha traz o gatilho, o que se espera do destinatário, as variáveis que o backend precisa mandar em <code>dynamic_template_data</code> e o espaço do <code>template_id</code> do SendGrid, que se preenche quando o template for criado.</p>
  <p class="aviso"><b>Proposta, não fechado.</b> Esta lista foi derivada do fluxo do sacado no app e do desenho da operação. Ela precisa ser conferida contra o fluxo que está no Figma e validada com o jurídico antes de virar template.</p>
  <div class="tablewrap"><table class="sacado">
    <thead><tr>
      <th>Comunicação</th><th>Gatilho</th><th>O que se espera</th>
      <th>Variáveis</th><th>Template ID</th><th>Status</th>
    </tr></thead>
    <tbody>{sacado_rows}</tbody>
  </table></div>
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

print("site/ gerado:", sorted(p.name for p in SITE.iterdir()))
