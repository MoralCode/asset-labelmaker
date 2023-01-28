# ASSETID=
TMPDIR=labelgen/
BARCODERAWTMP = "$(TMPDIR)barcode$(ASSETID).eps"
BARCODETMP = "$(TMPDIR)barcode$(ASSETID).png"
QRTMP = "$(TMPDIR)qrcode$(ASSETID).png"
OUTPUT = "$(OUTPUTDIR)label-$(ASSETID).png"
PROPERTY_LABEL = "Property of RIT Rowing"
# this is a bit of a hack to generate barcodes closer in size to the label itself to prevent issues when scaling the barcode. its value is the width of the label that the python script generates minus two times the padding value (to give it some space on the left and right)
BARCODE_WIDTH = 845

barcode:
	mkdir -p "$(TMPDIR)"
	barcode -o $(BARCODERAWTMP) -b $(ASSETID) -n -e "128" -g "$(BARCODE_WIDTH)x$(BARCODE_HEIGHT)" -E
	convert $(BARCODERAWTMP) -colorspace RGB -background white -flatten $(BARCODETMP)
	rm $(BARCODERAWTMP)

qr:
	mkdir -p "$(TMPDIR)"
	qrencode -o $(QRTMP) $(ASSETID)

#https://stackoverflow.com/questions/15229833/set-makefile-variable-inside-target

big: BARCODE_HEIGHT=100
big: qr barcode
	pipenv run python3 ./labelgen.py --qr-path $(QRTMP) --barcode-path $(BARCODETMP) --label $(ASSETID) --configsection Full --output $(OUTPUT)
	rm $(BARCODETMP) $(QRTMP)


small: BARCODE_HEIGHT=60
small: qr barcode
	pipenv run python3 ./labelgen.py --qr-path $(QRTMP) --barcode-path $(BARCODETMP) --label $(ASSETID) --configsection Half --output $(OUTPUT)
	rm $(BARCODETMP) $(QRTMP)

big-virt: BARCODE_HEIGHT=100
big-virt: qr barcode
	pipenv run python3 ./labelgen.py --qr-path $(QRTMP) --barcode-path $(BARCODETMP) --label $(ASSETID) --configsection FullVertical --output $(OUTPUT)
	rm $(BARCODETMP) $(QRTMP)

default: big

clean:
	rm $(OUTPUT)