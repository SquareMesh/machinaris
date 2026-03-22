import io
import json
import logging
import os

import pyotp
import qrcode

TOTP_CONFIG_PATH = '/root/.chia/machinaris/config/totp_secret.json'

app_logger = logging.getLogger('gunicorn.error')

def is_configured():
    """Check if TOTP has been set up."""
    return os.path.exists(TOTP_CONFIG_PATH)

def generate_secret():
    """Generate a new TOTP secret (does not save it)."""
    return pyotp.random_base32()

def save_secret(secret):
    """Save the TOTP secret to persistent config."""
    os.makedirs(os.path.dirname(TOTP_CONFIG_PATH), exist_ok=True)
    with open(TOTP_CONFIG_PATH, 'w') as f:
        json.dump({'secret': secret}, f)
    os.chmod(TOTP_CONFIG_PATH, 0o600)
    app_logger.info("TOTP secret saved to %s", TOTP_CONFIG_PATH)

def load_secret():
    """Load the TOTP secret from persistent config. Returns None if not configured."""
    try:
        with open(TOTP_CONFIG_PATH, 'r') as f:
            return json.load(f)['secret']
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return None

def remove_secret():
    """Remove the TOTP secret file (disables authentication)."""
    try:
        os.remove(TOTP_CONFIG_PATH)
        app_logger.info("TOTP secret removed from %s", TOTP_CONFIG_PATH)
    except FileNotFoundError:
        pass

def get_provisioning_uri(secret, issuer='Machinaris'):
    """Generate the otpauth:// URI for authenticator app enrollment."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name='admin', issuer_name=issuer)

def generate_qr_code_base64(secret):
    """Generate a QR code as a base64-encoded PNG for embedding in HTML."""
    import base64
    uri = get_provisioning_uri(secret)
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('ascii')

def verify_code(code):
    """Verify a TOTP code against the saved secret. Returns True if valid."""
    secret = load_secret()
    if not secret:
        return False
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)
