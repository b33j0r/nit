#!/usr/bin/env bash
export NIT_LOG_LEVEL=INFO

rm a b

nit init --force

echo a > a

echo nit add a
nit add a

echo nit status
nit status

echo nit commit
nit commit
echo nit status
nit status

echo b > b

echo nit add b
nit add b
echo nit status
nit status

echo a2 > a

echo nit add a
nit add a
echo nit status
nit status

echo nit commit
nit commit
echo nit status
nit status

echo nit add ñ
nit add ñ
echo nit status
nit status

echo nit commit
nit commit
echo nit status
nit status

