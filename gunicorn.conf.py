from os import cpu_count
from isis_server import Config

# Listen on all interfaces
bind = "0.0.0.0:{}".format(Config.app.port)

# Allows for multi-threaded request processing
#workers = cpu_count() * 2 + 1

# Use a single worker for testing
workers = 1

# Allow for faster server restarts
reuse_port = True
