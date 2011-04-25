#!/bin/bash
pushd docs
rm -Rf _build
make html
popd
mkdir -p scout/public/docs
rm -Rf scout/public/docs/*
cp -R docs/_build/html/* scout/public/docs
