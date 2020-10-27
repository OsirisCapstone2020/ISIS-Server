from threading import Thread
from werkzeug.serving import make_server

from pytest import fixture

from isis_server import app

DEV_SERVER_HOST = "127.0.0.1"
DEV_SERVER_PORT = 8001
DEV_SERVER_ADDR = "http://{}:{}".format(DEV_SERVER_HOST, DEV_SERVER_PORT)


def stop_dev_server(server, server_thread):
    server.shutdown()
    server_thread.join()


@fixture
def start_dev_server(request):
    server = make_server(DEV_SERVER_HOST, DEV_SERVER_PORT, app)
    server_thread = Thread(target=server.serve_forever)
    server_thread.start()
    request.addfinalizer(lambda: stop_dev_server(server, server_thread))
