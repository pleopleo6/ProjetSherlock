"""
====================================================================
FICHIER PERSO - REECRITURE DES FONCTIONS "AI-LIKE"
====================================================================

UTILISATION:
    1. Mets ta cle API Google ci-dessous (sinon les tests Google sont skippes)
    2. Implemente chaque fonction (remplace le `pass`)
    3. Lance: python todo.py
       -> tu verras [OK] ou [FAIL] pour chaque fonction
    4. Quand tout est OK, copie la fonction dans le bon fichier de src/

Ordre suggere: de haut en bas (du plus AI-like au moins).
"""

import json
import re
import sqlite3
import ssl
import sys
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import certifi

# Pour les tests qui touchent a l'API Google, mets ta cle ici.
# Si laissee vide -> ces tests seront skippes.
API_KEY = ""

# Contexte SSL utilise par les requetes HTTP
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


# Pour les tests des couches plus hautes, on importe les classes du projet
sys.path.insert(0, str(Path(__file__).parent / "src"))
from location import Location, LocationSample, ListLocationProvider  # noqa: E402


# =====================================================================
# 1. MapsApiAdapter (classe abstraite)
#    Cible: src/location.py
# =====================================================================
# A FAIRE: une classe abstraite avec 2 methodes abstraites:
#   - get_place_name(latitude, longitude) -> str
#   - get_travel_distance_and_time(origin, destination, mode="walking")
#     -> tuple[int, timedelta]
# CONSEILS: heriter de ABC, decorateur @abstractmethod, corps = pass.

class MapsApiAdapter:  # TODO: heriter de ABC
    pass


# =====================================================================
# 2. GoogleMapsApiAdapter - constructeur + helpers
#    Cible: src/location.py
# =====================================================================
# A FAIRE:
#   - __init__(api_key): stocker dans self._api_key
#   - _check_api_key(): si vide -> raise ValueError
#   - set_api_key(api_key): remplace la cle
#   - _request_json(endpoint, params):
#       * verifier la cle
#       * ajouter "key" aux params
#       * construire l'URL: https://maps.googleapis.com/maps/api/<endpoint>/json?<encoded>
#       * urlopen(url, context=SSL_CONTEXT)
#       * lire/decoder/parser le JSON
#       * renvoyer le dict

class GoogleMapsApiAdapter(MapsApiAdapter):
    def __init__(self, api_key):
        pass

    def _check_api_key(self):
        pass

    def set_api_key(self, api_key):
        pass

    def _request_json(self, endpoint, params):
        pass

    # =================================================================
    # 3. get_place_name (Google Geocoding API)
    # =================================================================
    # A FAIRE:
    #   - params: {"latlng": "<lat>,<lng>", "language": "fr-FR"}
    #   - appeler self._request_json("geocode", params)
    #   - si status != "OK" -> retourner "unknown"
    #   - prendre results[0] (ou results[1] si address_components[0]
    #     types[0] == "plus_code")
    #   - renvoyer le champ "formatted_address"
    #   - try/except global -> retourner "unknown" si erreur
    def get_place_name(self, latitude, longitude):
        pass

    # =================================================================
    # 4. get_travel_distance_and_time (Google Distance Matrix API)
    # =================================================================
    # A FAIRE:
    #   - params: origins, destinations (format "lat,lng"), mode, units=metric, language=fr-FR
    #   - appeler self._request_json("distancematrix", params)
    #   - verifier status global puis status de l'element
    #   - element = donnees["rows"][0]["elements"][0]
    #   - distance = int(element["distance"]["value"])  # metres
    #   - duree = timedelta(seconds=int(element["duration"]["value"]))
    #   - retourner (distance, duree)
    def get_travel_distance_and_time(self, origin, destination, mode="walking"):
        pass


# =====================================================================
# 5. Location.get_name  (methode de la classe Location)
#    Cible: src/location.py (remplacer dans class Location)
# =====================================================================
# Pour pouvoir tester ici en isolation, on definit une fonction qui prend
# l'instance Location en parametre. Tu copieras le corps dans la methode
# get_name(self) de la classe Location.
#
# A FAIRE:
#   - Location._check_adapter_init()
#   - recuperer adapter = Location._api_adapter
#   - renvoyer adapter.get_place_name(lat, lng)

def location_get_name(location_instance):
    # TODO: meme logique que self.get_name() mais avec location_instance a la place de self
    pass


# =====================================================================
# 6. Location.get_travel_distance_and_time
#    Cible: src/location.py (remplacer dans class Location)
# =====================================================================
# A FAIRE:
#   - verifier adapter init
#   - construire les tuples (lat, lng) depuis self et other
#   - deleguer a adapter.get_travel_distance_and_time(...)
#   - retourner le tuple

def location_get_travel(location_self, location_other):
    # TODO
    pass


# =====================================================================
# 7. could_have_been_there  (methode de LocationProvider)
#    Cible: src/location.py
# =====================================================================
# A FAIRE:
#   - (avant, apres) = provider.get_surrounding_temporal_location_samples(sample.get_date())
#   - pour chaque cote present:
#       * temps_reel = difference des dates
#       * temps_api = provider API .get_travel_distance_and_time(...)[1]
#       * si temps_reel < temps_api / 2 -> renvoyer False
#   - sinon renvoyer True

