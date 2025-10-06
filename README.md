# LDraw2Houdini

### Import LDraw files directly into Houdini

Source individual parts or import entire models with one-button shelf tools!

[![render of example scene](/resources/help/brickini_example_scene.jpg)](https://youtu.be/JDEZ5LpPKfM)

[Watch YouTube Showcase Video](https://youtu.be/JDEZ5LpPKfM)

## Features
- **Import individual bricks & entire models**
- **Logo on studs**
- **LDR, L3B & MPD file support:** mpd files contain multiple sub models, referenced by a main model
- **Instancing support:** duplicate bricks are automatically packed and the color is read from the point data
- **Imperfections:** if importing a model, the bricks are not perfectly stacked/aligned to each other for a more realistic look. Bricks can also randomly yellow due to age.
- **Injection points:** options to procedurally add injection marks either on stud or on walls (vintage bricks ~70s and older)
- **Gaps between bricks:** bricks can be slightly squashed to get tiny gaps between them
- **Slope support** slopes are automatically detected so they can get a grainy texture
- **Bevel and subdivison support:** geometry is automagically cleaned up as much as possible and LDraw lines are used to determine edges that need to be beveled to allow proper subdivision
- **Auto caching** every imported part will automatically be cached in LDraw library; Importing times will decrease the more LDraw2Houdini is used.
- **Auto generate textures for prints/stickers** for modern cg workflows
- **Auto uvs**
- **Material properties:** simple config file to define softness, graininess and roughness for individual parts
- **Solaris + Karma template scene** contains MaterialX shader showcasing how to create high quality renderings
- **ACES colorspace:** LDraw colors are converted to acescg

## Requirements
- Houdini 21 (Py 3.11) - Other versions *might* work, see [Optional Step 8.](#optional_id)
- SideFX Labs for auto uv feature
- OCIO ACES colorspace configuration for Houdini

## Installation

1. Download the latest [release](https://github.com/stefanmuller/ldraw2houdini/releases)
2. Unpack to a directory called **ldraw2houdini**

        # Windows C:\Users\<username>\Documents\git\ldraw2houdini 
        # Linux ~/git/ldraw2houdini

3. Download [LDraw parts library](https://library.ldraw.org/updates?latest) - (complete.zip)
4. Unpack to a directory called **ldraw**

        # Windows C:\Users\<username>\Documents\ldraw
        # Linux ~/ldraw

5. Download **ldraw2houdini.json** from [release page](https://github.com/stefanmuller/ldraw2houdini/releases). Place it in the Houdini packages folder.
6. If packages folder doesn't exist create it yourself.

        # Windows C:\Users\<username>\Documents\houdiniXX.X\packages
        # Linux ~/houdiniXX.X/packages

7. Launch Houdini - Happy ldrawing!

<a id="optional_id"></a>
### Optional Steps
8. Make sure you have **Houdini 20.5 Python 3.11** installed. If you are running older or newer versions of Houdini and/or Python you have to rename the **python3.11libs** folder accordingly. I.e. if your Houdini Python version is 3.9 rename it to **python3.9libs** 

9. If you placed anything in different paths, adjust **ldraw2houdini.json** accordingly.
    - LDRAW2HOUDINI needs to point to the path of this plugin
    - LDRAW_LIB needs to point to the LDraw library
    - Under Windows $HOME points to C:\Users\\\<username>\Documents
    - Under Linux $HOME is ~/

                {
                "env": [
                        { "LDRAW2HOUDINI": "$HOME/git/ldraw2houdini" },
                        { "LDRAW_LIB": "$HOME/ldraw" },
                        { "LDRAW_CACHE": 0 }
                ],
                "path": [
                        "${LDRAW2HOUDINI}"
                ]
                }

10. Set LDRAW_CACHE to 0 or 1 to enable/disable caching. This will write bgeo files to **$LDRAW_LIB/bgeo**. Remember to delete this folder if you update your LDraw parts library.
11. If you install a new release and want to upgrade your hdas in an existing scene run the **Upgrade Brickini HDAs Shelf Tool**
12. See [release notes](https://github.com/stefanmuller/ldraw2houdini/releases) for more details and explanations of specific features


## Quickstart Guide

### Import a single part

1. Create a **Brickini LDraw Part** node inside a Geometry node in SOP context
2. Type a cool part number into the **Part** parameter: 2546p01
3. Change **Material** parameter to red
4. Look at that awesome classic parrot

![a parrot in the houdini viewport](/resources/help/brickini_ldraw_part.jpg)

### Import an entire model

1. Add the Brickini Shelf to your toolbar 
2. Click **LDraw Model** or **LDraw Model Dynamic**
3. Choose an LDraw model file
4. Prints won't show up in the viewport, if bricks are packed (default) but are supported when rendering with Karma/Solaris

### Render with Solaris and Karma

1. Open template scene:

        ldraw2houdini/resources/template.hiplc

2. Browse for LDraw model file in **Brickini LDraw Lop**
3. Click **Build**
4. Render!

![lagoon lockup](/resources/help/brickini_ldraw_model.jpg)

## Brickini
![island landscape generated with brickini](/resources/help/brickini_splash.jpg)

**Brickini Brickify** let's you generate vast and detailed landscapes entirely out of bricks in Houdini. **LDraw2Houdini** works quite well together with Brickini. [Surf to the Brickini Tools website to find out more!](https://brickini-tools.com/)

## Contributions
- LDraw Model HDA (Dynamic mode): Kai Stavginski
- Auto caching concept/idea: Kai Stavginski

## Resources

- [LDraw Official Model Repository](https://library.ldraw.org/omr) (There are many more models in the forums)
- Official sets made in LDraw
[Eurobricks Thread](https://www.eurobricks.com/forum/index.php?/forums/topic/48285-key-topic-official-lego-sets-made-in-ldraw/)

## If you like this and want to support me

- [Buy Me a Coffee](https://www.buymeacoffee.com/stefanmuller) :)