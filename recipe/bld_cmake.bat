:: MSVC is preferred.
setlocal
set CC=cl.exe
set CXX=cl.exe

rd /s /q build
mkdir build
pushd build

cmake ^
    -G "Ninja" ^
    -DCMAKE_INSTALL_PREFIX=%LIBRARY_PREFIX% ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DCMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP=True ^
    -DBUILD_SHARED_LIBS=ON ^
    %SRC_DIR%\%PKG_NAME%\src\work
if errorlevel 1 exit 1

cmake --build . --config Release --target install
if errorlevel 1 exit 1
