@echo off
ECHO This launches Houdini in command line mode and renders a turntable of a given LDraw model
ECHO ----------------------------------------------------------
ECHO Open this file in a text editor for help!
ECHO It might have to be adjusted if your installation paths are different.
ECHO ----------------------------------------------------------
ECHO When double clicking this .bat it will render still_life_mixed.ldr
ECHO You can drag and drop any LDraw file onto this .bat to render it instead!
ECHO ----------------------------------------------------------

REM If a file is dropped onto this .bat, it will be rendered instead of the default example
SET FILE_ARG=
IF NOT "%~1"=="" SET FILE_ARG=-f "%~1"

"%PROGRAMFILES%\Side Effects Software\Houdini 21.0.440\bin\hython" "%USERPROFILE%\git\ldraw2houdini\python3.11libs\ldraw_cli.py" %FILE_ARG%

PAUSE

REM You can get help by adding --help at the end like so:
REM "%PROGRAMFILES%\Side Effects Software\Houdini 21.0.440\bin\hython" "%USERPROFILE%\git\ldraw2houdini\python3.11libs\ldraw_cli.py" --help
REM ----------------------------------------------------------
REM To render with a custom amount of samples or a specific file try the following:
REM "%PROGRAMFILES%\Side Effects Software\Houdini 21.0.440\bin\hython" "%USERPROFILE%\git\ldraw2houdini\python3.11libs\ldraw_cli.py" -s 16 -f "%USERPROFILE%\git\ldraw2houdini\resources\example_files\still_life_transparent.ldr"

