"""This module provides utility functions."""

from __future__ import annotations

__email__ = "kevin.huguenin@unil.ch"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2026, The Information Security and Privacy Lab at the University of Lausanne (https://www.unil.ch/isplab/)"


# TODO: Implémenter une fonction indent qui prend en paramètre un texte (sous
#       forme de chaîne de caractère) et un espacement (par défaut '\t') et qui
#       ajoute l'espacement au début de chaque ligne du texte.
def indent(texte, espacement="\t"):
    lignes = texte.split("\n")
    texte2 = []

    for ligne in lignes:
        nouvelle_ligne = espacement + ligne
        texte2.append(nouvelle_ligne)
        
    return "\n".join(texte2)



if __name__ == "__main__":
    # Tester l'implémentation de cette classe avec les instructions de ce bloc
    # main (le résultat attendu est affiché ci-dessous).
    print(f"zero\n{indent('one\n' + indent('two\nthree', '\t-'))}")
