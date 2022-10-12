# SPDX-FileCopyrightText: 2021 Bluesy1 <68259537+Bluesy1@users.noreply.github.com>
# SPDX-License-Identifier: MIT

# Dice
error =
    { $user }:
    Error argumento inválido:
     Los dados especificados solo pueden ser d<int>, o si un modificador constante debe ser un entero perfecto, positivo o negativo, conectado con `+`, y sin espacios.
success = { $user } arrojó `{ $dice }` y obtuvo `{ $result }`para un total de `{ $total }`.
