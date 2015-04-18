#!/usr/bin/env bash
export NIT_LOG_LEVEL=INFO

rm a b c

nit init --force

echo a > a

nit add a
nit status

nit commit
nit status

echo b > b

nit add b
nit status

echo a2 > a

nit add a
nit status

nit commit
nit status

nit add ñ
nit status

nit commit
nit status
