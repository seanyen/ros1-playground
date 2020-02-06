setlocal

set "PYTHONPATH=%LIBRARY_PREFIX%\lib\site-packages;%SP_DIR%"

pushd %SRC_DIR%\%PKG_NAME%

%PYTHON% setup.py config
if errorlevel 1 exit 1

%PYTHON% setup.py build
if errorlevel 1 exit 1

mkdir %LIBRARY_PREFIX%\lib\site-packages

%PYTHON% setup.py install ^
    --prefix=%LIBRARY_PREFIX%
if errorlevel 1 exit 1
