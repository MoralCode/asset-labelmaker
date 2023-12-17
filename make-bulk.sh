#!/bin/bash
# $1 - testing mode - set this varible to enable

#Parallel runs in N-process batches
# https://unix.stackexchange.com/a/216475/

OUTPUTDIR="output/"
PREFIX="E"

function make_batch {
	# $1 - startng id
	# $2 - ending id
	# $3 - style (default: "default")
	# $4 - batch size (default: 5)
	# $5 - outputdir 
	STYLE="${3:-default}"
	echo $1
	echo $2
	#batch size
	N="${4:-5}"
	(
	for id in $(seq -w $1 $2); do 
	((i=i%N)); ((i++==0)) && wait
		pipenv run python3 ./labelgen.py --label "$PREFIX$id" --qr --barcode --configsection "$STYLE" --output "$5$PREFIX$id.png" &
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
	# $4 - outputdir 

	pipenv run python3 ./labelgen.py --label "$PREFIX$1" --barcode --qr --propertylabel "$3" --configsection "$2" --output "$4$PREFIX$1.png"
}


function make_batch_hrm {
	# $1 - startng id
	# $2 - ending id
	# $3 - style (default: "default")
	# $4 -batch size (default: 5)
	# $5 - property label
	# $6 - outputdir 
	STYLE="${3:-default}"
	echo $1
	echo $2
	#batch size
	N="${4:-5}"
	(
	for id in $(seq -w $1 $2); do 
	((i=i%N)); ((i++==0)) && wait
		make_hrm "$id" "$STYLE" "BT# $id" "$6"  &
	done
	wait
	echo "Done."
	exit 0
	)

}


if [ -z ${1+x} ];
then
	# generation mode
	echo "generation mode"

	mkdir -p "$OUTPUTDIR"

	# PREFIX="ERG"
	# make_batch 0051 0075 Full
	# PREFIX="MON"
	# make_batch 0051 0075 Half
	PREFIX="HRM"
	# make_batch_hrm 0001 0025 Qtr
	make_hrm 0001 Qtr "BT#27508" "$OUTPUTDIR"
	make_hrm 0002 Qtr "BT#26964" "$OUTPUTDIR"
	make_hrm 0003 Qtr "BT#58677" "$OUTPUTDIR"
	make_hrm 0004 Qtr "BT#26849" "$OUTPUTDIR"
	make_hrm 0005 Qtr "BT#27096" "$OUTPUTDIR"
	make_hrm 0006 Qtr "BT#58595" "$OUTPUTDIR"
	make_hrm 0007 Qtr "BT#26807" "$OUTPUTDIR"
	make_hrm 0008 Qtr "BT#60344" "$OUTPUTDIR"
	make_hrm 0009 Qtr "BT#26906" "$OUTPUTDIR"
	make_hrm 0010 Qtr "BT#58696" "$OUTPUTDIR"
	make_hrm 0011 Qtr "BT#58555" "$OUTPUTDIR"
	make_hrm 0012 Qtr "BT#27516" "$OUTPUTDIR"
	make_hrm 0013 Qtr "BT#26773" "$OUTPUTDIR"
	make_hrm 0014 Qtr "BT#26795" "$OUTPUTDIR"
	make_hrm 0015 Qtr "BT#     " "$OUTPUTDIR"
	make_hrm 0016 Qtr "BT#     " "$OUTPUTDIR"
	make_hrm 0017 Qtr "BT#     " "$OUTPUTDIR"
	make_hrm 0018 Qtr "BT#     " "$OUTPUTDIR"
	make_hrm 0019 Qtr "BT#     " "$OUTPUTDIR"
	make_hrm 0020 Qtr "BT#     " "$OUTPUTDIR"
	make_hrm 0021 Qtr "BT#     " "$OUTPUTDIR"
	make_hrm 0022 Qtr "BT#     " "$OUTPUTDIR"
	make_hrm 0023 Qtr "BT#     " "$OUTPUTDIR"
	make_hrm 0024 Qtr "BT#     " "$OUTPUTDIR"
else
	# testing mode 
	echo "testing mode"

	OUTPUTDIR="${OUTPUTDIR}test/"

	mkdir -p "$OUTPUTDIR"

	# testing/validation
	PREFIX="HRM"
	make_hrm 0001 Qtr "BT#00000" "$OUTPUTDIR"
	PREFIX="ERG"
	make_batch 0001 0001 Full 5 "$OUTPUTDIR"
	PREFIX="MON"
	make_batch 0001 0001 Half 5 "$OUTPUTDIR"
fi