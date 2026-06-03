"""This module provides the various Location base classes."""

from __future__ import annotations

__email__ = "kevin.huguenin@unil.ch"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2026, The Information Security and Privacy Lab at the University of Lausanne (https://www.unil.ch/isplab/)"

import base64
import math
import os
import sys
import tempfile
import ssl
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Self, TextIO, override
from urllib.parse import urlencode
from urllib.request import urlopen
import certifi

import folium
from PySide6.QtCore import QCoreApplication, QLoggingCategory, QUrl
from PySide6.QtGui import QIcon
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication

if TYPE_CHECKING:
    from collections.abc import Callable

try:
    from src import utils
    from src.configuration import Configuration
except ImportError:
    import utils
    from configuration import Configuration


def _configure_qt_webengine_logging() -> None:
    """Suppress noisy Chromium backend fallback logs emitted by Qt WebEngine."""
    existing_flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "").split()
    extra_flags = ["--disable-logging", "--log-level=3"]
    merged_flags = [*existing_flags]
    for flag in extra_flags:
        if flag not in merged_flags:
            merged_flags.append(flag)
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(merged_flags).strip()


_configure_qt_webengine_logging()


def _build_ssl_context() -> ssl.SSLContext:
    """Builds an SSL context with an explicit CA bundle when available."""
    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()


SSL_CONTEXT = _build_ssl_context()

import json
class MapsApiAdapter(ABC):
    """Adapter interface for map-related API operations."""

    # TODO: Déclarer une méthode get_place_name 
    # Déclarer cette méthode comme abstraite et définir sa signature.
    # Elle doit accepter en paramètre une latitude et une longitude (flottants)
    # et retourner un nom de lieu lisible par un humain (str).
    @abstractmethod
    def get_place_name(self, latitude: float, longitude: float) -> str:
        pass #implementee plus loin dans le fichier

    # TODO: Déclarer une méthode get_travel_distance_and_time
    # Déclarer cette méthode comme abstraite et définir sa signature.
    # Elle doit accepter en paramètre une origine et une destination (tuples de flottants)
    # ainsi qu'un mode de transport (str, "walking" par défaut),
    # et renvoyer un tuple contenant la distance en mètres (int)
    # et la durée du trajet (timedelta).  @abstractmethod
    def get_travel_distance_and_time(self, origin: tuple[float, float], destination: tuple[float, float], mode: str = "walking",) -> tuple[int, timedelta]:
        pass #implementee plus loin dans le fichier


