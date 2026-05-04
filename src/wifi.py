"""This module is the WifiLogsLocationProvider class."""

from __future__ import annotations

__email__ = "kevin.huguenin@unil.ch"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2026, The Information Security and Privacy Lab at the University of Lausanne (https://www.unil.ch/isplab/)"

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from sqlite3 import Connection
from typing import Any, override

try:
    from src.configuration import Configuration
    from src.location import ListLocationProvider, Location, LocationSample
except ImportError:
    from configuration import Configuration
    from location import ListLocationProvider, Location, LocationSample


# TODO: Définir la classe WifiLogsLocationProvider.
class WifiLogsLocationProvider:
    # TODO: Implémenter le constructeur.
    def __init__() -> None: ...

    # TODO: Redéfinir la méthode __str__.
    @override
    def __str__() -> str: ...

    @staticmethod
    def dict_factory(cursor: Connection, row: tuple) -> dict[str, Any]:
        """Dictionary factory to be used as a row_factory for SQL connection.

        It enables the use of query results as dictionaries.

        Args:
            cursor (Connection): The database cursor.
            row (tuple): The row data.

        Returns:
            dict: A dictionary containing all the row information where keys are column names and values are the values
                  stored in the given `row` for those columns.

        Examples:
            con = sqlite3.connect(":memory:")
            con.row_factory = dict_factory
            cur = con.cursor()
            cur.execute("select 1 as a")
            print(cur.fetchone()["a"])

        References:
            https://docs.python.org/3.6/library/sqlite3.html#sqlite3.Connection.row_factory
        """
        # noinspection PyUnresolvedReferences
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


if __name__ == "__main__":
    # Tester l'implémentation de cette classe avec les instructions de ce bloc
    # main (le résultat attendu est affiché ci-dessous).
    Configuration.get_instance().add_element("verbose", True)
    lp = WifiLogsLocationProvider("./data/db/wifi.db", "mbron")
    print(lp)
    lp.print_location_samples()

    ### Résultat attendu ###

    # WifiLogsLocationProvider (source: 'data/db/wifi.db', user 'mbron', 3 location samples)
    # LocationSample [datetime: 2026-03-17 15:49:02+02:00, location: Location [latitude: 46.52173, longitude: 6.58566]]
    # LocationSample [datetime: 2026-03-17 15:51:54+02:00, location: Location [latitude: 46.52157, longitude: 6.58306]]
    # LocationSample [datetime: 2026-03-17 16:01:06+02:00, location: Location [latitude: 46.52062, longitude: 6.57427]]