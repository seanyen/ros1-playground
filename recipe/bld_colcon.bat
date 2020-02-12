setlocal

set "PYTHONPATH=%LIBRARY_PREFIX%\lib\site-packages;%SP_DIR%"
set "CMAKE_BUILD_PARALLEL_LEVEL=%NUMBER_OF_PROCESSOR%"

:: MSVC is preferred.
set CC=cl.exe
set CXX=cl.exe

:: remove the build folder
rd /s /q "%SRC_DIR%\build"

pushd %PKG_NAME%

colcon build ^
    --build-base %SRC_DIR% ^
    --install-base %LIBRARY_PREFIX% ^
    --merge-install ^
    --event-handlers console_cohesion+ ^
    --cmake-args ^
        -G Ninja ^
        -DBUILD_TESTING=OFF ^
        -DCMAKE_BUILD_TYPE=Release
if errorlevel 1 exit 1

if exist %LIBRARY_PREFIX%\.colcon_install_layout (
    del %LIBRARY_PREFIX%\.colcon_install_layout
)
if exist %LIBRARY_PREFIX%\COLCON_IGNORE (
    del %LIBRARY_PREFIX%\COLCON_IGNORE
)
if exist %LIBRARY_PREFIX%\local_setup.bat (
    del %LIBRARY_PREFIX%\local_setup.bat
)
if exist %LIBRARY_PREFIX%\local_setup.ps1 (
    del %LIBRARY_PREFIX%\local_setup.ps1
)
if exist %LIBRARY_PREFIX%\setup.bat (
    del %LIBRARY_PREFIX%\setup.bat
)
if exist %LIBRARY_PREFIX%\setup.ps1 (
    del %LIBRARY_PREFIX%\setup.ps1
)
if exist %LIBRARY_PREFIX%\_local_setup_util_bat.py (
    del %LIBRARY_PREFIX%\_local_setup_util_bat.py
)
if exist %LIBRARY_PREFIX%\_local_setup_util_ps1.py (
    del %LIBRARY_PREFIX%\_local_setup_util_ps1.py
)
if exist %LIBRARY_PREFIX%\__pycache__\ (
    rd /s /q %LIBRARY_PREFIX%\__pycache__\
)
