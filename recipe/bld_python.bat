setlocal

set "PYTHONPATH=%LIBRARY_PREFIX%\lib\site-packages;%SP_DIR%"

pushd %SRC_DIR%\%PKG_NAME%\src\work

mkdir %LIBRARY_PREFIX%\lib\site-packages

pip setup.py install --prefix=%LIBRARY_PREFIX%
if errorlevel 1 exit 1
