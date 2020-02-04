:: MSVC is preferred.
set CC=cl.exe
set CXX=cl.exe

set IS_CATKIN_PKG=
set ADDITIONAL_ARGS=-DCATKIN_BUILD_BINARY_PACKAGE=ON
if "%PKG_NAME%" == "ros-noetic-catkin" (
    set ADDITIONAL_ARGS=
    set IS_CATKIN_PKG=1
)
if "%PKG_NAME%" == "ros-melodic-catkin" (
    set ADDITIONAL_ARGS=
    set IS_CATKIN_PKG=1
)

mkdir %PKG_NAME%\build
pushd %PKG_NAME%\build

set "CMAKE_PREFIX_PATH=%CMAKE_PREFIX_PATH:\=/%"
set "PYTHONPATH=%LIBRARY_LIB%\site-packages"
cmake ^
    -G "Ninja" ^
    -DCMAKE_INSTALL_PREFIX=%LIBRARY_PREFIX% ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DCMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP=True ^
    -DBUILD_SHARED_LIBS=ON ^
    -DSETUPTOOLS_DEB_LAYOUT=OFF ^
    %ADDITIONAL_ARGS% ^
    %SRC_DIR%\%PKG_NAME%
if errorlevel 1 exit 1

:: Build.
cmake --build . --config Release
if errorlevel 1 exit 1

:: Install.
cmake --build . --config Release --target install
if errorlevel 1 exit 1

if "%IS_CATKIN_PKG%" == "1" (

:: Copy the [de]activate scripts to %PREFIX%\etc\conda\[de]activate.d.
:: This will allow them to be run on environment activation.
for %%F in (activate deactivate) DO (
    if not exist %PREFIX%\etc\conda\%%F.d mkdir %PREFIX%\etc\conda\%%F.d
    copy %RECIPE_DIR%\%%F.bat %PREFIX%\etc\conda\%%F.d\%PKG_NAME%_%%F.bat
)

)