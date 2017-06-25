"""Feed Manager."""

import csv
import dateutil
import gzip
import os
import re
import requests
import sqlite3
import time
from datetime import datetime
from feed_schema_translator import FeedSchemaTranslator
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
        self.db_schemas = config.db_schemas
        self.db_translate_schemas = config.db_translate_schemas

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
        """Wrapper for feed file reconciliation against DBs."""
        last_timestamp = self.get_newest_record_time("cgi")
        print("FeedManager: Reconciling feed databases.  Please be patient...")
        this_timestamp = FeedManager.reconcile_db(self.db_schemas["cgi"],
                                                  self.db_translate_schemas["ocid"],  # NOQA
                                                  self.cgi_feed_files,
                                                  self.cgi_db,
                                                  self.target_radios,
                                                  last_timestamp)
        self.set_newest_record_time("cgi", this_timestamp)
        # This is specifically for FCC feedds, but the underpinnings exist
        # for others
        last_timestamp = self.get_newest_record_time("arfcn")
        this_timestamp = FeedManager.reconcile_db(self.db_schemas["arfcn"],
                                                  self.db_translate_schemas["fcc"],  # NOQA
                                                  self.arfcn_feed_files,
                                                  self.arfcn_db,
                                                  "",
                                                  last_timestamp)
        self.set_newest_record_time("arfcn", this_timestamp)

    def get_newest_record_time(self, db_type):
        """Get the newest record time from file in feed dir."""
        result = 0
        rx = r'^\d{10}$'
        if not os.path.isfile("%s.%s" % (self.newest_record_file, db_type)):
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

    def set_newest_record_time(self, db_type, timestamp):
        """Set the newest record time.

        Args:
            timestamp (str): Epoch time to be written to file  If not string,
                will be coerced to string.

        """
        record_file = "%s.%s" % (self.newest_record_file, db_type)
        with open(record_file, 'w') as u_file:
            print("FeedManager: Setting newest DB record to %s" % Utility.epoch_to_iso8601(timestamp))  # NOQA
            u_file.write(str(timestamp).replace('.0', ''))
        return

    @classmethod
    def reconcile_db(cls, db_schema, db_translate_schema, feed_files, db_file,
                     target_radios, last_update):
        """Reconcile feed files against the target DB.

        Args:
            feed_files (list): List of paths to feed files.
            db_file (str): Full path to CGI DB file.
            last_update (str): Epoch time of most recent record in DB

        Returns:
            str: Epoch timestamp of most recently updated DB record.
        """
        db_exists = os.path.isfile(db_file)
        # If DB file does not exist, create it, then rip the DB from file
        if not db_exists:
            ts = cls.create_and_populate_db(db_schema, db_translate_schema,
                                            feed_files, db_file, target_radios)
        else:
            ts = cls.merge_feed_files_into_db(db_schema, db_translate_schema,
                                              feed_files, db_file,
                                              target_radios, last_update)
        return ts

    @classmethod
    def merge_feed_files_into_db(cls, db_schema, db_translate_schema,
                                 feed_files, db_file, target_radios, last_upd):
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
                newest_ts = cls.dump_csv_to_db(db_schema, db_translate_schema,
                                               feed_file, db_file,
                                               target_radios, last_upd)
                if newest_ts > newest_ts_overall:
                    newest_ts_overall = float(newest_ts)
        return newest_ts_overall

    @classmethod
    def create_and_populate_db(cls, db_schema, db_translate_schema, feed_files,
                               db_file, target_radios):
        """Create DB, then merge all records from file.

        Args:
            db_schema (list): List of DB fields.
            feed_files (list): List of feed files to be merged.
            db_file (str): Full path of CGI DB file.

        Returns:
            str: Most recent timestamp from merge.
        """
        newest_ts_overall = float(0)  # Newest timestamp
        cls.create_db(db_file, db_schema)
        for feed_file in feed_files:
            feed_file_exists = os.path.isfile(feed_file)
            if not feed_file_exists:
                print("FeedManager: Feed file does not exist: %s" % feed_file)
            else:
                newest_ts = cls.dump_csv_to_db(db_schema, db_translate_schema,
                                               feed_file, db_file,
                                               target_radios)
                if newest_ts > newest_ts_overall:
                    newest_ts_overall = float(newest_ts)
        return newest_ts_overall

    @classmethod
    def should_update_record_epoch(cls, anchor_time, update_time):
        """Compare timestamps to determine if a record should be updated."""
        if update_time > anchor_time:
            result = True
        else:
            result = False
        return result

    @classmethod
    def should_update_record_iso(cls, anchor_time, update_time):
        """Compare timestamps to determine if a record should be updated."""
        if (dateutil.parser.parse(update_time) >
                dateutil.parser.parse(anchor_time)):
            result = True
        else:
            result = False
        return result

    @classmethod
    def dump_csv_to_db(cls, db_schema, db_translate_schema, feed_file, db_file,
                       target_radios, last_upd=0):
        """Merge CSV into DB, taking into account the record update time.

        Args:
            db_schema (dict): Dictionary produced from feed_db_schema.yaml.
                Only one key, ``cgi`` or ``arfcn``.
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
        db_type = db_schema.items()[0][0]
        translator = FeedSchemaTranslator(db_translate_schema)
        print("DB Type: %s" % db_type)
        db_fields = db_schema[db_type]["fields"]
        print("DB Fields: %s" % str(db_fields))
        with gzip.open(feed_file, 'r') as f_file:
            feed = csv.DictReader(f_file)
            for row in feed:
                rows_examined += 1
                if db_type == "cgi":
                    row_timestamp = float(row["updated"])
                elif db_type == "arfcn":
                    row_timestamp = float(dateutil.parser.parse(row["LAST_ACTION_DATE"]).strftime("%s"))  # NOQA
                if latest_timestamp < row_timestamp:
                    latest_timestamp = row_timestamp
                if not cls.should_update_record_epoch(last_upd, row_timestamp):  # NOQA
                    continue
                # Allow us to skip all but target radios for CGI DB
                if "radio" in row:
                    if not row["radio"] in target_radios:
                        continue
                if not rows_examined % 100000:
                    print("FeedManager: %s rows examined in %s" % (str(rows_examined), feed_file))  # NOQA
                if len(proc_chunk) < 9999:
                    trans_row = translator.translate_row(row)
                    proc_chunk.append(cls.tup_from_row(db_fields, trans_row))
                else:
                    trans_row = translator.translate_row(row)
                    proc_chunk.append(cls.tup_from_row(db_fields, trans_row))
                    cls.mass_insert(db_type, db_fields, proc_chunk, db_file)
                    rows_written += len(proc_chunk)
                    msg = "FeedManager: %s rows written to %s" % (str(rows_written), db_file)  # NOQA
                    print msg
                    proc_chunk = []
        cls.mass_insert(db_type, db_fields, proc_chunk, db_file)
        rows_written += len(proc_chunk)
        msg = "FeedManager: %s rows examined in %s, %s written to %s. Done." % (str(rows_examined), feed_file, str(rows_written), db_file)  # NOQA
        print msg
        return latest_timestamp

    @classmethod
    def mass_insert(cls, table, fields, rows, db_file):
        """Mass-insert records into the DB.

        Args:
            schema (list): List of DB fields.
            rows (list): List of tuples, each tuple contains values
                corresponding to the keys in `schema`.
            db_file (str): Path to sqlite file.

        """
        conn = sqlite3.connect(db_file)
        field_qmarks = ",".join(["?" for x in xrange(len(fields))])
        insert_string = "INSERT INTO %s VALUES (%s)" % (table, field_qmarks)
        conn.executemany(insert_string, rows)
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
    def create_db(cls, db_file, db_schema):
        """Create a DB.

        This creates either the CGI or ARFCN database.

        Args:
            db_file (str): Path to DB file.
            db_schema (dict): One top-level k:v from feed_db_schema.yaml
        """
        conn = sqlite3.connect(db_file)
        print("FeedManager: Creating %s DB" % db_file)
        create_table_str = cls.create_db_init_string(db_schema)
        print create_table_str
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

    @classmethod
    def create_db_init_string(cls, db_schema):
        """Create DB initialization string based on db_schema input.

        Expects a dictionary like this:
            {"table_name":
                 {"fields": ["field_1",
                             "field_2"
                             "field_3"],
                  "unique": ["field_1",
                             "field_2"]}}

        Args:
            db_schema (dict): Dictionary describing the DB schema
        """
        table_name = db_schema.keys()[0]
        fields = db_schema
        create_table = "create table %s" % table_name
        fields = " varchar, ".join(db_schema[table_name]["fields"]) + " varchar,"  # NOQA
        unique = ", ".join(db_schema[table_name]["unique"])
        result = "%s (%s UNIQUE (%s) ON CONFLICT REPLACE);" % (create_table,
                                                               fields, unique)
        return result
