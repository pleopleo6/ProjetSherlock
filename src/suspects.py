"""This module provides the Suspect class."""

from __future__ import annotations

__email__ = "kevin.huguenin@unil.ch"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2026, The Information Security and Privacy Lab at the University of Lausanne (https://www.unil.ch/isplab/)"

import json
import sys
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Self, override
from xml.etree import ElementTree as ET

if TYPE_CHECKING:
    from collections.abc import Callable

try:
    from src.configuration import Configuration
    from src.location import CompositeLocationProvider, LocationProvider
    from src.logs import LogsLocationProvider
    from src.picture import PictureLocationProvider
    from src.wifi import WifiLogsLocationProvider
except ImportError:
    from configuration import Configuration
    from location import CompositeLocationProvider, LocationProvider
    from logs import LogsLocationProvider
    from picture import PictureLocationProvider
    from wifi import WifiLogsLocationProvider


# TODO: Définir la classe Suspect qui décrit des informations contenues dans un
#       fichier (nom, LocationProvider).
class Suspect:

    __nom = ""
    __lp = LocationProvider

    # TODO: Implémenter le constructeur et les getters
    def __init__(self, nom, lp):
        self.__nom = nom  
        self.__lp = lp     

    def get_name(self):
        return self.__nom

    def get_location_provider(self):
        return self.__lp

    # TODO: Définir la méthode __str__ pour afficher un Suspect de la manière
    #       suivante :
    # [Suspect] Name: jdoe, Location provider: PictureLocationProvider (source: ' ../ data/pics /jdoe' (JPG,JPEG,jpg,jpeg), 2 location samples)
    @override
    def __str__(self):
        return f"[Suspect] Name: {self.__nom}, Location provider: {self.__lp}"

    __repr__: Callable[[Self], str] = __str__

    # TODO: Implémenter une méthode create_suspects_from_xml_file qui prend un
    #       nom de fichier XML en paramètre et le parse pour créer une liste de
    #       suspects.
    @staticmethod
    def create_suspects_from_xml_file(nom_fichier):
        dossier = Path(nom_fichier).parent
        arbre = ET.parse(nom_fichier)
        racine = arbre.getroot()

        suspects = []
        for suspect_xml in racine.findall("suspect"):
            nom_xml = suspect_xml.find("name")
            nom = nom_xml.text
            providers = []

            sources_xml = suspect_xml.find("sources")
            for source_xml in sources_xml.findall("source"):
                try:
                    type_xml = source_xml.find("type")
                    type_source = type_xml.text

                    if type_source == "Photographs":
                        dossier_photos_xml = source_xml.find("dir")
                        dossier_photos = dossier_photos_xml.text
                        chemin = dossier.joinpath(dossier_photos)
                        provider = PictureLocationProvider(str(chemin))
                        providers.append(provider)
                    elif type_source == "Wi-Fi":
                        db_xml = source_xml.find("db")
                        username_xml = source_xml.find("username")
                        db = db_xml.text
                        username = username_xml.text
                        chemin = dossier.joinpath(db)
                        provider = WifiLogsLocationProvider(str(chemin), username)
                        providers.append(provider)

                    elif type_source == "Logs":
                        fichier_logs_xml = source_xml.find("file")
                        fichier_logs = fichier_logs_xml.text
                        chemin = dossier.joinpath(fichier_logs)
                        provider = LogsLocationProvider(str(chemin))
                        providers.append(provider)
                except Exception as erreur:
                    if Configuration.get_instance().get_element("verbose"):
                        print(f"erreur :  ({erreur})",file=sys.stderr)
            
            provider_final = providers[0]
            for provider in providers[1:]:
                provider_final = provider_final + provider

            suspect = Suspect(nom, provider_final)
            suspects.append(suspect)
        return suspects

    # TODO: (Alternative) implémenter une méthode similaire pour les fichiers JSON
    @staticmethod
    def create_suspects_from_json_file(nom_fichier):
        dossier = Path(nom_fichier).parent
        fichier = open(nom_fichier, "r")
        donnees = json.load(fichier)
        fichier.close()

        suspects = []

        suspects_json = donnees["suspects"]

        for suspect_json in suspects_json:
            nom = suspect_json["name"]
            providers = []
            sources_json = suspect_json["sources"]

            for source_json in sources_json:

                try:
                    type_source = source_json["type"]
                    if type_source == "Photographs":
                        dossier_photos = source_json["dir"]
                        chemin = dossier.joinpath(dossier_photos)
                        provider = PictureLocationProvider(str(chemin))
                        providers.append(provider)
                    elif type_source == "Wi-Fi":
                        db = source_json["db"]
                        username = source_json["username"]
                        chemin = dossier.joinpath(db)
                        provider = WifiLogsLocationProvider(str(chemin), username)
                        providers.append(provider)
                    elif type_source == "Logs":
                        fichier_logs = source_json["file"]
                        chemin = dossier.joinpath(fichier_logs)
                        provider = LogsLocationProvider(str(chemin))
                        providers.append(provider)
                except Exception as erreur:
                    if Configuration.get_instance().get_element("verbose"):
                        print(f"erreur : ({erreur})",file=sys.stderr)

            provider_final = providers[0]
            for provider in providers[1:]:
                provider_final = provider_final + provider
            suspect = Suspect(nom, provider_final)
            suspects.append(suspect)
        return suspects


if __name__ == "__main__":
    pass
    # Tester l'implémentation de cette classe avec les instructions de ce bloc
    # main (le résultat attendu est affiché ci-dessous).
    # Configuration.get_instance().add_element("verbose", True)
    Configuration.get_instance().add_element(
        "crime_date",
        datetime(2026, 5, 17, 15, 52, 31, tzinfo=timezone(timedelta(hours=2))),
    )

    brand = Suspect("hbrand", PictureLocationProvider("../data/pics/hbrand"))
    print(brand)

    suspects = Suspect.create_suspects_from_xml_file("../data/suspects.xml")
    print("\n".join(map(str, suspects)))

    suspects = Suspect.create_suspects_from_json_file("../data/suspects.json")
    print("\n".join(map(str, suspects)))

    ### Résultat attendu ###
    # [Suspect] Name: hbrand, Location provider: PictureLocationProvider (source: '../data/pics/hbrand' (.JPG,.JPEG,.jpg,.jpeg), 3 location samples)
    # [Suspect] Name: Miles Bron, Location provider: CompositeLocationProvider (5 location samples)
    # +      PictureLocationProvider (source: '/Users/frankressat/Documents/info2-project/data/pics/mbron' (.JPG,.JPEG,.jpg,.jpeg), 2 location samples)
    # +      WifiLogsLocationProvider (source: '/Users/frankressat/Documents/info2-project/data/db/wifi.db', user 'mbron', 3 location samples)
    # [Suspect] Name: Lionel Toussaint, Location provider: CompositeLocationProvider (5 location samples)
    # +      LogsLocationProvider (source: /Users/frankressat/Documents/info2-project/src/../data/../data/logs/ltoussaint.log, 4 location samples)
    # +      WifiLogsLocationProvider (source: '/Users/frankressat/Documents/info2-project/data/db/wifi.db', user 'ltoussaint', 1 location samples)
    # [Suspect] Name: Claire Debella, Location provider: CompositeLocationProvider (5 location samples)
    # +      PictureLocationProvider (source: '/Users/frankressat/Documents/info2-project/data/pics/cdebella' (.JPG,.JPEG,.jpg,.jpeg), 2 location samples)
    # +      LogsLocationProvider (source: /Users/frankressat/Documents/info2-project/src/../data/../data/logs/cdebella.log, 3 location samples)
    # [Suspect] Name: Birdie Jay, Location provider: CompositeLocationProvider (5 location samples)
    # +      PictureLocationProvider (source: '/Users/frankressat/Documents/info2-project/data/pics/bjay' (.JPG,.JPEG,.jpg,.jpeg), 2 location samples)
    # +      LogsLocationProvider (source: /Users/frankressat/Documents/info2-project/src/../data/../data/logs/bjay.log, 3 location samples)
    # [Suspect] Name: Duke Cody, Location provider: CompositeLocationProvider (5 location samples)
    # +      PictureLocationProvider (source: '/Users/frankressat/Documents/info2-project/data/pics/dcody' (.JPG,.JPEG,.jpg,.jpeg), 3 location samples)
    # +      WifiLogsLocationProvider (source: '/Users/frankressat/Documents/info2-project/data/db/wifi.db', user 'dcody', 2 location samples)
    # [Suspect] Name: Helen Brand, Location provider: CompositeLocationProvider (6 location samples)
    # +      CompositeLocationProvider (4 location samples)
    #         +      PictureLocationProvider (source: '/Users/frankressat/Documents/info2-project/data/pics/hbrand' (.JPG,.JPEG,.jpg,.jpeg), 3 location samples)
    #         +      LogsLocationProvider (source: /Users/frankressat/Documents/info2-project/src/../data/../data/logs/hbrand.log, 1 location samples)
    # +      WifiLogsLocationProvider (source: '/Users/frankressat/Documents/info2-project/data/db/wifi.db', user 'hbrand', 2 location samples)
    # [Suspect] Name: Miles Bron, Location provider: CompositeLocationProvider (5 location samples)
    # +      PictureLocationProvider (source: '../data/../data/pics/mbron' (.JPG,.JPEG,.jpg,.jpeg), 2 location samples)
    # +      WifiLogsLocationProvider (source: '../data/../data/db/wifi.db', user 'mbron', 3 location samples)
    # [Suspect] Name: Lionel Toussaint, Location provider: CompositeLocationProvider (5 location samples)
    # +      LogsLocationProvider (source: /Users/frankressat/Documents/info2-project/src/../data/../data/logs/ltoussaint.log, 4 location samples)
    # +      WifiLogsLocationProvider (source: '../data/../data/db/wifi.db', user 'ltoussaint', 1 location samples)
    # [Suspect] Name: Claire Debella, Location provider: CompositeLocationProvider (5 location samples)
    # +      PictureLocationProvider (source: '../data/../data/pics/cdebella' (.JPG,.JPEG,.jpg,.jpeg), 2 location samples)
    # +      LogsLocationProvider (source: /Users/frankressat/Documents/info2-project/src/../data/../data/logs/cdebella.log, 3 location samples)
    # [Suspect] Name: Birdie Jay, Location provider: CompositeLocationProvider (5 location samples)
    # +      PictureLocationProvider (source: '../data/../data/pics/bjay' (.JPG,.JPEG,.jpg,.jpeg), 2 location samples)
    # +      LogsLocationProvider (source: /Users/frankressat/Documents/info2-project/src/../data/../data/logs/bjay.log, 3 location samples)
    # [Suspect] Name: Duke Cody, Location provider: CompositeLocationProvider (5 location samples)
    # +      PictureLocationProvider (source: '../data/../data/pics/dcody' (.JPG,.JPEG,.jpg,.jpeg), 3 location samples)
    # +      WifiLogsLocationProvider (source: '../data/../data/db/wifi.db', user 'dcody', 2 location samples)
    # [Suspect] Name: Helen Brand, Location provider: CompositeLocationProvider (6 location samples)
    # +      CompositeLocationProvider (4 location samples)
    #         +      PictureLocationProvider (source: '../data/../data/pics/hbrand' (.JPG,.JPEG,.jpg,.jpeg), 3 location samples)
    #         +      LogsLocationProvider (source: /Users/frankressat/Documents/info2-project/src/../data/../data/logs/hbrand.log, 1 location samples)
    # +      WifiLogsLocationProvider (source: '../data/../data/db/wifi.db', user 'hbrand', 2 location samples)
