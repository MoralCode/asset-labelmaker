# Asset LabelMaker

This is a quick script i threw together to generate Snipe-IT Asset labels in a way that was independent of any particular installation or domain name. The barcodes and QR codes only encode the asset tag value itself.


This is somewhat early stages and may not be as easy to use as something more fully-polished. A lot of assumptions were made for the sake of development speed, like:
- linux environment
- you want a label layout with a similar design to the default snipe-it one with a QR code on the left and a Code 128 barcode at the bottom


## Usage

This script creates a label using the supplied parameters supplied text into a label. 

Set up of dependencies is managed with pipenv. `pipenv install` should just work. Tun with `pipenv run python3 ./labelgen.py <options>`.

The script is set up to use argparse. Run it with the `--help` flag to learn about the options available.

### The bash script
If you want to make a ton of labels at once, this bash script can help - its literally a for loop to repeatedly call the makefile with different asset tag values.

The only fanciness is that it loops in batches to take advantage of some amount of system parallelism to generate labels a bunch faster without slamming the system with too many labels at once. 

You should only need to edit the last line for the most part

**Testing Mode**

The script also contains a testing mode to generate one of each style kind of label to serve as a quick glance/way to generate comparison information to ensure that nothing gets broken as changes are made in future.

to use it, simply supply an argument to the script, such as `./make_bulk.sh true`