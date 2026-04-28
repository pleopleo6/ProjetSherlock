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
class LogsLocationProvider:
    # TODO: Implémenter le constructeur où l'on définit en attribut le nom du
    #       fichier de log et où l'on construit la liste de samples.
    def __init__() -> None:
        ...
        # L'attribut contenant le nom du fichier est privé et l'attribut
        # _samples est hérité de ListLocationProvider

        # TODO: parcourir les logs et filtrer ceux qui contiennent des appels
        #       GPS valides (coordonnées + temps).

        # TODO: filtrer le log et extraire les données temporelles, créer un
        #       datetime.

        # TODO: filtrer le log et extraire les données GPS.

        # TODO: retourner un triplet contenant le datetime, la latitude et la
        #       longitude.

        # TODO: Générer un sample pour chaque log valide et l'ajouter à une
        #       liste temporaire.
        #       Appeler ensuite super en passant cette liste temporaire pour
        #       définir l'attribut _samples

    # TODO: Implémenter la méthode __str__ pour afficher les objets de la forme
    #       suivante.
    # LogsLocationProvider (source: ../data/logs/cblanco.log, 2 location samples)

    @override
    def __str__() -> str: ...


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
