from pysis import IsisPool
from .ISISRequest import ISISInputFile
from .logger import get_logger


class ISISCommand:
    def __init__(self, command, **command_args):
        self.command = command
        self.command_args = command_args
        self.output_files = list()
        self.logger = get_logger(self.command)

    def run(self, *files: ISISInputFile):
        self.logger.debug("Running {}...".format(self.command))
        with IsisPool() as isis:
            isis_command = getattr(isis, self.command)
            for file in files:
                isis_command(
                    from_=file.input_target,
                    to=file.output_target,
                    **self.command_args
                )
        self.logger.debug("{} complete".format(self.command))
