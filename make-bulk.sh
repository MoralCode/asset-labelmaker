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
		ASSETID="$PREFIX$id" OUTPUTDIR="$OUTPUTDIR" make $STYLE &
	done
	wait
	echo "Done."
	exit 0
	)

}

mkdir -p "$OUTPUTDIR"
