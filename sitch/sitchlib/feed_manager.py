import os
import requests
from datetime import datetime


class FeedManager(object):
    def __init__(self, config):
        self.mcc_list = config.mcc_list
        self.feed_dir = config.feed_dir
        self.url_base = config.feed_url_base
        self.feed_cache = []
        self.born_on_date = datetime.now()

    def update_mcc_feeds(self):
        for mcc in self.mcc_list:
            print "Pulling down feed for MCC %s" % str(mcc)
            FeedManager.update_mcc_feed_file(self.feed_dir, self.url_base, mcc)
        print "Finished pulling all MCC feed files"
        return

    def update_fcc_feed_files(self):
        for state in self.state_list:
            print "Pulling down feed for state: %s" % str(state)
            FeedManager.update_fcc_feed_file(self.feed_dir, self.url_base, state)
        print "Finished pulling all state feed files"
        return

    @classmethod
    def update_mcc_feed_file(cls, feed_dir, url_base, mcc):
        destination_file = FeedManager.construct_feed_file_name(feed_dir, mcc)
        temp_file = "%s.TEMP" % destination_file
        origin_url = FeedManager.get_source_url(url_base, mcc)
        response = requests.get(origin_url, stream=True)
        with open(temp_file, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    out_file.write(chunk)
        os.rename(temp_file, destination_file)

    @classmethod
    def update_fcc_feed_file(cls, feed_dir, url_base, state):
        destination_file = FeedManager.construct_feed_file_name(feed_dir,
                                                                state)
        temp_file = "%s.TEMP" % destination_file
        origin_url = FeedManager.get_source_url(url_base, state)
        response = requests.get(origin_url, stream=True)
        with open(destination_file, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    out_file.write(chunk)
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

"""
    def get_feed_info_for_tower(self, mcc, mnc, lac, cellid):
        if self.feed_cache != []:
            for x in self.feed_cache:
                if (x["mcc"] == mcc and
                        x["mnc"] == mnc and
                        x["lac"] == lac and
                        x["cellid"] == cellid):
                    return x
            print "Cache miss!  Attempt to get from feed files..."
        normalized = self.get_feed_info_from_files(mcc, mnc, lac, cellid)
        self.feed_cache.append(normalized)
        return normalized


    @classmethod
    def normalize_feed_info_for_cache(cls, feed_item):
        cache_item = {}
        cache_item["mcc"] = feed_item["mcc"]
        cache_item["mnc"] = feed_item["net"]
        cache_item["lac"] = feed_item["area"]
        cache_item["cellid"] = feed_item["cell"]
        cache_item["lon"] = feed_item["lon"]
        cache_item["lat"] = feed_item["lat"]
        cache_item["range"] = feed_item["range"]
        return cache_item
"""
"""
    def get_feed_info_from_files(self, mcc, mnc, lac, cellid):
        # Field names get changed when loaded into the cache, to
        # match field IDs used elsewhere.
        feed_file = FeedManager.construct_feed_file_name(self.feed_dir, mcc)
        with gzip.open(feed_file, 'r') as feed_data:
            consumer = csv.DictReader(feed_data)
            for cell in consumer:
                if (cell["mcc"] == mcc and
                        cell["net"] == mnc and
                        cell["area"] == lac and
                        cell["cell"] == cellid):
                    normalzed = FeedManager.normalize_feed_info_for_cache(cell)
                    return normalzed
        # Unable to locate cell in file, we populate the
        # cache with obviously fake values
        cell = {"mcc": mcc, "net": mnc, "area": lac, "cell": cellid,
                "lon": 0, "lat": 0, "range": 0}
        normalized = FeedManager.normalize_feed_info_for_cache(cell)
        return normalized
"""
