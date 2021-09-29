set pythonCommand=python
if not "%*"=="" set "pythonCommand=%*"

msiexec /x eink-32bit.msi
%pythonCommand% -m pip uninstall eink