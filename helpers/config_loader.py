"""
Class for creating configuration files.
"""
import json
import logging


class ConfigLoader:

    def __init__(self, keys, filename):
        self.config = {}
        self.keys = keys
        self.filename = filename

        try:
            self.load_from_file()
        except FileNotFoundError:
            self.create_file()

    def add_element(self, key, value):
        """
        Add an element to the configuration
        """
        self.config[key] = value

    def get_element(self, key):
        """
        Returns value associated with a key
        """
        return self.config[key]

    def load_from_file(self):
        """
        Loads config data from a file
        """
        with open(self.filename, "r") as f:
            self.config = json.load(f)

    def create_file(self):
        """
        Creates a config file
        """
        with open(self.filename, "w") as f:
            json.dump(dict.fromkeys(self.keys), f)
        raise RuntimeError(f"Please fill out {self.filename}")
