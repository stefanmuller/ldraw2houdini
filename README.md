# LDraw 2 Houdini

Import LDraw files directly into Houdini!

You can either source individual parts with the **Brickini LDraw Part HDA** or import entire models with a one button shelf tool!

![boutique hotel](/resources/help/brickini_ldraw_header.jpg)

## Features
- **import individual bricks & entire models**
- **logo on studs:** studs are instanced for extra efficiency
- **mpd file support:** mpd files contain multiple sub models, referenced by a main model
- **instancing support:** duplicate bricks are automatically packed and the color is read from the point data
- **imperfections:** if importing a model, the bricks are not perfectly stacked/aligned to each other, for a more realistic look and bricks can randomly yellow due to age.
- **gaps between bricks:** bricks can be slightly squashed to get tiny gaps between them
- **slope support** slopes are automatically detected so they can get a grainy texture
- **bevel and subdivison support:** geometry is automagically cleaned up as much as possible and LDraw lines are used to determine edges that need to be beveled to allow proper subdivision
- **cache toggle:** either load geo dynamically from LDraw library or save in hip file
- **auto generate textures for prints/stickers** for modern cg workflows
- **auto uvs**
- **solaris + karma example scene** contains MaterialX shader showcasing how to create high quality renderings 

## Requirements
- houdini 19.5
- sidefx labs for auto uv feature

## Installation

1. Download the latest release
2. unpack to a directory called ldraw2houdini
3. Download [LDraw parts library](https://library.ldraw.org/updates?latest) or [Bricklink Studio](https://www.bricklink.com/v2/build/studio.page)
5. add the following lines to your houdini.env

        # path to ldraw library
        LDRAW_LIB = "C:\Program Files\Studio 2.0\ldraw"

        # if you don't have other plugins installed:
        HOUDINI_PATH = "C:\Users\<username>\Documents\ldraw2houdini;&"

        # if you have other plugins installed:
        HOUDINI_PATH = "C:\Users\<username>\Documents\ldraw2houdini;$HOUDINI_PATH"

6. happy ldrawing!

## Quickstart Guide

### Import a single part

1. create a **Brickini LDraw Part** node in SOP context
2. type a cool part number into the **Part** parameter: 2546p01
3. Change **Color** parameter to red
4. Look at that awesome classic parrot

![a parrot in the houdini viewport](/resources/help/brickini_ldraw_part.jpg)

### Import an entire model

1. Add the Brickini Shelf to your toolbar 
2. Click **LDraw Model**
3. choose a LDraw model file
4. aar, matey!

![forbidden island set in the houdini viewport](/resources/help/brickini_ldraw_model.jpg)

## Resources

LDraw Official Model Repository
[LDraw OMR](https://omr.ldraw.org/)  
Official sets made in LDraw Eurobricks thread
[Eurobricks Thread](https://www.eurobricks.com/forum/index.php?/forums/topic/48285-key-topic-official-lego-sets-made-in-ldraw/)

## If you like this and want to support me

you can buy me a coffee :) [Buy Me a Coffee](https://www.buymeacoffee.com/stefanmuller)