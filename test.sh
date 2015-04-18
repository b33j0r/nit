#!/usr/bin/env bash
export NIT_DEBUG_LEVEL=TRACE

rm a b c

nit init --force

echo a > a

nit add a
nit commit

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
