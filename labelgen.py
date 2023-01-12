import argparse
from PIL import Image

# Generate a single asset label for an erg given the QR code and the barcode
#  



parser = argparse.ArgumentParser(description='Generate asset labels for an Erg')
parser.add_argument('--qr-path',
                    help='the path to an image of a 2d QR code to include in the label')
parser.add_argument('--barcode-path',
                    help='the path to an image of a 1D barcode to include in the label')
parser.add_argument('--label',
                    help='Text to write on the label')
parser.add_argument('--output',
                    help='the path to write the final image to')

args = parser.parse_args()


background = Image.new('RGBA', (800, 266), (255, 255, 255, 255))
bg_w, bg_h = background.size
padding = 5

if args.qr_path:
	qr = Image.open(args.qr_path, 'r')
	qr_height_factor = .8
	qr_size = int(qr_height_factor*bg_h)
	qr = qr.resize((qr_size,qr_size))
	qr_w, qr_h = qr.size

	# centered horizontally
	# x = (bg_w - qr_w) // 2
	#centered vertically
	# y = (bg_h - qr_h) // 2

	x = y = padding

	offset = (x, y)
	background.paste(qr, offset)


if args.barcode_path:
	barcode = Image.open(args.barcode_path, 'r')
	bcode_w, bcode_h = barcode.size
	barcode = barcode.resize((bg_w - (padding*2), bcode_h), resample=Image.Resampling.NEAREST)
	bcode_w, bcode_h = barcode.size

	# centered horizontally
	x = (bg_w - bcode_w) // 2
	#end vertically
	y = (bg_h - bcode_h)- padding

	offset = (x, y)
	background.paste(barcode, offset)


if args.label:
	draw = ImageDraw.Draw(background)
	# font = ImageFont.truetype(<font-file>, <font-size>)
	font = ImageFont.truetype("/usr/share/fonts/truetype/open-sans/OpenSans-Bold.ttf", 128)
	font_w, font_h = draw.textsize(args.label,font=font)

	w=(bg_w-font_w)/2
	if args.qr_path:
		w += qr_w/2
	
	h=(bg_h-font_h)/2
	if args.barcode_path:
		h -= bcode_h/2
	draw.text((w,h), args.label, fill="black",font=font)
if args.output:
	background.save(args.output)