class GoogleMapsApiAdapter(MapsApiAdapter):
    _BASE_URL = "https://maps.googleapis.com/maps/api"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    # TODO: Implémenter une méthode d'instance permettant de vérifier si une clé API GoogleMaps existe
    def _check_api_key(self) -> None:
        if not self._api_key:
            raise ValueError("Google Maps API key is not set.")

    def set_api_key(self, api_key: str) -> None:
        self._api_key = api_key

    def _request_json(self, endpoint: str, params: dict[str, str]) -> dict:
        params_requete = params.copy()  # pas modifier dico original
        params_requete["key"] = self._api_key
        params_url = urlencode(params_requete)
        url = self._BASE_URL + "/" + endpoint + "/json?" + params_url
        reponse = urlopen(url, context=SSL_CONTEXT)
        contenu = reponse.read().decode("utf-8")
        return json.loads(contenu)

    @override
    def get_place_name(self, latitude: float, longitude: float) -> str:
        # TODO: Implémenter le géocodage inverse via l'endpoint "geocode" de Google Maps.
        # - Appeler _request_json avec les coordonnées (latitude,longitude)
        #   et la langue "fr-FR".
        # - Extraire le nom de lieu depuis le premier résultat retourné.
        #   Attention : si le premier composant d'adresse est de type "plus_code",
        #   utiliser le deuxième résultat à la place.
        # - En cas d'erreur, renvoyer la chaîne "unknown"
        #   (et affichez un avertissement sur stderr si le mode verbose est activé).
        # aide sur l'api ici : https://developers.google.com/maps/documentation/geocoding/requests-reverse-geocoding

        parametres = {
            "latlng": f"{latitude},{longitude}",
            "language": "fr-FR",
        }

        try:
            donnees = self._request_json("geocode", parametres)

            if donnees["status"] != "OK":
                if Configuration.get_instance().get_element("verbose"):
                    print(f"erreur API Geocoding ({donnees['status']})", file=sys.stderr)
                return "unknown"

            resultats = donnees["results"]

            if len(resultats) == 0:
                return "unknown"

            resultat = resultats[0]

            premier_composant = resultat["address_components"][0]

            if "plus_code" in premier_composant["types"]:
                if len(resultats) < 2:
                    return "unknown"
                resultat = resultats[1]

            return resultat["formatted_address"]

        except Exception as erreur:
            if Configuration.get_instance().get_element("verbose"):
                print(f"erreur API Geocoding ({erreur})", file=sys.stderr)
            return "unknown"

    @override
    def get_travel_distance_and_time(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        mode: str = "walking",
    ) -> tuple[int, timedelta]:
        # TODO: Implémenter le calcul de distance et de durée via l'endpoint
        # "distancematrix" de Google Maps.
        # - Appeler _request_json avec l'origine, la destination, le mode
        #   de transport, les unités métriques et la langue "fr-FR".
        # - Extraire la distance (en mètres, int) et la durée (en secondes,
        #   à convertir en timedelta) depuis la réponse.
        # - Renvoyer un tuple (distance, durée).
        # doc : https://developers.google.com/maps/documentation/distance-matrix/distance-matrix
       
        parametres={
            "origins": f"{origin[0]},{origin[1]}",
            "destinations": f"{destination[0]},{destination[1]}",
            "mode": mode,
            "units": "metric",
            "language": "fr-FR",
        }

        donnees = self._request_json("distancematrix", parametres)
        element = donnees["rows"][0]["elements"][0]
        distance_metres = element["distance"]["value"]
        duree_secondes = element["duration"]["value"]

        duree = timedelta(seconds=duree_secondes)

        return distance_metres, duree

        #TP 4 si api marche pas ?
        # if Configuration.get_instance().get_element("verbose"):
        #     print(f"Attention: erreur API Distance Matrix ({erreur}), fallback Haversine", file=sys.stderr)

        # r = 6371000  # rayon de la Terre en mètres
        # lat1 = math.radians(origin[0])
        # lon1 = math.radians(origin[1])
        # lat2 = math.radians(destination[0])
        # lon2 = math.radians(destination[1])
        # dlat = lat2 - lat1
        # dlon = lon2 - lon1
        # a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        # c = 2 * math.asin(math.sqrt(a))
        # distance_metres = int(r * c)

        # vitesse_m_par_s = 4.0 * 1000 / 3600  # 4 km/h en m/s
        # duree_secondes = distance_metres / vitesse_m_par_s
        # duree = timedelta(seconds=duree_secondes)

        # return (distance_metres, duree)

