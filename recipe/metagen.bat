@echo off
setlocal

set CURRENT_PATH=%~dp0
set UP_TO_PACKAGE=%1

if "%UP_TO_PACKAGE%" == "" (
  echo "Usage: metagen.bat <up-to-package>"
  exit /b 0
)

set TEMP_PATH=%TEMP%\%RANDOM%
mkdir %TEMP_PATH%
IF %ERRORLEVEL% NEQ 0 (
  echo "Cannot create a temp folder: %TEMP_PATH%"
  exit /b 1
)

echo Temp directory: %TEMP_PATH%

mkdir %TEMP_PATH%\etc
set ROS_ETC_DIR=%TEMP_PATH%\etc

rosdep init

set "URI_PATH=%CURRENT_PATH:\=/%/conda-forge.yaml"
echo yaml file:///%URI_PATH% conda > %ROS_ETC_DIR%\rosdep\sources.list.d\00-default.list

rosdep update

copy metagen.py %TEMP_PATH%\metagen.py /y

pushd %TEMP_PATH%

set ROS_DISTRO=eloquent
set ROS_PACKAGE_PATH=%TEMP_PATH%\src
set ROS_PYTHON_VERSION=3

rosinstall_generator %UP_TO_PACKAGE% --deps --flat ^
  --exclude ^
    rmw_cyclonedds_cpp rmw_opensplice_cpp rmw_connext_cpp ^
    gmock_vendor gtest_vendor libyaml_vendor ^
  > ros.rosinstall
IF %ERRORLEVEL% NEQ 0 (
  echo "Cannot create meta.yaml"
  exit /b 1
)

mkdir src
vcs import src < ros.rosinstall

:: del unwanted files
::del /f /q src\roslisp\manifest.xml

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

rd /s /q %TEMP_PATH%

echo Succeeded! Checkout the genereated meta.yaml file!
