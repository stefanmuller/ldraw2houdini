# Ldraw 2 Houdini

Import ldraw files directly into houdini!

You can either source individual parts with the **Brickini Ldraw Part HDA** or even build entire models with a one button shelf tool!


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

1. Press **Ldraw Model** from the Brickini shelf toolbar
2. choose a ldraw model file
3. aar, matey!

![forbidden island set in the houdini viewport](/resources/help/brickini_ldraw_model.jpg)