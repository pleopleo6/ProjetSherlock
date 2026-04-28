"""This module provides the Configuration singleton class."""

from __future__ import annotations

import datetime

__email__ = "kevin.huguenin@unil.ch"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2026, The Information Security and Privacy Lab at the University of Lausanne (https://www.unil.ch/isplab/)"

from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from datetime import date, datetime


# TODO: Créer une classe Configuration contenant:
#       - une structure de données adéquate pour stocker des couples
#         clefs-valeurs pour les paramètres de configuration
#       - une méthode add_element pour ajouter un nouvel élément
#       - une méthode get_element pour récupérer la valeur d'un paramètre à
#         partir de sa clef


# TODO: Utiliser le patron de conception Singleton pour cette classe, pour
#       manipuler la configuration de manière globale dans tout le programme.
class Configuration:
    def __init__() -> None: ...

    def add_element() -> None: ...

    def get_element() -> bool | str | float | date | datetime | None: ...


if __name__ == "__main__":
    pass
    # conf: Configuration = Configuration.get_instance()

    # conf.add_element('verbose', True)
    # conf.add_element('N', 6)
    # print(conf)

    # max = conf.get_element('max', 42)
    # print(max, conf.get_element('max'), conf.get_element('verbose'))

    # print(conf == Configuration.get_instance())

    ### Résultat attendu ###

    # {'verbose': True, 'N': 6}
    # 42 None True
    # True
