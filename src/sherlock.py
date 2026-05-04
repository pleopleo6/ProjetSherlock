#!python3
"""This module is the main entrypoint of the program."""

from __future__ import annotations

__email__ = "kevin.huguenin@unil.ch"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2026, The Information Security and Privacy Lab at the University of Lausanne (https://www.unil.ch/isplab/)"

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from src.configuration import Configuration
    from src.location import Location, LocationSample
    from src.suspects import Suspect
except ImportError:
    from configuration import Configuration
    from location import Location, LocationSample
    from suspects import Suspect

DESCRIPTION = (
    "Identifie les suspect.e.s les plus plausibles à partir de leurs traces de mobilité (issues de "
    "sources multiples incluant les localisations contenues dans les traces Wi-Fi et les flux de photos "
    "géo-taggées) pour un crime spécifié par une date/heure et une localisation."
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    # TODO: Ajouter les différents arguments de la ligne de commande à
    #       l'analyseur "parser".

    # parser.add_argument( #marche pas
    #     "-h", "--help",
    #     action="store_true",
    #     help="show this help message and exit",
    # )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="affiche les détails de l'exécution du programme et les avertissements.",
    )
    parser.add_argument(
        "-s", "--suspects",
        required=True,
        help="fichier contenant la liste des suspect.e.s et les sources de données de localisation.",
    )
    parser.add_argument(
        "-g", "--geo-api-key",
        required=True,
        help="clé pour l'accès à l'API du SIG.",
    )
    parser.add_argument(
        "-lat", "--latitude",
        required=True,
        type=float,
        help="latitude de la scène du crime.",
    )
    parser.add_argument(
        "-lng", "--longitude",
        required=True,
        type=float,
        help="longitude de la scène du crime.",
    )
    parser.add_argument(
        "-d", "--date",
        required=True,
        help="date et heure du crime (au format JJ/MM/AAAA-hh:mm, par exemple 17/03/2026-15:52:31).",
    )

    args = parser.parse_args()

    # TODO: Stocker les paramètres importants dans un objet Configuration
    #       accessible depuis tous les modules du programme.

    # TODO: Afficher le message d'accueil du logiciel.

    # TODO: Lire le fichier suspect, l'analyser, construire les objets Suspect
    #       correspondants et les stocker dans une liste. Utiliser les méthodes
    #       createObjectFromXMLFile() / createObjectFromJSONFile().

    # TODO: Pour chaque suspect, déterminer s'il a pu se rendre et repartir du
    #       lieu du crime.
