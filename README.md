# Students Repository for HSLU Module "DevOps"

The following commands are all ment to be executed in the root directory of the project.

## Mac/Linux

### Run your Script

For example, the hangman.py script

```
source ../.venv/bin/activate # if not already activated
export PYTHONPATH=$(pwd)
python server/py/hangman.py
```

### Run the Benchmark

```
source ../.venv/bin/activate # if not already activated
export PYTHONPATH=$(pwd)
python benchmark/benchmark_hangman.py python hangman.Hangman # or battleship.Battleship
```

### Start the Server

```
source ../.venv/bin/activate # if not already activated
uvicorn server.py.main:app --reload
```

Open up your browser and go to http://localhost:8000

## Windows

### Run your Script

For example, the hangman.py script

```
"../.venv\Scripts\activate" # if not already activated
set PYTHONPATH=%cd%
python server/py/hangman.py
```

### Run the Benchmark

```
"../.venv\Scripts\activate" # if not already activated
set PYTHONPATH=%cd%
python benchmark/benchmark_hangman.py python hangman.Hangman # or battleship.Battleship
```

### Start the Server

```
"../.venv\Scripts\activate" # if not already activated
uvicorn server.py.main:app --reload
start chrome http://localhost:8000
```

### Additional Notes Nick

#### Run Dog Benchmark (with Python on Mac)

```
python benchmark/benchmark_dog.py python dog.Dog
```

#### Run Dog Test (on Mac)

```
python test/test_dog.py
```

The Benchmark File `benchmark_dog.py` contains many helper functions which need to be copied to the test file `test_dog.py` to pass some of the tests.

Helper functions are marked with the comment `# helper functions our code needs to run` at the end of the file.
