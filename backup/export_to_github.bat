@echo off
REM Skrypt do eksportu projektu na GitHub

REM Ustawienia
set REPO_PATH=C:\Users\klif\prosta_gra_lebowa
set GIT_BRANCH=main
set COMMIT_MESSAGE="Aktualizacja projektu"

REM Przejście do katalogu projektu
cd %REPO_PATH%

REM Inicjalizacja repozytorium (jeśli nie istnieje)
git init

REM Zmiana nazwy domyślnej gałęzi na 'main'
git branch -M %GIT_BRANCH%

REM Dodanie wszystkich plików
git add .

REM Commit zmian
git commit -m %COMMIT_MESSAGE%

REM Sprawdzenie, czy zdalne repozytorium już istnieje
(git remote get-url origin >nul 2>nul && git remote set-url origin https://github.com/koradus4/prosta_gra_lebowa) || git remote add origin https://github.com/koradus4/prosta_gra_lebowa

REM Wypchnięcie zmian na zdalne repozytorium
git push -u origin %GIT_BRANCH%

@echo Projekt został wypchnięty na GitHub!
