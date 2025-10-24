# 🚀 Guida Deploy PCOS Care WebApp su GitHub Pages

## ✨ Nuove Feature Aggiunte

### Backend API
- ✅ **Autenticazione JWT** con login/registro
- ✅ **Gestione utenti** con email, username, password (bcrypt)
- ✅ **API Keys personalizzate** per Anthropic Claude e OpenAI
- ✅ **Chatbot AI conversazionale** con integrazione RAG
- ✅ **CORS** configurato per GitHub Pages

### Frontend React
- ✅ **Login/Register pages** con design PCOS-themed bellissimo
- ✅ **Dashboard** con overview sistema
- ✅ **Chat Page** - Chatbot AI conversazionale user-friendly
- ✅ **Settings Page** - Gestione account e API keys
- ✅ **Protected Routes** con redirect automatico
- ✅ **AuthContext** per gestione stato globale
- ✅ Tracciamento Sintomi, Cicli, Analytics, Knowledge Base

## 📝 Step-by-Step Deploy

### 1. Preparazione Repository

Se non hai ancora il repository su GitHub:

```bash
cd /Users/paolinamazza/pcos-care-mcp

# Inizializza git (se non già fatto)
git init
git add .
git commit -m "feat: add complete webapp with auth and AI chatbot"

# Crea repository su GitHub (vai su github.com)
# Poi collega:
git remote add origin https://github.com/paolinamazza/pcos-care-mcp.git
git branch -M main
git push -u origin main
```

### 2. Configurare GitHub Pages

1. **Vai su GitHub** → tuo repository `pcos-care-mcp`

2. **Settings** → **Pages** (nella sidebar sinistra)

3. **Source**: Seleziona "GitHub Actions"
   - NON selezionare "Deploy from branch"
   - Deve essere "GitHub Actions"

4. **Salva** (se richiesto)

### 3. Push del Workflow

Il file `.github/workflows/deploy.yml` è già stato creato.

Quando fai push, GitHub Actions si attiverà automaticamente:

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: add GitHub Pages deploy workflow"
git push
```

### 4. Verificare il Deploy

1. Vai su **Actions** tab nel tuo repository
2. Vedrai il workflow "Deploy to GitHub Pages" in esecuzione
3. Aspetta che completi (circa 1-2 minuti)
4. La webapp sarà disponibile su:

```
https://paolinamazza.github.io/pcos-care-mcp/
```

### 5. Backend Setup (Importante!)

⚠️ **ATTENZIONE**: GitHub Pages ospita solo file statici (frontend).
Il backend API deve essere ospitato separatamente.

#### Opzione A: Backend Locale (per sviluppo)

```bash
cd /Users/paolinamazza/pcos-care-mcp/webapp/api
python main.py
```

Il backend sarà su `http://localhost:8000`

**Limitazione**: Solo tu puoi usare la webapp, perché il backend è sul tuo computer.

#### Opzione B: Deploy Backend su Cloud (per produzione)

Opzioni consigliate:

**1. Railway.app** (Facile, free tier disponibile)
```bash
# Installa Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
cd /Users/paolinamazza/pcos-care-mcp
railway init
railway up
```

**2. Render.com** (Free tier, ottimo per Python)
- Vai su render.com
- New → Web Service
- Connetti GitHub repo
- Settings:
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `cd webapp/api && python main.py`
  - Environment: Python 3

**3. Fly.io** (Free tier, veloce)
```bash
# Installa flyctl
brew install flyctl  # macOS

# Login e deploy
fly launch
fly deploy
```

#### Opzione C: Backend su VPS (per controllo completo)

Provider raccomandati:
- DigitalOcean Droplet ($4/mese)
- Linode ($5/mese)
- Hetzner (€4/mese)

Setup:
```bash
# SSH nel server
ssh root@your-server-ip

# Installa dipendenze
apt update
apt install python3 python3-pip nginx certbot

# Clone repo
git clone https://github.com/paolinamazza/pcos-care-mcp.git
cd pcos-care-mcp
pip3 install -r requirements.txt

# Setup systemd service
# (crea /etc/systemd/system/pcos-api.service)

# Setup nginx reverse proxy
# (crea /etc/nginx/sites-available/pcos-api)

# SSL con Let's Encrypt
certbot --nginx -d api.yourdomain.com
```

### 6. Collegare Frontend a Backend

Una volta che hai il backend online, aggiorna il frontend:

```javascript
// webapp/frontend/src/services/api.js
const API_BASE_URL = 'https://your-backend-url.com';  // Cambia questo
```

Poi rebuild e redeploy:

