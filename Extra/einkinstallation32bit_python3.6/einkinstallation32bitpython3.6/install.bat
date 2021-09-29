set pythonCommand=python
if not "%*"=="" set "pythonCommand=%*"

eink-32bit.msi
%pythonCommand% -m pip install eink-0.2.tar.gz