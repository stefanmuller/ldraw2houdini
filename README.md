# LDraw 2 Houdini

### Import LDraw files directly into Houdini!

You can source individual parts with the **Brickini LDraw Part HDA** or import entire models with a one-button shelf tool!

[![render of example scene](/resources/help/brickini_example_scene.jpg)](https://youtu.be/JDEZ5LpPKfM)

[Watch YouTube Showcase Video](https://youtu.be/JDEZ5LpPKfM)

## Features
- **Import individual bricks & entire models**
- **Logo on studs:** studs are instanced for extra efficiency
- **MPD file support:** mpd files contain multiple sub models, referenced by a main model
- **Instancing support:** duplicate bricks are automatically packed and the color is read from the point data
- **Imperfections:** if importing a model, the bricks are not perfectly stacked/aligned to each other, for a more realistic look and bricks can randomly yellow due to age.
- **Gaps between bricks:** bricks can be slightly squashed to get tiny gaps between them
- **Slope support** slopes are automatically detected so they can get a grainy texture
- **Bevel and subdivison support:** geometry is automagically cleaned up as much as possible and LDraw lines are used to determine edges that need to be beveled to allow proper subdivision
- **Cache toggle:** either load geo dynamically from LDraw library or save in hip file
- **Auto generate textures for prints/stickers** for modern cg workflows
- **Auto uvs**
- **Solaris + Karma example scene** contains MaterialX shader showcasing how to create high quality renderings 

## Requirements
- Houdini 19.5
- SideFX Labs for auto uv feature

## Installation

1. Download the latest release
2. Unpack to a directory called ldraw2houdini
3. Download [LDraw parts library](https://library.ldraw.org/updates?latest) or [Bricklink Studio](https://www.bricklink.com/v2/build/studio.page)
5. add the following lines to your houdini.env

        # path to ldraw library
        LDRAW_LIB = "C:\Program Files\Studio 2.0\ldraw"

        # if you don't have other plugins installed:
        HOUDINI_PATH = "C:\Users\<username>\Documents\ldraw2houdini;&"

        # if you have other plugins installed:
        HOUDINI_PATH = "C:\Users\<username>\Documents\ldraw2houdini;$HOUDINI_PATH"

6. Happy ldrawing!

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
3. Choose a LDraw model file
4. Behold the beauty

![boutique hotel](/resources/help/brickini_ldraw_model.jpg)

## Resources

- [LDraw Official Model Repository](https://omr.ldraw.org/)  
- Official sets made in LDraw
[Eurobricks Thread](https://www.eurobricks.com/forum/index.php?/forums/topic/48285-key-topic-official-lego-sets-made-in-ldraw/)

## If you like this and want to support me

You can buy me a coffee :) [Buy Me a Coffee](https://www.buymeacoffee.com/stefanmuller)