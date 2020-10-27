from os import cpu_count

# Listen on all interfaces
bind = "0.0.0.0:8000"

# Allows for multi-threaded request processing
workers = cpu_count() * 2 + 1

# Allow for faster server restarts
reuse_port = True
