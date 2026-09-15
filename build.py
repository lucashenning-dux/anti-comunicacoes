#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador da régua de emails transacionais do ANTI.

Cada email vira um arquivo HTML standalone em emails/dist/, pronto para
colar no code editor de um Dynamic Template do SendGrid (Handlebars).

Uso:  python3 build.py
"""
import json, os, pathlib, re

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"

# ---------------------------------------------------------------- tokens
INK      = "#171717"
YELLOW   = "#e9fc00"
ZINC     = "#f4f4f5"
WHITE    = "#ffffff"
BODY     = "#52525b"
MUTED    = "#8a8a90"
LINE     = "#e6e6e9"
SUCCESS  = "#1a7f37"
WARNING  = "#c2700a"
ERROR    = "#c53030"

F_TITLE  = "'IBM Plex Sans','Helvetica Neue',Helvetica,Arial,sans-serif"
F_BODY   = "'Inter','Helvetica Neue',Helvetica,Arial,sans-serif"
F_MONO   = "'IBM Plex Mono','SFMono-Regular',Consolas,'Courier New',monospace"

ACCENT = {"neutral": INK, "success": SUCCESS, "warning": WARNING, "error": ERROR}

# ---------------------------------------------------------------- blocos
def eyebrow(text):
    return (f'<div style="font-family:{F_MONO};font-weight:700;font-size:10px;'
            f'line-height:1.4;color:{MUTED};text-transform:uppercase;'
            f'letter-spacing:0.12em;padding-bottom:10px;">{text}</div>')

def title(text):
    return (f'<h1 class="t-title" style="margin:0 0 14px;font-family:{F_TITLE};'
            f'font-weight:700;font-size:26px;line-height:1.25;letter-spacing:-0.5px;'
            f'color:{INK};">{text}</h1>')

def paragraph(text):
    return (f'<p style="margin:0 0 16px;font-family:{F_BODY};font-size:15px;'
            f'line-height:1.65;color:{BODY};">{text}</p>')

def code_box(var, label):
    return f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:8px 0 22px;">
<tr><td align="center" bgcolor="{ZINC}" style="border-radius:16px;padding:26px 20px;">
<div style="font-family:{F_MONO};font-weight:700;font-size:10px;color:{MUTED};text-transform:uppercase;letter-spacing:0.12em;padding-bottom:12px;">{label}</div>
<div style="font-family:{F_MONO};font-weight:700;font-size:34px;line-height:1;letter-spacing:0.22em;color:{INK};">{{{{{var}}}}}</div>
</td></tr></table>"""

def data_rows(rows):
    """rows = [(label, value_html)]"""
    trs = []
    for i, (lbl, val) in enumerate(rows):
        top = f"border-top:1px solid {LINE};" if i else ""
        trs.append(f"""<tr>
<td style="{top}padding:12px 0;font-family:{F_MONO};font-size:11px;line-height:1.4;color:{MUTED};text-transform:uppercase;letter-spacing:0.06em;">{lbl}</td>
<td align="right" style="{top}padding:12px 0;font-family:{F_TITLE};font-weight:700;font-size:14px;line-height:1.4;color:{INK};">{val}</td>
</tr>""")
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            f'border="0" style="margin:4px 0 24px;">' + "".join(trs) + "</table>")

def callout(text, tone="warning", label=None):
    c = ACCENT.get(tone, INK)
    head = (f'<div style="font-family:{F_MONO};font-weight:700;font-size:10px;color:{c};'
            f'text-transform:uppercase;letter-spacing:0.12em;padding-bottom:8px;">{label}</div>') if label else ""
    return f"""<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 24px;">
<tr><td bgcolor="{ZINC}" style="border-radius:12px;border-left:3px solid {c};padding:16px 18px;">
{head}<div style="font-family:{F_BODY};font-size:14px;line-height:1.6;color:{INK};">{text}</div>
</td></tr></table>"""

def button(label, url):
    return f"""<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:4px 0 10px;">
<tr><td align="center" bgcolor="{YELLOW}" style="border-radius:100px;">
<a href="{url}" style="display:inline-block;padding:16px 34px;font-family:{F_TITLE};font-weight:700;font-size:13px;letter-spacing:0.03em;color:{INK};text-decoration:none;border-radius:100px;">{label}</a>
</td></tr></table>"""

def small(text):
    return (f'<p style="margin:14px 0 0;font-family:{F_BODY};font-size:12px;'
            f'line-height:1.6;color:{MUTED};">{text}</p>')

