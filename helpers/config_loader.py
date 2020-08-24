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

        if not self.are_keys_same():
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
            new_keys = set(self.keys) - self.config.keys()
            new_entries = dict.fromkeys(new_keys)
            self.config.update(new_entries)
            json.dump(self.config, f)
        raise RuntimeError(f"Please fill out {self.filename}")

    def are_keys_same(self):
        """
        Checks if the config file has all options
        :return: True if it does, false if it doesn't
        """
        old_keys = set(self.keys)
        new_keys = self.config.keys()

        return old_keys == new_keys
