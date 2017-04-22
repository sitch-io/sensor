"""Feed Manager."""

import csv
import gzip
import os
import re
import requests
import sqlite3
import time
from datetime import datetime
from utility import Utility


class FeedManager(object):
    """Manage downloading the feed DB, and merging it into the sqlite DB."""

    def __init__(self, config):
        """Initialize FeedManager.

        Args:
            config (obj): Configuration object.
        """
        self.mcc_list = config.mcc_list
        self.state_list = config.state_list
        self.feed_dir = config.feed_dir
        self.target_radios = config.feed_radio_targets
        self.url_base = config.feed_url_base
        self.cgi_feed_files = []
        self.arfcn_feed_files = []
        self.born_on_date = datetime.now()
        self.cgi_db = os.path.join(self.feed_dir, "cgi.db")
        self.newest_record_file = os.path.join(self.feed_dir, "newest_record")
        self.arfcn_db = os.path.join(self.feed_dir, "arfcn.db")
        self.no_feed_update = config.no_feed_update

    def update_feed_files(self):
        """Wrapper for feed file retrieval routines."""
        if (os.path.isfile(self.cgi_db) and self.no_feed_update is not None):
            # Skip the update process if db exists and config says no update.
            print("FeedManager: DB exists. NO_FEED_UPDATE is set...")
            print("FeedManager: Skipping feed update!")
            return
        for feed_id in self.mcc_list:
            feed_file = FeedManager.place_feed_file(self.feed_dir,
                                                    self.url_base,
                                                    feed_id)
            self.cgi_feed_files.append(feed_file)
        for feed_id in self.state_list:
            feed_file = FeedManager.place_feed_file(self.feed_dir,
                                                    self.url_base,
                                                    feed_id)
            self.arfcn_feed_files.append(feed_file)
        print("FeedManager: Finished pulling all feed files")
        return

    def update_feed_db(self):
        """Wrapper for feed file reconciliation against CGI DB."""
        last_timestamp = self.get_newest_record_time()
        print("FeedManager: Reconciling feed database.  Please be patient...")
        this_timestamp = FeedManager.reconcile_cgi_db(self.cgi_feed_files,
                                                      self.cgi_db,
                                                      self.target_radios,
                                                      last_timestamp)
        self.set_newest_record_time(this_timestamp)

    def get_newest_record_time(self):
        """Get the newest record time from file in feed dir."""
        result = 0
        rx = r'^\d{10}$'
        if not os.path.isfile(self.newest_record_file):
            print("FeedManager: No record of last update found...")
            return result
        with open(self.newest_record_file, 'r') as u_file:
            first_line = u_file.readline().replace('\n', '').replace('.0', '')
            if re.match(rx, first_line):
                result = first_line
                print("FeedManager: Newest DB record timestamp is %s" % Utility.epoch_to_iso8601(result))  # NOQA
            else:
                print("FeedManager: Unable to parse newest DB record timestamp!")  # NOQA
        return result

    def set_newest_record_time(self, timestamp):
        """Set the newest record time.

        Args:
            timestamp (str): Epoch time to be written to file  If not string,
                will be coerced to string.

        """
        with open(self.newest_record_file, 'w') as u_file:
            print("FeedManager: Setting newest DB record to %s" % Utility.epoch_to_iso8601(timestamp))  # NOQA
            u_file.write(str(timestamp).replace('.0', ''))
        return

    @classmethod
    def reconcile_cgi_db(cls, feed_files, db_file, target_radios, last_update):
        """Reconcile all feed files against the CGI DB.

        Args:
            feed_files (list): List of paths to feed files.
            db_file (str): Full path to CGI DB file.
            last_update (str): Epoch time of most recent record in DB

        Returns:
            str: Epoch timestamp of most recently updated DB record.
        """
        db_exists = os.path.isfile(db_file)
        schema = ["radio", "mcc", "net", "area", "cell",
                  "unit", "lon", "lat", "range", "carrier"]
        # If DB file does not exist, create it, then rip the DB from file
        if not db_exists:
            ts = cls.create_and_populate_cgi_db(schema, feed_files,
                                                db_file, target_radios)
        else:
            ts = cls.merge_feed_files_into_db(schema, feed_files, db_file,
                                              target_radios, last_update)
        return ts

    @classmethod
    def merge_feed_files_into_db(cls, schema, feed_files, db_file, target_radios, last_upd):  # NOQA
        """Wrapper for merging feed file data into CGI DB.

        Args:
            schema (list): List of fields in DB
            feed_file (str): Path to feed file to be merged into CGI DB.
            db_file (str): Path to CGI DB file.
            last_upd (str): Epoch time stamp, will not attempt to merge any
                records with timestamps before this time.

        Returns:
            str: Most recent timestamp from merged feed file.
        """
        newest_ts_overall = float(0)
        for feed_file in feed_files:
            feed_file_exists = os.path.isfile(feed_file)
            if not feed_file_exists:
                print("FeedManager: Feed file does not exist: %s" % feed_file)
            else:
                newest_ts = cls.cgi_csv_dump_to_db(schema, feed_file, db_file, target_radios, last_upd)  # NOQA
                if newest_ts > newest_ts_overall:
                    newest_ts_overall = float(newest_ts)
        return newest_ts_overall

    @classmethod
    def create_and_populate_cgi_db(cls, schema, feed_files, db_file, target_radios):  # NOQA
        """Create DB, then merge all records from file.

        Args:
            schema (list): List of DB fields.
            feed_files (list): List of feed files to be merged.
            db_file (str): Full path of CGI DB file.

        Returns:
            str: Most recent timestamp from merge.
        """
        newest_ts_overall = float(0)  # Newest timestamp
        cls.create_cgi_db(db_file)
        for feed_file in feed_files:
            feed_file_exists = os.path.isfile(feed_file)
            if not feed_file_exists:
                print("FeedManager: Feed file does not exist: %s" % feed_file)
            else:
                newest_ts = cls.cgi_csv_dump_to_db(schema, feed_file, db_file,
                                                   target_radios)
                if newest_ts > newest_ts_overall:
                    newest_ts_overall = float(newest_ts)
        return newest_ts_overall

    @classmethod
    def should_update_record(cls, anchor_time, update_time):
        """Compare timestamps to determine if a record should be updated."""
        if update_time > anchor_time:
            result = True
        else:
            result = False
        return result

    @classmethod
    def cgi_csv_dump_to_db(cls, schema, feed_file, db_file, target_radios, last_upd=0):
        """Merge CSV into DB, taking into account the record update time.

        Args:
            schema (list): List of rows in DB.
            feed_file (str): Path to feed CSV file.
            db_file (str): Path to sqlite DB file.
            last_upd (:obj:`int`, optional): Epoch time.  Records updated
                before this date will not be inserted into the DB.
        """
        print("FeedManager: Reconciling %s against feed DB..." % feed_file)
        proc_chunk = []
        rows_written = 0
        rows_examined = 0
        latest_timestamp = float(0)
        with gzip.open(feed_file, 'r') as f_file:
            feed = csv.DictReader(f_file)
            for row in feed:
                rows_examined += 1
                if latest_timestamp < float(row["updated"]):
                    latest_timestamp = float(row["updated"])
                if not cls.should_update_record(last_upd, row["updated"]):
                    continue
                if not row["radio"] in target_radios:
                    continue
                if not rows_examined % 100000:
                    print("FeedManager: %s rows examined in %s" % (str(rows_examined), feed_file))  # NOQA
                if len(proc_chunk) < 9999:
                    proc_chunk.append(cls.tup_from_row(schema, row))
                else:
                    proc_chunk.append(cls.tup_from_row(schema, row))
                    cls.cgi_mass_insert(schema, proc_chunk, db_file)
                    rows_written += len(proc_chunk)
                    msg = "FeedManager: %s rows written to %s" % (str(rows_written), db_file)  # NOQA
                    print msg
                    proc_chunk = []
        cls.cgi_mass_insert(schema, proc_chunk, db_file)
        rows_written += len(proc_chunk)
        msg = "FeedManager: %s rows examined in %s, %s written to %s. Done." % (str(rows_examined), feed_file, str(rows_written), db_file)  # NOQA
        print msg
        return latest_timestamp

    @classmethod
    def cgi_mass_insert(cls, schema, rows, db_file):
        """Mass-insert records into the DB.

        Args:
            schema (list): List of DB fields.
            rows (list): List of tuples, each tuple contains values
                corresponding to the keys in `schema`.
            db_file (str): Path to sqlite file.

        """
        conn = sqlite3.connect(db_file)
        conn.executemany("INSERT INTO cgi VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
        conn.commit()
        conn.close()

    @classmethod
    def tup_from_row(cls, schema, row):
        """Convert a row into a tuple, for insertion into DB.

        Args:
            schema (list): Field list for DB.
            row (dict): Row of data.  Keys align with items in `schema`.

        Returns:
            tuple: Tuple representing values to be inserted into DB, ordered
                by fields in `schema`.
        """
        retlst = []
        for s in schema:
            retlst.append(row[s])
        return tuple(retlst)

    @classmethod
    def create_cgi_db(cls, cgi_db):
        """Create a DB for CGIs.

        This DB has only one table, named `cgi` and the mcc+mnc+lac+cellid is
            unique.

        Args:
            cgi_db (str): Path to CGI DB.
        """
        conn = sqlite3.connect(cgi_db)
        print("FeedManager: Creating CGI DB at %s" % cgi_db)
        create_table_str = ("create table cgi (radio varchar, mcc varchar, " +
                            "net varchar, area varchar, cell varchar, " +
                            "unit varchar, lon varchar, lat varchar, " +
                            "range varchar, carrier varchar, " +
                            "UNIQUE (mcc, net, area, cell) " +
                            "ON CONFLICT REPLACE);")
        conn.execute(create_table_str)
        conn.close()

    @classmethod
    def place_feed_file(cls, feed_dir, url_base, item_id):
        """Retrieve and places feed files for use by the Enricher modules.

        Args:
            feed_dir (str): Destination directory for feed files
            url_base (str): Base URL for hosted feed files
            item_id(str): For FCC, this is the two-letter ("CA" or "TN",
                for example), which is used in the retrieval of the feed file
                 as well as the construction of the local feed file name.  For
                 MCC this is the MCC, but in string form.  Not integer.

        """
        destination_file = Utility.construct_feed_file_name(feed_dir,
                                                            item_id)
        temp_file = "%s.TEMP" % destination_file
        origin_url = FeedManager.get_source_url(url_base, item_id)
        msg = "FeedManager: Downloading %s to %s" % (origin_url, temp_file)
        print(msg)
        response = requests.get(origin_url, stream=True)
        with open(temp_file, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    out_file.write(chunk)
        time.sleep(1)
        print("FeedManager: Moving %s to %s" % (temp_file, destination_file))
        os.rename(temp_file, destination_file)
        return destination_file

    @classmethod
    def get_source_url(cls, url_base, mcc):
        """Create source URL for MCC file.

        Args:
            url_base (str): Base URL for MCC file.
            mcc (str): MCC for feed file.
        """
        src_url = "%s/%s.csv.gz" % (url_base, mcc)
        return src_url
