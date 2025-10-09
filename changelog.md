## Star Apple v4.0.0

#### Brickini LDraw Part
- Big updates to ldraw_part for massively improved performance
- New auto mesh clean up function that attempts to fix some bad geometry to improve beveling
- New crease attribute in LDraw part to allow subdividing in Solaris
- Tweaked edge detection in LDraw part
- Improved ldraw_part_properties performance by only calling slow setAttribValue() function when necessary
- Added new global description attr
- Ignoring gap parm if part is a sticker
- Ignoring bevel parm if part is a Sail
- Added subd group to automatically tag parts as subdivision surfaces in Solaris
- Skip print separation if part is a composite. To support this properly we would have to search for base composites and if they don't exist, use the base dat in the file itself and apply transform
- Fixed direct color parsing and added acescg conversion
- Round parts like 3941 that have disabled logo lines are now processed when the logo option is enabled

#### Brickini Imperfections
- Fixed random number generation

#### Solaris Example Scene
- Completely overhauled and turned into a new template scene to easily render turntables
- New **Ldraw Lop** node for easy LDraw import into Solaris
- Primvars need to be indexed to support correct subdividing in Karma XPU
- New Karma Settings for higher quality result
- New **Brickini Turntable** node
- Tweaked parameters all over the place to reduce info/warning messages in Solaris log

#### Brickini Karma Material
- Opgraded material with new karma parameters
- Added rounded edge since Karma XPU in H21 supports this now in combination with bump mapping

#### Resources
- New brick_wall.ldr
- New still lifes
- Added hdri from hdriHaven for better lighting

#### LDraw Model
- Added color penetration support for submodels in mpd files (e.g. 6334-1.mpd from OMR)
- Made hierarchy option invisible
- Refactored all model related code in a new ldraw_model.py Using an object-oriented approach, there is now a higher degree of code reusability and modularity and less code in otls and the shelf.

#### Experimental Command line Rendering
- Added new ldraw_cli.py that allows for rendering turntables of LDraw files from the command line.
- See render_turntable.bat for example usage

#### Known Issues/Limitations
- Textures can't be baked when in lops. One needs to create the part in SOPs, switch it to texture, and afterwards it should render in Karma when texture mode is used
- ld_colors.json is outdated. There are tons of new colors in LDConfig. However I need to update the LDraw Part menu to support this. Kind of annoying. Need to see if I can future proof this somehow.
- Print handling set to texture breaks parts that don't have any. Ideally this setting is ignored and falls back to seperate behind the scenes
- Texture mode not fully supported for baseplates. Studs don't receive correct colors


## Banana v3.0.0

- Houdini 20.5/Py 3.11 compatibility updates
- New texture workflow with Karma XPU support. Please have a look at the updated example scene
- HDAs now include type category in name
- Several minor tweaks to LDraw part HDA
- Updated ld_colors.json with new color names and some tweaked values (black looks actually black now and not oddly blue)
- Updated part_properties.json with additional values
- Additional information in readme on how to use ldraw2houdini with alternative Houdini/Python versions. This may or may not require additional adjustments that I'll leave up to the user to work out, as I don't have the time to support more than one version at a time.