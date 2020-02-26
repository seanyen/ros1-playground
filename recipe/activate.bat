@if not defined CONDA_PREFIX goto:eof

@if defined SYS_PREFIX exit /b 0

@call "%CONDA_PREFIX%\Library\local_setup.bat"
