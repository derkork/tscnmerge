@echo off
java -jar antlr-4.9.1-complete.jar -o gen -visitor -Dlanguage=Python3 grammar/tscn_lexer.g4 grammar/tscn_parser.g4
python -m pipenv run pyinstaller -F tscnmerge.py