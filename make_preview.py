#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera preview.html: a régua completa + os 18 emails renderizados."""
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
        <td class="d-name"><a href="#guia">Régua do app</a></td>
        <td>O cedente — quem tem conta no ANTI</td>
        <td>As dezoito comunicações deste documento, da criação da conta à liquidação da operação</td>
        <td><span class="pill-wip">Em construção</span><span class="d-note">desenhadas, nenhuma implementada</span></td>
      </tr>
      <tr>
        <td class="d-name"><a href="#sacado">Régua do sacado</a></td>
        <td>O sacado — o devedor da nota, sem conta no app</td>
        <td>Confirmação da operação, notificação da cessão, vencimento e pagamento</td>
        <td><span class="pill-wip">Em construção</span><span class="d-note">a definir, com jurídico</span></td>
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

PAGE = f"""<title>Guideline das Réguas de Comunicação</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500;700&family=Inter:wght@400;500;600&display=swap">
<style>
:root {{
  --ink:#171717; --ink-2:#3f3f42; --paper:#fbfbf7; --card:#ffffff;
  --line:#e4e4e0; --line-2:#efefeb; --body:#55555c; --mute:#8a8a90;
  --acid:#e9fc00; --acid-deep:#b3c400;
  --auth:#5b5bd6; --kyc:#c2700a; --ant:#1a7f37; --conta:#0f6f8f; --err:#c53030;
  --f-dis:'IBM Plex Sans','Helvetica Neue',Helvetica,Arial,sans-serif;
  --f-body:'Inter','Helvetica Neue',Helvetica,Arial,sans-serif;
  --f-mono:'IBM Plex Mono',ui-monospace,'SFMono-Regular',Consolas,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ink:#f4f4f0; --ink-2:#d2d2cc; --paper:#101011; --card:#18181a;
    --line:#2b2b2e; --line-2:#242427; --body:#a5a5ac; --mute:#7c7c84;
    --acid-deep:#e9fc00;
    --auth:#9b9bf0; --kyc:#e0a24a; --ant:#5fc27e; --conta:#5ab7d6; --err:#e57373;
  }}
}}
:root[data-theme="dark"] {{
  --ink:#f4f4f0; --ink-2:#d2d2cc; --paper:#101011; --card:#18181a;
  --line:#2b2b2e; --line-2:#242427; --body:#a5a5ac; --mute:#7c7c84;
  --acid-deep:#e9fc00;
  --auth:#9b9bf0; --kyc:#e0a24a; --ant:#5fc27e; --conta:#5ab7d6; --err:#e57373;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--paper); color:var(--ink); font-family:var(--f-body); font-size:15px; line-height:1.6; }}
.shell {{ max-width:1080px; margin:0 auto; padding:0 28px 96px; }}
a {{ color:var(--ink); }}
h1,h2,h3 {{ font-family:var(--f-dis); text-wrap:balance; margin:0; }}
code {{ font-family:var(--f-mono); font-size:0.86em; }}
.kicker {{ font-family:var(--f-mono); font-weight:700; font-size:10px; letter-spacing:.16em; text-transform:uppercase; color:var(--mute); }}

/* ---- topo ---- */
header.hero {{ padding:64px 0 52px; margin-bottom:0; }}
header.hero h1 {{ font-size:clamp(38px,6vw,60px); font-weight:700; letter-spacing:-1.8px; line-height:1.02; margin:16px 0 0; }}
header.hero h1 em {{ font-style:normal; color:var(--acid-deep); }}
.lede {{ max-width:60ch; color:var(--body); font-size:17px; margin:22px 0 0; }}
.facts {{ display:flex; flex-wrap:wrap; gap:0; margin-top:34px; border:1px solid var(--line); border-radius:14px; overflow:hidden; background:var(--card); }}
.fact {{ flex:1 1 168px; padding:16px 20px; border-right:1px solid var(--line-2); }}
.fact:last-child {{ border-right:0; }}
.fact b {{ display:block; font-family:var(--f-dis); font-weight:700; font-size:22px; letter-spacing:-.4px; font-variant-numeric:tabular-nums; }}
.fact span {{ font-family:var(--f-mono); font-size:10px; text-transform:uppercase; letter-spacing:.1em; color:var(--mute); }}

h2.sec {{ display:flex; align-items:baseline; gap:16px; font-family:var(--f-dis); font-weight:700; font-size:clamp(24px,3vw,31px); line-height:1.1; letter-spacing:-.8px; text-transform:none; color:var(--ink); border-bottom:0; padding:0; margin:0 0 28px; }}
h2.sec::before {{ content:counter(sec,decimal-leading-zero); font-family:var(--f-mono); font-weight:700; font-size:12px; letter-spacing:.06em; color:var(--acid-deep); flex:none; }}
.block {{ counter-increment:sec; border-top:2px solid var(--ink); padding-top:30px; margin-bottom:96px; scroll-margin-top:20px; }}
.shell {{ counter-reset:sec; }}

/* ---- anatomia ---- */
.anatomy {{ display:grid; grid-template-columns:minmax(0,380px) minmax(0,1fr); gap:44px; align-items:start; }}
.anatomy ol {{ list-style:none; margin:0; padding:0; counter-reset:an; }}
.anatomy li {{ counter-increment:an; display:grid; grid-template-columns:auto 1fr; gap:4px 16px; padding:16px 0; border-top:1px solid var(--line-2); }}
.anatomy li:first-child {{ border-top:0; padding-top:0; }}
.anatomy li::before {{ content:counter(an,decimal-leading-zero); grid-row:span 3; font-family:var(--f-mono); font-size:11px; font-weight:700; color:var(--acid-deep); padding-top:3px; }}
.an-name {{ font-family:var(--f-dis); font-weight:700; font-size:15px; }}
.an-spec {{ font-family:var(--f-mono); font-size:11px; color:var(--mute); }}
.an-why {{ color:var(--body); font-size:14px; }}

/* ---- etapas ---- */
.stage {{ display:grid; grid-template-columns:minmax(0,300px) minmax(0,1fr); gap:40px; padding:34px 0; border-top:1px solid var(--line); align-items:start; }}
.stage-head h3 {{ font-size:27px; font-weight:700; letter-spacing:-.7px; margin:8px 0 10px; }}
.stage-n {{ font-family:var(--f-mono); font-weight:700; font-size:10px; letter-spacing:.16em; text-transform:uppercase; color:var(--acid-deep); }}
.stage-sub {{ margin:0 0 12px; font-size:15px; color:var(--ink-2); }}
.stage-note {{ margin:0 0 14px; font-size:13.5px; color:var(--body); }}
.stage-count {{ font-family:var(--f-mono); font-size:10px; text-transform:uppercase; letter-spacing:.1em; color:var(--mute); border:1px solid var(--line); border-radius:100px; padding:5px 12px; }}
.tablewrap {{ overflow-x:auto; }}
table.regua {{ width:100%; border-collapse:collapse; font-size:13.5px; }}
table.regua th {{ text-align:left; font-family:var(--f-mono); font-weight:700; font-size:9.5px; text-transform:uppercase; letter-spacing:.12em; color:var(--mute); padding:0 14px 10px 0; border-bottom:1px solid var(--line); }}
table.regua td {{ padding:13px 14px 13px 0; border-bottom:1px solid var(--line-2); vertical-align:top; color:var(--body); }}
.c-id {{ font-family:var(--f-mono); font-weight:700; color:var(--mute); font-variant-numeric:tabular-nums; }}
.c-sub {{ color:var(--ink); font-weight:500; }}
.c-scr code {{ font-size:11.5px; color:var(--ink-2); white-space:nowrap; }}

/* ---- cards de email ---- */
.mails {{ display:grid; gap:26px; grid-template-columns:repeat(auto-fill,minmax(430px,1fr)); }}
.mail {{ background:var(--card); border:1px solid var(--line); border-radius:16px; overflow:hidden; display:flex; flex-direction:column; }}
.mail-head {{ display:grid; grid-template-columns:auto 1fr; gap:16px; padding:20px 22px 18px; }}
.mail-id {{ font-family:var(--f-mono); font-weight:700; font-size:11px; color:var(--acid-deep); padding-top:3px; }}
.mail-meta h3 {{ font-size:16.5px; font-weight:700; letter-spacing:-.3px; margin:0 0 6px; }}
.mail-trigger {{ margin:0 0 10px; font-size:13px; color:var(--body); }}
.mail-tags {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:10px; }}
.tag {{ font-family:var(--f-mono); font-size:9.5px; font-weight:700; text-transform:uppercase; letter-spacing:.09em; padding:4px 9px; border-radius:100px; border:1px solid currentColor; }}
.tag-auth {{ color:var(--auth); }} .tag-kyc {{ color:var(--kyc); }}
.tag-ant {{ color:var(--ant); }} .tag-conta {{ color:var(--conta); }}
.tag-screen {{ color:var(--mute); }}
.mail-pre {{ margin:0 0 10px; font-size:12.5px; color:var(--body); }}
.mail-pre b {{ font-family:var(--f-mono); font-size:9.5px; text-transform:uppercase; letter-spacing:.1em; color:var(--mute); font-weight:700; margin-right:6px; }}
.vars {{ display:flex; flex-wrap:wrap; gap:5px; }}
.vars code {{ font-size:10.5px; color:var(--ink-2); background:var(--line-2); border-radius:5px; padding:3px 6px; }}
.viewport {{ position:relative; height:440px; overflow:hidden; border-top:1px solid var(--line); background:#f4f4f5; }}
.viewport iframe {{ position:absolute; top:0; left:50%; width:648px; height:1000px; border:0; transform:translateX(-50%) scale(.66); transform-origin:top center; }}
.mail.tall .viewport {{ height:560px; }}

/* ---- implementação ---- */
.impl {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:0; border:1px solid var(--line); border-radius:16px; overflow:hidden; background:var(--card); }}
.step {{ padding:24px; border-right:1px solid var(--line-2); border-bottom:1px solid var(--line-2); }}
.step h4 {{ font-family:var(--f-dis); font-size:15.5px; font-weight:700; margin:8px 0 8px; }}
.step p {{ margin:0; font-size:13.5px; color:var(--body); }}
.step .kicker {{ color:var(--acid-deep); }}
.note {{ margin-top:22px; border-left:3px solid var(--err); background:var(--card); border-radius:0 12px 12px 0; padding:18px 22px; }}
.note b {{ font-family:var(--f-mono); font-size:10px; text-transform:uppercase; letter-spacing:.12em; color:var(--err); display:block; margin-bottom:6px; }}
.note p {{ margin:0; font-size:14px; color:var(--body); }}
.files {{ font-family:var(--f-mono); font-size:12.5px; color:var(--body); background:var(--card); border:1px solid var(--line); border-radius:12px; padding:18px 22px; margin-top:24px; overflow-x:auto; white-space:pre; line-height:1.8; }}
footer.end {{ border-top:1px solid var(--line); margin-top:20px; padding-top:26px; font-family:var(--f-mono); font-size:10.5px; text-transform:uppercase; letter-spacing:.1em; color:var(--mute); }}

/* ---- tabela-guia ---- */
table.guide {{ width:100%; border-collapse:collapse; font-size:13.5px; min-width:900px; }}
table.guide thead th {{ text-align:left; font-family:var(--f-mono); font-weight:700; font-size:9.5px; text-transform:uppercase; letter-spacing:.12em; color:var(--mute); padding:0 16px 11px 0; border-bottom:1px solid var(--ink); }}
table.guide thead th.st, table.guide tfoot th.st, table.guide td.st {{ text-align:center; width:104px; padding-right:0; }}
table.guide td {{ padding:14px 16px 14px 0; border-bottom:1px solid var(--line-2); vertical-align:top; color:var(--body); }}
tr.grow th {{ text-align:left; padding:26px 0 9px; border-bottom:1px solid var(--line); }}
tr.grow:first-child th {{ padding-top:8px; }}
.grow-n {{ font-family:var(--f-mono); font-weight:700; font-size:9.5px; letter-spacing:.14em; text-transform:uppercase; color:var(--acid-deep); margin-right:12px; }}
.grow-name {{ font-family:var(--f-dis); font-weight:700; font-size:17px; letter-spacing:-.3px; color:var(--ink); margin-right:12px; }}
.grow-sub {{ font-family:var(--f-body); font-weight:400; font-size:13px; color:var(--mute); }}
.grow-count {{ float:right; font-family:var(--f-mono); font-size:10px; letter-spacing:.08em; color:var(--mute); font-variant-numeric:tabular-nums; }}
.g-name {{ color:var(--ink); font-weight:500; white-space:nowrap; }}
.g-num {{ font-family:var(--f-mono); font-size:10.5px; color:var(--mute); margin-right:9px; font-variant-numeric:tabular-nums; }}
.g-trig {{ max-width:34ch; }}
.g-scr {{ display:block; font-family:var(--f-mono); font-size:10.5px; color:var(--mute); margin-top:4px; }}
.g-pers {{ max-width:30ch; }}
.pers {{ display:inline-block; font-family:var(--f-mono); font-size:9.5px; font-weight:700; text-transform:uppercase; letter-spacing:.09em; padding:3px 9px; border-radius:100px; border:1px solid currentColor; }}
.p-yes {{ color:var(--ant); }}
.p-no {{ color:var(--mute); }}
.pers-why {{ display:block; font-size:12px; color:var(--mute); margin-top:6px; line-height:1.5; }}
.g-link a {{ font-family:var(--f-mono); font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:var(--ink); text-decoration:none; border-bottom:1px solid var(--acid-deep); padding-bottom:2px; white-space:nowrap; }}
.g-link a:hover {{ background:var(--acid); color:#171717; }}
.g-link a:focus-visible {{ outline:2px solid var(--acid-deep); outline-offset:3px; }}
.mark {{ display:inline-flex; align-items:center; justify-content:center; width:24px; height:24px; border-radius:6px; font-size:12px; font-weight:700; }}
.mark.no {{ color:var(--mute); background:var(--line-2); }}
.mark.yes {{ color:#171717; background:var(--acid); }}
table.guide tfoot th {{ text-align:left; font-family:var(--f-mono); font-size:10px; text-transform:uppercase; letter-spacing:.1em; color:var(--ink); padding:14px 16px 0 0; border-top:1px solid var(--ink); font-variant-numeric:tabular-nums; }}
.legend {{ font-family:var(--f-mono); font-size:10.5px; color:var(--mute); display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin:18px 0 0; }}
.legend .mark {{ width:19px; height:19px; font-size:10px; }}
.mail {{ scroll-margin-top:24px; }}
.mail:target {{ border-color:var(--acid-deep); box-shadow:0 0 0 3px var(--acid); }}


/* ---- dominios de envio ---- */
.doms {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:18px; }}
.dom {{ background:var(--card); border:1px solid var(--line); border-radius:16px; padding:24px; display:flex; flex-direction:column; gap:10px; }}
.dom-role {{ font-family:var(--f-mono); font-weight:700; font-size:9.5px; text-transform:uppercase; letter-spacing:.14em; }}
.dom-1 .dom-role {{ color:var(--conta); }}
.dom-2 .dom-role {{ color:var(--ant); }}
.dom-3 .dom-role {{ color:var(--kyc); }}
.dom-addr {{ font-family:var(--f-dis); font-weight:700; font-size:17px; letter-spacing:-.3px; color:var(--ink); word-break:break-all; }}
.dom-what {{ font-size:13.5px; color:var(--body); margin:0; }}
.dom-rule {{ font-family:var(--f-mono); font-size:11px; line-height:1.6; color:var(--mute); border-top:1px solid var(--line-2); padding-top:10px; margin-top:auto; }}
.dom-3 {{ border-style:dashed; }}

/* ---- em construcao ---- */
.wip {{ border:1px dashed var(--line); border-radius:16px; padding:30px 32px; background:var(--card); }}
.wip-badge {{ display:inline-block; font-family:var(--f-mono); font-weight:700; font-size:9.5px; text-transform:uppercase; letter-spacing:.14em; color:var(--kyc); border:1px solid currentColor; border-radius:100px; padding:5px 12px; margin-bottom:16px; }}
.wip h3 {{ font-family:var(--f-dis); font-weight:700; font-size:24px; letter-spacing:-.6px; margin:0 0 14px; color:var(--ink); }}
.wip p {{ max-width:62ch; font-size:14.5px; color:var(--body); margin:0 0 14px; }}
.wip-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:22px; margin-top:26px; padding-top:24px; border-top:1px solid var(--line-2); }}
.wip-col h4 {{ font-family:var(--f-mono); font-weight:700; font-size:9.5px; text-transform:uppercase; letter-spacing:.14em; color:var(--mute); margin:0 0 12px; }}
.wip-col ul {{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:10px; }}
.wip-col li {{ font-size:13.5px; color:var(--body); padding-left:20px; position:relative; line-height:1.55; }}
.wip-col li::before {{ content:"—"; position:absolute; left:0; color:var(--mute); font-family:var(--f-mono); }}
.wip-col.q li::before {{ content:"?"; color:var(--kyc); font-weight:700; }}
.wip-col li b {{ color:var(--ink); font-weight:600; }}


/* ---- chips das etapas ---- */
.stage-body {{ display:flex; flex-direction:column; gap:16px; }}
.chips {{ display:flex; flex-wrap:wrap; gap:7px; }}
.chip {{ font-family:var(--f-mono); font-size:10.5px; color:var(--ink-2); text-decoration:none; border:1px solid var(--line); border-radius:100px; padding:6px 12px; transition:background .12s,color .12s; }}
.chip:hover {{ background:var(--ink); color:var(--paper); border-color:var(--ink); }}
.chip:focus-visible {{ outline:2px solid var(--acid-deep); outline-offset:2px; }}
.g-sub {{ display:block; font-family:var(--f-body); font-weight:400; font-size:12px; color:var(--mute); margin-top:4px; max-width:26ch; }}

/* ---- workflow: caixas e setas ---- */
.flowwrap {{ overflow-x:auto; padding-bottom:6px; }}
ol.flowmap {{ list-style:none; margin:0; padding:2px; display:flex; align-items:stretch; gap:0; min-width:940px; }}
.fm-step {{ flex:1 1 0; min-width:0; background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px 18px 20px; display:flex; flex-direction:column; gap:9px; }}
.fm-step:first-child {{ border-color:var(--ink); border-width:2px; padding:17px 17px 19px; }}
.fm-step:last-child {{ background:var(--ink); border-color:var(--ink); }}
.fm-step:last-child h4, .fm-step:last-child p {{ color:var(--paper); }}
.fm-step:last-child .fm-owner {{ color:var(--acid); border-color:var(--acid); }}
.fm-step:last-child p code {{ background:rgba(255,255,255,.14); color:var(--paper); }}
.fm-top {{ display:flex; align-items:center; justify-content:space-between; gap:8px; }}
.fm-n {{ font-family:var(--f-mono); font-weight:700; font-size:11px; color:var(--acid-deep); font-variant-numeric:tabular-nums; }}
.fm-owner {{ font-family:var(--f-mono); font-size:8.5px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:var(--mute); border:1px solid var(--line); border-radius:100px; padding:3px 8px; white-space:nowrap; }}
.fm-step h4 {{ font-family:var(--f-dis); font-weight:700; font-size:15px; line-height:1.2; letter-spacing:-.3px; color:var(--ink); margin:0; text-wrap:balance; }}
.fm-step p {{ margin:0; font-size:12.5px; line-height:1.55; color:var(--body); }}
.fm-step p code {{ font-size:11px; background:var(--line-2); border-radius:4px; padding:1px 5px; color:var(--ink-2); }}
.fm-arrow {{ flex:0 0 34px; display:flex; align-items:center; justify-content:center; font-family:var(--f-mono); font-size:17px; color:var(--mute); }}
.flow-title {{ font-family:var(--f-mono); font-weight:700; font-size:9.5px; text-transform:uppercase; letter-spacing:.14em; color:var(--mute); margin:0 0 14px; }}

/* ---- as duas réguas ---- */
table.duas {{ width:100%; border-collapse:collapse; font-size:13.5px; min-width:640px; margin-bottom:38px; }}
table.duas th {{ text-align:left; font-family:var(--f-mono); font-weight:700; font-size:9.5px; text-transform:uppercase; letter-spacing:.12em; color:var(--mute); padding:0 18px 11px 0; border-bottom:1px solid var(--ink); }}
table.duas td {{ padding:16px 18px 16px 0; border-bottom:1px solid var(--line-2); vertical-align:top; color:var(--body); }}
.d-name a {{ font-family:var(--f-dis); font-weight:700; font-size:15px; color:var(--ink); text-decoration:none; border-bottom:1px solid var(--acid-deep); padding-bottom:2px; white-space:nowrap; }}
.d-name a:hover {{ background:var(--acid); color:#171717; }}
.d-name a:focus-visible {{ outline:2px solid var(--acid-deep); outline-offset:3px; }}
.pill-wip {{ display:inline-block; font-family:var(--f-mono); font-size:9.5px; font-weight:700; text-transform:uppercase; letter-spacing:.09em; color:var(--kyc); border:1px dashed currentColor; border-radius:100px; padding:4px 10px; white-space:nowrap; }}
.d-note {{ display:block; font-family:var(--f-mono); font-size:10.5px; color:var(--mute); margin-top:7px; }}
.flow-title {{ font-family:var(--f-mono); font-weight:700; font-size:9.5px; text-transform:uppercase; letter-spacing:.14em; color:var(--mute); margin:0 0 4px; }}

@media (max-width:820px) {{
  .anatomy, .stage {{ grid-template-columns:1fr; gap:24px; }}
  .mails {{ grid-template-columns:1fr; }}
  ol.flowmap {{ flex-direction:column; min-width:0; }}
  .fm-arrow {{ flex:0 0 30px; transform:rotate(90deg); }}
  .g-trig, .g-pers {{ max-width:none; }}
}}
</style>

<div class="shell">
<header class="hero">
  <div class="kicker">ANTI · Guideline · v1 · set 2026</div>
  <h1>Guideline das<br><em>réguas de comunicação</em>.</h1>
  <p class="lede">De qual domínio sai cada mensagem, por qual caminho ela é aprovada, como ela é construída e em que ponto da jornada ela dispara. No centro, dezoito emails de serviço — um para cada mudança de estado que o app já comunica na Central de Notificações. Mesmo gatilho, mesma taxonomia, mesmo texto: o email é a versão do aviso que sobrevive fora do app, na caixa de entrada do cedente.</p>
  <div class="facts">
    <div class="fact"><b>18</b><span>templates</span></div>
    <div class="fact"><b>4</b><span>etapas da jornada</span></div>
    <div class="fact"><b>1</b><span>layout, oito blocos</span></div>
    <div class="fact"><b>600px</b><span>largura · tabelas</span></div>
    <div class="fact"><b>0</b><span>imagens externas</span></div>
  </div>
</header>

<div class="block">
  <h2 class="sec">Domínios de envio</h2>
  <p class="lede" style="margin:0 0 26px;">Na hora de autenticar os domínios no SendGrid, a separação importa mais do que parece: reputação de entrega é medida por domínio. Se um disparo de marketing for marcado como spam em volume, quem paga a conta é o domínio que mandou o disparo &mdash; e a régua transacional não pode ser esse domínio, porque dela depende o código de acesso que destrava o login.</p>
  <div class="doms">
    <div class="dom dom-1">
      <div class="dom-role">Corporativo &middot; interno</div>
      <div class="dom-addr">@wearedux.com</div>
      <p class="dom-what">O email das pessoas da Dux. Circulação interna, conversa com cliente, jurídico, cobrança, assinatura de contrato.</p>
      <div class="dom-rule">Nunca usado para envio automático nem em massa.</div>
    </div>
    <div class="dom dom-2">
      <div class="dom-role">Transacional &middot; a régua</div>
      <div class="dom-addr">@sejaanti.com.br</div>
      <p class="dom-what">Os dezoito emails deste documento. Tudo que o sistema dispara sozinho a partir de uma mudança de estado: código, KYC, proposta, liquidação, comprovante.</p>
      <div class="dom-rule">É o domínio mais crítico dos três. Nada de marketing passa por aqui.</div>
    </div>
    <div class="dom dom-3">
      <div class="dom-role">Marketing &middot; a definir</div>
      <div class="dom-addr">@mkt.sejaanti.com.br</div>
      <p class="dom-what">Campanha, novidade de produto, conteúdo, reengajamento. Subdomínio proposto, ainda não decidido.</p>
      <div class="dom-rule">Subdomínio próprio justamente para não sujar o transacional.</div>
    </div>
  </div>
  <div class="note" style="border-left-color:var(--conta);"><b>Ao configurar no SendGrid</b><p>Autentique cada domínio separadamente, e mantenha o marketing em subuser e IP próprios. O grupo de descadastro (<i>unsubscribe group</i>) existe só no marketing: email de serviço não pode cair no mesmo opt-out, porque enquanto a conta estiver ativa o cliente precisa receber o aviso de documento rejeitado e o comprovante de transferência. O <code>Reply-To</code> da régua transacional aponta para uma caixa monitorada de verdade &mdash; nada de <code>no-reply</code> que devolve bounce.</p></div>
</div>

{workflow_block}
<div class="block">
  <h2 class="sec">O layout</h2>
  <div class="anatomy">
    <div class="viewport" style="height:640px;border:1px solid var(--line);border-radius:14px;border-top:1px solid var(--line);">
      <iframe title="Anatomia do template" srcdoc="{html.escape(fill((DIST / '09-proposta-disponivel.html').read_text(encoding='utf-8')), quote=True)}"></iframe>
    </div>
    <ol>{anatomy_rows}</ol>
  </div>
</div>

<div class="block">
  <h2 class="sec">Os tipos de comunicação</h2>
  {"".join(sections)}
</div>

{guide_table}

<div class="block">
  <h2 class="sec">Os dezoito emails</h2>
  <div class="mails">{cards}</div>
</div>

<div class="block">
  <h2 class="sec">Levar para o SendGrid</h2>
  <div class="impl">
    <div class="step"><div class="kicker">Passo 1</div><h4>Um Dynamic Template por arquivo</h4><p>Email API → Dynamic Templates → Create. Cole o HTML no <i>Code Editor</i> (não no Design Editor, que reescreve o markup). O assunto vai no campo Subject, separado do corpo.</p></div>
    <div class="step"><div class="kicker">Passo 2</div><h4>Handlebars, não substitution tags</h4><p>As variáveis já estão no formato <code>{{{{first_name}}}}</code>, que é o dos Dynamic Templates. Cole o JSON de exemplo em <i>Test Data</i> para ver o preview preenchido.</p></div>
    <div class="step"><div class="kicker">Passo 3</div><h4>Disparo pelo backend</h4><p>Cada mudança de estado chama a Mail Send API com o <code>template_id</code> e o objeto <code>dynamic_template_data</code>. O mesmo evento que cria a notificação in-app dispara o email.</p></div>
    <div class="step"><div class="kicker">Passo 4</div><h4>IP e domínio separados</h4><p>Transacional e marketing em subdomínios distintos, com <i>unsubscribe group</i> só no marketing. Emails de serviço não podem cair no mesmo grupo de opt-out da conta ativa.</p></div>
  </div>
  <div class="note"><b>Um ajuste de premissa</b><p>O SendGrid não importa XML. O que ele aceita é HTML colado no editor de código de um Dynamic Template, ou criado via API (<code>POST /v3/templates/{{id}}/versions</code>) com o HTML no corpo do JSON. É por isso que cada email aqui é um arquivo <code>.html</code> autocontido: nada de CSS externo, nada de imagem hospedada, nada de <code>&lt;div&gt;</code> onde cliente antigo precisa de tabela.</p></div>
  <div class="files">anti-comunicacoes/          repositório próprio, fora do código do app
├── build.py                gerador — o copy e a régua moram aqui
├── regua.json              índice: gatilho, tela, assunto, variáveis
├── make_preview.py         gera esta página
├── dist/                   18 HTML autocontidos, prontos para colar no SendGrid
└── testdata/               JSON de exemplo para o campo Test Data</div>
</div>

<div class="block" id="sacado">
  <h2 class="sec">Régua do sacado</h2>
  <div class="wip">
    <span class="wip-badge">Em construção</span>
    <h3>O sacado também vai receber email.</h3>
    <p>Risco sacado é o modelo padrão da operação: a decisão de crédito olha principalmente para quem vai pagar a nota, não para quem a vendeu. É no sacado que mora o risco &mdash; e, em 95% das operações, é o pagamento dele que precisa cair na conta escrow antes de chegar ao cliente.</p>
    <p>Isso faz dele um destinatário de comunicação, não só um nome no cadastro. Só que uma régua para o sacado não é uma extensão desta: ele não tem conta no app, não pediu nada à ANTI, e o que se diz a ele tem peso jurídico sobre o domicílio de pagamento. Merece desenho próprio, com jurídico na mesa.</p>
    <p>O app já prevê os dois primeiros passos desse caminho &mdash; as telas de informar o sacado e de solicitação enviada, e o estado de operação aguardando confirmação. O que falta é a comunicação que sai dali.</p>
    <div class="wip-grid">
      <div class="wip-col">
        <h4>O que provavelmente entra</h4>
        <ul>
          <li><b>Confirmação da operação</b> &mdash; pedido ao sacado para confirmar a nota e o valor</li>
          <li><b>Notificação da cessão</b> &mdash; aviso de que o crédito mudou de titular e de qual passa a ser o domicílio de pagamento</li>
          <li><b>Lembrete de vencimento</b> &mdash; antes da data</li>
          <li><b>Confirmação de pagamento</b> &mdash; recibo depois da liquidação</li>
        </ul>
      </div>
      <div class="wip-col q">
        <h4>O que precisa ser decidido antes</h4>
        <ul>
          <li>Quem assina o email aos olhos do sacado &mdash; ANTI, Dux, ou o próprio cedente</li>
          <li>Qual domínio envia, já que não é o mesmo público da régua do cedente</li>
          <li>Base legal do contato: o sacado nunca deu dado à ANTI</li>
          <li>Se a instrução de pagamento vive no email ou só no boleto e no CNAB</li>
          <li>Se há persistência em algum lugar, já que ele não tem app</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<footer class="end">ANTI · uma empresa DUX · ponto de partida para revisão de copy e jurídico</footer>
</div>
"""
(ROOT / "preview.html").write_text(PAGE, encoding="utf-8")
print("preview.html", len(PAGE), "bytes")
