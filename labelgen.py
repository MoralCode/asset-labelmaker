import argparse
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from configfinder import ConfigFinder
import qrcode
from pubcode import Code128

# Generate a single asset label for an erg given a path to a QR code and barcode


def code39(filepath=".", text="", size=200, orientation="horizontal", printText=False, sizeFactor=8):
  code_dict = {"0":"111221211","1":"211211112","2":"112211112","3":"212211111","4":"111221112","5":"211221111","6":"112221111","7":"111211212","8":"211211211","9":"112211211","A":"211112112","B":"112112112","C":"212112111","D":"111122112","E":"211122111","F":"112122111","G":"111112212","H":"211112211","I":"112112211","J":"111122211","K":"211111122","L":"112111122","M":"212111121","N":"111121122","O":"211121121","P":"112121121","Q":"111111222","R":"211111221","S":"112111221","T":"111121221","U":"221111112","V":"122111112","W":"222111111","X":"121121112","Y":"221121111","Z":"122121111","-":"121111212",".":"221111211"," ":"122111211","$":"121212111","/":"121211121","+":"121112121","%":"111212121","*":"121121211"}
  upper_text = text.upper()
  code_string = ''.join([code_dict[c] + "1" for c in upper_text])
  code_string = "1211212111" + code_string + "121121211"

  padding = 5

  code_length = padding * 2
# temporary
  im = Image.new("L",(500,500),255)
  draw = ImageDraw.Draw(im)

  font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 12 * sizeFactor)
  textl, textt, textr, textb = draw.textbbox((0,0), upper_text,font=font)
  alpha_w, alpha_h = (textr-textl), (textb-textt)
  text_height = alpha_h + 20 if printText else 0

  code_length += sum([int(e) for e in code_string])

  width = 0
  height = 0
  if(orientation == "horizontal"):
    width = code_length * sizeFactor
    height = size
  else:
    height = code_length * sizeFactor
    width = size

  im = Image.new("L",(width,height + text_height),255)
  draw = ImageDraw.Draw(im)
  
  if(printText):
    #font = ImageFont.truetype("Arial.ttf", 12 * sizeFactor)
    textPosition = (width - alpha_w) // 2
    draw.text((textPosition,height),upper_text,0,font)

  loc = padding
  for i,e in enumerate([int(e) for e in code_string]):
    cur_size = loc  + e
    if(orientation == "horizontal"):
      draw.rectangle([loc*sizeFactor,0,cur_size*sizeFactor,height], 0 if (i %2 == 0) else 255)
    else:
      draw.rectangle([0,loc*sizeFactor,width,cur_size*sizeFactor], 0 if (i %2 == 0) else 255)
    loc = cur_size
  del(draw)
  # im = im.rotate(90,expand=True).resize(((height+text_height),width),Image.LANCZOS)
  return im
  # im.save(filepath + "/" + text +".png")


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
parser.add_argument('--propertylabel',
                    help='Text to write on the "property of" portion of the label (if present)')
parser.add_argument('--auxlabel',
                    help='Auxiliary label text to add as a separate label (if present)')
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
		start_w = self.config.getInteger("HumanLabelHorizontalOffset") 
		start_h = self.config.getInteger("HumanLabelVerticalOffset")

		if self.has_qr:
			qr_x_offset = 0
			qr_y_offset = 0

			if self.config.getString("HumanLabelPositionToQR") == "beside":
				qr_x_offset = qr_w + qr_x
				qr_y_offset = qr_y
			elif self.config.getString("HumanLabelPositionToQR") == "below":
				qr_x_offset = qr_x
				qr_y_offset = qr_h + qr_y

			# this was messing with the quarter labels for HRMs
			start_w += qr_x_offset 
			start_h += qr_y_offset #+ int(padding/2)#+ qr_y
			#int((bg_h-bcode_h-padding-alpha_h-num_h)/2)
		# draw text
		textpos = (start_w, start_h)
		# TODO: migrate to new, cleaner text alignment methods
		# https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html#PIL.ImageDraw.ImageDraw.textbbox
		textl, textt, textr, textb = draw.textbbox(textpos, lines[0],font=alphafont)
		alpha_w, alpha_h = (textr-textl), (textb-textt)
		
		print(alpha_h)
		draw.text(textpos, lines[0], fill="black",font=alphafont)

		# draw number
		labelnumoffset = (start_w, start_h)
		if self.config.getString("HumanLabelTextStacking") == "horizontal":
			labelnumoffset = (start_w + alpha_w+(self.config.getInteger("HumanLabelNumberPaddingFromAlphaFactor") * padding), start_h + self.config.getInteger("HumanLabelNumberVerticalOffsetFromAlpha"))

		elif self.config.getString("HumanLabelTextStacking") == "vertical":
			labelnumoffset = (start_w, start_h + alpha_h + self.config.getInteger("HumanLabelNumberVerticalOffsetFromAlpha"))
			

		draw.text(labelnumoffset, lines[1], fill="black",font=numfont)

		textcontents = args.propertylabel or self.config.getString("PropertyLabelText")
		if textcontents != "":
			draw = ImageDraw.Draw(background)

			propertyfont = ImageFont.truetype(self.config.getString("PropertyLabelFont"), self.config.getInteger("PropertyLabelFontSize"))

			textpos = (int(bg_w/2) + self.config.getInteger("PropertyLabelHorizontalOffsetFromCenter"), self.config.getInteger("PropertyLabelVerticalPosition"))


			# prop_alpha_w, prop_alpha_h = draw.textsize(textcontents,anchor="ms", font=propertyfont)
			draw.text(textpos, textcontents, anchor="ms", fill="black",font=propertyfont)

			# manual override to also add the property of label because theres vertical space now
			po_x, po_y = textpos

		# aux label
	# AuxLabelVerticalPosition=190
	# AuxLabelHorizontalOffsetFromCenter=100
	# AuxLabelFont=/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf
	# AuxLabelFontSize=42
		textcontents = args.auxlabel or self.config.getString("AuxLabelText")
		if textcontents != "":

			textpos = (int(bg_w/2) + self.config.getInteger("AuxLabelHorizontalOffsetFromCenter"), self.config.getInteger("AuxLabelVerticalPosition"))

			draw.text(textpos, textcontents, anchor="ms", fill="black",font=ImageFont.truetype(self.config.getString("AuxLabelFont"), int(self.config.getInteger("AuxLabelFontSize"))))
			

		self.background = background
	
	def save(self, path):
		angle = stringToAngle(self.config.getString("LabelRoation"))
		rotated = self.background.rotate(angle, expand=True)

		rotated.save(path)

label = Label(config, args.label, asset_tag=args.asset_tag, has_qr=args.qr, has_barcode=args.barcode)

label.build()

if args.output:
	label.save(args.output)
	
