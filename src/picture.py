"""This modules provides the PictureLocationProvider class."""

from __future__ import annotations

__email__ = "kevin.huguenin@unil.ch"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2026, The Information Security and Privacy Lab at the University of Lausanne (https://www.unil.ch/isplab/)"

import sys
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, override

import exifread

if TYPE_CHECKING:
    from exifread.classes import IfdTag

try:
    from src.configuration import Configuration
    from src.location import ListLocationProvider, Location, LocationSample
except ImportError:
    from configuration import Configuration
    from location import ListLocationProvider, Location, LocationSample


# TODO: Définir la classe PictureLocationProvider qui désigne des objets
#       LocationProvider obtenus à partir d'images.
class PictureLocationProvider(ListLocationProvider):
    # TODO: Définir les extensions valides et un getter pour y accéder.
    # Attribut de classe : les extensions de fichiers acceptées (tuple = non modifiable)
    fichier_accepte = (".JPG", ".JPEG", ".jpg", ".jpeg")

    # TODO: Implémenter le constructeur.
    def __init__(self, directory: str) -> None:
        self.__dir: Path = Path(directory)

        # TODO: Utiliser le paramètre 'description' du constructeur de LocationSample
        #       pour garder une trace de l'origine de chaque image
        # samples doit contenir les LocationSample.
        samples: list[LocationSample] = []

        # TODO: scanner le répertoire contenant les photos prises par le suspect
        #       et extraire un objet LocationSample pour les photos ayant une
        #       extension valide (et qui contiennent des informations de
        #       localisation).
        for fichier in self.__dir.iterdir():
            extension = fichier.suffix

            if extension not in self.fichier_accepte: #verif des extemsions autorisées
                continue

            informations = PictureLocationProvider._extract_location_sample_from_picture(fichier)

            date = informations[0]
            lat = informations[1]
            lng = informations[2]

            manque_date = date is None
            mauque_lat = lat is None
            manque_long = lng is None

            if manque_date or mauque_lat or manque_long:

                configuration = Configuration.get_instance()
                verbose = configuration.get_element("verbose")

                if verbose:
                    nom_fichier = fichier.name
                    print(f"fichier ignoré :'{nom_fichier}'")
                continue

            lieu = Location(lat, lng)
            chemin_fichier = str(fichier)
            sample = LocationSample(date, lieu, chemin_fichier)
            samples.append(sample)

        super().__init__(samples)

    def get_validfichier_accepte(self) -> tuple[str, ...]:
        return self.fichier_accepte

    # TODO: Redéfinir la méthode __str__ pour afficher les objets sous la forme
    #       suivante :
    # PictureLocationProvider (source: '../ data/pics /jdoe’ (JPG,JPEG,jpg,jpeg), 2 location samples)
    @override
    def __str__(self) -> str:
        nb = len(self.get_location_samples())
        extensions = ",".join(self.fichier_accepte)
        return f"PictureLocationProvider (source: '{self.__dir}' ({extensions}), {nb} location samples)"

    @staticmethod
    def _convert_to_degrees(value: IfdTag) -> float:
        """Converts the GPS coordinates in a photo to float values.

        Args:
            value: IfdTag containing GPS coordinates information.

        Returns:
            Coordinate value converted to float.
        """
        d = float(value.values[0].num) / float(value.values[0].den)
        m = float(value.values[1].num) / float(value.values[1].den)
        s = float(value.values[2].num) / float(value.values[2].den)

        return d + (m / 60.0) + (s / 3600.0)

    # TODO: Compléter la méthode _extract_location_sample_from_picture.
    @staticmethod
    def _extract_location_sample_from_picture(
        filename: str | Path,
    ) -> tuple[datetime | None, float | None, float | None]:
        """Extracts the time, latitude, and longitude from the EXIF in the file.

        If the data is not available, None is returned for the missing type of
        information.

        Args:
            filename: Path to the file that should be opened.

        Returns:
            Tuple containing the time, latitude, and longitude (if available)
            that was extracted from the EXIF tags of `filename`.
        """
        t = None
        lat = None
        lng = None

        with open(filename, "rb") as f:
            exif_data = exifread.process_file(f)

            gps_latitude = exif_data.get("GPS GPSLatitude")
            gps_latitude_ref = exif_data.get("GPS GPSLatitudeRef")
            gps_longitude = exif_data.get("GPS GPSLongitude")
            gps_longitude_ref = exif_data.get("GPS GPSLongitudeRef")

            # Check that all GPS data was extracted
            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat = PictureLocationProvider._convert_to_degrees(gps_latitude)
                if gps_latitude_ref.values[0] != "N":
                    lat = -lat

                lng = PictureLocationProvider._convert_to_degrees(gps_longitude)
                if gps_longitude_ref.values[0] != "E":
                    lng = -lng

            # Even better, use the GPS information: it is in UTC format, and it
            # corresponds to the time at which the GPS coordinates were
            # acquired, not the time at which the photo was shot per se.
            date = exif_data.get("GPS GPSDate")
            timestamp = exif_data.get("GPS GPSTimeStamp")

            # TODO: Convertir la date (au format textuel) contenue dans le EXIF
            #       tag en datetime et le stocker dans la variable t.
            # date.values  ressemble à "2026:03:17"  (chaîne)
            # timestamp.values  ressemble à [13, 52, 46]  (heure, minutes, secondes)
            if date is not None and timestamp is not None:
                time = timestamp.values
                heures = time[0]
                minutes = time[1]
                secondes = time[2]

                date_complete = f"{date.values} {heures}:{minutes}:{secondes}"
                t = datetime.strptime(date_complete, "%Y:%m:%d %H:%M:%S")
                t = t.replace(tzinfo=UTC) # remplacment en UTC
               

        return t, lat, lng


if __name__ == "__main__":
    # Tester l'implémentation de cette classe avec les instructions de ce bloc
    # main (le résultat attendu est affiché ci-dessous).
    Configuration.get_instance().add_element("verbose", True)
    lp = PictureLocationProvider("./data/pics/cdebella")
    print(lp)
    lp.show_location_samples()
    lp.print_location_samples()

    ### Résultat attendu ###

    # Warning: Skipping file 'IMG_0003.jpg' (Missing time and/or location information.)
    # PictureLocationProvider (source: 'data/pics/cdebella' (.JPG,.JPEG,.jpg,.jpeg), 2 location samples)
    # Creating temporary file for the map to be displayed '/var/folders/9y/7k97pqb533b1w3hc60xpjly40000gn/T/sherlock_6t7tf803_map.html'
    # LocationSample [datetime: 2026-03-17 13:52:46+00:00, location: Location [latitude: 46.52266, longitude: 6.58026]]
    # LocationSample [datetime: 2026-03-17 13:56:12+00:00, location: Location [latitude: 46.52167, longitude: 6.57814]]
