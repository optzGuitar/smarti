from enum import Flag
import enum


class ClassLoaderFlags(Flag):
    """Flags for the smarti.ClassLoader"""
    ALL_DEPENDENCIES_AUTOWIRED = enum.auto()
    IGNORE_POSSIBLE_THREAD_ERRORS = enum.auto()

    NO_FLAGS = enum.auto()
