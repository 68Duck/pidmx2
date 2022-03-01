import sqlite3 as lite
from os import path
import os

from dict_factory import dict_factory


class Database_manager(object):
    def __init__(self):
        self.DATABASE = "pidmx2.db"
        if not path.exists("databases"):
            os.makedirs("databases")
            print("ERROR Database folder does not exist. A new database folder had been created")
        self.create_initial_tables()

    def get_db(self):
        file_directory = path.dirname(__file__)
        database_file_directory = path.join(file_directory,"databases")
        con = lite.connect(path.join(database_file_directory,self.DATABASE),isolation_level=None)
        con.execute("PRAGMA foreign_keys = 1")
        return con

    def query_db(self,query,args=()):
        cur = self.get_db().execute(query,args)
        cur.row_factory = dict_factory
        results = cur.fetchall()
        cur.close()
        return results

    def create_initial_tables(self):
        self.create_accounts_table()
        self.create_bars_table()
        self.create_bars_in_locations_table()
        self.create_channel_values_table()
        self.create_light_effects_table()
        self.create_lights_table()
        self.create_lights_in_rigs_table()
        self.create_lights_in_sequence_table()
        self.create_locations_table()
        self.create_locations_in_account_table()
        self.create_playback_effects_table()
        self.create_playbacked_table()
        self.create_playbacks_table()
        self.create_rectangles_table()
        self.create_rectangles_in_locations_table()
        self.create_rigs_table()
        self.create_rigs_in_account_table()
        self.create_sequence_playbacks_table()
        self.create_sequences_table()
        self.create_ipv4_address_table()


    def create_ipv4_address_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Ipv4_address" (
    	"id"	INTEGER NOT NULL UNIQUE,
    	"port_1"	INTEGER,
    	"port_2"	INTEGER,
    	"port_3"	INTEGER,
    	"port_4"	INTEGER,
    	PRIMARY KEY("id" AUTOINCREMENT)
        )""")

    def create_accounts_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Accounts" (
    	"account_id"	INTEGER NOT NULL UNIQUE,
    	"username"	TEXT NOT NULL,
    	"hashed_password"	TEXT NOT NULL,
    	PRIMARY KEY("account_id" AUTOINCREMENT)
        )""")

    def create_bars_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Bars" (
    	"bars_id"	INTEGER NOT NULL UNIQUE,
    	"width"	INTEGER NOT NULL,
    	"height"	INTEGER NOT NULL,
    	"xpos"	INTEGER NOT NULL,
    	"ypos"	INTEGER NOT NULL,
    	"is_horizontal"	INTEGER NOT NULL,
    	"bar_name"	TEXT NOT NULL,
    	PRIMARY KEY("bars_id" AUTOINCREMENT)
        )""")

    def create_bars_in_locations_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Bars_in_locations" (
    	"bars_in_locations_id"	INTEGER NOT NULL UNIQUE,
    	"location_id"	INTEGER NOT NULL,
    	"bars_id"	INTEGER NOT NULL,
    	FOREIGN KEY("location_id") REFERENCES "Locations"("location_id") ON DELETE CASCADE,
    	FOREIGN KEY("bars_id") REFERENCES "Bars"("bars_id") ON DELETE CASCADE,
    	PRIMARY KEY("bars_in_locations_id" AUTOINCREMENT)
        )""")

    def create_channel_values_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Channel_values" (
    	"channel_values_id"	INTEGER NOT NULL UNIQUE,
    	"channel_number"	INTEGER NOT NULL,
    	"channel_value"	INTEGER NOT NULL,
    	PRIMARY KEY("channel_values_id" AUTOINCREMENT)
        )""")

    def create_light_effects_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Light_effects" (
    	"light_effects_id"	INTEGER NOT NULL UNIQUE,
    	"light_id"	INTEGER NOT NULL,
    	"effect_name"	TEXT NOT NULL,
    	"effect_value"	INTEGER NOT NULL,
    	FOREIGN KEY("light_id") REFERENCES "Lights"("light_id") ON DELETE CASCADE,
    	PRIMARY KEY("light_effects_id" AUTOINCREMENT)
        )""")

    def create_lights_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Lights" (
    	"light_id"	INTEGER NOT NULL UNIQUE,
    	"light_type"	TEXT NOT NULL,
    	"xpos"	INTEGER NOT NULL,
    	"ypos"	INTEGER NOT NULL,
    	"start_channel"	INTEGER NOT NULL,
    	PRIMARY KEY("light_id" AUTOINCREMENT)
        )""")

    def create_lights_in_rigs_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Lights_in_rigs" (
    	"lights_in_rigs_id"	INTEGER NOT NULL UNIQUE,
    	"rig_id"	INTEGER NOT NULL,
    	"light_id"	INTEGER NOT NULL,
    	FOREIGN KEY("rig_id") REFERENCES "Rigs"("rig_id") ON DELETE CASCADE,
    	FOREIGN KEY("light_id") REFERENCES "Lights"("light_id") ON DELETE CASCADE,
    	PRIMARY KEY("lights_in_rigs_id" AUTOINCREMENT)
        )""")

    def create_lights_in_sequence_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Lights_in_sequence" (
    	"lights_in_sequence_id"	INTEGER NOT NULL UNIQUE,
    	"sequence_id"	INTEGER NOT NULL,
    	"light_id"	INTEGER NOT NULL,
    	FOREIGN KEY("light_id") REFERENCES "Lights"("light_id") ON DELETE CASCADE,
    	FOREIGN KEY("sequence_id") REFERENCES "Sequences"("sequence_id") ON DELETE CASCADE,
    	PRIMARY KEY("lights_in_sequence_id" AUTOINCREMENT)
        )""")
    def create_locations_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Locations" (
    	"location_id"	INTEGER NOT NULL UNIQUE,
    	"location_name"	TEXT NOT NULL,
    	PRIMARY KEY("location_id" AUTOINCREMENT)
        )""")
    def create_locations_in_account_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Locations_in_account" (
    	"locations_in_account_id"	INTEGER NOT NULL UNIQUE,
    	"account_id"	INTEGER NOT NULL,
    	"location_id"	INTEGER NOT NULL,
    	FOREIGN KEY("account_id") REFERENCES "Accounts"("account_id") ON DELETE CASCADE,
    	FOREIGN KEY("location_id") REFERENCES "Locations"("location_id") ON DELETE CASCADE,
    	PRIMARY KEY("locations_in_account_id" AUTOINCREMENT)
        )""")
    def create_playback_effects_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Playback_effects" (
    	"playback_effects_id"	INTEGER NOT NULL UNIQUE,
    	"playback_id"	INTEGER NOT NULL,
    	"light_effects_id"	INTEGER NOT NULL,
    	FOREIGN KEY("playback_id") REFERENCES "Playbacks"("playback_id") ON DELETE CASCADE,
    	PRIMARY KEY("playback_effects_id" AUTOINCREMENT),
    	FOREIGN KEY("light_effects_id") REFERENCES "Light_effects"("light_effects_id") ON DELETE CASCADE
        )""")

    def create_playbacked_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Playbacked" (
    	"playbacked_id"	INTEGER NOT NULL UNIQUE,
    	"playback_id"	INTEGER NOT NULL,
    	"channel_values_id"	INTEGER NOT NULL,
    	PRIMARY KEY("playbacked_id" AUTOINCREMENT),
    	FOREIGN KEY("playback_id") REFERENCES "Playbacks"("playback_id") ON DELETE CASCADE,
    	FOREIGN KEY("channel_values_id") REFERENCES "Channel_values"("channel_values_id") ON DELETE CASCADE
        )""")

    def create_playbacks_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Playbacks" (
    	"playback_id"	INTEGER NOT NULL UNIQUE,
    	"rig_id"	INTEGER NOT NULL,
    	"playback_name"	TEXT NOT NULL,
    	FOREIGN KEY("rig_id") REFERENCES "Rigs"("rig_id") ON DELETE CASCADE,
    	PRIMARY KEY("playback_id" AUTOINCREMENT)
        )""")

    def create_rectangles_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Rectangles" (
    	"rectangles_id"	INTEGER NOT NULL UNIQUE,
    	"width"	INTEGER NOT NULL,
    	"height"	INTEGER NOT NULL,
    	"xpos"	INTEGER NOT NULL,
    	"ypos"	INTEGER NOT NULL,
    	PRIMARY KEY("rectangles_id" AUTOINCREMENT)
        )""")

    def create_rectangles_in_locations_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Rectangles_in_locations" (
    	"rectangles_in_locations_id"	INTEGER NOT NULL UNIQUE,
    	"location_id"	INTEGER NOT NULL,
    	"rectangles_id"	INTEGER NOT NULL,
    	PRIMARY KEY("rectangles_in_locations_id" AUTOINCREMENT),
    	FOREIGN KEY("location_id") REFERENCES "Locations"("location_id") ON DELETE CASCADE,
    	FOREIGN KEY("rectangles_id") REFERENCES "Rectangles"("rectangles_id") ON DELETE CASCADE
        )""")

    def create_rigs_in_account_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Rigs_in_account" (
    	"rigs_in_account_id"	INTEGER NOT NULL UNIQUE,
    	"account_id"	INTEGER NOT NULL,
    	"rig_id"	INTEGER NOT NULL,
    	FOREIGN KEY("rig_id") REFERENCES "Rigs"("rig_id") ON DELETE CASCADE,
    	FOREIGN KEY("account_id") REFERENCES "Accounts"("account_id") ON DELETE CASCADE,
    	PRIMARY KEY("rigs_in_account_id" AUTOINCREMENT)
        )""")

    def create_rigs_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS  "Rigs" (
    	"rig_id"	INTEGER NOT NULL UNIQUE,
    	"rig_name"	TEXT NOT NULL,
    	PRIMARY KEY("rig_id" AUTOINCREMENT)
        )""")

    def create_sequence_playbacks_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Sequence_playbacks" (
    	"sequence_playback_id"	INTEGER NOT NULL UNIQUE,
    	"sequence_id"	INTEGER NOT NULL,
    	"playback_id"	INTEGER NOT NULL,
    	"time_delay"	REAL NOT NULL,
    	FOREIGN KEY("sequence_id") REFERENCES "Sequences"("sequence_id") ON DELETE CASCADE,
    	PRIMARY KEY("sequence_playback_id" AUTOINCREMENT),
    	FOREIGN KEY("playback_id") REFERENCES "Playbacks"("playback_id") ON DELETE CASCADE
        )""")

    def create_sequences_table(self):
        self.query_db("""CREATE TABLE IF NOT EXISTS "Sequences" (
    	"sequence_id"	INTEGER NOT NULL UNIQUE,
    	"rig_id"	INTEGER NOT NULL,
    	"sequence_name"	TEXT NOT NULL,
    	PRIMARY KEY("sequence_id" AUTOINCREMENT)
        )""")


if __name__ == "__main__":
    db_manager = Database_manager()
