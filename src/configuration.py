"""This module provides the Configuration singleton class."""

__email__ = "kevin.huguenin@unil.ch"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2026, The Information Security and Privacy Lab at the University of Lausanne (https://www.unil.ch/isplab/)"


# TODO: Créer une classe Configuration contenant:
#       - une structure de données adéquate pour stocker des couples
#         clefs-valeurs pour les paramètres de configuration
#       - une méthode add_element pour ajouter un nouvel élément
#       - une méthode get_element pour récupérer la valeur d'un paramètre à
#         partir de sa clef


# TODO: Utiliser le patron de conception Singleton pour cette classe, pour
#       manipuler la configuration de manière globale dans tout le programme.
class Configuration:
    instance = None #singleton
    dico: dict = {}

    def __init__(self):
        self.dico = {}

    @classmethod
    def get_instance(configuration):
        if configuration.instance == None:
            configuration.instance = Configuration()
        return configuration.instance

    def add_element(self, key, value):
        self.dico[key] = value

    def get_element(self, key, default=None):
        if key in self.dico:
            return self.dico[key]
        return default

    def __str__(self):
        return str(self.dico)


if __name__ == "__main__":
    conf = Configuration.get_instance()

    conf.add_element('verbose', True)
    conf.add_element('N', 6)
    print(conf)

    max = conf.get_element('max', 42)
    print(max, conf.get_element('max'), conf.get_element('verbose'))

    print(conf == Configuration.get_instance())

    ### Résultat attendu ###
    # {'verbose': True, 'N': 6}
    # 42 None True
    # True
