#!/bin/bash

for i in {00001..00050}
do
	ASSETID="E$i" make default &
done