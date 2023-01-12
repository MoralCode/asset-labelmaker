import argparse
from PIL import Image

# Generate a single asset label for an erg given the QR code and the barcode
#  



parser = argparse.ArgumentParser(description='Generate asset labels for an Erg')
parser.add_argument('--qr-path',
                    help='the path to an image of a 2d QR code to include in the label')
parser.add_argument('--barcode-path',
                    help='the path to an image of a 1D barcode to include in the label')
parser.add_argument('--output',
                    help='the path to write the final image to')

args = parser.parse_args()


background = Image.new('RGBA', (800, 266), (255, 255, 255, 255))
bg_w, bg_h = background.size

if args.qr_path:
	qr = Image.open(args.qr_path, 'r')
	qr_w, qr_h = qr.size

	# centered
	offset = ((bg_w - qr_w) // 2, (bg_h - qr_h) // 2)
	background.paste(qr, offset)






if args.output:
	background.save(args.output)
