# TOTP Authentication with pyotp and qrcode

**Category:** tools
**Relevance:** CONFIGURATION.md §6 (Security), web UI authentication
**Date researched:** 2026-03-22

## Summary
pyotp implements RFC 6238 TOTP (Time-based One-Time Password) for authenticator app integration. qrcode generates QR codes for enrollment. Both are pure Python with no C extensions, making them trivial to add to Docker builds.

## Key Findings
- `pyotp.random_base32()` generates a 32-character base32 secret (160 bits of entropy)
- `pyotp.TOTP(secret).verify(code, valid_window=1)` validates codes with ±1 step tolerance (90 seconds total)
- `totp.provisioning_uri(name, issuer_name)` generates the `otpauth://` URI that authenticator apps understand
- `qrcode.make(uri)` generates a PIL image from any string
- `qrcode[pil]` extra installs Pillow for PNG output; without it, only SVG is available
- Flask's `Markup` is from markupsafe (already a Flask dependency), so no new dependency for that

## Code Example
```python
import pyotp
import qrcode

secret = pyotp.random_base32()
totp = pyotp.TOTP(secret)
uri = totp.provisioning_uri(name='admin', issuer_name='Machinaris')
qr = qrcode.make(uri)  # PIL Image

# Verify a 6-digit code
is_valid = totp.verify('123456', valid_window=1)
```

## Decision / Recommendation
Use pyotp + qrcode for TOTP auth. Lightweight, well-maintained, pure Python. No alternatives were seriously considered — these are the standard libraries for this purpose.

## Sources
- pyotp: https://pypi.org/project/pyotp/
- qrcode: https://pypi.org/project/qrcode/
