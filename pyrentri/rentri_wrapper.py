import base64
import hashlib
import json
import os
import uuid
import warnings
from configparser import ConfigParser
from datetime import datetime, timedelta
from typing import Tuple

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.serialization import pkcs12

from pyrentri.rentri_enum import RENTRIStatus


class RentriWrapper:
    """
    author: Antonio Porcelli
    username: Progressify
    github: https://github.com/progressify
    site: https://progressify.dev    
    ig: https://www.instagram.com/progressify/
    """

    def __init__(self, config_path='./'):
        if os.path.isfile(config_path):
            ini_file = config_path
        else:
            ini_file = os.path.join(config_path, 'config.ini')

        if not os.path.exists(ini_file):
            raise FileNotFoundError(f"File di configurazione non trovato: {ini_file}")

        config = ConfigParser()
        config.read(ini_file)

        if "RENTRI" not in config:
            raise ValueError(f"Sezione [RENTRI] mancante nel file {ini_file}")

        self.sandbox = config.getboolean("RENTRI", "sandbox", fallback=True)
        if self.sandbox:
            self.base_api = "https://demoapi.rentri.gov.it"
            self.audience = "rentrigov.demo.api"
        else:
            self.base_api = "https://api.rentri.gov.it"
            self.audience = "rentrigov.api"

        self.vat_number = config["RENTRI"]["vat_number"]
        self.p12_path = config["RENTRI"]["p12_path"]
        if not os.path.isabs(self.p12_path) and not os.path.exists(self.p12_path):
            alt_p12 = os.path.join(os.path.dirname(ini_file), self.p12_path)
            if os.path.exists(alt_p12):
                self.p12_path = alt_p12

        self.p12_password = os.getenv('P12_PASSWORD', None)
        if self.p12_password is None:
            self.p12_password = config["RENTRI"]["p12_password"]

        # Carica la chiave privata
        self.private_key, self.certificate = self.load_private_key_and_certificate_from_p12()
        # Serializza la chiave privata in formato PEM
        self.serialized_private_key = self.serialize_private_key()
        self.algorithm = self.determine_algorithm()
        self.cert_b64 = self.get_cert_base64()

    def serialize_private_key(self):
        # Serializza la chiave privata in formato PEM
        return self.private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption()
        ).decode('utf-8')

    def load_private_key_and_certificate_from_p12(self):
        # Legge la chiave privata e il certificato dal file P12
        with open(self.p12_path, "rb") as p12_file:
            p12_data = p12_file.read()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                p12_data, self.p12_password.encode(), backend=default_backend()
            )

        if private_key is None or certificate is None:
            raise ValueError("Chiave privata o certificato non trovati nel file P12.")
        return private_key, certificate

    def determine_algorithm(self):
        # Determina il tipo di algoritmo in base alla chiave privata
        if isinstance(self.private_key, rsa.RSAPrivateKey):
            return "RS256"  # Algoritmo per chiavi RSA
        elif isinstance(self.private_key, ec.EllipticCurvePrivateKey):
            return "ES256"  # Algoritmo per chiavi EC
        else:
            raise ValueError("Tipo di chiave non supportato per la firma JWT.")

    def get_cert_base64(self):
        # Serializza il certificato in Base64
        cert_der = self.certificate.public_bytes(Encoding.DER)  # Ottieni il certificato in formato DER
        cert_b64 = base64.b64encode(cert_der).decode('utf-8')  # Codifica in Base64

        return cert_b64

    def create_signature(self, data_to_sign):
        return self.private_key.sign(
            data_to_sign.encode("utf-8"),
            ec.ECDSA(hashes.SHA256())
        )

    def create_jwt_token(self, content: dict = None, content_type: str = None):
        headers = {
            "alg": self.algorithm,
            "typ": "JWT",
            "x5c": [self.cert_b64]
        }

        # Definisci il payload JWT
        datetime_now = datetime.now()
        payload = {
            "iss": self.vat_number,
            "aud": self.audience,
            "jti": str(uuid.uuid4()),
            "iat": int(datetime_now.timestamp()),  # momento di emissione
            "nbf": int(datetime_now.timestamp()),  # valido da subito
            "exp": int((datetime_now + timedelta(days=1)).timestamp())  # scade tra 1 giorno
        }

        digest = None
        if content is not None:
            content_string = json.dumps(content)
            json_sha_256 = hashlib.sha256(content_string.encode('utf-8')).digest()
            json_base_64 = base64.b64encode(json_sha_256).decode('utf-8')
            digest = f"SHA-256={json_base_64}"
            payload["signed_headers"] = {
                "digest": digest,
                "content-type": content_type,
            }

        # Firma il token JWT con la chiave privata serializzata
        jwt_token = jwt.encode(
            payload,
            self.serialized_private_key,
            algorithm=self.algorithm,
            headers=headers
        )

        return jwt_token, digest

    def _validate_headers_for_payload(self, data, headers):
        if data is not None and bool(data):
            if not headers or not any(k.lower() == "agid-jwt-signature" for k in headers.keys()):
                raise ValueError("L'header 'Agid-JWT-Signature' è obbligatorio per richieste con payload.")

    def post(self, endpoint, data=None, headers=None):
        self._validate_headers_for_payload(data, headers)
        url = f"{self.base_api}{endpoint}"
        response = requests.post(url, json=data, headers=headers)
        return response.json()

    def get(self, endpoint, headers=None):
        url = f"{self.base_api}{endpoint}"
        response = requests.get(url, headers=headers)
        return response.json()

    def put(self, endpoint, data=None, headers=None):
        self._validate_headers_for_payload(data, headers)
        url = f"{self.base_api}{endpoint}"
        response = requests.put(url, json=data, headers=headers)
        return response.json()

    def status_api(self, api) -> Tuple[RENTRIStatus, dict]:
        token, _ = self.create_jwt_token()
        api_url = f"{self.base_api}/{api}/v1.0/status"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/problem+json"
        }
        response = requests.get(api_url, headers=headers)
        try:
            payload = response.json()
        except Exception:
            payload = {"error": response.text}

        if response.status_code == 200:
            status = (
                RENTRIStatus.WARNING
                if isinstance(payload, dict) and payload.get("status") == "Warning"
                else RENTRIStatus.OK
            )
            return status, payload
        else:
            return RENTRIStatus.ERROR, payload
