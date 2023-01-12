.PHONY: default
# ERGID=
BARCODERAWTMP = "barcode.eps"
BARCODETMP = "barcode.png"
QRTMP = "qrcode.png"
OUTPUT = "label-$(ERGID).png"
WIDTH = 790

barcode:
	barcode -o $(BARCODERAWTMP) -b $(ERGID) -n -e "128" -g "$(WIDTH)x50" -E
	convert $(BARCODERAWTMP) -colorspace RGB -background white -flatten $(BARCODETMP)
	rm $(BARCODERAWTMP)

qr: 
	qrencode -o $(QRTMP) $(ERGID)

default: qr barcode
	pipenv run python3 ./labelgen.py --qr-path $(QRTMP) --barcode-path $(BARCODETMP) --label $(ERGID) --output $(OUTPUT)
	rm $(BARCODETMP) $(QRTMP)


clean:
	rm $(OUTPUT)