@echo off
set USERNAME=fakeuser
set PASSWORD=WrongPassword
set DOMAIN=localhost

:: Attempt to use incorrect credentials
cmdkey /add:%DOMAIN% /user:%USERNAME% /pass:%PASSWORD%
runas /user:%USERNAME% notepad.exe
