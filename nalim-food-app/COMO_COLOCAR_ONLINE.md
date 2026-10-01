# NALIM Food Service — Instruções para Colocar Online (Custo R$ 0)

Este projeto foi totalmente preparado para rodar na nuvem em servidores gratuitos com suporte a HTTPS, 4G/5G, múltiplos logins e banco de dados.

---

## 🚀 Opção 1: Publicar no Render.com (Recomendado - 100% Gratuito)

O **Render** permite rodar o FastAPI Python e servir as páginas Web sem custo de hospedagem.

### Passo 1: Criar repositório no GitHub
1. Abra sua conta no [GitHub.com](https://github.com) (se não tiver, crie gratuitamente).
2. Crie um novo repositório chamado `nalim-food-app` (pode ser Público ou Privado).
3. Suba os arquivos desta pasta `nalim-food-app` para o GitHub:
   ```bash
   git init
   git add .
   git commit -m "NALIM Food Service release"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/nalim-food-app.git
   git push -u origin main
   ```

### Passo 2: Conectar ao Render
1. Acesse [render.com](https://render.com) e faça login com seu GitHub.
2. Clique no botão **New +** e selecione **Web Service**.
3. Selecione o repositório `nalim-food-app` que acabou de subir.
4. Preencha as configurações simples:
   - **Name:** `nalim-gestao` (ou o nome que preferir)
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free` (R$ 0)
5. Clique em **Create Web Service**.

🎉 **Pronto!** Em 2 a 3 minutos você receberá um link público seguro com cadeado HTTPS:
`https://nalim-gestao.onrender.com`

---

## 📱 Como usar nos celulares dos Garçons (4G / 5G)
1. No celular do garçom (Android ou iPhone), abra o navegador e acerte:
   `https://nalim-gestao.onrender.com/garcom`
2. No menu do Chrome ou Safari, clique em:
   **"Adicionar à tela inicial"** ou **"Instalar Aplicativo"**.
3. O ícone do NALIM ficará salvo na tela do celular como se fosse um app da Play Store!
4. O garçom faz login com `operador@nalim.com.br` e senha `operador123`. Ele **nunca** terá acesso a lucro, DRE, custos ou faturamento.

---

## 💻 Como acessar a Gestão (Dono & Gerente)
- Acesse `https://nalim-gestao.onrender.com` em qualquer notebook ou computador.
- Faça login com seu perfil:
  - **Dono:** `dono@nalim.com.br` / `dono123` (Acesso completo a DRE, Lucro Real, Margem, iFood).
  - **Gerente:** `gerente@nalim.com.br` / `gerente123` (Gestão operacional, fichas e insumos).
