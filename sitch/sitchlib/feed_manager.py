import os
import requests
import time
from datetime import datetime


class FeedManager(object):
    def __init__(self, config):
        self.mcc_list = config.mcc_list
        self.state_list = config.state_list
        self.feed_dir = config.feed_dir
        self.url_base = config.feed_url_base
        self.feed_cache = []
        self.born_on_date = datetime.now()

    def update_mcc_feeds(self):
        for mcc in self.mcc_list:
            print "Feed: Pulling down feed for MCC %s" % str(mcc)
            FeedManager.update_mcc_feed_file(self.feed_dir, self.url_base, mcc)
        print "Feed: Finished pulling all MCC feed files"
        return

    def update_fcc_feed_files(self):
        for state in self.state_list:
            print "Feed: Pulling down feed for state: %s" % str(state)
            FeedManager.update_fcc_feed_file(self.feed_dir, self.url_base, state)
        print "Feed: Finished pulling all state feed files"
        return

    @classmethod
    def update_mcc_feed_file(cls, feed_dir, url_base, mcc):
        destination_file = FeedManager.construct_feed_file_name(feed_dir, mcc)
        temp_file = "%s.TEMP" % destination_file
        origin_url = FeedManager.get_source_url(url_base, mcc)
        print "Feed: Downloading %s to %s" % (origin_url, temp_file)
        response = requests.get(origin_url, stream=True)
        with open(temp_file, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    out_file.write(chunk)
        time.sleep(2)
        print "Feed: Moving %s to %s" % (temp_file, destination_file)
        os.rename(temp_file, destination_file)

    @classmethod
    def update_fcc_feed_file(cls, feed_dir, url_base, state):
        destination_file = FeedManager.construct_feed_file_name(feed_dir,
                                                                state)
        temp_file = "%s.TEMP" % destination_file
        origin_url = FeedManager.get_source_url(url_base, state)
        print "Feed: Downloading %s to %s" % (origin_url, temp_file)
        response = requests.get(origin_url, stream=True)
        with open(temp_file, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    out_file.write(chunk)
        time.sleep(2)
        print "Feed: Moving %s to %s" % (temp_file, destination_file)
        os.rename(temp_file, destination_file)

    @classmethod
    def construct_feed_file_name(cls, feed_dir, prefix):
        file_name = "%s.csv.gz" % prefix
        dest_file_name = os.path.join(feed_dir, file_name)
        return dest_file_name

    @classmethod
    def get_source_url(cls, url_base, mcc):
        src_url = "%s/%s.csv.gz" % (url_base, mcc)
        return src_url
