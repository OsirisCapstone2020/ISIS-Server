import dotenv
from os import getenv
from logging import getLevelName

dotenv.load_dotenv()


def check_env_exists(env_var: str) -> str:
    """
    Checks that the given environment variable is defined.
    Throws an error if it doesn't.
    """
    val = getenv(env_var)
    if val is None:
        raise RuntimeError("'{}' is not set!".format(env_var))
    return val


class _AppConfig:
    """
    Class representing the app's core config
    """

    _ENV_APP_PORT = "APP_PORT"
    _ENV_APP_LOG_LEVEL = "APP_LOG_LEVEL"

    _ENV_SMTP_SERVER = "APP_SMTP_SERVER"
    _ENV_SMTP_PORT = "APP_SMTP_PORT"
    _ENV_SMTP_USER = "APP_SMTP_USERNAME"
    _ENV_SMTP_PASSWORD = "APP_SMTP_PASSWORD"

    _DEFAULT_APP_PORT = "8080"
    _DEFAULT_LOG_LEVEL = "info"
    _DEFAULT_SMTP_PORT = "587"

    port = int(getenv(_ENV_APP_PORT, _DEFAULT_APP_PORT))
    log_level = getLevelName(
        getenv(_ENV_APP_LOG_LEVEL, _DEFAULT_LOG_LEVEL).upper()
    )

    smtp_server = getenv(_ENV_SMTP_SERVER)
    smtp_port = getenv(_ENV_SMTP_PORT, _DEFAULT_SMTP_PORT)
    smtp_username = getenv(_ENV_SMTP_USER)
    smtp_password = getenv(_ENV_SMTP_PASSWORD)


class _S3Config:
    """
    Class representing the app's S3 config based on environment variables
    """

    _ENV_S3_SERVER = "S3_SERVER"
    _ENV_S3_BUCKET = "S3_BUCKET"
    _ENV_S3_ACCESS_KEY = "S3_ACCESS_KEY"
    _ENV_S3_SECRET_KEY = "S3_SECRET_KEY"

    server = check_env_exists(_ENV_S3_SERVER)
    bucket = check_env_exists(_ENV_S3_BUCKET)
    access_key = check_env_exists(_ENV_S3_ACCESS_KEY)
    secret_key = check_env_exists(_ENV_S3_SECRET_KEY)


class Config:
    """
    Class representing the ISIS server's configuration based on environment
    variables
    """
    app = _AppConfig
    s3 = _S3Config
