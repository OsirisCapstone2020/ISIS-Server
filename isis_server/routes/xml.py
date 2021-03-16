from flask import jsonify, make_response, current_app


def get_all_commands():
    return jsonify(current_app.isis_commands)


def get_command(command_name):
    for command in current_app.isis_commands:
        if command["name"] == command_name:
            return jsonify(command)

    return make_response(jsonify(), 404)
