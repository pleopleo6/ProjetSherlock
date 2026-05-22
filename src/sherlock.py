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
    # on récupère l'instance unique de Configuration (singleton)
    configuration = Configuration.get_instance()

    # convertit date
    format_date = "%d/%m/%Y-%H:%M:%S"
    date_crime = datetime.strptime(args.date, format_date)

    configuration.add_element("verbose", args.verbose)
    configuration.add_element("suspects", args.suspects)
    configuration.add_element("geo_api_key", args.geo_api_key)
    configuration.add_element("latitude", args.latitude)
    configuration.add_element("longitude", args.longitude)
    configuration.add_element("crime_date", date_crime)

    # TODO: Afficher le message d'accueil du logiciel.
    # on importe ici GoogleMapsApiAdapter (depuis location)
    try:
        from src.location import GoogleMapsApiAdapter
    except ImportError:
        from location import GoogleMapsApiAdapter

    cle_api = args.geo_api_key
    adapter_google = GoogleMapsApiAdapter(cle_api)
    Location.set_maps_adapter(adapter_google)
    lieu_crime = Location(args.latitude, args.longitude)
    date_formatee = date_crime.strftime("%d/%m/%Y à %H:%M:%S")
    nom_lieu = lieu_crime.get_name()
    lat_arrondie = round(lieu_crime.get_latitude(), 5)
    lng_arrondie = round(lieu_crime.get_longitude(), 5)

    message_accueil = f"Investigation liée au crime du {date_formatee} @ {nom_lieu} ({lat_arrondie},{lng_arrondie})"
    print(message_accueil)

    # TODO: Lire le fichier suspect, l'analyser, construire les objets Suspect
    #       correspondants et les stocker dans une liste. Utiliser les méthodes
    #       createObjectFromXMLFile() / createObjectFromJSONFile().
    # Créer un objet Location décrivant le lieu du crime à partir de ses coordonnées (obtenues depuis la ligne de commande)
    fichier_suspects = args.suspects
    if fichier_suspects.endswith(".json"):
        liste_suspects = Suspect.create_suspects_from_json_file(fichier_suspects)
    else:
        liste_suspects = Suspect.create_suspects_from_xml_file(fichier_suspects)

    #fuseau horaire UTC+2
    fuseau_horaire = timezone(timedelta(hours=2))
    date_crime_avec_tz = date_crime.replace(tzinfo=fuseau_horaire)
    sample_crime = LocationSample(date_crime_avec_tz, lieu_crime, "Lieu du crime")

    # TODO: Pour chaque suspect, déterminer s'il a pu se rendre et repartir du
    #       lieu du crime.
    print("\nSuspects plausibles :")
    suspects_plausibles = []

    for suspect in liste_suspects:
        try:
            provider = suspect.get_location_provider()
            a_pu_y_etre = provider.could_have_been_there(sample_crime)

            if a_pu_y_etre:
                nom_suspect = suspect.get_name()
                print(f" - {nom_suspect}")
                suspects_plausibles.append(suspect)
        except Exception as erreur:
            print(f"Errreur : {erreur}")

    # on affiche la carte pour chaque suspect plausible
    for suspect in suspects_plausibles:
        provider = suspect.get_location_provider()
        nom_suspect = suspect.get_name()
        provider.show_location_samples(marker=sample_crime, show_path=True, title=nom_suspect)