def could_have_been_there(provider, location_sample):
    # TODO
    pass


# =====================================================================
# 8. WifiLogsLocationProvider.__init__
#    Cible: src/wifi.py
# =====================================================================
# A FAIRE: ouvrir SQLite, requete JOIN, convertir en LocationSample.
#   - tz=UTC+2 pour les timestamps
#   - SQL: SELECT timestamp, latitude, longitude FROM location_samples
#          JOIN users ON uid=users.id
#          JOIN hotspots ON hid=hotspots.id
#          WHERE users.name = ?
#          ORDER BY timestamp
# Renvoie la liste des LocationSample (la classe finale appellera super().__init__(liste))

def wifi_build_samples(db_path, username):
    # TODO: retourner list[LocationSample]
    pass


# =====================================================================
# 9. WifiLogsLocationProvider.__str__
# =====================================================================
# Format: WifiLogsLocationProvider (source: '<db>', user '<username>', N location samples)

def wifi_str(db_path, username, nb_samples):
    # TODO: retourner la chaine attendue
    pass


# =====================================================================
# 10. LogsLocationProvider.__init__
#     Cible: src/logs.py
# =====================================================================
# A FAIRE: parser le fichier log ligne par ligne avec une regex.
#   - garder seulement les lignes "source: GPS"
#   - extraire timestamp [YYYY-MM-DDTHH:MM:SS.xxx], lat, lng
#   - lat/lng peuvent etre entre guillemets ou pas
#   - tz=UTC+2
# Renvoie la liste des LocationSample.

def logs_build_samples(file_name):
    # TODO: retourner list[LocationSample]
    pass


# =====================================================================
# 11. LogsLocationProvider.__str__
# =====================================================================
# Format: LogsLocationProvider (source: <chemin>, N location samples)

def logs_str(file_name, nb_samples):
    # TODO: retourner la chaine attendue
    pass


# =====================================================================
# =====================================================================
#                         SYSTEME DE TESTS
# =====================================================================
# =====================================================================

# Compteurs globaux
_pass = 0
_fail = 0
_skip = 0


def check(nom, condition, detail=""):
    global _pass, _fail
    if condition:
        print(f"  [OK]   {nom}")
        _pass += 1
    else:
        print(f"  [FAIL] {nom}  {detail}")
        _fail += 1


def skip(nom, raison):
    global _skip
    print(f"  [SKIP] {nom}  ({raison})")
    _skip += 1


def test_1_maps_api_adapter():
    print("\n[1] MapsApiAdapter")
    check("classe abstraite (heriter de ABC)", issubclass(MapsApiAdapter, ABC))
    methods = ["get_place_name", "get_travel_distance_and_time"]
    for m in methods:
        check(f"methode abstraite '{m}'", getattr(MapsApiAdapter, m, None) is not None)
    # On verifie qu'on ne peut pas instancier
    try:
        MapsApiAdapter()
        check("ne peut pas etre instanciee directement", False)
    except TypeError:
        check("ne peut pas etre instanciee directement", True)


def test_2_google_adapter_core():
    print("\n[2] GoogleMapsApiAdapter constructeur + helpers")
    try:
        a = GoogleMapsApiAdapter("ma_cle")
        check("__init__ stocke la cle", getattr(a, "_api_key", None) == "ma_cle")
        a.set_api_key("autre")
        check("set_api_key remplace la cle", a._api_key == "autre")
    except Exception as e:
        check("instanciation", False, str(e))
        return
    # _check_api_key avec cle vide
    try:
        vide = GoogleMapsApiAdapter("")
        try:
            vide._check_api_key()
            check("_check_api_key leve si cle vide", False)
        except ValueError:
            check("_check_api_key leve si cle vide", True)
    except Exception as e:
        check("_check_api_key sur cle vide", False, str(e))


def test_3_get_place_name():
    print("\n[3] GoogleMapsApiAdapter.get_place_name")
    if not API_KEY:
        skip("get_place_name (Lausanne)", "API_KEY non definie")
        return
    a = GoogleMapsApiAdapter(API_KEY)
    nom = a.get_place_name(46.517738, 6.632233)
    check("renvoie une str", isinstance(nom, str))
    check("contient 'Lausanne' ou 'unknown'", ("Lausanne" in (nom or "")) or nom == "unknown",
          f"recu: {nom!r}")


def test_4_get_travel():
    print("\n[4] GoogleMapsApiAdapter.get_travel_distance_and_time")
    if not API_KEY:
        skip("get_travel (proche)", "API_KEY non definie")
        return
    a = GoogleMapsApiAdapter(API_KEY)
    res = a.get_travel_distance_and_time((46.52273, 6.58081), (46.521045, 6.574664))
    check("retourne un tuple de 2", isinstance(res, tuple) and len(res) == 2)
    if isinstance(res, tuple) and len(res) == 2:
        d, t = res
        check("distance est un int > 0", isinstance(d, int) and d > 0, f"recu: {d}")
        check("duree est un timedelta > 0", isinstance(t, timedelta) and t.total_seconds() > 0,
              f"recu: {t}")


