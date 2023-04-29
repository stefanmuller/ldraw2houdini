# Ldraw 2 Houdini

Import ldraw files directly into houdini!

You can either source individual parts with the **Brickini Ldraw Part HDA** or import entire models with a one button shelf tool!

![boutique hotel](/resources/help/brickini_ldraw_header.jpg)

## Features
- **import individual bricks & entire models**
- **logo on studs!**
- **color support**: 8 bit ldraw colors are converted to floating point)
- **mpd file support**: mpd files contain multiple sub models, referenced by a main model)
- **instancing support**: duplicate bricks are automatically packed and the color is read from the point data
- **imperfect alignment**: if importing a model, the bricks are not perfectly aligned to each other, for a more realistic look
- **gaps between bricks**: bricks can be slightly squashed to get tiny gaps between them

## To-do

- resolve $HOME etc variables
- slope texture
- karma material for bricks, transparent, rubber, chrome
- add simple solaris example file for rendering
- caching toggle

## Installation

1. Download the latest release
2. unpack to a directory called ldraw2houdini
3. Download [ldraw parts library](https://library.ldraw.org/updates?latest)
4. unpack to a directory called ldraw
5. add the following lines to your houdini.env

        LDRAW_LIB = "/home/user/ldraw"
        HOUDINI_PATH = "/home/user/ldraw2houdini/:$HOUDINI_PATH"

6. happy ldrawing!

## Quickstart Guide

### import a single part

1. create a **Brickini Ldraw Part** node in SOP context
2. type a cool part number into the **Part** parameter: 2546p01
3. Change **Color** parameter to red
4. Look at that awesome classic parrot

![a parrot in the houdini viewport](/resources/help/brickini_ldraw_part.jpg)

### import an entire model

1. Add the Brickini Shelf to your toolbar 
2. Click **Ldraw Model**
3. choose a ldraw model file
4. aar, matey!

![forbidden island set in the houdini viewport](/resources/help/brickini_ldraw_model.jpg)

## Resources

LDraw Official Model Repository
[Ldraw OMR](https://omr.ldraw.org/)  
Official sets made in ldraw eurobricks thread
[Eurobricks Thread](https://www.eurobricks.com/forum/index.php?/forums/topic/48285-key-topic-official-lego-sets-made-in-ldraw/)

## If you like this and want to support me

you can buy me a coffee :) [Buy Me a Coffee](https://www.buymeacoffee.com/stefanmuller)