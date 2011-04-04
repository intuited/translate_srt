``translate_srt``
=================

Provides functions and a CLI to facilitate the translation of .srt files.

Translation is done using the `pytranslate`_ module,
which uses the Google Translate API.
Note that it is currently (2011-04-03)
still indicated as being in the "Planning" stage of development.

.. _pytranslate: http://pypi.python.org/pypi/pytranslate/0.1.4


ISSUES
------

-   Separate translation requests are done for each individual caption.
    This means that users with busy network connections
    will experience longer than optimal translation times.

-   I don't really know what the format for an .srt file is supposed to be.
    The routines seem to work for the files I'm using.
    See the source for details on my assumptions.

-   Caption text is joined into a single line.
    This may cause problems with some players (I really don't know).
    It will also break captions with two speakers such as ::
        - Interrupting cow wh--
        - MOOOO!!!
    This line would end up being displayed as ::
        - Interrupting cow wh-- - MOOOO!!!