# TODO: Définir la classe Location désignant des objets contenant une latitude
#       et une longitude.
class Location:
    # Attribut de classe partagé par toutes les Location
    _api_adapter: MapsApiAdapter | None = None

    # TODO: Implémenter le constructeur et les getters.
    def __init__(self, latitude, longitude):
        self.__latitude = float(latitude)
        self.__longitude = float(longitude)

    # TODO: Implémenter la méthode __str__ pour afficher une Location de la
    #       forme suivante (en limitant le nombre de décimales à 5).
    # Location [latitude: 48.85479, longitude: 2.34756]
    @override
    def __str__(self):
        return f"Location [latitude: {self.__latitude:.5f}, longitude: {self.__longitude:.5f}]"

    __repr__ = __str__

    @classmethod #Section X verif config api ?
    def _check_adapter_init(location):
        if location._api_adapter is None:
            raise ValueError("Spécifier un Adapter valide pour utiliser l'API du SIG. Utiliser Location.set_maps_adapter(...)")

    @classmethod
    def set_maps_adapter(location, adapter):
        location._api_adapter = adapter

    def get_latitude(self):
        return self.__latitude

    def get_longitude(self):
        return self.__longitude

    # TODO: Définir une méthode get_name(self) -> str qui retourne, en utilisant
    #       GoogleMapsApiAdapter qui envoie une requête API de reverse geocoding, le nom
    #       correspondant aux coordonnées contenues dans l'objet Location.
    # "Avenue de la Gare 46, 1003 Lausanne, Suisse" pour 46.517738, 6.632233
    def get_name(self):
        adapter = Location._api_adapter # GOOGLE APi
        nom = adapter.get_place_name(self.__latitude, self.__longitude)
        return nom

    # TODO: Implémenter la méthode get_travel_distance_and_time qui renvoie le
    #       couple (distance, temps) pour atteindre le lieu correspondant à un
    #       autre objet Location, en utilisant GoogleMapsApiAdapter qui envoie 
    #       requête HTTP urllib vers un service d'itinéraires.
    def get_travel_distance_and_time(self, other) -> tuple[int, timedelta]:
        # Source : Google Maps Distance Matrix API
        # Doc officielle : https://developers.google.com/maps/documentation/distance-matrix/overview
        adapter = Location._api_adapter

        # demandé par la doc Google "origins" et "destinations"
        origine = (self.__latitude, self.__longitude)
        destination = (other.get_latitude(), other.get_longitude())

        #mode "walking" 
        resultat = adapter.get_travel_distance_and_time(origine, destination, "walking")
        distance = resultat[0]
        temps = resultat[1]
        return (distance, temps)

    # TP : à utiliser ?
    def verif_lat(self):
        if self.__latitude < -90 or self.__latitude > 90:
            raise ValueError("La latitude doit être comprise entre -90 et 90 !")
    
    # TP : à utiliser ?
    def verif_long(self):
        if self.__longitude < -180 or self.__longitude > 180:
            raise ValueError("La longitude doit être comprise entre -180 et 180 !")


# TODO: Définir la classe LocationSample désignant des objets contenant un
#       datetime et un objet Location.
class LocationSample:
    # TODO: Implémenter le constructeur.
    def __init__(self, date, location, description=""):
        if not isinstance(location, Location):
            raise ValueError("location doit être une instance de Location !")
        if not isinstance(date, datetime):
            raise ValueError("date doit être une instance de datetime !")

        self.__date = date
        self.__location = location
        self.__description = description

    # TODO: Implémenter les getters.
    def get_location(self) -> Location:
        return self.__location

    def get_date(self) -> datetime:
        return self.__date

    def get_description(self) -> str:
        return self.__description

    # TODO: Implémenter la méthode __str__ pour afficher une LocationSample de la façon suivante:
    #       LocationSample [datetime: 2024-04-03 12:25:00, location: Location [latitude: 48.85479, longitude: 2.34756]]
    @override
    def __str__(self):
        return f"LocationSample [datetime: {self.__date}, location: {self.__location}]"

    __repr__ = __str__

    # TODO: Définir les opérateurs de comparaison. TOUS ???
    def __lt__(self, autre):
        return self.__date < autre.__date

    def __le__(self, autre):
        return self.__date <= autre.__date

    def __gt__(self, autre):
        return self.__date > autre.__date

    def __ge__(self, autre):
        return self.__date >= autre.__date

    def __eq__(self, autre):
        return self.__date == autre.__date

    def __ne__(self, autre):
        return self.__date != autre.__date


