# ZenCode language documentation

This repository contains the ZenCode language and systems documentation. It contains the full language specification as well as other meaningful information related to the language and the systems.

## Contributing

If you have ideas to be contributed, these need to be discussed first in the form of an RFC. We want to keep the language clean, tidy and easy to understand, yet at the same time want to remain open to good ideas that may improve the language.

## Compiling to HTML

Make sure you have Python 3 installed.

Then setup venv as follows:

```commandline
python -m venv .venv

# for windows
.venv\Scripts\activate
# for linux
source .venv\Bin\activate

pip -r requirements.txt
```

You can then run and compile as follows:

```commandline
python compile.py
```