```bash
cd webapp/frontend
npm run build
git add .
git commit -m "feat: connect to production backend"
git push
```

GitHub Actions farà il deploy automaticamente!

## 🔐 Configurazione CORS Backend

Se hai il backend su un dominio diverso, aggiorna il CORS:

```python
# webapp/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Dev locale
        "https://paolinamazza.github.io",  # GitHub Pages
        "https://your-custom-domain.com",  # Se hai un dominio personalizzato
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📱 Uso della WebApp

### Per Utenti

1. **Vai su**: https://paolinamazza.github.io/pcos-care-mcp/

2. **Registrati**:
   - Email
   - Username
   - Password
   - (opzionale) Nome completo

3. **Configura API Keys**:
   - Vai su Settings (icona utente in alto a destra)
   - Aggiungi la tua Anthropic API key O OpenAI API key
   - Ottieni le keys da:
     - Anthropic: https://console.anthropic.com/settings/keys
     - OpenAI: https://platform.openai.com/api-keys

4. **Usa il Chatbot**:
   - Vai su "💬 AI Chat"
   - Attiva "📚 Usa Knowledge Base (RAG)" per avere risposte basate sui 28 PDF
   - Filtra per categoria se vuoi informazioni specifiche
   - Chatta normalmente!

5. **Traccia Sintomi e Cicli**:
   - Registra sintomi con intensità
   - Traccia cicli mestruali
   - Visualizza analytics e pattern

## 🔧 Troubleshooting

### La webapp non si carica

- Controlla che il workflow sia completato (tab Actions)
- Verifica che GitHub Pages sia configurato su "GitHub Actions"
- Aspetta qualche minuto dopo il deploy (cache DNS)

### Errore "API not available"

- Il backend non è raggiungibile
- Controlla che il backend sia online
- Verifica l'URL in `src/services/api.js`
- Controlla CORS nel backend

### Login non funziona

- Verifica che il backend sia online
- Controlla console browser (F12) per errori
- Verifica che CORS sia configurato correttamente

### Chatbot dice "No API keys"

- Vai su Settings
- Aggiungi almeno una API key (Anthropic o OpenAI)
- Salva

## 📊 Monitoraggio

### Backend Logs

Se usi Railway/Render/Fly:
```bash
# Railway
railway logs

# Render
# Vai sul dashboard → Logs

# Fly
fly logs
```

### Frontend Analytics

Aggiungi Google Analytics (opzionale):

```html
<!-- webapp/frontend/index.html, dentro <head> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-YOUR-ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-YOUR-ID');
</script>
```

## 🎨 Personalizzazione

### Cambiare il nome del repository

Se vuoi un URL più carino:

1. Rinomina il repository su GitHub in `pcos-care` (senza -mcp)
2. Aggiorna `vite.config.js`:
```javascript
base: '/pcos-care/',  // Nuovo nome
```
3. Push

La webapp sarà su: `https://paolinamazza.github.io/pcos-care/`

### Dominio Personalizzato

1. Compra un dominio (es: `pcos-care.com` su Namecheap/Google Domains)
2. GitHub Pages Settings → Custom domain: `pcos-care.com`
3. Configura DNS:
   - Type: A
   - Name: @
   - Value: 185.199.108.153 (e gli altri IP di GitHub)
4. Aspetta propagazione DNS (max 24h)

## 🚀 Deploy Completo - Checklist

- [ ] Repository su GitHub creato
- [ ] GitHub Pages configurato su "GitHub Actions"
- [ ] Workflow `.github/workflows/deploy.yml` pushato
- [ ] Build completato con successo (tab Actions)
- [ ] Frontend accessibile su `https://paolinamazza.github.io/pcos-care-mcp/`
- [ ] Backend deployato su cloud (Railway/Render/Fly/VPS)
- [ ] CORS configurato con URL frontend
- [ ] Frontend collegato a backend (API_BASE_URL aggiornato)
- [ ] Test registrazione utente
- [ ] Test login
- [ ] Test configurazione API keys
- [ ] Test chatbot AI
- [ ] Test tracciamento sintomi/cicli

## 🎉 Congratulazioni!

Hai deployato con successo PCOS Care WebApp!

La tua webapp include:
- 🔐 Autenticazione sicura con JWT
- 🤖 Chatbot AI con Claude/GPT
- 📚 Knowledge Base RAG con 28 PDF scientifici
- 📊 Analytics avanzate
- 🎨 Design PCOS-themed bellissimo
- 📱 Responsive mobile-friendly

Condividi il link con le persone che potrebbero trovarlo utile!

---

Per supporto o domande, apri una issue su GitHub.