# TODO: Définir la classe abstraite LocationProvider qui permet de produire une
#       liste d'objets LocationSample.
#       Utiliser la classe ABC et le décorateur @abstractmethod de Python.
class LocationProvider(ABC):
    _app: QCoreApplication | None = None
    _web: QWebEngineView | None = None

    # TODO: Spécifier l'existence d'une méthode abstraite get_location_samples.
    @abstractmethod
    def get_location_samples(self):
        pass

    # TODO: Implémenter la méthode print_location_samples en utilisant
    #       get_location_samples (renvoyant une liste de LocationSample), qui
    #       affiche dans le terminal une chaîne de caractères décrivant des objets LocationSamples.
    def print_location_samples(self):
        l = self.get_location_samples()
        liste_str = []
        for i in l:
            liste_str.append(str(i))
        print(liste_str)

    # TODO: Implémenter la méthode get_surrounding_temporal_location_samples qui
    #       prend en paramètre un datetime et renvoie les objets LocationSample
    #       (via get_location_samples) situés juste avant et après le datetime.
    def get_surrounding_temporal_location_samples(self, date):
        l = self.get_location_samples()
        avant = None
        apres = None
        for i in l:
            if i.get_date() < date:
                avant = i
            else:
                apres = i
                break
        return (avant, apres)

    # TODO: Implémenter la méthode could_have_been_there qui prend en paramètre
    #       un LocationSample et renvoie si un suspect a eu le temps de s'y
    #       rendre.
    def could_have_been_there(self, locationsample):
        date_crime = locationsample.get_date()
        lieu_crime = locationsample.get_location()

        avant, apres = self.get_surrounding_temporal_location_samples(date_crime)
        possible = True

        if avant is not None:
            date_avant = avant.get_date()
            lieu_avant = avant.get_location()
            temps_disponible = date_crime - date_avant  # temps disponible entre le lieu avant et le crime
            resultat = lieu_avant.get_travel_distance_and_time(lieu_crime)
            temps_google = resultat[1]
            temps_minimum = temps_google / 2 # /2 comme spécifié dans la consigne
            if temps_disponible < temps_minimum:
                possible = False

        if apres is not None:
            date_apres = apres.get_date()
            lieu_apres = apres.get_location()
            temps_disponible = date_apres - date_crime
            resultat = lieu_crime.get_travel_distance_and_time(lieu_apres)
            temps_google = resultat[1]
            temps_minimum = temps_google / 2
            if temps_disponible < temps_minimum:
                possible = False

        return possible

    # TODO: Implémenter la méthode __str__ de sorte à afﬁcher un objet
    #       LocationProvider sous la forme suivante :
    #       LocationProvider (5 location samples)
    def __str__(self):
        l = self.get_location_samples()
        nbr_samples = len(l)
        return f"{self.__class__.__name__} ({nbr_samples} location samples)"

    __repr__: Callable[[Self], str] = __str__

    def __add__(self, other):
        return CompositeLocationProvider(self, other)

    # Cette fonction est donnée, vous n'avez pas besoin de la modifier.
    def show_location_samples(
    self,
    marker: LocationSample | None = None,
    show_path: bool = False,
    title: str | None = None,
) -> None:
        """Displays the location samples using clickable markers on an interactive map."""

        def verbose_print(message: str, file: TextIO = sys.stdout) -> None:
            try:
                if Configuration.get_instance().get_element(key="verbose", default=False):
                    print(message, file=file)
            except (AttributeError, KeyError):
                print(message, file=file)

        def add_arrowhead(from_: tuple, to_: tuple, map: folium.Map, color: str = "#3388ff"):
            lat_diff = to_[0] - from_[0]
            lon_diff = to_[1] - from_[1]
            bearing = (math.degrees(math.atan2(
                lon_diff * math.cos(math.radians((to_[0] + from_[0]) / 2)), lat_diff
            )) + 270) % 360
            arrow_pos = (from_[0] + (to_[0] - from_[0]) * 0.97, from_[1] + (to_[1] - from_[1]) * 0.97)
            folium.RegularPolygonMarker(
                location=arrow_pos, fill=True, fillColor=color,
                number_of_sides=3, radius=8, rotation=round(bearing),
            ).add_to(map)

        def make_popup(local_ts: str, original_ts: str, description: str) -> folium.Popup:
            return folium.Popup(
                folium.Html(
                    f"<strong>Heure locale: {local_ts}</strong><br /><br />"
                    f"Heure source: {original_ts}<br /> Source: {description}",
                    script=True,
                ),
                max_width=270,
            )

        def to_local(ts) -> str:
            return ts.astimezone(timezone(timedelta(hours=2))).strftime("%Y-%m-%d at %I:%M:%S%p %Z")

        def to_utc_str(ts) -> str:
            return ts.strftime("%Y-%m-%d at %I:%M:%S%p %Z")

        samples = self.get_location_samples()
        if not samples:
            return

        # --- Qt setup ---
        QLoggingCategory.setFilterRules("*.info=false")
        if self.__class__._app is None:
            self.__class__._app = QApplication.instance() or QApplication()
            icon = Path(__file__).parent / "sherlock.png"
            if icon.is_file():
                self.__class__._app.setWindowIcon(QIcon(str(icon)))

        if self.__class__._web is None:
            self.__class__._web = QWebEngineView()
            for attr in [
                QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,
                QWebEngineSettings.WebAttribute.JavascriptEnabled,
            ]:
                self.__class__._web.settings().setAttribute(attr, True)

        web = self.__class__._web
        web.setWindowTitle(f"Trace de mobilité {f'({title})' if title else ''}")

        # --- Data extraction ---
        coords = [(s.get_location().get_latitude(), s.get_location().get_longitude()) for s in samples]
        timestamps = [s.get_date() for s in samples]
        try:
            descriptions = [s.get_description() for s in samples]
        except AttributeError:
            descriptions = [""] * len(samples)

        # --- Build map ---
        k = base64.b64decode("cGsuZXlKMUlqb2lhWE53YkdGaUxYVnVhV3dpTENKaElqb2lZMm94ZUdsNGVURnVNREF3WVRKeGJ6QjBiWGcxZG14emNDSjkuZDE0ZGxkWUg1TnByYWNCUEYzWDRwZw==").decode()
        folium_map = folium.Map(
            location=coords[0], zoom_start=15, detect_retina=False, API_key=k,
            tiles=f"https://api.mapbox.com/styles/v1/mapbox/streets-v10/tiles/256/{{z}}/{{x}}/{{y}}?access_token={k}",
            attr="Mapbox",
        )

        folium.PolyLine(locations=coords).add_to(folium_map)
        for prev, next_ in zip(coords, coords[1:]):
            add_arrowhead(prev, next_, folium_map)

        for coord, ts, desc in zip(coords, timestamps, descriptions):
            make_popup(to_local(ts), to_utc_str(ts), desc).add_to(
                folium.Marker(coord).add_to(folium_map)
            )

        # --- Optional extra marker ---
        if marker is not None:
            coord = (marker.get_location().get_latitude(), marker.get_location().get_longitude())
            popup = make_popup(to_local(marker.get_date()), to_utc_str(marker.get_date()), marker.get_description())
            folium.Marker(coord, popup=popup, icon=folium.Icon(color="red")).add_to(folium_map)
            coords.append(coord)

            if show_path:
                ls_before, ls_after = self.get_surrounding_temporal_location_samples(marker.get_date())
                for ls, is_before in [(ls_before, True), (ls_after, False)]:
                    if ls is None:
                        continue
                    dt_actual = marker.get_date() - ls.get_date() if is_before else ls.get_date() - marker.get_date()
                    try:
                        src, dst = (ls.get_location(), marker.get_location()) if is_before else (marker.get_location(), ls.get_location())
                        _, dt_needed = src.get_travel_distance_and_time(dst)
                    except:
                        dt_needed = "Pas disponible"
                    path_popup = folium.Popup(folium.Html(
                        f'Temps vers le lieu du crime :</br><ul style="margin-left:-2em;">'
                        f"<li>Réel : {dt_actual}</li><li>Google Maps : {dt_needed}</li></ul>",
                        script=True,
                    ))
                    line_coords = [(s.get_location().get_latitude(), s.get_location().get_longitude()) for s in ([ls, marker] if is_before else [marker, ls])]
                    folium.PolyLine(popup=path_popup, locations=line_coords, color="red", weight=2).add_to(folium_map)

        # --- Render ---
        folium_map.fit_bounds(coords)
        _, tmp_path = tempfile.mkstemp(prefix="sherlock_", suffix="_map.html")
        verbose_print(f"Creating temporary file for the map '{tmp_path}'")
        folium_map.save(tmp_path)
        web.load(QUrl(Path(tmp_path).resolve().as_uri()))
        web.show()

        status = self.__class__._app.exec()
        if status != 0:
            verbose_print(f"Warning: QApplication finished with exit code {status}", file=sys.stderr)

        try:
            Path(tmp_path).unlink()
        except OSError as e:
            verbose_print(f"Warning: Error removing temporary file ({e})", file=sys.stderr)


