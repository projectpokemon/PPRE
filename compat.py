import sys

# TODO: python six

try:
    import ConfigParser as configparser
    input = raw_input
except:
    import configparser
    input = input