# ---------------------------------------------------------------- shell
def render(e):
    blocks = "\n".join(e["blocks"])
    footer_note = e.get("footer_note",
        "Você recebeu este email porque tem uma conta no ANTI. Emails de serviço como este "
        "não podem ser desativados enquanto sua conta estiver ativa.")
    return f"""<!DOCTYPE html>
<html lang="pt-BR" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="x-apple-disable-message-reformatting">
<meta name="color-scheme" content="light only">
<meta name="supported-color-schemes" content="light only">
<title>{e["subject"]}</title>
<!--[if mso]><style>*{{font-family:Arial,Helvetica,sans-serif !important;}}</style><![endif]-->
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;700&family=IBM+Plex+Mono:wght@400;700&family=Inter:wght@400;600&display=swap');
  body,table,td,a{{-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;}}
  img{{border:0;line-height:100%;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic;}}
  a{{color:{INK};}}
  @media only screen and (max-width:620px){{
    .wrap{{width:100% !important;}}
    .pad{{padding-left:24px !important;padding-right:24px !important;}}
    .t-title{{font-size:22px !important;}}
  }}
</style>
</head>
<body style="margin:0;padding:0;background:{ZINC};">
<div style="display:none;font-size:1px;color:{ZINC};line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;">{e["preheader"]}&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{ZINC}" style="background:{ZINC};">
<tr><td align="center" style="padding:32px 12px;">

<table role="presentation" class="wrap" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:600px;">

  <!-- HEADER -->
  <tr><td bgcolor="{INK}" style="background:{INK};border-radius:20px 20px 0 0;padding:22px 40px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
      <td align="left" style="font-family:{F_TITLE};font-weight:700;font-size:19px;letter-spacing:-0.3px;color:{WHITE};">ANTI<span style="color:{YELLOW};">.</span></td>
      <td align="right" style="font-family:{F_MONO};font-weight:700;font-size:9px;color:rgba(255,255,255,0.45);text-transform:uppercase;letter-spacing:0.14em;">{e["header_tag"]}</td>
    </tr></table>
  </td></tr>

  <!-- CORPO -->
  <tr><td class="pad" bgcolor="{WHITE}" style="background:{WHITE};padding:36px 40px 34px;">
{blocks}
  </td></tr>

  <!-- RODAPE -->
  <tr><td class="pad" bgcolor="{WHITE}" style="background:{WHITE};border-top:1px solid {LINE};border-radius:0 0 20px 20px;padding:26px 40px 30px;">
    <div style="font-family:{F_MONO};font-weight:700;font-size:9px;color:{MUTED};text-transform:uppercase;letter-spacing:0.14em;padding-bottom:10px;">ANTI &middot; UMA EMPRESA DUX</div>
    <div style="font-family:{F_BODY};font-size:11px;line-height:1.7;color:{MUTED};">
      {footer_note}<br><br>
      Precisa de ajuda? Fale com a gente em <a href="mailto:suporte@anti.com.br" style="color:{BODY};text-decoration:underline;">suporte@anti.com.br</a>.<br>
      Nunca pedimos senha, PIN ou código de verificação por email, telefone ou WhatsApp.
    </div>
    <div style="font-family:{F_MONO};font-size:10px;line-height:1.7;color:#b4b4ba;padding-top:14px;">
      {{{{company_legal_name}}}} &middot; {{{{company_address}}}}<br>
      <a href="{{{{preferences_url}}}}" style="color:#b4b4ba;text-decoration:underline;">Preferências de email</a>
    </div>
  </td></tr>

</table>
</td></tr></table>
</body>
</html>
"""

APP = "{{app_url}}"

