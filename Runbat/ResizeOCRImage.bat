@echo on
set tool_path="C:\Program Files\ImageMagick-7.0.10-Q16-HDRI"
set SRC_DIR="C:\HHS\Labels\OCR\Tmp"
set SRC_TYPE="png"
set DES_TYPE="png"
::if not exist ("%tool_path%\convert.exe") echo ("PLEASE CHECK IF ..\Image Magic..\convert.exe is available")
::pause
::exit /B 5
::cd %tool_path%
:: no carriage return in command line after DO in FOR loop
for /r %SRC_DIR% %%f in (*.%SRC_TYPE%) do (
	echo "Find %%f"		
	magick %%f -filter LanczosSharp -background white -resize 800x600 -gravity center -extent 800x600 -colorspace Gray -dither FloydSteinberg -quality 75 -define png:color-type=0 -define png:bit-depth=8 %%f
	echo "%%~nxf is converted OK"		

)

