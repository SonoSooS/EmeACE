@"C:\Data\lolol\HzNG\tool\armips.exe" payload.S
@if %ERRORLEVEL% NEQ 0 @(
pause
goto :EOF
)
@"C:\Python36\python.exe" chkfix.py
@if %ERRORLEVEL% NEQ 0 @(
pause
goto :EOF
)