# TODO: Implémenter la classe ListLocationProvider.
class ListLocationProvider(LocationProvider):
    def __init__(self, liste):
        self.__samples = sorted(deepcopy(liste))

    @override
    def get_location_samples(self):
        return deepcopy(self.__samples)


# TODO: Créer une classe qui implémente le patron de conception Composite
#       pour la classe LocationProvider.
class CompositeLocationProvider(LocationProvider):
    # La classe CompositeLocationProvider contient "deux" LocationProvider
    # TODO: Définir le constructeur.
    def __init__(self, lp1: LocationProvider, lp2: LocationProvider):
        self.__lp1 = lp1
        self.__lp2 = lp2

    # TODO: Implémenter la méthode get_location_samples.
    @override
    def get_location_samples(self):
        return sorted(self.__lp1.get_location_samples() + self.__lp2.get_location_samples())

    # TODO: Définir la méthode __str__.
    @override
    def __str__(self):
        nbr_samples = len(self.get_location_samples())
        ligne_principale = f"{self.__class__.__name__} ({nbr_samples} location samples)"
        enfant1 = utils.indent(f"+\t{self.__lp1}")
        enfant2 = utils.indent(f"+\t{self.__lp2}")
        return f"{ligne_principale}\n{enfant1}\n{enfant2}"


