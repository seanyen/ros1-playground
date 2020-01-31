@echo off
setlocal

set CURRENT_PATH=%~dp0

set TEMP_PATH=%TEMP%\%RANDOM%
mkdir %TEMP_PATH%
IF %ERRORLEVEL% NEQ 0 (
  echo "Cannot create a temp folder: %TEMP_PATH%"
  exit /b 1
)

copy metagen.py %TEMP_PATH%\metagen.py /y

pushd %TEMP_PATH%

set ROS_DISTRO=noetic
set ROS_PACKAGE_PATH=%TEMP_PATH%\src
set ROS_PYTHON_VERSION=3

rosinstall_generator roscpp_core rospack --deps --tar --flat > ros.rosinstall

rd /s /q src
mkdir src
wstool init src
wstool merge -r -y -t src ros.rosinstall
wstool update -t src

python metagen.py
IF %ERRORLEVEL% NEQ 0 (
  echo "Cannot create meta.yaml"
  exit /b 1
)

popd

copy %TEMP_PATH%\meta.yaml meta.yaml /y
IF %ERRORLEVEL% NEQ 0 (
  echo "Cannot copy over meta.yaml"
  exit /b 1
)

echo "Succeeded!"
