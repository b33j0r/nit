#! /usr/bin/env python
"""
I had an idea to do this, and after some googling used this as a starting point:

http://leigh.cudd.li/article/Cross_Platform_Colorized_Logger_Output_Using_Pythons_logging_Module_And_Colorama
"""

from logging import (
    StreamHandler,
    DEBUG,
    WARN,
    INFO,
    getLogger as realGetLogger,
    Formatter
)

from colorama import Fore, Back, Style, Cursor


class ColorizedStreamHandler(StreamHandler):

    """
    A colorized output SteamHandler
    """

    def __init__(self, stream=None, tty_formatter=None):
        super().__init__(stream)
        self.tty_formatter = tty_formatter

    def format(self, record):
        if self.is_tty:
            return self.tty_formatter.format(record)
        else:
            return super(ColorizedStreamHandler, self).format(record)

    @property
    def is_tty(self):

        """
        Check if we are using a "real" TTY. If we are not using a TTY it means that
        the colour output should be disabled.

        :return (bool): True if using a TTY status
        """

        try:
            return getattr(self.stream, 'isatty', None)()
        except AttributeError:
            return False


class ColorizedFormatter(Formatter):

    """
    """

    def __init__(self, fmt=None, datefmt=None, style='{'):
        self.prefix_separator = " "

        super().__init__(fmt, datefmt, style)

    def colorizeString(self, string, fore=None, back=None, style=Style.NORMAL):
        parts = []

        if style:
            parts.append(style)
        if fore:
            parts.append(fore)
        if back:
            parts.append(back)

        parts.append(string)

        parts.append(Style.RESET_ALL)

        return "".join(parts)

    def formatMessagePrefix(self, prefix="", fore=None, back=None, style=None):
        if not prefix:
            return ""

        prefix_len = len(prefix)
        prefix_padding = (9-prefix_len) // 2

        prefix_padded = " "*prefix_padding + prefix + " "*prefix_padding

        return self.colorizeString(
            prefix_padded, fore=fore, back=back, style=style
        )

    def formatMessageSummary(
            self, record, fore=None, back=None, style=Style.RESET_ALL
    ):
        return self.colorizeString(
            super().formatMessage(record),
            fore=fore,
            back=back,
            style=style
        )

    def formatMessageCritical(self, record):
        return (
            self.formatMessagePrefix(
                prefix="BUG",
                fore=Fore.LIGHTWHITE_EX,
                back=Back.LIGHTMAGENTA_EX,
                style=Style.BRIGHT
            ) + self.prefix_separator +
            self.formatMessageSummary(
                record,
                fore=Fore.LIGHTMAGENTA_EX
            )
        )

    def formatMessageError(self, record):
        return (
            self.formatMessagePrefix(
                prefix="ERROR",
                fore=Fore.LIGHTWHITE_EX,
                back=Back.LIGHTRED_EX,
                style=Style.BRIGHT
            ) + self.prefix_separator +
            self.formatMessageSummary(
                record,
                fore=Fore.LIGHTRED_EX
            )
        )

    def formatMessageWarning(self, record):
        return (
            self.formatMessagePrefix(
                prefix="WARNING",
                fore=Fore.BLACK,
                back=Back.LIGHTYELLOW_EX
            ) + self.prefix_separator +
            self.formatMessageSummary(
                record,
                fore=Fore.LIGHTYELLOW_EX
            )
        )

    def formatMessageDebug(self, record):
        return (
            self.formatMessagePrefix(
                prefix="DEBUG",
                fore=Fore.BLACK,
                back=Back.LIGHTCYAN_EX
            ) + self.prefix_separator +
            self.formatMessageSummary(
                record,
                fore=Fore.LIGHTCYAN_EX
            )
        )

    def formatMessageInfo(self, record):
        return self.formatMessageSummary(
            record,
            style=Style.RESET_ALL
        )

    def formatMessage(self, record):
        if record.levelname in ["CRIT", "CRITICAL"]:
            return self.formatMessageCritical(record)
        if record.levelname == "ERROR":
            return self.formatMessageError(record)
        if record.levelname == "WARNING":
            return self.formatMessageWarning(record)
        if record.levelname == "DEBUG":
            return self.formatMessageDebug(record)
        if record.levelname == "INFO":
            return self.formatMessageInfo(record)
        return super().formatMessage(record)

    has_colour = True


def getLogger(name=None, fmt='{message}'):
    """
    Get and initialize a colourised logging instance if
    the system supports it

    :param name: Name of the logger
    :type name (str): str
    :param fmt: Message format to use
    :type fmt: str
    :return: Logger instance
    :rtype: Logger
    """
    log = realGetLogger(name)

    formatter = ColorizedFormatter(fmt, style="{")

    handler = ColorizedStreamHandler(tty_formatter=formatter)
    handler.setLevel(DEBUG)
    handler.setFormatter(formatter)

    log.addHandler(handler)
    #log.setLevel(DEBUG)
    log.setLevel(INFO)
    log.propagate = 0  # Don't bubble up to the root logger

    log.Fore = Fore
    log.Back = Back
    log.Style = Style
    log.Cursor = Cursor

    return log
