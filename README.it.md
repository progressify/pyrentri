<img src="https://progressify.dev/img/progressify-logo.png" alt="logo" height="120" align="right" />

# pyrentri

**Un wrapper Python per l'interoperabilità con le API di RENTRI (Registro Elettronico Nazionale per la Tracciabilità dei Rifiuti).**

[![PyPI version](https://img.shields.io/pypi/v/pyrentri.svg)](https://pypi.org/project/pyrentri/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/progressify/pyrentri/graphs/commit-activity)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Paypal Donate](https://img.shields.io/badge/PayPal-Donate%20to%20Author-blue.svg)](https://www.paypal.me/progressify) 
[![Satispay Donate](https://img.shields.io/badge/Satispay-Donate%20to%20Author-red.svg)](https://tag.satispay.com/progressify) 
[![Ask Me Anything !](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg)](https://github.com/progressify/pyrentri/issues)

---

🌐 **Lingue / Languages**: [🇬🇧 Read in English](https://github.com/progressify/pyrentri/blob/master/README.md) | **🇮🇹 Italiano**

---

## ⚠️ Disclaimer Importante & Scopo della Libreria

> **`pyrentri` è uno strumento per la gestione dell'autenticazione e del trasporto HTTP, NON un sostituto della piattaforma ufficiale RENTRI né delle sue specifiche sui dati.**
>
> - **Cosa FA questa libreria**: Automatizza interamente il complesso flusso di sicurezza e crittografia richiesto dalle specifiche RENTRI. Gestisce l'estrazione e il parsing dei certificati `.p12` (PKCS#12) con supporto per chiavi RSA ed Elliptic Curve, la generazione dei token JWT firmati con la catena di certificati (`x5c`), il calcolo del digest SHA-256 dei payload per gli `signed_headers`, e semplifica le chiamate HTTP verso gli endpoint governativi.
> - **Cosa NON FA questa libreria**: Non valida, non costruisce e non altera i payload (es. formulari FIR, movimentazioni del registro cronologico). In qualità di sviluppatore, è tuo compito consultare la [documentazione ufficiale di RENTRI](https://demoapi.rentri.gov.it/docs?page=home#lista-dei-servizi-di-interoperabilit-resi-disponibili-tramite-api) e strutturare i payload JSON delle richieste e processare le relative risposte in piena conformità con gli standard normativi.

---

## 💡 Contesto & Origine del Progetto

Questo progetto nasce dall'esigenza pratica di approfondire e testare sul campo le specifiche tecniche e i flussi di interoperabilità delle API di RENTRI, a supporto delle attività di studio e progettazione di un SDK interno per un cliente.

Il presente wrapper è stato realizzato in totale autonomia come strumento personale di ausilio, prototipazione e collaudo per verificare il funzionamento dei servizi e la corretta interpretazione della documentazione ufficiale. Il codice pubblicato è originale al 100%, è stato ad esclusivo uso personale fino al momento della pubblicazione e non viola alcun accordo di riservatezza o vincolo contrattuale in essere. Viene condiviso con la community open source per semplificare a sviluppatori e aziende la gestione del livello crittografico e di autenticazione governativa.

---

## Caratteristiche

- 🔐 **Gestione Automatica PKCS#12**: Estrazione sicura di chiave privata e certificato X.509 da file `.p12`.
- ⚡ **Riconoscimento Automatico dell'Algoritmo di Firma**: Supporto per chiavi RSA (`RS256`) ed Elliptic Curve (`ES256`).
- 🛡️ **Generazione Token JWT & Digest**: Composizione automatica dell'header `x5c` con il certificato in Base64 e hashing del body con `SHA-256` per l'integrità dei dati.
- 🔄 **Supporto Multi-Ambiente**: Passaggio immediato tra ambiente Demo/Sandbox (`demoapi.rentri.gov.it`) e Produzione (`api.rentri.gov.it`).
- 🔒 **Configurazione Flessibile e Sicura**: Supporto a file `config.ini` e variabile d'ambiente (`P12_PASSWORD`) per l'impiego in container Docker e ambienti cloud.

---

## Installazione

Installazione tramite `pip`:

```bash
pip install pyrentri
```

Oppure aggiungendolo al file `requirements.txt`:

```txt
pyrentri>=0.1.0
```

È inoltre possibile installare l'ultima versione di sviluppo direttamente da GitHub:

```bash
pip install git+https://github.com/progressify/pyrentri.git
```

---

## Configurazione

`pyrentri` legge le credenziali di accesso da un file `config.ini` presente nella cartella di lavoro (o a un percorso personalizzato passato come parametro).

### 1. `config.ini`

Crea un file `config.ini` basandoti sul modello fornito:

```ini
[RENTRI]
sandbox = True
p12_path = ./tuo_certificato.p12
p12_password = tua_password_p12
vat_number = 12345678901
```

- **`sandbox`**: Imposta su `True` per l'ambiente di test/demo (`demoapi.rentri.gov.it`) oppure `False` per l'ambiente di produzione (`api.rentri.gov.it`).
- **`p12_path`**: Percorso al file del certificato PKCS#12 (`.p12`).
- **`p12_password`**: Password di protezione del certificato `.p12`.
- **`vat_number`**: Partita IVA o Codice Fiscale dell'ente/azienda accreditata su RENTRI.

### 2. Variabili d'Ambiente (Consigliato in Produzione e con Docker)

Per evitare di inserire la password in chiaro nel file `config.ini`, puoi impostare la variabile d'ambiente `P12_PASSWORD`. Se presente, avrà la precedenza rispetto alla password indicata nel file INI:

```bash
export P12_PASSWORD="tua_password_sicura"
```

---

## Utilizzo

### 1. Inizializzazione del Client

```python
from pyrentri import RentriWrapper

# Inizializza leggendo config.ini dalla directory corrente
rentri = RentriWrapper()

# È possibile specificare un percorso alternativo:
# rentri = RentriWrapper(config_path="/path/to/config/")
```

### 2. Verifica Stato dei Servizi

Verifica lo stato operativo e la connettività di un servizio RENTRI specifico (es. `formulari`, `anagrafiche`, `dati-registri`):

```python
from pyrentri.rentri_enum import RENTRIStatus

status, response = rentri.status_api("formulari")

if status == RENTRIStatus.OK:
    print("Servizio operativo:", response)
elif status == RENTRIStatus.WARNING:
    print("Avviso sul servizio:", response)
else:
    print("Errore o servizio non disponibile:", response)
```

### 3. Invio Richieste Autenticate (con JWT e Digest del Payload)

Per le richieste che inviano un payload JSON (es. `POST` o `PUT`), le specifiche RENTRI richiedono un JWT firmato contenente il digest SHA-256 del corpo. Usa `create_jwt_token` per generare token e digest, quindi effettua la chiamata:

```python
# 1. Definisci il payload secondo le specifiche ufficiali RENTRI
payload = {
    "num_iscr_sito": "OP2501KCJ031133-NA0001",
    "dati_partenza": {
        # Campi del formulario / movimentazione...
    }
}

# 2. Genera il token JWT firmato e il relativo digest SHA-256
token, digest = rentri.create_jwt_token(content=payload, content_type="application/json")

# 3. Prepara gli header HTTP richiesti
headers = {
    "Authorization": f"Bearer {token}",
    "Agid-JWT-Signature": token,
    "Digest": digest,
    "Content-Type": "application/json",
    "Accept": "application/json, application/problem+json"
}

# 4. Esegui la richiesta POST
response = rentri.post("/formulari/v1.0/creazione", data=payload, headers=headers)
print("Risposta:", response)
```

Allo stesso modo, per richieste `GET` (senza payload):

```python
# Richiesta GET senza payload
token, _ = rentri.create_jwt_token()

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json, application/problem+json"
}

response = rentri.get("/codifiche/v1.0/lookup/nazioni?lang=it", headers=headers)
print("Nazioni:", response)
```

---

## Documentazione & Risorse Ufficiali

- **Documentazione Ufficiale API RENTRI**: [demoapi.rentri.gov.it/docs](https://demoapi.rentri.gov.it/docs?page=home#lista-dei-servizi-di-interoperabilit-resi-disponibili-tramite-api)
- **Portale Ufficiale RENTRI**: [www.rentri.gov.it](https://www.rentri.gov.it)

---

## 💼 Consulenza & Sviluppo Personalizzato

Hai bisogno di integrare le API di RENTRI all'interno del tuo software gestionale, ERP o nella tua infrastruttura aziendale?

Offro supporto tecnico specializzato e servizi di sviluppo su misura:
- Architetture per la gestione asincrona delle trasmissioni massive e monitoraggio degli esiti.
- Gestione della firma digitale e dei certificati in ambienti di produzione e cloud.

📩 **Contattami**: invia un'email a antonio@progressify.dev o visita il sito **[progressify.dev](https://progressify.dev)** per valutare insieme le tue esigenze di integrazione.

---

## Autore & Supporto

Sviluppato con ❤️ da **[Antonio Porcelli (Progressify)](https://progressify.dev)**.

Se questo progetto ti è stato utile o ti ha fatto risparmiare tempo, valuta una donazione per supportarne la manutenzione:

- ☕ [Dona con PayPal](https://www.paypal.me/progressify)
- 💳 [Dona con Satispay](https://tag.satispay.com/progressify)
- 💬 [Apri una Segnalazione / Fai una Domanda](https://github.com/progressify/pyrentri/issues)

---

## Licenza

Questo progetto è rilasciato sotto licenza MIT - consulta il file [LICENSE](LICENSE) per i dettagli.
