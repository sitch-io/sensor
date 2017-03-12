"""Fcc Feed."""

import csv
import gzip
from utility import Utility


class FccFeed(object):
    """Wrap the FCC Feed with an iterator."""

    def __init__(self, states, feed_base):
        """Initialize the FccFeed object.

        Args:
            states (list): List of strings, each being a US state code.
            feed_base (str): Directory where feed files can be found.
        """
        self.feed_files = self.build_feed_file_names(states, feed_base)

    def __iter__(self):
        """Yield one row at a time from the FCC feed."""
        for f_file in self.feed_files:
            with gzip.open(f_file, 'r') as feed_data:
                consumer = csv.DictReader(feed_data)
                for row in consumer:
                    yield row

    def build_feed_file_names(self, states, feed_base):
        """Construct full feed file path."""
        file_names = []
        for state in states:
            file_names.append(Utility.construct_feed_file_name(feed_base,
                                                               state))
        return file_names
