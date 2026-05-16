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
class WifiLogsLocationProvider(ListLocationProvider):
    # TODO: Implémenter le constructeur.
    def __init__(self, path, username) -> None:
        self.__db = path
        self.__username = username

        # 1) On se connecte à la base SQLite
        connexion = sqlite3.connect(self.__db)

        # 2) On utilise dict_factory pour récupérer les résultats sous forme de dict
        connexion.row_factory = WifiLogsLocationProvider.dict_factory

        # 3) On crée un curseur pour exécuter la requête
        curseur = connexion.cursor()

        # 4) On écrit la requête SQL avec deux JOIN et un WHERE
        #    On trie directement par timestamp pour avoir l'ordre chronologique
        requete = """
            SELECT location_samples.timestamp, hotspots.latitude, hotspots.longitude
            FROM location_samples
            JOIN users ON location_samples.uid = users.id
            JOIN hotspots ON location_samples.hid = hotspots.id
            WHERE users.name = ?
            ORDER BY location_samples.timestamp
        """

        # 5) On exécute la requête avec le nom d'utilisateur comme paramètre
        curseur.execute(requete, (self.__username,))

        # 6) On récupère tous les résultats
        resultats = curseur.fetchall()

        # 7) On crée une liste de LocationSample
        samples = []
        for ligne in resultats:
            # Le timestamp est un entier (epoch Unix), on le convertit en datetime UTC+2
            date = datetime.fromtimestamp(ligne["timestamp"], tz=timezone(timedelta(hours=2)))

            # On crée la Location à partir des coordonnées du hotspot
            lieu = Location(ligne["latitude"], ligne["longitude"])

            # On crée le LocationSample
            sample = LocationSample(date, lieu, f"Wi-Fi ({self.__username})")
            samples.append(sample)

        # 8) On ferme la connexion
        connexion.close()

        # 9) On passe la liste au parent (ListLocationProvider)
        super().__init__(samples)

    # TODO: Redéfinir la méthode __str__.
    @override
    def __str__(self) -> str:
        nb = len(self.get_location_samples())
        return f"WifiLogsLocationProvider (source: '{self.__db}', user '{self.__username}', {nb} location samples)"

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