#!/bin/bash

#Parallel runs in N-process batches
# https://unix.stackexchange.com/a/216475/

OUTPUTDIR="output/"
PREFIX="E"

function make_batch {
	# $1 - startng id
	# $2 - ending id
	# $3 - style (default: "default")
	# $4 -batch size (default: 5)
	STYLE="${3:-default}"
	echo $1
	echo $2
	#batch size
	N="${4:-5}"
	(
	for id in $(seq -w $1 $2); do 
	((i=i%N)); ((i++==0)) && wait
		pipenv run python3 ./labelgen.py --label "$PREFIX$id" --qr --barcode --configsection "$STYLE" --output "$OUTPUTDIR$PREFIX$id.png" &
	done
	wait
	echo "Done."
	exit 0
	)

}

function make_hrm {
	# $1 - id
	# $2 - style
	# $3 - property label

	pipenv run python3 ./labelgen.py --label "$PREFIX$1" --barcode --propertylabel "$3" --configsection "$2" --output "$OUTPUTDIR$PREFIX$1.png"
}


function make_batch_hrm {
	# $1 - startng id
	# $2 - ending id
	# $3 - style (default: "default")
	# $4 -batch size (default: 5)
	# $5 - property label
	STYLE="${3:-default}"
	echo $1
	echo $2
	#batch size
	N="${4:-5}"
	(
	for id in $(seq -w $1 $2); do 
	((i=i%N)); ((i++==0)) && wait
		make_hrm "$id" "$STYLE" "BT# $id"  &
	done
	wait
	echo "Done."
	exit 0
	)

}

mkdir -p "$OUTPUTDIR"

PREFIX="DEMO"
make_batch 0001 0015 Full