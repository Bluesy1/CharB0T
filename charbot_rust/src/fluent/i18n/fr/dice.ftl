# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-License-Identifier: MIT

# Dice
error =
    { $user }:
    Erreur d'argument :
     Les dés spécifiés ne peuvent être que d<int>, ou si un modificateur constant il doit s'agir d'un entier parfait, positif ou négatif, connecté par `+`, et sans espace.
success = { $user } a roulé `{ $dice }` et a obtenu `{ $result }`pour un total de `{ $total }`.