def test_5_location_get_name():
    print("\n[5] location_get_name")
    if not API_KEY:
        skip("location_get_name", "API_KEY non definie")
        return
    Location.set_maps_adapter(GoogleMapsApiAdapter(API_KEY))
    loc = Location(46.517738, 6.632233)
    nom = location_get_name(loc)
    check("renvoie une str non vide", isinstance(nom, str) and len(nom) > 0, f"recu: {nom!r}")


def test_6_location_get_travel():
    print("\n[6] location_get_travel")
    if not API_KEY:
        skip("location_get_travel", "API_KEY non definie")
        return
    Location.set_maps_adapter(GoogleMapsApiAdapter(API_KEY))
    a = Location(46.52273, 6.58081)
    b = Location(46.521045, 6.574664)
    res = location_get_travel(a, b)
    check("retourne un tuple (distance, timedelta)",
          isinstance(res, tuple) and len(res) == 2
          and isinstance(res[0], int) and isinstance(res[1], timedelta),
          f"recu: {res}")


def test_7_could_have_been_there():
    print("\n[7] could_have_been_there")
    tz = timezone(timedelta(hours=2))
    crime = LocationSample(datetime(2026, 3, 17, 15, 52, 31, tzinfo=tz),
                           Location(46.522735, 6.580811), "crime")
    # Cree un provider avec 2 samples: un avant et un apres, tres proches en temps
    avant = LocationSample(datetime(2026, 3, 17, 15, 50, 0, tzinfo=tz),
                           Location(46.522, 6.580), "avant")
    apres = LocationSample(datetime(2026, 3, 17, 15, 55, 0, tzinfo=tz),
                           Location(46.523, 6.581), "apres")
    provider = ListLocationProvider([avant, apres])
    try:
        resultat = could_have_been_there(provider, crime)
        check("retourne un bool", isinstance(resultat, bool), f"recu: {resultat}")
    except Exception as e:
        check("execution sans crash", False, str(e))


def test_8_wifi_build_samples():
    print("\n[8] wifi_build_samples")
    db = "data/db/wifi.db"
    samples = wifi_build_samples(db, "mbron")
    check("retourne une liste", isinstance(samples, list), f"recu: {type(samples)}")
    if not isinstance(samples, list):
        return
    check("3 samples pour mbron", len(samples) == 3, f"recu: {len(samples)}")
    if len(samples) == 3:
        s0 = samples[0]
        check("element est un LocationSample", isinstance(s0, LocationSample))
        check("premier timestamp = 15:49:02 (UTC+2)",
              s0.get_date().strftime("%H:%M:%S %z") == "15:49:02 +0200",
              f"recu: {s0.get_date()}")


def test_9_wifi_str():
    print("\n[9] wifi_str")
    attendu = "WifiLogsLocationProvider (source: 'data/db/wifi.db', user 'mbron', 3 location samples)"
    obtenu = wifi_str("data/db/wifi.db", "mbron", 3)
    check("format attendu", obtenu == attendu, f"\n     attendu: {attendu}\n     obtenu : {obtenu}")


def test_10_logs_build_samples():
    print("\n[10] logs_build_samples")
    samples = logs_build_samples("data/logs/ltoussaint.log")
    check("retourne une liste", isinstance(samples, list))
    if not isinstance(samples, list):
        return
    check("4 samples GPS pour ltoussaint", len(samples) == 4, f"recu: {len(samples)}")
    if len(samples) == 4:
        s0 = samples[0]
        check("premier timestamp = 15:48:11 (UTC+2)",
              s0.get_date().strftime("%H:%M:%S %z") == "15:48:11 +0200",
              f"recu: {s0.get_date()}")
        check("premiere lat ~ 46.52181",
              abs(s0.get_location().get_latitude() - 46.5218117) < 1e-6)


def test_11_logs_str():
    print("\n[11] logs_str")
    attendu = "LogsLocationProvider (source: data/logs/ltoussaint.log, 4 location samples)"
    obtenu = logs_str("data/logs/ltoussaint.log", 4)
    check("format attendu", obtenu == attendu, f"\n     attendu: {attendu}\n     obtenu : {obtenu}")


def run_tests():
    print("=" * 60)
    print("  TESTS DES FONCTIONS A REECRIRE")
    print("=" * 60)
    if not API_KEY:
        print("  Note: API_KEY vide -> tests Google API seront SKIPPED")

    test_1_maps_api_adapter()
    test_2_google_adapter_core()
    test_3_get_place_name()
    test_4_get_travel()
    test_5_location_get_name()
    test_6_location_get_travel()
    test_7_could_have_been_there()
    test_8_wifi_build_samples()
    test_9_wifi_str()
    test_10_logs_build_samples()
    test_11_logs_str()

    print("\n" + "=" * 60)
    print(f"  Resultat: {_pass} OK, {_fail} FAIL, {_skip} SKIP")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
