from datetime import timedelta

from flask import Blueprint, render_template, redirect, url_for, request, session, flash, current_app
from flask_babel import _

from common.utils import totp

auth_bp = Blueprint('auth', __name__)

# Routes that never require authentication
PUBLIC_ENDPOINTS = {
    'landing.landing',
    'setup.setup',
    'auth.login',
    'auth.setup_totp',
    'auth.logout',
    'static',
}


def is_authenticated():
    """Check if the current session is authenticated."""
    return session.get('totp_authenticated', False)


@auth_bp.before_app_request
def require_authentication():
    """Protect all web UI routes with TOTP authentication."""
    # Skip if TOTP is not configured — app runs unauthenticated (backwards compatible)
    if not totp.is_configured():
        return

    # Allow public endpoints
    if request.endpoint in PUBLIC_ENDPOINTS:
        return

    # Allow already authenticated sessions
    if is_authenticated():
        return

    # Redirect to login
    return redirect(url_for('auth.login', next=request.path))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If TOTP isn't configured, redirect to setup
    if not totp.is_configured():
        return redirect(url_for('auth.setup_totp'))

    # If already authenticated, go to the requested page
    if is_authenticated():
        next_url = request.args.get('next', url_for('index.index'))
        return redirect(next_url)

    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        if totp.verify_code(code):
            session['totp_authenticated'] = True
            session.permanent = True
            current_app.logger.info("TOTP authentication successful")
            next_url = request.form.get('next', url_for('index.index'))
            return redirect(next_url)
        else:
            current_app.logger.warning("TOTP authentication failed — invalid code")
            flash(_('Invalid authentication code. Please try again.'), 'danger')

    return render_template('auth/login.html', next=request.args.get('next', ''))


@auth_bp.route('/auth/setup', methods=['GET', 'POST'])
def setup_totp():
    # If TOTP is already configured, only allow access if authenticated
    if totp.is_configured():
        if not is_authenticated():
            return redirect(url_for('auth.login'))
        # Allow re-enrollment: authenticated user can reset TOTP

    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        secret = request.form.get('secret', '')

        if not secret:
            flash(_('Setup error. Please try again.'), 'danger')
            return redirect(url_for('auth.setup_totp'))

        # Verify the code against the pending secret before saving
        import pyotp
        pending_totp = pyotp.TOTP(secret)
        if pending_totp.verify(code, valid_window=1):
            totp.save_secret(secret)
            session['totp_authenticated'] = True
            session.permanent = True
            current_app.logger.info("TOTP setup completed successfully")
            flash(_('Two-factor authentication has been set up successfully.'), 'success')
            return redirect(url_for('index.index'))
        else:
            flash(_('Invalid code. Please scan the QR code again and enter the current 6-digit code.'), 'danger')
            # Re-render with the same secret so the QR code stays stable
            qr_base64 = totp.generate_qr_code_base64(secret)
            return render_template('auth/setup_totp.html', secret=secret, qr_base64=qr_base64)

    # GET — generate a new secret and show the QR code
    secret = totp.generate_secret()
    qr_base64 = totp.generate_qr_code_base64(secret)
    return render_template('auth/setup_totp.html', secret=secret, qr_base64=qr_base64)


@auth_bp.route('/logout')
def logout():
    session.pop('totp_authenticated', None)
    flash(_('You have been logged out.'), 'success')
    return redirect(url_for('auth.login'))
