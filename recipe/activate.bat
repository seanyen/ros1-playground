@if not defined CONDA_PREFIX goto:eof

@if defined SYS_PREFIX exit /b 0

@if defined CONDA_PREFIX_1 set "PYTHONPATH=%CONDA_PREFIX_1%\lib\site-packages;%PYTHONPATH%"

@set "PYTHONPATH=%CONDA_PREFIX%\lib\site-packages;%PYTHONPATH%"
@call "%CONDA_PREFIX%\Library\local_setup.bat"
