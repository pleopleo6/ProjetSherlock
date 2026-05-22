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
        # groupe 1 : date
        # groupe 2 : latitude
        # groupe 3 : longitude
        motif = re.compile(
            r"\[(.*?)\].*"
            r"coordinates:\s*\((-?\d+\.\d+),\s*(-?\d+\.\d+)\).*"
            r"source:\s*GPS"
        )
        
        samples = []
        fichier_ouvert = open(self.__file_name, "r")
        for ligne in fichier_ouvert:
            ligne = ligne.strip()
            resultat = motif.search(ligne)

            # Si la ligne ne correspond pas, on l'ignore
            if resultat is None:
                continue

            # TODO: filtrer le log et extraire les données temporelles, créer un
            #       datetime.
            timestamp_str = resultat.group(1)

            # On enlève les millisecondes
            timestamp_str = timestamp_str.split(".")[0]

            date = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
            date = date.replace(tzinfo=timezone(timedelta(hours=2)))

            # TODO: filtrer le log et extraire les données GPS.
            latitude = float(resultat.group(2))
            longitude = float(resultat.group(3))

            # TODO: retourner un triplet contenant le datetime, la latitude et la
            #       longitude.
            triplet = (date, latitude, longitude)

            # TODO: Générer un sample pour chaque log valide et l'ajouter à une
            #       liste temporaire.
            #       Appeler ensuite super en passant cette liste temporaire pour
            #       définir l'attribut _samples
            lieu = Location(triplet[1], triplet[2])
            sample = LocationSample(triplet[0],lieu,f"log GPS ({self.__file_name})")
            samples.append(sample)

        fichier_ouvert.close()
        super().__init__(samples)

    # TODO: Implémenter la méthode __str__ pour afficher les objets de la forme
    #       suivante.
    # LogsLocationProvider (source: ../data/logs/cblanco.log, 2 location samples)
    @override
    def __str__(self) -> str:
        nombre = len(self.get_location_samples())
        return f"LogsLocationProvider (source: {self.__file_name}, {nombre} location samples)"

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
