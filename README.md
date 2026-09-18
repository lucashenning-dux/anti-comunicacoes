# ANTI · Guideline das Regras de Comunicação

Régua de emails transacionais do ANTI: o copy, o layout e as regras de quando cada
mensagem dispara. Dezoito emails de serviço, um para cada mudança de estado que o
aplicativo já comunica na Central de Notificações.

Este repositório é a fonte de verdade do **conteúdo** das comunicações. Ele não é
código do aplicativo e não sobe junto com ele — os templates vivem no SendGrid, que
tem ciclo de publicação próprio. Uma mudança de texto aqui não exige release do app.

## Começando

Não há dependências. Python 3 e mais nada.

```bash
python3 build.py          # regenera os 18 HTML em dist/
python3 make_preview.py   # regenera preview.html
```

Abra `preview.html` no navegador para ver a régua completa, os gatilhos, o status de
implementação de cada email e os dezoito layouts renderizados com dados de exemplo.

## Estrutura

```
build.py          gerador — o copy, os gatilhos e a régua moram aqui
regua.json        índice gerado: gatilho, tela, assunto, preheader, variáveis
make_preview.py   gera a página de revisão
preview.html      página de revisão (gerada)
dist/             18 HTML autocontidos, prontos para colar no SendGrid (gerado)
testdata/         JSON de exemplo para o campo Test Data do SendGrid
```

`dist/` é gerado, mas está versionado de propósito: é o arquivo que a pessoa copia e
cola no SendGrid, e ter o diff dele no histórico mostra exatamente o que mudou em cada
template a cada alteração de copy.

## Alterando o texto de um email

Todo o conteúdo mora na lista `EMAILS` em `build.py` — um dicionário por email, com
assunto, preheader, gatilho, tela correspondente no app e os blocos do corpo. Edite
ali e rode `python3 build.py`. Nunca edite os arquivos em `dist/` à mão: eles são
sobrescritos no build seguinte.

Os blocos disponíveis para montar um corpo são funções no topo do `build.py`:
`eyebrow`, `title`, `paragraph`, `code_box`, `data_rows`, `callout`, `button` e
`small`. Compor um email novo é escrever uma entrada na lista usando esses blocos —
não é escrever HTML.

## Publicando no SendGrid

1. Email API › Dynamic Templates › **Create**.
2. Abra o **Code Editor** — não o Design Editor, que reescreve o markup ao salvar.
3. Cole o arquivo de `dist/` inteiro, do `<!DOCTYPE html>` ao `</html>`.
4. O assunto vai no campo **Subject**, separado do corpo. Ele está em `regua.json`.
5. Cole o JSON de `testdata/` no painel **Test Data** para ver o preview preenchido.
6. O backend dispara pela Mail Send API com o `template_id` e o objeto
   `dynamic_template_data`. O mesmo evento que cria a notificação no app manda o email.

As variáveis estão em Handlebars (`{{first_name}}`), que é o formato dos Dynamic
Templates — não as substitution tags antigas do SendGrid.

## Workflow

Cinco passos, com dono em cada um. A ordem existe para que nenhuma comunicação chegue
ao cliente sem revisão de texto, e para que o HTML tenha uma origem só.

1. **Solicitação** (Dux) — o pedido da comunicação, dizendo em que etapa da jornada
   ela entra e o que precisa dizer.
2. **Materialização no Figma** (Claude) — vira layout, com variáveis à mostra e com
   dados de teste.
3. **Revisão interna do texto** (Dux) — o time aprova o copy contra a etapa da jornada.
4. **Exportação para o SendGrid** (Dux) — o HTML sai de `dist/`, não do Figma, e vai
   para o Code Editor de um Dynamic Template. Cada comunicação ganha um `template_id`.
5. **Disparo por chamada de API** (backend) — no evento, o backend chama a Mail Send
   API com o `template_id` e os parâmetros em `dynamic_template_data`.

A via de volta é o Event Webhook: o SendGrid chama nosso endpoint a cada entrega,
abertura, bounce ou marcação de spam. É o que diz se a régua está funcionando.

## Domínios de envio

Reputação de entrega é medida por domínio, então os três públicos ficam separados na
configuração do SendGrid:

| Domínio | Uso | Regra |
|---|---|---|
| `@wearedux.com` | email corporativo das pessoas da Dux | nunca envia automático nem em massa |
| `@sejaanti.com.br` | a régua transacional deste repositório | nada de marketing passa por aqui |
| `@mkt.sejaanti.com.br` | email marketing (subdomínio proposto, a definir) | subuser e IP próprios |

O transacional é o domínio mais crítico dos três: é dele que sai o código de acesso
que destrava o login. Se um disparo de marketing for marcado como spam em volume,
quem paga é o domínio que enviou — por isso o marketing mora num subdomínio à parte.

O grupo de descadastro existe só no marketing. Email de serviço não entra no mesmo
opt-out: enquanto a conta estiver ativa, o cliente precisa receber o aviso de
documento rejeitado e o comprovante de transferência.

## Regras de layout

Elas não são preferência estética; são o que sobrevive ao Outlook, que renderiza com
o motor do Word.

- **Tabelas para estrutura.** Nada de `div` posicionada, flexbox ou grid.
- **Estilo inline no elemento.** O único `<style>` no `<head>` existe para a media
  query, que é a única regra que não dá para inlinear.
- **Nenhum arquivo externo.** Sem CSS separado, sem imagem hospedada. Cliente de email
  não busca recurso externo: o Gmail remove `<link>` e o Outlook o ignora.
- **600px de largura**, com fallback para 100% abaixo de 620px.
- **Fonte com pilha de fallback real.** Gmail e Outlook não carregam webfont; o email
  chega em Helvetica ou Arial, e o layout precisa se manter assim.

Por isso o HTML não sai de exportação de ferramenta de design. O Figma serve para
decidir o layout; o arquivo nasce aqui.

## Onde cada email se encaixa

| Seção | Emails |
|---|---|
| Autenticação | código de acesso, redefinição de senha, senha alterada, boas-vindas |
| KYC | documentos em análise, documento rejeitado, conta aprovada, convite ao representante |
| Antecipação | proposta, contrato, pedido em análise, aguardando sacado, sacado confirmou, liquidada, cancelado |
| Conta | transferência enviada, boleto emitido, pagamento recusado |

A tabela completa — com gatilho, tela do app, persistência na Central de Notificações
e status de implementação — está em `preview.html`.

## Pendências

- **Nenhum template está implementado.** O placar em `preview.html` está zerado nas
  duas colunas (implementada e em produção). O status mora no dicionário `STATUS` em
  `make_preview.py`.
- **Subdomínio de marketing não decidido.** `mkt.sejaanti.com.br` é proposta, não
  decisão. O corporativo e o transacional já estão definidos.
- **Régua do sacado em construção.** O sacado é onde mora o risco da operação e o
  pagamento dele passa pela conta escrow, o que faz dele destinatário de comunicação
  — com peso jurídico sobre o domicílio de pagamento. A régua ainda não existe; o que
  se sabe e o que precisa ser decidido está em `preview.html`.
- **`testdata/` cobre só o email 04.** Os demais precisam do JSON de exemplo.
- **Idioma único.** O copy está em PT-BR; o app é bilíngue. Falta decidir se o email
  segue o idioma do perfil.
