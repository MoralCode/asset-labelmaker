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








class Label():

	def __init__(self, config, label, asset_tag=None, has_qr=True, has_barcode=True ):
		self.config = config
		self.has_qr = has_qr
		self.has_barcode = has_barcode
		self.label = label
		self.asset_tag = asset_tag or label
		#TODO: what if this is still none???

	def _build_qr(self, asset_tag, config, background_height):
		qr = qrcode.make(asset_tag)
		qr_height_factor = config.getFloat("QRHeightFactor")
		qr_size = int(qr_height_factor*background_height)
		qr = qr.resize((qr_size,qr_size))
		return qr

	
	def _build_barcode(self, asset_tag, config):
		
		height = config.getInteger("BarcodeHeight")
		width = config.getInteger("LabelWidth") - (2* config.getInteger("BarcodeSidePadding"))
		barcode = Code128(asset_tag, charset='B')
		barcode.quiet_zone = 1 #num of modules
		# first  rough pass, try to get close to the right size
		mod_width = int(width/barcode.width())
		vert_border_size = 0#barcode.quiet_zone * mod_width
		barcode = barcode.image(height=height-(vert_border_size * 2), module_width=mod_width, add_quiet_zone=True)

		# second final pass, more precisely resize
		bcode_w, bcode_h = barcode.size
		barcode = barcode.resize((width, bcode_h), resample=Image.Resampling.NEAREST)

		return barcode

	def build(self):
		background = Image.new('RGBA', (self.config.getInteger("LabelWidth"), self.config.getInteger("Labelheight")), (255, 255, 255, 255))
		bg_w, bg_h = background.size
		# padding = int(.025*self.config.getInteger("LabelWidth"))
		padding = self.config.getInteger("LabelPadding")

		if self.has_qr:
			qr = self._build_qr(self.asset_tag, self.config, bg_h)
			qr_w, qr_h = qr.size
			print(qr)

			# centered horizontally
			# x = (bg_w - qr_w) // 2
			#centered vertically
			# y = (bg_h - qr_h) // 2

			qr_x = self.config.getInteger("QRHorizontalOffset") #padding 
			qr_y = self.config.getInteger("QRVerticalOffset") # upper vertically
			# qr_y = bg_h - qr_h # lower vertically
			# qr_y = int((bg_h - qr_h)/2) # centered vertically


			qr_offset = (qr_x, qr_y)
			background.paste(qr, qr_offset)

		if self.has_barcode:
			barcode = self._build_barcode(self.asset_tag, self.config)
			bcode_w, bcode_h = barcode.size
			
			# centered horizontally
			bcode_x = (bg_w - bcode_w) // 2
			#end vertically
			bcode_y = (bg_h - bcode_h) - self.config.getInteger("BarcodeBottomPaddingFactor") * padding

			bcode_offset = (bcode_x, bcode_y)
			background.paste(barcode, bcode_offset)

		text = self.label
		# apply special processing for alpha-prefixed numeric asset tags to split it up
		print(splitAlphaAndNumeric(text))
		lines = splitAlphaAndNumeric(text)

		draw = ImageDraw.Draw(background)
		alphafont = ImageFont.truetype(self.config.getString("HumanLabelAlphaFont"), self.config.getInteger("HumanLabelAlphaFontSize"))
		numfont = ImageFont.truetype(self.config.getString("HumanLabelNumericFont"), self.config.getInteger("HumanLabelNumericFontSize"))


		start_w = 0
		start_h = 0

		
		# num_w, num_h = draw.textsize(lines[0],font=numfont)


		if self.has_qr:
			qr_x_offset = 0
			qr_y_offset = 0

			if self.config.getString("HumanLabelPositionToQR") == "beside":
				qr_x_offset = qr_w + qr_x
				qr_y_offset = qr_y
			elif self.config.getString("HumanLabelPositionToQR") == "below":
				qr_x_offset = qr_x
				qr_y_offset = qr_h + qr_y

			start_w = qr_x_offset + self.config.getInteger("HumanLabelHorizontalOffset") 
			start_h = qr_y_offset + self.config.getInteger("HumanLabelVerticalOffset") #+ int(padding/2)#+ qr_y
			#int((bg_h-bcode_h-padding-alpha_h-num_h)/2)
		# draw text
		alpha_w, alpha_h = draw.textsize(lines[0],font=alphafont)
		
		print(alpha_h)
		draw.text((start_w, start_h), lines[0], fill="black",font=alphafont)

		# draw number
		labelnumoffset = (start_w, start_h)
		if self.config.getString("HumanLabelTextStacking") == "horizontal":
			labelnumoffset = (start_w + alpha_w+(self.config.getInteger("HumanLabelNumberPaddingFromAlphaFactor") * padding), start_h + self.config.getInteger("HumanLabelNumberVerticalOffsetFromAlpha"))

		elif self.config.getString("HumanLabelTextStacking") == "vertical":
			labelnumoffset = (start_w, start_h + alpha_h + self.config.getInteger("HumanLabelNumberVerticalOffsetFromAlpha"))
			

		draw.text(labelnumoffset, lines[1], fill="black",font=numfont)


		if self.config.getString("PropertyLabelText") != "":
			draw = ImageDraw.Draw(background)

			propertyfont = ImageFont.truetype(self.config.getString("PropertyLabelFont"), self.config.getInteger("PropertyLabelFontSize"))
			prop_alpha_w, prop_alpha_h = draw.textsize(self.config.getString("PropertyLabelText"),font=propertyfont)

			draw.text((int((bg_w - prop_alpha_w)/2 + self.config.getInteger("PropertyLabelHorizontalOffsetFromCenter")), self.config.getInteger("PropertyLabelVerticalPosition")), self.config.getString("PropertyLabelText"), fill="black",font=propertyfont)
		self.background = background
	
	def save(self, path):
		angle = stringToAngle(self.config.getString("LabelRoation"))
		rotated = self.background.rotate(angle, expand=True)

		rotated.save(path)

label = Label(config, args.label, asset_tag=args.asset_tag, has_qr=args.qr, has_barcode=args.barcode)

label.build()

if args.output:
	label.save(args.output)
	
