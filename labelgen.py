import argparse
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from configfinder import ConfigFinder
import qrcode
from pubcode import Code128

# Generate a single asset label for an erg given a path to a QR code and barcode


# https://stackoverflow.com/a/430665/
def splitAlphaAndNumeric(s):
    head = s.rstrip('0123456789')
    tail = s[len(head):]
    return head, tail

def stringToAngle(directionStr):
	"""convert a string cardinal direction into a rotation in degrees counterclockwise for  Pillow
	Returns:
		int: number of degrees coutnerclockwise
	"""
    
	if directionStr.lower() == "north":
		return 0
	elif directionStr.lower() == "east":
		return 270
	elif directionStr.lower() == "south":
		return 180
	elif directionStr.lower() == "west":
		return 90
	else:
		return 0 


parser = argparse.ArgumentParser(description='Generate asset labels for an Erg')
parser.add_argument('--qr', action="store_true",
                    help='whether or not to include a QR code in the generated label')
parser.add_argument('--barcode', action="store_true",
                    help='whether or not to include a Code128B barcode in the generated label')
parser.add_argument('--asset-tag',
                    help='data to write to the codes (if different from the label)')
parser.add_argument('--label',
                    help='Text to write on the label')
parser.add_argument('--configpath', default="config.ini",
                    help='path to config ini file')		
parser.add_argument('--configsection', default="default",
                    help='name of the config section to use')			
parser.add_argument('--output',
                    help='the path to write the final image to')

args = parser.parse_args()

config = ConfigFinder(args.configpath, args.configsection)

print(config.getFloat("LabelWidth"))
# print(config.getInteger("test"))

background = Image.new('RGBA', (config.getInteger("LabelWidth"), config.getInteger("Labelheight")), (255, 255, 255, 255))
bg_w, bg_h = background.size
# padding = int(.025*config.getInteger("LabelWidth"))
padding = config.getInteger("LabelPadding")

tag_data = args.asset_tag or args.label

# build QR:

def build_qr(asset_tag, config):
	qr = qrcode.make(asset_tag)
	qr_height_factor = config.getFloat("QRHeightFactor")
	qr_size = int(qr_height_factor*bg_h)
	qr = qr.resize((qr_size,qr_size))
	return qr



if args.qr:
	qr = build_qr(tag_data, config)
	qr_w, qr_h = qr.size

	# centered horizontally
	# x = (bg_w - qr_w) // 2
	#centered vertically
	# y = (bg_h - qr_h) // 2

	qr_x = config.getInteger("QRHorizontalOffset") #padding 
	qr_y = config.getInteger("QRVerticalOffset") # upper vertically
	# qr_y = bg_h - qr_h # lower vertically
	# qr_y = int((bg_h - qr_h)/2) # centered vertically


	qr_offset = (qr_x, qr_y)
	background.paste(qr, qr_offset)



def build_barcode(asset_tag, config):
	
	height = config.getInteger("BarcodeHeight")
	barcode = Code128(args.label, charset='B')
	barcode.quiet_zone = 1 #num of modules
	mod_width = 10
	vert_border_size = 0#barcode.quiet_zone * mod_width
	barcode = barcode.image(height=height-(vert_border_size * 2), module_width=mod_width, add_quiet_zone=True)
	
	return barcode

if args.barcode:
	barcode = build_barcode(tag_data, config)
	bcode_w, bcode_h = barcode.size
	# barcode = barcode.resize((bg_w - (padding*2), bcode_h), resample=Image.Resampling.NEAREST)
	# bcode_w, bcode_h = barcode.size

	# centered horizontally
	bcode_x = (bg_w - bcode_w) // 2
	#end vertically
	bcode_y = (bg_h - bcode_h) - config.getInteger("BarcodeBottomPaddingFactor") * padding

	bcode_offset = (bcode_x, bcode_y)
	background.paste(barcode, bcode_offset)


if args.label:

	text = args.label
	# apply special processing for alpha-prefixed numeric asset tags to split it up
	print(splitAlphaAndNumeric(text))
	lines = splitAlphaAndNumeric(text)

	draw = ImageDraw.Draw(background)
	alphafont = ImageFont.truetype(config.getString("HumanLabelAlphaFont"), config.getInteger("HumanLabelAlphaFontSize"))
	numfont = ImageFont.truetype(config.getString("HumanLabelNumericFont"), config.getInteger("HumanLabelNumericFontSize"))


	start_w = 0
	start_h = 0

	
	# num_w, num_h = draw.textsize(lines[0],font=numfont)


	if args.qr:
		qr_x_offset = 0
		qr_y_offset = 0

		if config.getString("HumanLabelPositionToQR") == "beside":
			qr_x_offset = qr_w + qr_x
			qr_y_offset = qr_y
		elif config.getString("HumanLabelPositionToQR") == "below":
			qr_x_offset = qr_x
			qr_y_offset = qr_h + qr_y

		start_w = qr_x_offset + config.getInteger("HumanLabelHorizontalOffset") 
		start_h = qr_y_offset + config.getInteger("HumanLabelVerticalOffset") #+ int(padding/2)#+ qr_y
		#int((bg_h-bcode_h-padding-alpha_h-num_h)/2)
	# draw text
	alpha_w, alpha_h = draw.textsize(lines[0],font=alphafont)
	
	print(alpha_h)
	draw.text((start_w, start_h), lines[0], fill="black",font=alphafont)

	# draw number
	labelnumoffset = (start_w, start_h)
	if config.getString("HumanLabelTextStacking") == "horizontal":
		labelnumoffset = (start_w + alpha_w+(config.getInteger("HumanLabelNumberPaddingFromAlphaFactor") * padding), start_h + config.getInteger("HumanLabelNumberVerticalOffsetFromAlpha"))

	elif config.getString("HumanLabelTextStacking") == "vertical":
		labelnumoffset = (start_w, start_h + alpha_h + config.getInteger("HumanLabelNumberVerticalOffsetFromAlpha"))
		

	draw.text(labelnumoffset, lines[1], fill="black",font=numfont)

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

if config.getString("PropertyLabelText") != "":
	draw = ImageDraw.Draw(background)

	propertyfont = ImageFont.truetype(config.getString("PropertyLabelFont"), config.getInteger("PropertyLabelFontSize"))
	prop_alpha_w, prop_alpha_h = draw.textsize(config.getString("PropertyLabelText"),font=propertyfont)

	draw.text((int((bg_w - prop_alpha_w)/2 + config.getInteger("PropertyLabelHorizontalOffsetFromCenter")), config.getInteger("PropertyLabelVerticalPosition")), config.getString("PropertyLabelText"), fill="black",font=propertyfont)

if args.output:
	angle = stringToAngle(config.getString("LabelRoation"))
	rotated = background.rotate(angle, expand=True)

	rotated.save(args.output)
