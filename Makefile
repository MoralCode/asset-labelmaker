.PHONY: default
# ASSETID=
BARCODERAWTMP = "barcode$(ASSETID).eps"
BARCODETMP = "barcode$(ASSETID).png"
QRTMP = "qrcode$(ASSETID).png"
OUTPUT = "label-$(ASSETID).png"
WIDTH = 790 # this is a bit of a hack to generate barcodes closer in size to the label itself to prevent issues when scaling the barcode. its value is the width of the label that the python script generates minus two times the padding value (to give it some space on the left and right)

barcode:
	barcode -o $(BARCODERAWTMP) -b $(ASSETID) -n -e "128" -g "$(WIDTH)x50" -E
	convert $(BARCODERAWTMP) -colorspace RGB -background white -flatten $(BARCODETMP)
	rm $(BARCODERAWTMP)

qr: 
	qrencode -o $(QRTMP) $(ASSETID)

default: qr barcode
	pipenv run python3 ./labelgen.py --qr-path $(QRTMP) --barcode-path $(BARCODETMP) --label $(ASSETID) --output $(OUTPUT)
	rm $(BARCODETMP) $(QRTMP)


clean:
	rm $(OUTPUT)