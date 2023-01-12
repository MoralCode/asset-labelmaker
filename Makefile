.PHONY: default
# ASSETID=
BARCODERAWTMP = "barcode.eps"
BARCODETMP = "barcode.png"
QRTMP = "qrcode.png"
OUTPUT = "label-$(ASSETID).png"
WIDTH = 790

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