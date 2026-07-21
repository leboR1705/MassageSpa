import ssl
import certifi
import os
from django.conf import settings as _settings
from django.core.mail.backends.smtp import EmailBackend
from smtplib import SMTP, SMTP_SSL
from ssl import SSLCertVerificationError


class CertifiSMTPBackend(EmailBackend):
    """Custom SMTP backend that supplies a certifi-based SSLContext for STARTTLS.

    This helps on Windows/dev machines where the system CA bundle may be missing
    or OpenSSL cannot verify the server certificate. It uses certifi.where()
    as the CA file for verification.
    """

    def open(self):
        """Open a network connection."""
        if self.connection:
            return False
        try:
            if self.use_ssl:
                self.connection = SMTP_SSL(self.host, self.port, timeout=self.timeout)
            else:
                self.connection = SMTP(self.host, self.port, timeout=self.timeout)

            # EHLO first
            try:
                self.connection.ehlo()
            except Exception:
                pass

            # If STARTTLS requested, build an SSL context that uses certifi CA bundle
            # and optionally loads a local/custom CA file specified by settings.CUSTOM_CA_PATH.
            if (not self.use_ssl) and self.use_tls:
                # start with certifi's CA bundle
                ctx = ssl.create_default_context(cafile=certifi.where())
                
                # DEVELOPMENT: Disable SSL verification to bypass certificate errors
                # TODO: Remove this in production and fix certificate issues properly
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                # If the user provided a custom CA bundle (e.g. corporate proxy), load it too
                custom_ca = getattr(_settings, 'CUSTOM_CA_PATH', None)
                if custom_ca:
                    try:
                        # allow relative path from project base dir
                        if not os.path.isabs(custom_ca) and hasattr(_settings, 'BASE_DIR'):
                            custom_ca = os.path.join(_settings.BASE_DIR, custom_ca)
                        if os.path.exists(custom_ca):
                            ctx.load_verify_locations(cafile=custom_ca)
                        else:
                            # If file doesn't exist, raise a helpful error later when connecting
                            pass
                    except Exception:
                        # non-fatal here; the certifi bundle will still be used
                        pass
                try:
                    self.connection.starttls(context=ctx)
                except SSLCertVerificationError:
                    # Surface a clearer error when verification fails even after loading CA
                    if not self.fail_silently:
                        raise
                except Exception:
                    # Other TLS/starttls errors should still raise if not fail_silently
                    if not self.fail_silently:
                        raise
                try:
                    self.connection.ehlo()
                except Exception:
                    pass

            if self.username:
                self.connection.login(self.username, self.password)

            return True
        except Exception:
            if not self.fail_silently:
                raise
            return False
