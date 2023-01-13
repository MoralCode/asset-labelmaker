# LabelGen

This is a quick script i threw together to generate Snipe-IT Asset labels in a way that was independent of any particular installation or domain name. The barcodes and QR codes only encode the asset tag value itself.


This is somewhat early stages and may not be as easy to use as something more fully-polished. A lot of assumptions were made for the sake of development speed, like:
- linux environment
- you want a label layout with a similar design to the default snipe-it one with a QR code on the left and a Code 128 barcode at the bottom


## Usage

There are a few ways to use this.
If you have the QR codes already, you can jump directly to using the python script.

If you need to generate the bar/matrix codes or want one-off labels, use the makefile.

If you want bulk labels fast, tweak the `make-bulk.sh` script for your needs and let er rip.

### Python Script
This script assembles the barcode images and supplied text into a label. this is where all the laying out and resizing happens. It works best if the barcodes and labels are already roughly the right size. If you see shades of grayscale between the white and black bars of the barcode, try playing with the barcodes size 

Set up of dependencies is managed with pipenv. `pipenv install` should just work. run with `pipenv run python3 ./labelgen.py <options>`.

It uses argparse. Run it with the `--help` flag to learn about the options available, the code isnt too complicated either if you want to dive in directly.


### Makefile
This essentially just a slightly more formal way to run the series of bash commands needed to generate the barcode and QR images and get them set up for input to the python script.

You need to supply an `ASSETID` environment variable to tell it the asset tag to generate everything for.

`make qr` will create a QR code as a PNG image
`make barcode` makes a Code 128 barcode as a PNG image
`make` (or `make default`) makes a whole label with both barcode types and also uses the python script to assemble it. It also cleans up the temporary barcode files left by the barcode generation.

### The bash script
Its literally a for loop to repeatedly call the makefile with different asset tag values.

The only fanciness is that it loops in batches to take advantage of some amount of system parallelism to generate labels a bunch faster without slamming the system with all of potentially hundreds of labels at once. 
