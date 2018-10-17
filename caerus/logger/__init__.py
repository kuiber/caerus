__author__ = "kav"

import logging
from logging import handlers
import inspect
import sys
import traceback
import time
from functools import wraps
from os.path import dirname, exists as path_exists
from os import makedirs


def suppress(f):
    @wraps(f)
    def suppress_output(*args, **kwargs):

        suppress_stdout_logging = kwargs.get("suppress", False)
        current_log_level = logger.console_logger.level
        # set the log level to 100 -  i.e. nothing to console
        if suppress_stdout_logging:
            logger.set_console_logger_level(100)

        result = f(*args, **kwargs)

        # return log level back
        if suppress_stdout_logging:
            logger.set_console_logger_level(current_log_level)
        return result

    return suppress_output


class Log:
    def __init__(self):
        """
        default console log level: INFO
        default file log level: DEBUG
        """
        if len(inspect.stack()) > 1:
            calling_module = inspect.stack()[1][1]
        else:
            calling_module = __name__

        self.logger = logging.getLogger(calling_module)
        self.logger.setLevel(logging.DEBUG)

        # console_logger handle
        self.console_logger = logging.StreamHandler()
        self.console_logger.setLevel(logging.INFO)

        self.formatter = logging.Formatter('%(levelname)s - %(message)s')
        self.console_logger.setFormatter(self.formatter)
        self.logger.addHandler(self.console_logger)
        self.file_logger = None

    @staticmethod
    def make_dir(log_file):
        """
        make the directory where logs are going if it doesn't exist
        :param log_file: full log_path
        :return: True or False for directory creation
        """
        directory_path = dirname(log_file)

        if not path_exists(directory_path):
            logger.debug("creating directory: {0}".format(directory_path))
            try:
                makedirs(directory_path, mode=0o0700)
            except OSError:
                logger.exception("Unable to make directory '{0}'".format(directory_path))
                raise
            return True
        return False

    def add_file_logger(self, filename, log_level=logging.DEBUG, maxBytes=10485760, backupCount=5):
        """
        create a file logger
        dd if=/dev/zero of=/tmp/out.file bs=10m count=1 to get the exact size in bytes
        :param filename: full filename to write to
        :param log_level: default log level for file log
        :param maxBytes: max file size in bytes (default 10MB)
        :param backupCount: number of files to keep on file system (default 5)
        :return: None
        """
        Log.make_dir(filename)
        self.file_logger = handlers.RotatingFileHandler(filename, maxBytes=maxBytes, backupCount=backupCount)
        self.file_logger.setLevel(log_level)

        self.formatter = logging.Formatter(
            '%(asctime)s - %(threadName)s - %(levelname)s - %(process)d - %(extra)s - %(message)s')
        self.file_logger.setFormatter(self.formatter)

        self.logger.addHandler(self.file_logger)

    def set_console_logger_level(self, log_level=logging.INFO):
        self.debug("setting console log level to {0}".format(logging.getLevelName(log_level)))
        self.console_logger.setLevel(log_level)

    def set_file_logger_level(self, log_level=logging.DEBUG):
        self.debug("setting file log level to {0}".format(logging.getLevelName(log_level)))
        self.file_logger.setLevel(log_level)

    def __make_message(self, msg, *args):
        if len(args[0]) == 0:
            return str(msg)
        try:
            return str(msg) + " " + " ".join([str(i) for i in args[0]])
        except TypeError:
            return str(msg) + " " + args[0]

    def __get_calling_function_details(self, stack):
        """
        inspect the calling method to extract filename, line number and function name
        :param stack: inspect.stack()
        :return: calling_file, calling_line_number, calling_function
        """

        try:
            stack = stack[2]  # we want the 3rd element. 1st is Log class, 2nd is @suppress decorator
        except IndexError:
            stack = stack[0]

        calling_file, calling_line_number, calling_function = stack[1:4]
        # "extra" in the dict corresponds to "extra" in logging.Formatter
        return {"extra": "{0}:{1} {2}".format(calling_file, calling_line_number, calling_function)}

    @suppress
    def debug(self, msg, *args, **kwargs):
        self.logger.debug(self.__make_message(msg, args), extra=self.__get_calling_function_details(inspect.stack()))

    @suppress
    def info(self, msg, *args, **kwargs):
        self.logger.info(self.__make_message(msg, args), extra=self.__get_calling_function_details(inspect.stack()))

    @suppress
    def warn(self, msg, *args, **kwargs):
        self.logger.warn(self.__make_message(msg, args), extra=self.__get_calling_function_details(inspect.stack()))

    @suppress
    def error(self, msg, *args, **kwargs):
        self.logger.error(self.__make_message(msg, args), extra=self.__get_calling_function_details(inspect.stack()))

    @suppress
    def critical(self, msg, *args, **kwargs):
        self.logger.critical(self.__make_message(msg, args), extra=self.__get_calling_function_details(inspect.stack()),
                             exc_info=True)

    @suppress
    def exception(self, msg, *args, **kwargs):
        # self.logger.exception(self.__make_message(msg, args))
        self.critical(self.__make_message(msg, args), extra=self.__get_calling_function_details(inspect.stack()),
                      exc_info=True)

    def uncaught_exception(self, typ, value, tb, *args, **kwargs):
        stack = ''.join(traceback.format_tb(tb))
        self.logger.critical('Uncaught Exception\n{0}{1}: {2}'.format(stack, typ.__name__, value),
                             extra=self.__get_calling_function_details(inspect.stack()))


logger = Log()
sys.excepthook = logger.uncaught_exception


def timeit(f):
    @wraps(f)
    def timed(*args, **kwargs):
        max_arg_length = 5
        if len(args) > max_arg_length:
            logger.debug("truncating args from len {0} to {1}".format(len(args), max_arg_length))
            args = args[:max_arg_length]
        logger.debug("Start: {0}(args = {1}, kwargs = {2})".format(f.__name__, args, kwargs))
        start = time.time()
        try:
            result = f(*args, **kwargs)
        except:
            end = time.time()
            logger.exception("exception found")
            logger.debug("End (with exception): {0}(args = {1}, kwargs = {2}) took {3}".format(f.__name__, args, kwargs,
                                                                                               end - start))
            raise
        else:
            end = time.time()
            logger.debug("End: {0}(args = {1}, kwargs = {2}) took {3}".format(f.__name__, args, kwargs, end - start))
            return result

    return timed


def requires_unittest(comment=None):
    """
    decorator to log a WARN message that this function needs a unittest
    :param comment: optional comment string
    :return: function
    """

    def requires_unittest_wrapper(f):
        @wraps(f)
        def function_requires_unittest(*args, **kwargs):
            if comment:
                logger.warn("function: {0} in file {1}:{2} requires a unit test '{3}'".format(f.__name__,
                                                                                              f.func_code.co_filename,
                                                                                              f.func_code.co_firstlineno,
                                                                                              comment))
            else:
                logger.warn("function: {0} in file {1}:{2} requires a unit test".format(f.__name__,
                                                                                        f.func_code.co_filename,
                                                                                        f.func_code.co_firstlineno,
                                                                                        ))
            return f(*args, **kwargs)

        return function_requires_unittest

    return requires_unittest_wrapper
