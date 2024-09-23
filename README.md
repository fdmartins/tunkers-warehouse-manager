== Projeto Tunkers Gerenciamento Armazem LGVs ==

python 3.12.1

== Para gerar um executavel ==

pyinstaller --icon=../icons/fav-icon.png  --add-data "instance/gerenciador_tunkers.db;instance" --add-data "configs/*;configs" --add-data "templates;templates" --add-data "static;static" run.py