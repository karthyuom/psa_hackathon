set PATH=D:\sam\tools\nginx-1.10.1\sqlite3;D:\sam\tools\nginx-1.10.1\sqlite3\sqlite-tools;C:\msys\1.0\bin;D:\Python\ANACONDA;D:\Python\ANACONDA\Scripts;D:\Python\ANACONDA\Lib;%PATH%;
@ECHO OFF
taskkill /f /IM nginx.exe
taskkill /f /IM php-cgi.exe
echo starting php-cgi
cd D:\sam\tools\nginx-1.10.1\
RunHiddenConsole.exe php\php-cgi.exe -b 127.0.0.1:9000 -c php\php.ini
echo php-cgi started
RunHiddenConsole.exe nginx.exe
ping 127.0.0.1 -n 1>NUL
echo Starting nginx
echo .
echo .
echo .
ping 127.0.0.1 >NUL
EXIT