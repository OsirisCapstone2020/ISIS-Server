from pysis import isis
from logging import getLogger, DEBUG, StreamHandler
from sys import stdout

isis_logger = getLogger("isis")
isis_logger.setLevel(DEBUG)
isis_logger.addHandler(StreamHandler(stdout))

CMD_LOWPASS = "lowpass"


def lowpass(input_file, output_file):
    isis_logger.info("Running lowpass on {} --> {}...".format(input_file, output_file))
    isis.lowpass(from_=input_file, to=output_file, samples=1, lines=3)
    isis_logger.info("lowpass complete on {}\n".format(output_file))
