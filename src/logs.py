"""This module provides the LogsLocationProvider class."""

from __future__ import annotations

__email__ = "kevin.huguenin@unil.ch"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2026, The Information Security and Privacy Lab at the University of Lausanne (https://www.unil.ch/isplab/)"

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import override

try:
    from src.location import ListLocationProvider, Location, LocationSample
except ImportError:
    from location import ListLocationProvider, Location, LocationSample


# TODO: Définir la classe LogsLocationProvider qui désigne des objets
#       LocationProvider obtenus à partir de logs.
class LogsLocationProvider(ListLocationProvider):
    # TODO: Implémenter le constructeur où l'on définit en attribut le nom du
    #       fichier de log et où l'on construit la liste de samples.
    def __init__(self, fichier) -> None:
        # L'attribut contenant le nom du fichier est privé et l'attribut
        # _samples est hérité de ListLocationProvider
        self.__file_name = fichier

        # TODO: parcourir les logs et filtrer ceux qui contiennent des appels
        #       GPS valides (coordonnées + temps).
        # On écrit une regex qui capture timestamp + lat + lng et qui exige "source: GPS"
        motif = re.compile(
            r"\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\.\d+\]"
            r".*?coordinates:\s*\(['\"]?(-?\d+\.\d+)['\"]?,\s*"
            r"['\"]?(-?\d+\.\d+)['\"]?\),\s*source:\s*GPS"
        )

        samples = []
        fichier_ouvert = open(self.__file_name, "r")
        for ligne in fichier_ouvert:
            ligne = ligne.strip()
            resultat = motif.search(ligne)
            if resultat is None:
                continue

            # TODO: filtrer le log et extraire les données temporelles, créer un
            #       datetime.
            timestamp_str = resultat.group(1)
            date = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
            date = date.replace(tzinfo=timezone(timedelta(hours=2)))

            # TODO: filtrer le log et extraire les données GPS.
            lat = float(resultat.group(2))
            lng = float(resultat.group(3))

            # TODO: retourner un triplet contenant le datetime, la latitude et la
            #       longitude.
            triplet = (date, lat, lng)

            # TODO: Générer un sample pour chaque log valide et l'ajouter à une
            #       liste temporaire.
            #       Appeler ensuite super en passant cette liste temporaire pour
            #       définir l'attribut _samples
            lieu = Location(triplet[1], triplet[2])
            sample = LocationSample(triplet[0], lieu, f"Log GPS ({self.__file_name})")
            samples.append(sample)

        fichier_ouvert.close()
        super().__init__(samples)

    # TODO: Implémenter la méthode __str__ pour afficher les objets de la forme
    #       suivante.
    # LogsLocationProvider (source: ../data/logs/cblanco.log, 2 location samples)

    @override
    def __str__(self) -> str:
        nb = len(self.get_location_samples())
        return f"LogsLocationProvider (source: {self.__file_name}, {nb} location samples)"


if __name__ == "__main__":
    # Tester l'implémentation de cette classe avec les instructions de ce bloc
    # main (le résultat attendu est affiché ci-dessous).

    lp = LogsLocationProvider("./data/logs/ltoussaint.log")
    
    print(lp)
    lp.show_location_samples()
    lp.print_location_samples()

    ### Résultat attendu ###

    # LogsLocationProvider (source: /Users/admin/.../Info2-Proj-2026/info2-project/data/logs/ltoussaint.log, 4 location samples)
    # LocationSample [datetime: 2026-03-17 15:48:11+03:00, location: Location [latitude: 46.52181, longitude: 6.57870]]
    # LocationSample [datetime: 2026-03-17 15:50:59+03:00, location: Location [latitude: 46.52259, longitude: 6.58003]]
    # LocationSample [datetime: 2026-03-17 15:55:31+03:00, location: Location [latitude: 46.52258, longitude: 6.58066]]
    # LocationSample [datetime: 2026-03-17 15:59:26+03:00, location: Location [latitude: 46.52272, longitude: 6.58127]]
