from os import cpu_count
from isis_server import Config

LOG_FMT = "[%(asctime)s][%(levelname)s][%(name)s] %(message)s"
LOG_DATE_FMT = "%F %T"

logconfig_dict = {
    # This prevents duplicate logs
    "root": {
        "level": "INFO",
        "handlers": []
    },
    # This configures logging
    "level": Config.app.log_level,
    "formatters": {
        "generic": {
            "format": LOG_FMT,
            "datefmt": LOG_DATE_FMT
        }
    }
}

# Listen on all interfaces
bind = "0.0.0.0:{}".format(Config.app.port)

# Allows for multi-core request processing
#workers = cpu_count() * 2 + 1

# Use a single worker for testing
workers = 1

# Allow for faster server restarts
reuse_port = True

# Disable timeouts, we deal with a lot of big files
timeout = 0
