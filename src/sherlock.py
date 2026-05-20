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
    configurationClasse = Configuration.get_instance()
    formatDate = "%d/%m/%Y-%H:%M:%S"
    date_crime = datetime.strptime(args.date, formatDate) #enoncé à vérifier si ça marche
    configurationClasse.add_element("verbose", args.verbose)
    configurationClasse.add_element("suspects", args.suspects)
    configurationClasse.add_element("geo_api_key", args.geo_api_key)
    configurationClasse.add_element("latitude", args.latitude)
    configurationClasse.add_element("longitude", args.longitude)
    configurationClasse.add_element("crime_date", date_crime)

    # TODO: Afficher le message d'accueil du logiciel.
    try:
        from src.location import GoogleMapsApiAdapter
    except ImportError:
        from location import GoogleMapsApiAdapter
    Location.set_maps_adapter(GoogleMapsApiAdapter(args.geo_api_key))
    crime_location = Location(args.latitude, args.longitude)
    
    #print checker la strcture du print pour qu'il soit indentique à la consigne
    print(f"Investigation liée au crime du {date_crime.strftime('%d/%m/%Y à %H:%M:%S')} @ "f"{crime_location.get_name()} ({crime_location.get_latitude():.5f},{crime_location.get_longitude():.5f})")

    # TODO: Lire le fichier suspect, l'analyser, construire les objets Suspect
    #       correspondants et les stocker dans une liste. Utiliser les méthodes
    #       createObjectFromXMLFile() / createObjectFromJSONFile().
    # Créer un objet Location décrivant le lieu du crime à partir de ses coordonnées (obtenues depuis la ligne de commande)
    if args.suspects.endswith(".json"):
        suspects = Suspect.create_suspects_from_json_file(args.suspects)
    else:
        suspects = Suspect.create_suspects_from_xml_file(args.suspects)
    crime_sample = LocationSample(
        date_crime.replace(tzinfo=timezone(timedelta(hours=2))),
        crime_location,
        "Lieu du crime",
    )

    # TODO: Pour chaque suspect, déterminer s'il a pu se rendre et repartir du
    #       lieu du crime.
    print("\nSuspects plausibles :")
    for s in suspects:
        if s.get_location_provider().could_have_been_there(crime_sample):
            print(f" - {s.get_name()}")
