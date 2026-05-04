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

    args = parser.parse_args()

    # TODO: Stocker les paramètres importants dans un objet Configuration
    #       accessible depuis tous les modules du programme.

    # TODO: Afficher le message d'accueil du logiciel.

    # TODO: Lire le fichier suspect, l'analyser, construire les objets Suspect
    #       correspondants et les stocker dans une liste. Utiliser les méthodes
    #       createObjectFromXMLFile() / createObjectFromJSONFile().

    # TODO: Pour chaque suspect, déterminer s'il a pu se rendre et repartir du
    #       lieu du crime.