# ---------------------------------------------------------------- a régua
EMAILS = [
 # ===================== 1. AUTENTICACAO & CONTA =====================
 dict(id="01-codigo-verificacao", group="Autenticação", screen="S1 -> S2",
      trigger="Usuário pede o código de acesso no cadastro ou no login",
      subject="{{code}} é o seu código ANTI",
      preheader="Válido por 10 minutos. Não compartilhe com ninguem.",
      header_tag="Verificação",
      vars=["first_name","code"],
      blocks=[eyebrow("Código de acesso"),
              title("Seu código chegou."),
              paragraph("Use o código abaixo para continuar seu acesso ao ANTI."),
              code_box("code","Código de 6 dígitos"),
              callout("O código expira em 10 minutos e vale para um único acesso. Se não foi você que pediu, ignore este email e troque sua senha.", "warning", "Segurança"),
              small("Nunca compartilhe este código. Nenhum time do ANTI vai pedi-lo.")]),

 dict(id="02-recuperar-senha", group="Autenticação", screen="Login -> S6",
      trigger='Clique em "Esqueci minha senha"',
      subject="Redefinir sua senha do ANTI",
      preheader="Link válido por 30 minutos.",
      header_tag="Segurança",
      vars=["first_name","reset_url","request_ip","request_device"],
      blocks=[eyebrow("Redefinição de senha"),
              title("Vamos criar uma senha nova."),
              paragraph("Olá, {{first_name}}. Recebemos um pedido para redefinir a senha da sua conta ANTI. Clique no botão abaixo para escolher uma nova."),
              button("REDEFINIR SENHA &nbsp;&rarr;","{{reset_url}}"),
              data_rows([("Pedido feito de","{{request_device}}"),("Endereço IP","{{request_ip}}"),("Link válido por","30 minutos")]),
              callout("Se não foi você que pediu, não clique no link. Sua senha atual continua valida e nada muda na sua conta.", "error", "Não pediu isso?"),
              small("O link expira em 30 minutos e pode ser usado uma única vez.")]),

 dict(id="03-senha-alterada", group="Autenticação", screen="S6 / screen-tx-password",
      trigger="Senha de acesso ou senha transacional alterada com sucesso",
      subject="Sua senha do ANTI foi alterada",
      preheader="Se não foi você, fale com o suporte agora.",
      header_tag="Segurança",
      vars=["first_name","changed_at","request_device"],
      blocks=[eyebrow("Alerta de segurança"),
              title("Sua senha foi alterada."),
              paragraph("Olá, {{first_name}}. A senha da sua conta ANTI acabou de ser alterada. Se foi você, está tudo certo e não precisa fazer nada."),
              data_rows([("Alterada em","{{changed_at}}"),("Dispositivo","{{request_device}}")]),
              callout("Se não foi você, sua conta pode estar comprometida. Fale com o suporte imediatamente para bloquear o acesso.", "error", "Não reconhece?"),
              button("FALAR COM O SUPORTE &nbsp;&rarr;", APP + "/suporte")]),

 dict(id="04-boas-vindas", group="Autenticação", screen="Success / T1",
      trigger="Cadastro concluído (empresa + PIN definidos)",
      subject="Bem-vindo ao ANTI, {{first_name}}",
      preheader="Sua conta está criada. Faltam poucos passos para antecipar.",
      header_tag="Boas-vindas",
      vars=["first_name","company_name"],
      blocks=[eyebrow("Conta criada"),
              title("Bem-vindo ao ANTI."),
              paragraph("Olá, {{first_name}}. A conta da <b>{{company_name}}</b> está criada. Agora falta só a verificação de identidade para você começar a antecipar seus recebíveis."),
              data_rows([("Empresa","{{company_name}}"),("Status","Aguardando verificação"),("Próximo passo","Enviar documentos")]),
              button("COMPLETAR VERIFICAÇÃO &nbsp;&rarr;", APP + "/kyc"),
              small("A verificação leva de 1 a 2 dias úteis depois do envio dos documentos.")]),

 # ===================== 2. ONBOARDING & KYC =====================
 dict(id="05-documentos-em-analise", group="KYC", screen="screen-docs-sent",
      trigger="Todos os documentos do KYC enviados",
      subject="Recebemos seus documentos",
      preheader="Análise em até 2 dias úteis. Avisamos por aqui e no app.",
      header_tag="Verificação",
      vars=["first_name","company_name","submitted_at"],
      blocks=[eyebrow("Documentos em análise"),
              title("Recebemos tudo."),
              paragraph("Olá, {{first_name}}. Os documentos da <b>{{company_name}}</b> chegaram e nosso time já está analisando. Você não precisa fazer nada agora."),
              data_rows([("Enviado em","{{submitted_at}}"),("Análise de identidade","1 a 2 dias úteis"),("Conta ativada","Você será avisado")]),
              paragraph("Se faltar alguma informação, avisamos por email e por notificação no app com o que precisa ser reenviado."),
              button("ACOMPANHAR NO APP &nbsp;&rarr;", APP + "/kyc")]),

 dict(id="06-documento-rejeitado", group="KYC", screen="screen-kyc-rejected",
      trigger="Um documento específico foi reprovado na análise",
      subject="Precisamos que você reenvie um documento",
      preheader="{{doc_name}} não foi aprovado. Reenviar leva 2 minutos.",
      header_tag="Ação necessária",
      vars=["first_name","doc_name","reject_reason","company_name"],
      blocks=[eyebrow("Ação necessária"),
              title("Um documento precisa ser reenviado."),
              paragraph("Olá, {{first_name}}. Não conseguimos validar um dos documentos da <b>{{company_name}}</b>. Isso costuma acontecer por qualidade de imagem ou por dados divergentes."),
              data_rows([("Documento","{{doc_name}}"),("Status","Não aprovado")]),
              callout("{{reject_reason}}", "error", "Motivo"),
              button("REENVIAR DOCUMENTO &nbsp;&rarr;", APP + "/kyc"),
              small("Dica: fotografe o documento original em superfície plana, com boa luz, sem flash e sem cortar as bordas.")]),

 dict(id="07-conta-aprovada", group="KYC", screen="screen-upgrade-approved / T1c",
      trigger="KYC aprovado e conta habilitada para transacionar",
      subject="Sua conta ANTI está ativa",
      preheader="Verificação aprovada. Você já pode antecipar.",
      header_tag="Conta ativa",
      vars=["first_name","company_name","credit_limit"],
      blocks=[eyebrow("Verificação aprovada"),
              title("Sua conta está ativa."),
              paragraph("Olá, {{first_name}}. A verificação da <b>{{company_name}}</b> foi aprovada. Sua conta está ativa e você já pode antecipar recebíveis, emitir boletos e movimentar dinheiro."),
              data_rows([("Empresa","{{company_name}}"),("Status","Ativa"),("Limite pré-aprovado","{{credit_limit}}")]),
              button("FAZER MINHA PRIMEIRA ANTECIPAÇÃO &nbsp;&rarr;", APP + "/antecipar"),
              small("O limite pré-aprovado é uma estimativa e pode variar conforme a nota e o sacado de cada operação.")]),

 dict(id="08-convite-representante", group="KYC", screen="screen-invite-rep",
      trigger="Usuário convida o representante legal para concluir a verificação",
      subject="{{inviter_name}} pediu sua verificação no ANTI",
      preheader="Você foi indicado como representante legal da {{company_name}}.",
      header_tag="Convite",
      vars=["rep_name","inviter_name","company_name","invite_url"],
      footer_note=("Você recebeu este email porque foi indicado como representante legal da "
                   "{{company_name}} no ANTI. Se não reconhece este convite, ignore esta mensagem."),
      blocks=[eyebrow("Convite de verificação"),
              title("Sua verificação foi solicitada."),
              paragraph("Olá, {{rep_name}}. <b>{{inviter_name}}</b> indicou você como representante legal da <b>{{company_name}}</b> no ANTI. Para liberar a conta, precisamos verificar sua identidade."),
              data_rows([("Empresa","{{company_name}}"),("Solicitado por","{{inviter_name}}"),("Tempo estimado","3 minutos")]),
              button("VERIFICAR MINHA IDENTIDADE &nbsp;&rarr;","{{invite_url}}"),
              small("Você vai precisar de um documento com foto e do celular em mãos para a selfie.")]),

 # ===================== 3. ANTECIPACAO =====================
 dict(id="09-proposta-disponivel", group="Antecipação", screen="screen-proposal",
      trigger="Proposta gerada e disponível para o cedente aceitar",
      subject="Sua proposta de antecipação está pronta",
      preheader="{{net_amount}} disponiveis. Proposta valida até {{expires_at}}.",
      header_tag="Proposta",
      vars=["first_name","order_id","net_amount","gross_amount","rate","expires_at"],
      blocks=[eyebrow("Proposta disponível"),
              title("Você tem uma proposta."),
              paragraph("Olá, {{first_name}}. Analisamos sua nota e a proposta de antecipação está pronta para sua revisão."),
              data_rows([("Pedido","{{order_id}}"),("Valor da nota","{{gross_amount}}"),("Taxa","{{rate}}"),("Você recebe","{{net_amount}}"),("Válida até́","{{expires_at}}")]),
              button("REVISAR PROPOSTA &nbsp;&rarr;", APP + "/pedidos/{{order_id}}"),
              small("Depois de aceitar, seguimos para a confirmação do sacado. Nada é debitado ou cobrado nesta etapa.")]),

 dict(id="10-contrato-para-assinatura", group="Antecipação", screen="A11 / A12",
      trigger="Proposta aceita, contrato gerado e enviado para assinatura",
      subject="Seu contrato está pronto para assinatura",
      preheader="Assine para liberar a operação {{order_id}}.",
      header_tag="Contrato",
      vars=["first_name","order_id","net_amount","sign_url"],
      blocks=[eyebrow("Assinatura pendente"),
              title("Falta só a sua assinatura."),
              paragraph("Olá, {{first_name}}. O contrato do pedido <b>{{order_id}}</b> foi gerado. Assine digitalmente para que a operação siga para liquidação."),
              data_rows([("Pedido","{{order_id}}"),("Valor a receber","{{net_amount}}"),("Assinatura","Digital, pelo celular")]),
              button("ASSINAR CONTRATO &nbsp;&rarr;","{{sign_url}}"),
              small("O link de assinatura é pessoal. Não encaminhe este email.")]),

 dict(id="11-pedido-em-analise", group="Antecipação", screen="screen-a13-submitted / OT2",
      trigger="Pedido de antecipação enviado e em análise de risco",
      subject="Pedido {{order_id}} em análise",
      preheader="Recebemos seu pedido. Resposta em algumas horas.",
      header_tag="Em análise",
      vars=["first_name","order_id","gross_amount","sacado_name"],
      blocks=[eyebrow("Pedido recebido"),
              title("Estamos analisando seu pedido."),
              paragraph("Olá, {{first_name}}. Seu pedido de antecipação entrou na fila de análise. Avisamos assim que tivermos uma resposta."),
              data_rows([("Pedido","{{order_id}}"),("Sacado","{{sacado_name}}"),("Valor da nota","{{gross_amount}}"),("Status","Em análise")]),
              button("ACOMPANHAR PEDIDO &nbsp;&rarr;", APP + "/pedidos/{{order_id}}")]),

 dict(id="12-aguardando-sacado", group="Antecipação", screen="OT3",
      trigger="Operação aguardando confirmação do sacado",
      subject="Aguardando confirmação do sacado",
      preheader="{{sacado_name}} precisa confirmar a operação {{order_id}}.",
      header_tag="Aguardando",
      vars=["first_name","order_id","sacado_name","sacado_contact"],
      blocks=[eyebrow("Aguardando terceiro"),
              title("Falta a confirmação do sacado."),
              paragraph("Olá, {{first_name}}. Enviamos a solicitação de confirmação para <b>{{sacado_name}}</b>. Assim que ele confirmar, seguimos para o pagamento."),
              data_rows([("Pedido","{{order_id}}"),("Sacado","{{sacado_name}}"),("Contato usado","{{sacado_contact}}"),("Status","Aguardando confirmação")]),
              button("VER STATUS DO PEDIDO &nbsp;&rarr;", APP + "/pedidos/{{order_id}}"),
              small("Se o contato estiver errado, você pode corrigi-lo no app e reenviaremos a solicitação.")]),

 dict(id="13-sacado-confirmou", group="Antecipação", screen="OT3b",
      trigger="Sacado confirmou a operação",
      subject="O sacado confirmou sua operação",
      preheader="{{order_id}} confirmada. Pagamento a caminho.",
      header_tag="Confirmado",
      vars=["first_name","order_id","sacado_name","net_amount","expected_payment"],
      blocks=[eyebrow("Confirmação recebida"),
              title("Sacado confirmou."),
              paragraph("Olá, {{first_name}}. <b>{{sacado_name}}</b> confirmou a operação. Seu pagamento já está na fila de liquidação."),
              data_rows([("Pedido","{{order_id}}"),("Confirmado por","{{sacado_name}}"),("Você recebe","{{net_amount}}"),("Previsão de crédito","{{expected_payment}}")]),
              button("VER PEDIDO &nbsp;&rarr;", APP + "/pedidos/{{order_id}}")]),

 dict(id="14-operacao-liquidada", group="Antecipação", screen="OT4",
      trigger="Pagamento efetivado na conta do cedente",
      subject="Dinheiro na conta: {{net_amount}}",
      preheader="Operação {{order_id}} liquidada com sucesso.",
      header_tag="Liquidada",
      vars=["first_name","order_id","net_amount","paid_at","bank_account"],
      blocks=[eyebrow("Operação liquidada"),
              title("O dinheiro está na sua conta."),
              paragraph("Olá, {{first_name}}. A operação <b>{{order_id}}</b> foi liquidada e o valor já foi creditado."),
              data_rows([("Pedido","{{order_id}}"),("Valor creditado","{{net_amount}}"),("Creditado em","{{paid_at}}"),("Conta de destino","{{bank_account}}")]),
              button("VER COMPROVANTE &nbsp;&rarr;", APP + "/pedidos/{{order_id}}"),
              small("O comprovante completo fica disponível no extrato do app.")]),

 dict(id="15-pedido-cancelado", group="Antecipação", screen="OT5",
      trigger="Pedido cancelado, recusado ou expirado",
      subject="Pedido {{order_id}} cancelado",
      preheader="Entenda o motivo e o que fazer agora.",
      header_tag="Cancelado",
      vars=["first_name","order_id","cancel_reason"],
      blocks=[eyebrow("Pedido encerrado"),
              title("Seu pedido foi cancelado."),
              paragraph("Olá, {{first_name}}. O pedido <b>{{order_id}}</b> foi cancelado e não seguirá para pagamento. Nenhum valor foi debitado."),
              data_rows([("Pedido","{{order_id}}"),("Status","Cancelado")]),
              callout("{{cancel_reason}}", "warning", "Motivo"),
              paragraph("Você pode enviar um novo pedido a qualquer momento, com a mesma nota corrigida ou com outra."),
              button("CRIAR NOVO PEDIDO &nbsp;&rarr;", APP + "/antecipar")]),

 # ===================== 4. CONTA DIGITAL =====================
 dict(id="16-transferencia-enviada", group="Conta", screen="screen-fs2c-success",
      trigger="Transferência (Pix/TED) concluída",
      subject="Comprovante: {{amount}} enviados",
      preheader="Transferência para {{recipient_name}} concluída.",
      header_tag="Comprovante",
      vars=["first_name","amount","recipient_name","recipient_doc","tx_id","paid_at"],
      blocks=[eyebrow("Transferência enviada"),
              title("Transferência concluída."),
              paragraph("Olá, {{first_name}}. Sua transferência foi enviada com sucesso. Guarde este email como comprovante."),
              data_rows([("Valor","{{amount}}"),("Para","{{recipient_name}}"),("CPF/CNPJ","{{recipient_doc}}"),("Data e hora","{{paid_at}}"),("ID da transação","{{tx_id}}")]),
              button("VER NO EXTRATO &nbsp;&rarr;", APP + "/extrato")]),

 dict(id="17-boleto-emitido", group="Conta", screen="FS3",
      trigger="Boleto emitido pelo usuário",
      subject="Boleto emitido: {{amount}}",
      preheader="Vencimento em {{due_date}}. Link para envio ao pagador.",
      header_tag="Boleto",
      vars=["first_name","amount","payer_name","due_date","boleto_url"],
      blocks=[eyebrow("Boleto emitido"),
              title("Seu boleto está pronto."),
              paragraph("Olá, {{first_name}}. O boleto foi emitido e já pode ser enviado ao pagador."),
              data_rows([("Valor","{{amount}}"),("Pagador","{{payer_name}}"),("Vencimento","{{due_date}}")]),
              button("BAIXAR BOLETO &nbsp;&rarr;","{{boleto_url}}"),
              small("O crédito cai na sua conta ANTI em até 1 dia útil após o pagamento.")]),

 dict(id="18-pagamento-falhou", group="Conta", screen="screen-payment-failed",
      trigger="Pagamento ou transferência recusada",
      subject="Não conseguimos concluir seu pagamento",
      preheader="Nenhum valor foi debitado. Veja o motivo.",
      header_tag="Falha",
      vars=["first_name","amount","fail_reason","tx_id"],
      blocks=[eyebrow("Pagamento não concluído"),
              title("O pagamento falhou."),
              paragraph("Olá, {{first_name}}. Não conseguimos concluir seu pagamento. Nenhum valor foi debitado da sua conta."),
              data_rows([("Valor","{{amount}}"),("Tentativa","{{tx_id}}"),("Status","Não concluído")]),
              callout("{{fail_reason}}", "error", "Motivo"),
              button("TENTAR NOVAMENTE &nbsp;&rarr;", APP + "/pagar")]),
]

# ---------------------------------------------------------------- build
def main():
    DIST.mkdir(parents=True, exist_ok=True)
    index = []
    for e in EMAILS:
        (DIST / f'{e["id"]}.html').write_text(render(e), encoding="utf-8")
        index.append({k: e[k] for k in ("id","group","screen","trigger","subject","preheader","vars")})
    (ROOT / "regua.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(EMAILS)} templates -> {DIST}")

if __name__ == "__main__":
    main()
