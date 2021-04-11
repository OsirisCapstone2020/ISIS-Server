from typing import Dict

from pysis.exceptions import ProcessError

from isis_server.ISISRequest import ISISInputFile
from pysis import IsisPool
from copy import deepcopy
from multiprocessing import Lock
from .logger import get_logger


class ISISCommand:
    def __init__(self, command_name, extra_args: Dict[str, str] = None, disable_to_arg=False):
        self._command_name = command_name
        self._disable_to_arg = disable_to_arg
        self._logger = get_logger(command_name)
        if extra_args is None:
            self._extra_args = dict()
        else:
            self._extra_args = extra_args

    def run(self, *files: ISISInputFile):
        errors = list()
        proc_lock = Lock()

        self._logger.debug("Running {}...".format(self._command_name))

        with IsisPool() as isis:
            isis_cmd = getattr(isis, self._command_name)

            for file in files:
                args = deepcopy(self._extra_args)
                args["from"] = file.input_target

                if not self._disable_to_arg:
                    args["to"] = file.output_target

                try:
                    isis_cmd(**args)
                except ProcessError as e:
                    err = e.stderr.decode("utf-8")
                    with proc_lock:
                        self._logger.error(
                            "{} error: {}".format(self._command_name, err)
                        )
                        errors.append(err)

        self._logger.debug("{} complete".format(self._command_name))

        return errors
