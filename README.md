<img src="https://progressify.dev/img/progressify-logo.png" alt="logo" height="120" align="right" />

# pyrentri

**A lightweight Python wrapper for the Italian RENTRI API (Registro Elettronico Nazionale per la Tracciabilità dei Rifiuti).**

[![PyPI version](https://img.shields.io/pypi/v/pyrentri.svg)](https://pypi.org/project/pyrentri/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/progressify/pyrentri/graphs/commit-activity)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Paypal Donate](https://img.shields.io/badge/PayPal-Donate%20to%20Author-blue.svg)](https://www.paypal.me/progressify) 
[![Satispay Donate](https://img.shields.io/badge/Satispay-Donate%20to%20Author-red.svg)](https://tag.satispay.com/progressify) 
[![Ask Me Anything !](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg)](https://github.com/progressify/pyrentri/issues)

---

🌐 **Languages / Lingue**: **🇬🇧 English** | [🇮🇹 Leggi in Italiano](https://github.com/progressify/pyrentri/blob/master/README.it.md)

---

## ⚠️ Important Disclaimer & Library Scope

> **`pyrentri` is an authentication and transport bridge, NOT a replacement for the official RENTRI platform or its data specifications.**
>
> - **What this library DOES**: It automates the complex security and cryptographic workflow required by RENTRI. It handles `.p12` (PKCS#12) certificate parsing (RSA and Elliptic Curve), generates signed JWT tokens with certificate chains (`x5c`), computes SHA-256 payload digests for `signed_headers`, and simplifies HTTP communication.
> - **What this library DOES NOT do**: It does **not** validate, construct, or alter business payloads (e.g., FIR forms, waste registry movements). As a developer, you must consult the [official RENTRI documentation](https://demoapi.rentri.gov.it/docs?page=home#lista-dei-servizi-di-interoperabilit-resi-disponibili-tramite-api) and build the request JSON payloads and process responses according to official regulatory standards.

---

## 💡 Background & Origin

This project originated from the practical need to explore, test, and validate the technical specifications and interoperability flows of the RENTRI APIs while supporting a client in designing their internal corporate SDK.

This wrapper was developed independently as a personal sandbox and testing tool to verify API behaviors and the proper interpretation of the official documentation. The open-sourced code is 100% original, served solely for personal aid until its public release, and does not violate any non-disclosure agreements or existing contractual obligations. It is shared with the community to help other developers bypass the initial complexity of RENTRI's cryptographic and authentication layer.

---

## Features

- 🔐 **Automated PKCS#12 Handling**: Reads private keys and X.509 certificates from `.p12` files.
- ⚡ **Auto-detect Signature Algorithm**: Supports both RSA (`RS256`) and Elliptic Curve (`ES256`) keys.
- 🛡️ **JWT & Digest Generation**: Formats tokens with the certificate chain (`x5c`) and automatically hashes payload bodies (`SHA-256` digest).
- 🔄 **Multi-Environment**: Seamlessly switch between Demo/Sandbox (`demoapi.rentri.gov.it`) and Production (`api.rentri.gov.it`).
- 🔒 **Secure Configuration**: Supports `config.ini` and environment variables (`P12_PASSWORD`) for Docker and cloud deployments.

---

## Installation

Install using `pip`:

```bash
pip install pyrentri
```

Or add it to your `requirements.txt`:

```txt
pyrentri>=0.1.0
```

You can also install the latest development version directly from GitHub:

```bash
pip install git+https://github.com/progressify/pyrentri.git
```

---

## Configuration

`pyrentri` reads its configuration from a `config.ini` file located in your project directory (or a custom path passed to the constructor).

### 1. `config.ini`

Create a `config.ini` file based on the provided template:

```ini
[RENTRI]
sandbox = True
p12_path = ./your_certificate.p12
p12_password = your_p12_password
vat_number = 12345678901
```

- **`sandbox`**: Set to `True` for the demo/testing environment (`demoapi.rentri.gov.it`) or `False` for production (`api.rentri.gov.it`).
- **`p12_path`**: Path to your PKCS#12 certificate file (`.p12`).
- **`p12_password`**: Password for your `.p12` file.
- **`vat_number`**: Fiscal code / VAT number associated with the RENTRI accreditation.

### 2. Environment Variables (Recommended for Production & Docker)

To avoid storing passwords in plain text inside `config.ini`, you can set the `P12_PASSWORD` environment variable. If set, it will override the password defined in the INI file:

```bash
export P12_PASSWORD="your_secure_password"
```

---

## Usage

### 1. Initialize the Wrapper

```python
from pyrentri import RentriWrapper

# Reads config.ini from the current directory
rentri = RentriWrapper()
```

### 2. Check Service Status

Verify connection and operational status of a specific RENTRI API service (e.g. `formulari`, `anagrafiche`, `dati-registri`):

```python
from pyrentri.rentri_enum import RENTRIStatus

status, response = rentri.status_api("formulari")

if status == RENTRIStatus.OK:
    print("Service is operational:", response)
elif status == RENTRIStatus.WARNING:
    print("Service warning:", response)
else:
    print("Service error or unavailable:", response)
```

### 3. Send Authenticated Requests (with JWT & Payload Digest)

When sending requests with a JSON body, RENTRI requires a signed JWT containing a SHA-256 digest of the payload. Use `create_jwt_token` to generate the token and digest, then send the request:

```python
# 1. Define your business payload according to the official RENTRI specifications
payload = {
    "num_iscr_sito": "OP2501KCJ031133-NA0001",
    "dati_partenza": {
        # Your form/movement fields here...
    }
}

# 2. Generate signed JWT token and SHA-256 digest
token, digest = rentri.create_jwt_token(content=payload, content_type="application/json")

# 3. Prepare headers
headers = {
    "Authorization": f"Bearer {token}",
    "Agid-JWT-Signature": token,
    "Digest": digest,
    "Content-Type": "application/json",
    "Accept": "application/json, application/problem+json"
}

# 4. Perform the POST request
response = rentri.post("/formulari/v1.0/creazione", data=payload, headers=headers)
print("Response:", response)
```

Similarly, for `GET` requests:

```python
# GET request without payload
token, _ = rentri.create_jwt_token()

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json, application/problem+json"
}

response = rentri.get("/codifiche/v1.0/lookup/nazioni?lang=it", headers=headers)
print("Nazioni:", response)
```

---

## Documentation & Official Resources

- **Official RENTRI API Docs**: [demoapi.rentri.gov.it/docs](https://demoapi.rentri.gov.it/docs?page=home#lista-dei-servizi-di-interoperabilit-resi-disponibili-tramite-api)
- **Official RENTRI Portal**: [www.rentri.gov.it](https://www.rentri.gov.it)

---

## 💼 Commercial Support & Consulting

Need to integrate the RENTRI APIs into your corporate ERP, custom software, or cloud infrastructure?

I offer specialized technical consulting and tailored development services:
- Robust architectures for asynchronous batch transmissions and status polling.
- Secure certificate management and digital signature pipelines in cloud and on-premise environments.

📩 **Get in touch**: send an email to antonio@progressify.dev or visit **[progressify.dev](https://progressify.dev)** to discuss your integration needs.

---

## Author & Support

Developed with ❤️ by **[Antonio Porcelli (Progressify)](https://progressify.dev)**.

If this project helps you or saves you time, please consider supporting its maintenance:

- ☕ [Donate via PayPal](https://www.paypal.me/progressify)
- 💳 [Donate via Satispay](https://tag.satispay.com/progressify)
- 💬 [Open an Issue / Ask a Question](https://github.com/progressify/pyrentri/issues)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

