import csv
import gzip
from feed_manager import FeedManager


class FccFeed(object):
    def __init__(self, states, feed_base):
        self.feed_files = self.build_feed_file_names(states, feed_base)

    def __iter__(self):
        for f_file in self.feed_files:
            with gzip.open(f_file, 'r') as feed_data:
                consumer = csv.DictReader(feed_data)
                for row in consumer:
                    yield row

    def build_feed_file_names(self, states, feed_base):
        file_names = []
        for state in states:
            file_names.append(FeedManager.construct_feed_file_name(feed_base,
                                                                   state))
        return file_names
