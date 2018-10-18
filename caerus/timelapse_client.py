from caerus.logger import logger
from caerus.timelapse import TimeLapse
import datetime
from argparse import ArgumentParser

logger.add_file_logger("/tmp/caerus.log")


def main():
    parser = ArgumentParser()
    parser.add_argument("project", help="project name where images are saved")
    parser.add_argument("-i", "--interval", type=float, required=True, nargs=1, help="interval [float] in seconds between successive image captures")
    parser.add_argument("-d", "--duration", type=float, required=True, nargs=1, help="duration [float] in seconds of the total timelapse duration")
    args = parser.parse_args()

    logger.debug(args)

    timelapse = TimeLapse(args.project, args.interval[0], datetime.timedelta(seconds=args.duration[0]))
    timelapse.start()


if __name__ == "__main__":
    main()
