@echo off
cd /d "%~dp0"
set "MODEL=models\qwen2.5-3b-instruct-q4_k_m.gguf"
if not "%~1"=="" set "MODEL=%~1"
if not exist "llama\llama-server.exe" goto no_llama
if not exist "%MODEL%" goto no_model
echo Avvio llama-server su %MODEL% ...
llama\llama-server.exe serve -m "%MODEL%" -c 4096 -t 8 --port 8080 --host 127.0.0.1 --jinja
pause
exit /b
:no_llama
echo ERRORE: llama\llama-server.exe non trovato.
pause
exit /b 1
:no_model
echo ERRORE: modello non trovato: %MODEL%
pause
exit /b 1
