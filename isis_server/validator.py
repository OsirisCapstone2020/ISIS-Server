from isis_server.isis import CMD_LOWPASS

VALID_COMMANDS = [
    CMD_LOWPASS
]

REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "cmd": {
            "type": "string",
            "enum": VALID_COMMANDS,
        },
        "args": {
            "type": "array",
            "items": {"type": "string"}
        },
        "input_file": {"type": "string"}
    },
    "required": ["cmd", "args", "input_file"],
    "additionalProperties": False
}
