#!/bin/bash

if [ ! -e "originals" ]
then
    mkdir originals
    cp transmogrify/tests/testdata/horiz_img.jpg originals/
    cp transmogrify/tests/testdata/square_img.jpg originals/
    cp transmogrify/tests/testdata/vert_img.jpg originals/
fi
if [ ! -e "modified" ]
then
    mkdir modified
fi
if [ ! -e "originals/external" ]
then
    mkdir originals/external
fi
export TRANSMOGRIFY_BASE_PATH=`pwd`/modified
export TRANSMOGRIFY_ORIG_BASE_PATH=`pwd`/originals
export TRANSMOGRIFY_SECRET="debug"
export TRANSMOGRIFY_DEBUG=1
python -m transmogrify.wsgi