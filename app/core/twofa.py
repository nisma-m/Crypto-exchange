import pyotp


def generate_2fa_secret():

    return pyotp.random_base32()


def get_qr_uri(email: str, secret: str):

    totp = pyotp.TOTP(secret)

    return totp.provisioning_uri(
        name=email,
        issuer_name="CryptoExchange"
    )


def verify_2fa(secret: str, code: str):

    totp = pyotp.TOTP(secret)

    return totp.verify(code)