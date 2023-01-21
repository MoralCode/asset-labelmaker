import argparse
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

# Generate a single asset label for an erg given the QR code and the barcode
#  


# https://stackoverflow.com/a/430665/
def splitAlphaAndNumeric(s):
    head = s.rstrip('0123456789')
    tail = s[len(head):]
    return head, tail


parser = argparse.ArgumentParser(description='Generate asset labels for an Erg')
parser.add_argument('--qr-path',
                    help='the path to an image of a 2d QR code to include in the label')
parser.add_argument('--barcode-path',
                    help='the path to an image of a 1D barcode to include in the label')
parser.add_argument('--label',
                    help='Text to write on the label')
parser.add_argument('--width', default=800, type=int,
                    help='label width')
parser.add_argument('--height', default=266, type=int,
                    help='label height')
parser.add_argument('--property',
                    help='property identification label')
parser.add_argument('--output',
                    help='the path to write the final image to')

args = parser.parse_args()


background = Image.new('RGBA', (args.width, args.height), (255, 255, 255, 255))
bg_w, bg_h = background.size
padding = int(.025*args.width)

if args.qr_path:
	qr = Image.open(args.qr_path, 'r')
	qr_height_factor = .55
	qr_size = int(qr_height_factor*bg_h)
	qr = qr.resize((qr_size,qr_size))
	qr_w, qr_h = qr.size

	# centered horizontally
	# x = (bg_w - qr_w) // 2
	#centered vertically
	# y = (bg_h - qr_h) // 2

	qr_x = 0 #padding 
	qr_y = 50 # upper vertically
	# qr_y = bg_h - qr_h # lower vertically
	# qr_y = int((bg_h - qr_h)/2) # centered vertically


	offset = (qr_x, qr_y)
	background.paste(qr, offset)


if args.barcode_path:
	barcode = Image.open(args.barcode_path, 'r')
	bcode_w, bcode_h = barcode.size
	barcode = barcode.resize((bg_w - (padding*2), bcode_h), resample=Image.Resampling.NEAREST)
	bcode_w, bcode_h = barcode.size

	# centered horizontally
	bcode_x = (bg_w - bcode_w) // 2
	#end vertically
	bcode_y = (bg_h - bcode_h)- padding

	offset = (bcode_x, bcode_y)
	background.paste(barcode, offset)


if args.label:

	text = args.label
	# apply special processing for alpha-prefixed numeric asset tags to split it up
	print(splitAlphaAndNumeric(text))
	lines = splitAlphaAndNumeric(text)

	draw = ImageDraw.Draw(background)
	alphafont = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf", 64)
	numfont = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf", 220)


	start_w = 0
	start_h = 0

	
	# num_w, num_h = draw.textsize(lines[0],font=numfont)


	if args.qr_path:
		start_w = qr_w + qr_x - 20
		start_h = qr_y + 35#+ int(padding/2)#+ qr_y
		#int((bg_h-bcode_h-padding-alpha_h-num_h)/2)
	# draw text
	alpha_w, alpha_h = draw.textsize(lines[0],font=alphafont)
	
	print(alpha_h)
	draw.text((start_w, start_h), lines[0], fill="black",font=alphafont)

	# draw number
	draw.text((start_w, start_h + alpha_h), lines[1], fill="black",font=numfont)

	# for line in lines:
	# 	width, height = draw.textsize(line,font=font)
	# 	draw.text(((w - width) / 2, y_text), line, fill="black",font=font)
	# 	y_text += height
	

	# font = ImageFont.truetype(<font-file>, <font-size>)
	
	# font_w, font_h = draw.textsize(lines[1],font=numfont)

	# w=(bg_w-font_w)/2
	# if args.qr_path:
	# 	w += qr_w/2 - 25
	
	# h=(bg_h-font_h)/2
	# if args.barcode_path:
	# 	h -= bcode_h/2
	# start_w, start_h = (w,h)
	
	# draw.text((w,h), lines[1], fill="black",font=numfont)

if args.property:
	draw = ImageDraw.Draw(background)

	alphafont = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf", 48)
	alpha_w, alpha_h = draw.textsize(args.property,font=alphafont)

	draw.text((int((bg_w-alpha_w)/2), 430), args.property, fill="black",font=alphafont)

if args.output:
	background.save(args.output)
