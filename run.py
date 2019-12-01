from archiveit import bot
import logging
import argparse
import sys

parser = argparse.ArgumentParser(description='ArchiveIt bot')

parser.add_argument("--ll",
                    help="Log Level, either DEBUG, INFO, WARNING, ERROR or CRITICAL. Default: WARNING",
                    default="WARNING")
parser.add_argument("--log_file",
                    help="Path to log file. Default: None",
                    default=None)
args = parser.parse_args()


numeric_level = getattr(logging, args.ll.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % args.ll)




logger = logging.getLogger("archiveit")
logger.setLevel(numeric_level)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S%p')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
if args.log_file is not None:
    file_handler = logging.FileHandler(args.log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


if __name__ == '__main__':
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot shutting down")
        sys.exit(0)


