# NALIM Food Service — Manual Master SaaS & Como Colocar Online

Este documento contém o guia definitivo para hospedar a plataforma **NALIM Gestão**, configurar seu domínio próprio **`NALIMGESTAO.COM.BR`** e operar a empresa como um software SaaS (venda de assinaturas para restaurantes).

---

## 🌐 1. Estrutura de URLs Oficiais (Domínio: nalimgestao.com.br)

Todo o ecossistema agora roda sob a marca e domínio oficial:

| Canal | URL Oficial | Para Quem |
|---|---|---|
| **Painel Master SuperAdmin** | `https://nalimgestao.com.br/admin` | **Natanael (Você)**: Cadastro de clientes, controle de mensalidades, métricas MRR e acesso 1-clique a qualquer restaurante. |
| **Login Geral** | `https://nalimgestao.com.br/login` | Portal de entrada para donos de restaurantes, gerentes e operadores. |
| **Painel de Gestão do Cliente** | `https://nalimgestao.com.br/app` | Dashboard de DRE, Fichas Técnicas, Fluxo de Caixa, CMV e KDS da loja autenticada. |
| **App Garçom Mobile (PWA)** | `https://nalimgestao.com.br/garcom` | Garçons registram pedidos nas mesas e recebem push notification de pedido pronto. |
| **Cardápio Digital / QR Code Mesa** | `https://nalimgestao.com.br/cardapio?tenant={slug}` | Clientes da mesa escaneiam o QR Code para ver fotos, preços e pedir no WhatsApp do restaurante. |

---

## 🔑 2. Acesso do SuperAdmin Master

- **URL:** `https://nalimgestao.com.br/admin` (ou acesse `https://nalimgestao.com.br/login`)
- **E-mail:** `admin@nalimgestao.com.br`
- **Senha Padrão:** `nalim2026master`

> O sistema identifica automaticamente sua credencial Master e abre o **Dashboard SaaS**. Donos de restaurantes comuns não conseguem acessar esta rota (recebem 403 Proibido).

---

## 🏢 3. Como Cadastrar um Novo Restaurante Cliente (Passo a Passo)

1. Entre em `https://nalimgestao.com.br/admin` com sua conta Master.
2. Clique no botão verde **"+ Novo Restaurante"**.
3. Preencha os dados do cliente:
   - **Nome do Restaurante:** Ex.: *Pizzaria Bella Napoli*
   - **Slug do Cardápio:** Ex.: `bella-napoli` (gerado automaticamente)
   - **Responsável / Dono:** Ex.: *Marco Antônio*
   - **WhatsApp:** Ex.: *(11) 98888-7777*
   - **E-mail do Dono:** Ex.: `marco@bellanapoli.com.br`
   - **Senha de Acesso:** Defina uma senha inicial (ex.: `napoli123`)
   - **Plano:** Selecione *Starter (R$ 99)*, *Pro (R$ 199)* ou *Enterprise (R$ 349)*
   - **Dia de Vencimento:** Ex.: dia 10
   - **Clonar Cardápio Modelo:** Deixe marcado para o cliente já iniciar com itens e fichas técnicas cadastradas como exemplo!
4. Clique em **"Salvar e Ativar Cliente"**.
5. **Pronto!** O restaurante é criado instantaneamente com banco de dados 100% isolado.
6. Na listagem de clientes:
   - Clique em **"Acessar"** (ícone de chave): você entra no painel do restaurante imediatamente sem precisar da senha dele!
   - Clique no ícone de **Compartilhar (WhatsApp)**: copia uma mensagem de boas-vindas formatada para enviar direto no WhatsApp do dono com todos os links prontos.

---

## 🔒 4. Como Funciona o Isolamento Multi-Tenant (Segurança)

- **Separação de Dados:** Cada restaurante possui um identificador único (`tenant_id`).
- Todas as operações (Cardápio, Pedidos, Mesas, Clientes, Insumos, Fichas Técnicas, Custos Fixos, Fechamentos de Caixa e DRE) são filtradas no banco de dados pelo `tenant_id` do usuário conectado via token JWT seguro.
- **Garantia de Sigilo:** O Restaurante A **nunca** consegue visualizar ou alterar os dados do Restaurante B.
- **Cardápio Público:** Ao acessar `cardapio.html?tenant=bella-napoli`, o sistema carrega apenas os produtos, fotos, categorias e o número de WhatsApp cadastrados para a *Bella Napoli*.

