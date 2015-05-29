#!/usr/bin/env bash

rm -rf ~/nit_test_proj2
mkdir ~/nit_test_proj2
cd ~/nit_test_proj2
nit init
echo a > a
nit add a
nit commit -m "added a:a"
echo b > b
nit add b
nit commit -m "added b:b"
nit log
