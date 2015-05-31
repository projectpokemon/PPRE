
Project Pokemon ROM Editor (PPRE)
=== 

URL: http://projectpokemon.org/ppre

Source Installation (All Operating Systems)
---
Download System Dependencies. You will need:

 * Git: https://git-scm.com/downloads
 * Python 2.7: https://www.python.org/downloads/
 * pip (if not included in Python installation)
 * PyQt4: http://www.riverbankcomputing.com/software/pyqt/download

Grab a copy of this repository. If you would like to clone it, do
`git clone https://github.com/projectpokemon/PPRE.git`, otherwise, just download
the zip/tarball and extract locally.

Install pip dependencies by running `pip install -r requirements.txt` inside of
PPRE's directory.

History
---

PPRE is a multi-purpose ROM editing tool for altering Nintendo DS Pokemon games.
The project was started originally to edit Pokemon Diamond and Pearl by SCV
based off of Treeki's Nitro Explorer and loadingNOW's thenewpoketext. pichu2000 
created a strong basis for the scripting capabilities that PPRE will always 
have. Alpha has added many new features to make PPRE as versatile as it is.
PPRE is written in Python and makes use of PyQt for its GUI. Development was led
by SCV and Alpha.

PPRE2 included a change in the core.

PPRE3 merged PPRE with RawDB for a more responsive rapid development. User interface is now automatically determined by its data structures.

Current version is PPRE 5. PPRE 5 features a the new RawDB that does not suffer from some of the original speed drawbacks. Many new data structures are being added to this version to provide much more functionality. PPRE 5 will include a GUI, CLI, and web API version in its final release.

To launch, run `python main5.py`

RawDB
=====

RawDB is a flexible binary reader and parser built primary for Pokémon and other NDS/3DS games. The goal of this is to make development of those games easier and more robust.

History
------
The origin of this project was from a need to use the same components for reading and writing in PPRE as the existing components in AlphaDB. Originally, AlphaDB was going to be used, except that it suffered from shaky data structures that required a lot of rewriting.

The first version of RawDB was just a quick rewrite of AlphaDB. It did not serve very well as an interface for writing data however. More write-able structures were added manually later.

RawDB:Atomic was a version built around the idea that this could become a very powerful binary parser that could accurately reconstruct the odd looking nitro data structures. After a few months of development, this was found to be horrendously slow at parsing despite the stronger read/write structures.

RawDB is again being re-written with the idea that incremental parsing and writing can be done well as long as data is carefully handled and exposed.

Usage
---
To make use of RawDB, add it to your Python path, or put it in your current working directory. Then it and its components can be imported directly.

To get the most usage out of this, you may wish to use a graphical user interface such as PPRE.