---

## 🚀 5. Como Configurar o Domínio NALIMGESTAO.COM.BR no Render

O Render oferece hospedagem com certificado SSL (HTTPS) gratuito automático.

### Passo 1: Subir o projeto para o GitHub
Se ainda não subiu o código atualizado:
```bash
git add .
git commit -m "NALIM SaaS Multi-tenant e Dominio nalimgestao.com.br"
git push origin main
```

### Passo 2: Criar o Serviço Web no Render
1. Acesse [render.com](https://render.com) e faça login.
2. Clique em **New +** > **Web Service**.
3. Selecione o repositório do GitHub `nalim-food-app`.
4. Configure:
   - **Name:** `nalimgestao`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free` (ou Starter $7/mês para não entrar em repouso quando você tiver vários clientes ativos).
5. Em **Environment Variables**, adicione (necessário para o Web Push do Garçom):
   - `VAPID_PUBLIC_KEY` = (sua chave pública VAPID)
   - `VAPID_PRIVATE_KEY` = (sua chave privada VAPID)
   - `VAPID_EMAIL` = `contato@nalimgestao.com.br`
6. Clique em **Deploy Web Service**.

### Passo 3: Configurar o Domínio no Render
1. No menu lateral do seu Web Service no Render, clique em **Settings**.
2. Role até a seção **Custom Domains** e clique em **Add Custom Domain**.
3. Digite: `nalimgestao.com.br` e depois adicione também `www.nalimgestao.com.br`.
4. O Render exibirá as entradas DNS que você deve cadastrar no Registro.br.

### Passo 4: Apontar o DNS no Registro.br
1. Acesse [registro.br](https://registro.br) e entre na sua conta.
2. Clique no domínio **`nalimgestao.com.br`**.
3. Role até **DNS** e clique em **Alterar Servidores DNS** ou **Configurar Zona DNS**.
4. Crie os seguintes apontamentos (conforme indicado pelo Render):
   - **Tipo A:**
     - Nome: `@` (ou em branco)
     - Dados/IP: `216.24.57.1` (verifique o IP exato que o Render indicar na tela)
   - **Tipo CNAME:**
     - Nome: `www`
     - Dados: `nalimgestao.onrender.com.` (o endereço do seu app no Render)
5. Salve as alterações.
6. A propagação leva de 15 minutos a algumas horas. Assim que propagar, o Render emitirá o certificado SSL (cadeado verde) e `https://nalimgestao.com.br` estará no ar!

---

## 💼 6. Tabela de Planos e Preços Recomendados

| Recurso | Plano STARTER | Plano PRO (Mais vendido) | Plano ENTERPRISE |
|---|:---:|:---:|:---:|
| **Preço Sugerido** | **R$ 99/mês** | **R$ 199/mês** | **R$ 349/mês** |
| Pedidos Balcão & Mesas | Sim | Sim | Sim |
| Cardápio Digital QR Code | Sim | Sim | Sim |
| Controle de Caixa Básico | Sim | Sim | Sim |
| App do Garçom (PWA Celular) | Até 2 garçons | Ilimitado | Ilimitado |
| Notificações Web Push | Não | Sim | Sim |
| KDS Cozinha em Tempo Real | Não | Sim | Sim |
| Fichas Técnicas & CMV Real | Não | Sim | Sim |
| DRE Gerencial & Saúde Financeira | Básico | Completo | Completo |
| Integração Webhook iFood | Não | Opcional | Sim |
| Suporte & Treinamento | E-mail/Ticket | WhatsApp Comercial | WhatsApp Dedicado + Consultoria |

---

## 🎯 7. Script de Onboarding do Primeiro Cliente

Ao fechar com um restaurante:
1. Abra seu painel Master (`nalimgestao.com.br/admin`).
2. Cadastre o restaurante em 30 segundos.
3. Copie a mensagem do WhatsApp gerada pelo botão de compartilhamento.
4. Envie para o dono:
   > *"Olá [Nome], seu sistema NALIM Gestão já está liberado! Acesse seu painel em https://nalimgestao.com.br/login com o e-mail cadastrado. Para seus garçons, basta abrir https://nalimgestao.com.br/garcom no celular e fixar na tela inicial. Qualquer dúvida, estou à disposição!"*
5. Se o cliente precisar de ajuda no primeiro dia, entre no seu painel Master, clique em **"Acessar"** ao lado do restaurante dele e configure as mesas e produtos para ele em tempo real!
