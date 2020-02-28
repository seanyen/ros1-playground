@if not defined CONDA_PREFIX goto:eof

@if defined SYS_PREFIX exit /b 0

@set "QT_PLUGIN_PATH=%CONDA_PREFIX%\Library\plugins"

@call "%CONDA_PREFIX%\Library\local_setup.bat"
