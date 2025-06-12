import passkeys


AUTH_USER_MODEL = "authentication.User"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]


# Passkeys
FIDO_SERVER_ID = (
    "localhost"  # Server rp id for FIDO2, it the full domain of your project
)
FIDO_SERVER_NAME = "TestApp"
KEY_ATTACHMENT = [
    None,
    passkeys.Attachment.CROSS_PLATFORM,
    passkeys.Attachment.PLATFORM,
]
