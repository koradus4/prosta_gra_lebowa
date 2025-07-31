import os
import subprocess

def export_to_github(repo_path, branch="main", commit_message="Aktualizacja projektu", remote_url=None):
    try:
        os.chdir(repo_path)

        # Inicjalizacja repozytorium, jeśli nie istnieje
        subprocess.run(["git", "init"], check=True)

        # Zmiana nazwy domyślnej gałęzi na 'main'
        subprocess.run(["git", "branch", "-M", branch], check=True)

        # Dodanie wszystkich plików
        subprocess.run(["git", "add", "."], check=True)

        # Commit zmian
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Ustawienie zdalnego repozytorium, jeśli podano
        if remote_url:
            subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)

        # Wypchnięcie zmian na zdalne repozytorium
        subprocess.run(["git", "push", "-u", "origin", branch], check=True)

        print("Projekt został wypchnięty na GitHub!")
    except subprocess.CalledProcessError as e:
        print(f"Wystąpił błąd: {e}")

# Przykład użycia
if __name__ == "__main__":
    repo_path = "C:\\Users\\klif\\prosta_gra_lebowa"
    branch = "main"
    commit_message = "Aktualizacja projektu"
    remote_url = "https://github.com/koradus4/prosta_gra_lebowa"  # Podmieniono na właściwy URL

    export_to_github(repo_path, branch, commit_message, remote_url)
