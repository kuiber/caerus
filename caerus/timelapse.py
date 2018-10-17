from caerus.logger import logger

logger.add_file_logger("/tmp/caerus.log")


def main():
    logger.error("hello world abc")


if __name__ == "__main__":
    main()
