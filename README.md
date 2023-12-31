# rinha-de-compiler

Python interpreter para a [Rinha de Compiler](https://github.com/aripiprazole/rinha-de-compiler)

## HOW TO RUN

**Clone**

```
git clone git@github.com:fernandozanutto/rinha-compiler.git
```

### With Docker

```
docker build -t rinha .
docker run -v /path/to/json:/var/rinha/source.rinha.json rinha
```

Example running `combination.json` file:

```
docker run -v ./files/combination.json:/var/rinha/source.rinha.json rinha
```

### CLI

```
python main.py json/file/location
```

## DONE

Basicamente as implementações
da [especificação da arvore sintática abstrata](https://github.com/aripiprazole/rinha-de-compiler/blob/main/SPECS.md)
foram feitas.

Os programas combination, fib e sum estão rodando.

## TODO

- [x] Tratamento e checagem de erros
- [x] Ajustes nas operação binárias
    - as aritméticas estão retornando floats
    - concatenação de string e int está dando erro
- [x] Fazer dockerfile