# ASSETID=
BARCODERAWTMP = "barcode$(ASSETID).eps"
BARCODETMP = "barcode$(ASSETID).png"
QRTMP = "qrcode$(ASSETID).png"
OUTPUT = "label-$(ASSETID).png"
PROPERTY_LABEL = "Property of RIT Rowing"
WIDTH = 875
# this is a bit of a hack to generate barcodes closer in size to the label itself to prevent issues when scaling the barcode. its value is the width of the label that the python script generates minus two times the padding value (to give it some space on the left and right)
BARCODE_WIDTH = 845

barcode:
	barcode -o $(BARCODERAWTMP) -b $(ASSETID) -n -e "128" -g "$(BARCODE_WIDTH)x$(BARCODE_HEIGHT)" -E
	convert $(BARCODERAWTMP) -colorspace RGB -background white -flatten $(BARCODETMP)
	rm $(BARCODERAWTMP)

qr:
	qrencode -o $(QRTMP) $(ASSETID)

#https://stackoverflow.com/questions/15229833/set-makefile-variable-inside-target

big: HEIGHT=625
big: BARCODE_HEIGHT=100
big: qr barcode
	pipenv run python3 ./labelgen.py --qr-path $(QRTMP) --barcode-path $(BARCODETMP) --label $(ASSETID) --width "$(WIDTH)" --height "$(HEIGHT)" --property $(PROPERTY_LABEL) --output $(OUTPUT)
	rm $(BARCODETMP) $(QRTMP)


small: HEIGHT=310
small: BARCODE_HEIGHT=60
small: qr barcode
	pipenv run python3 ./labelgen.py --qr-path $(QRTMP) --barcode-path $(BARCODETMP) --label $(ASSETID) --width "$(WIDTH)" --height "$(HEIGHT)" --property $(PROPERTY_LABEL) --output $(OUTPUT)
	rm $(BARCODETMP) $(QRTMP)


default: big

clean:
	rm $(OUTPUT)