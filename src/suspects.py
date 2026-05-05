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
        # Le dossier où se trouve le fichier XML (pour les chemins relatifs)
        dossier = Path(nom_fichier).parent

        # On parse le fichier XML
        arbre = ET.parse(nom_fichier)
        racine = arbre.getroot()

        suspects = []

        # Pour chaque <suspect> dans le XML
        for suspect_xml in racine.findall("suspect"):
            nom = suspect_xml.find("name").text

            # On construit la liste des LocationProvider de ce suspect
            providers = []
            for source in suspect_xml.find("sources").findall("source"):
                try:
                    type_source = source.find("type").text

                    if type_source == "Photographs":
                        chemin = dossier.joinpath(source.find("dir").text)
                        providers.append(PictureLocationProvider(str(chemin)))

                    elif type_source == "Wi-Fi":
                        chemin = dossier.joinpath(source.find("db").text)
                        user = source.find("username").text
                        providers.append(WifiLogsLocationProvider(str(chemin), user))

                    elif type_source == "Logs":
                        chemin = dossier.joinpath(source.find("file").text)
                        providers.append(LogsLocationProvider(str(chemin)))

                except Exception as erreur:
                    if Configuration.get_instance().get_element("verbose"):
                        print(f"Attention: Une erreur est survenue pendant le traitement de la source ({erreur})", file=sys.stderr)

            # On combine tous les providers en un seul (avec l'opérateur +)
            lp = providers[0]
            for p in providers[1:]:
                lp = lp + p

            suspects.append(Suspect(nom, lp))

        return suspects

    # TODO: (Alternative) implémenter une méthode similaire pour les fichiers JSON
    @staticmethod
    def create_suspects_from_json_file(nom_fichier):
        # Le dossier où se trouve le fichier JSON
        dossier = Path(nom_fichier).parent

        # On lit le fichier JSON
        with open(nom_fichier, "r") as f:
            donnees = json.load(f)

        suspects = []

        # Pour chaque suspect dans le JSON
        for suspect_dict in donnees["suspects"]:
            nom = suspect_dict["name"]

            providers = []
            for source in suspect_dict["sources"]:
                try:
                    type_source = source["type"]

                    if type_source == "Photographs":
                        chemin = dossier.joinpath(source["dir"])
                        providers.append(PictureLocationProvider(str(chemin)))

                    elif type_source == "Wi-Fi":
                        chemin = dossier.joinpath(source["db"])
                        providers.append(WifiLogsLocationProvider(str(chemin), source["username"]))

                    elif type_source == "Logs":
                        chemin = dossier.joinpath(source["file"])
                        providers.append(LogsLocationProvider(str(chemin)))

                except Exception as erreur:
                    if Configuration.get_instance().get_element("verbose"):
                        print(f"Attention: Une erreur est survenue pendant le traitement de la source ({erreur})", file=sys.stderr)

            # On combine les providers
            lp = providers[0]
            for p in providers[1:]:
                lp = lp + p

            suspects.append(Suspect(nom, lp))

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
