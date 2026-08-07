# pyright: reportMissingImports=false
import ldraw
import hou
from pathlib import PureWindowsPath
import argparse

def ldraw_render(args):
    template_path = PureWindowsPath(ldraw.resources() / 'template.hiplc').as_posix()

    hou.hipFile.load(template_path, ignore_load_warnings=True)

    karma_node = hou.node('/stage/karmarendersettings1')
    karma_node.parm('pathtracedsamples').set(args.samples)

    ldraw_lop_node = hou.node('/stage/brickini_ldraw_lop1')
    ldraw_lop_node.parm('ldraw_file').set(args.file)
    ldraw_lop_node.parm('build').pressButton()

    print('Rendering LDraw file {} with {} samples'.format(args.file, args.samples))

    render_node = hou.node('/stage/usdrender_rop1')
    render_node.parm('renderpreview').pressButton()

default_file = PureWindowsPath(ldraw.resources() / 'example_files' / 'still_life_mixed.ldr').as_posix()

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--samples', type=int,
                    help='number of samples', default=32)

parser.add_argument('-f', '--file', type=str,
                    help='LDraw file to render', default=default_file)

args = parser.parse_args()

ldraw_render(args)