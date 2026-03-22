# Two-Factor Authentication (TOTP) — User Guide

Machinaris supports optional two-factor authentication using TOTP (Time-based One-Time Password). This is the same technology used by Google Authenticator, Microsoft Authenticator, Authy, 1Password, and other authenticator apps.

## Overview

- **Single user** — no usernames or passwords. Just a 6-digit code from your authenticator app.
- **Optional** — if you don't set it up, Machinaris works exactly as before with no authentication.
- **7-day sessions** — once you log in, you stay authenticated for 7 days before needing to re-enter a code.
- **Web UI only** — authentication protects the browser-facing dashboard (port 8926). Internal API traffic between controller and worker containers (port 8927) is unaffected.

## Setup

### Step 1: Open the Setup Page

After updating to a version with TOTP support, you'll see an info banner on every page:

> **Security:** Two-factor authentication is not set up. **Set it up now** to protect your Machinaris dashboard.

Click "Set it up now" or navigate directly to `/auth/setup`.

### Step 2: Scan the QR Code

Open your authenticator app and scan the QR code displayed on the setup page. If you can't scan, manually enter the text key shown below the QR code.

**Recommended authenticator apps:**
- Google Authenticator (Android / iOS)
- Microsoft Authenticator (Android / iOS)
- Authy (Android / iOS / Desktop)
- 1Password (all platforms)

### Step 3: Enter the Verification Code

Your authenticator app will show a 6-digit code that refreshes every 30 seconds. Enter the current code and click "Activate Authentication."

### Step 4: Save Your Backup Key

**Important:** Before closing the setup page, save a copy of the manual key (the text string shown below the QR code). Store it somewhere safe — you'll need it if you ever lose access to your authenticator app.

## Daily Usage

After setup, navigating to any Machinaris page will redirect you to the login screen if your session has expired. Enter the current 6-digit code from your authenticator app and you're in.

Sessions last **7 days**. You won't need to re-authenticate unless:
- 7 days have passed since your last login
- You click "Logout" from the About menu
- The container restarts (only on the very first restart after a fresh install — subsequent restarts preserve your session key)

## Logging Out

Click the **About** dropdown in the sidebar, then click **Logout**. This ends your session immediately.

## What Is Protected

| Access Path | Protected? | Notes |
|---|---|---|
| Browser to Web UI (port 8926) | Yes | All pages except the landing splash and initial Chia setup |
| Controller-Worker API (port 8927) | No | Internal container traffic, not browser-accessible |
| Chia RPC (port 8555) | No | Controlled by Chia's own certificate auth |

## Lockout Recovery

If you lose access to your authenticator app and don't have the backup key:

### Option 1: Unraid Terminal

1. Open the Unraid web UI
2. Click on the Machinaris container
3. Click "Console"
4. Run: `rm /root/.chia/machinaris/config/totp_secret.json`
5. Refresh Machinaris in your browser — authentication is now disabled
6. Set up TOTP again with your new authenticator

### Option 2: Docker Exec

```bash
docker exec -it machinaris rm /root/.chia/machinaris/config/totp_secret.json
```

Then refresh your browser and re-enroll.

### Option 3: Direct File Access

The TOTP secret file is stored on the persistent Docker volume at:
```
/root/.chia/machinaris/config/totp_secret.json
```

On Unraid, this maps to your appdata share. Navigate to:
```
/mnt/user/appdata/machinaris/config/totp_secret.json
```

Delete the file and refresh your browser.

## Disabling Authentication

To permanently disable TOTP authentication, delete the secret file using any of the methods in "Lockout Recovery" above. As long as `totp_secret.json` does not exist, the app runs without authentication.

## Re-enrolling / Changing Authenticator

If you want to switch to a different authenticator app or device:

1. Log in with your current authenticator
2. Navigate to `/auth/setup`
3. Scan the new QR code with your new authenticator app
4. Enter the verification code to confirm
5. The old authenticator is automatically invalidated (the secret changes)

## Security Considerations

- **TOTP codes are time-based** — your container's clock must be reasonably accurate (within ~30 seconds of real time). Docker containers inherit the host's clock, so this is usually fine.
- **The secret file** (`totp_secret.json`) is stored with `600` permissions (owner-read-only). Anyone with root access inside the container can read it — this is inherent to how TOTP works (the server must know the shared secret).
- **Network eavesdropping** — TOTP protects against unauthorized access, but Machinaris serves HTTP by default (not HTTPS). If you access it over an untrusted network, consider putting it behind a reverse proxy with TLS (e.g., Nginx Proxy Manager, Caddy, or Traefik).
- **Brute force** — TOTP codes are 6 digits (1 million possibilities) and rotate every 30 seconds. The valid window is +/- 1 step (90 seconds), making brute force impractical. No rate limiting is implemented since the attack window is inherently narrow.
- **CSRF protection** — the login form is protected by CSRF tokens (Flask-WTF), preventing cross-site login attacks.