if __name__ == "__main__":
        # Tester l'implémentation de cette classe avec les instructions de ce bloc
    # main (le résultat attendu est affiché ci-dessous).
    Configuration.get_instance().add_element("verbose", True)
    # TODO: mettre a jour la clé d'API Google
    Location.set_maps_adapter(GoogleMapsApiAdapter("AIzaSyBGrCeG_x0e8YuFAIcosvJKREJuHR6Tdoo")) # TODO: Ajouter votre clé Google pour tester

    # Time zone
    zurich_tz = timezone(timedelta(hours=2))

    # Locations
    paris = Location(48.854788, 2.347557)
    lausanne = Location(46.517738, 6.632233)
    crime_scene = Location(46.52273, 6.58081)
    nearby = Location(46.521045, 6.574664)
    print(lausanne.get_name())

    # Location samples
    paris_sample = LocationSample(
        datetime(2026, 3, 3, 12, 25, tzinfo=zurich_tz), paris, "Paris"
    )
    lausanne_sample = LocationSample(
        datetime(2026, 3, 3, 14, 56, 5, tzinfo=zurich_tz), lausanne, "Lausanne"
    )
    crime = LocationSample(
        datetime(2026, 3, 17, 15, 52, 31, tzinfo=zurich_tz), crime_scene, "Crime"
    )

    print(paris_sample.get_location())
    print(paris_sample.get_date())
    print(paris_sample)
    print(paris_sample < lausanne_sample)

    # Sorting
    samples = sorted([lausanne_sample, paris_sample])
    print([str(s) for s in samples])

    # Distance/time from crime scene to nearby location
    print(crime_scene.get_travel_distance_and_time(nearby))

    # Location providers
    main_provider = ListLocationProvider([paris_sample, lausanne_sample])
    crime_provider = ListLocationProvider([crime])

    print(main_provider.get_location_samples())
    main_provider.show_location_samples()

    # Test de l'opérateur __add__
    print(main_provider + crime_provider)

    ### Résultat attendu ###

    # Av. Sainte-Luce 8, 1003 Lausanne, Suisse
    # Location [latitude: 48.85479, longitude: 2.34756]
    # 2026-03-03 12:25:00+02:00
    # LocationSample [datetime: 2026-03-03 12:25:00+02:00, location: Location [latitude: 48.85479, longitude: 2.34756]]
    # True
    # ['LocationSample [datetime: 2026-03-03 12:25:00+02:00, location: Location [latitude: 48.85479, longitude: 2.34756]]', 'LocationSample [datetime: 2026-03-03 14:56:05+02:00, location: Location [latitude: 46.51774, longitude: 6.63223]]']
    # (549, datetime.timedelta(seconds=493))
    # [LocationSample(datetime.datetime(2026, 3, 3, 12, 25, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))), Location(48.854788, 2.347557), 'Paris'), LocationSample(datetime.datetime(2026, 3, 3, 14, 56, 5, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))), Location(46.517738, 6.632233), 'Lausanne')]
    # Creating temporary file for the map to be displayed '/var/folders/9y/7k97pqb533b1w3hc60xpjly40000gn/T/sherlock_jn3e6l53_map.html'
    # CompositeLocationProvider (3 location samples)
    # +      ListLocationProvider (2 location samples)
    # +      ListLocationProvider (1 location samples)