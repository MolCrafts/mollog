# Rich Console Logging

`mollog` ships with [`rich`](https://rich.readthedocs.io) as a base
dependency, exposed as a **formatter** rather than a handler. Pair it
with any handler that writes strings (`StreamHandler`, `FileHandler`,
...).

## Basic usage

```python
import sys

from mollog import Logger, RichFormatter, StreamHandler

handler = StreamHandler(stream=sys.stderr)
handler.set_formatter(RichFormatter())

logger = Logger("cli")
logger.add_handler(handler)

logger.info("render complete", frame=128)
logger.warning("value outside expected range", field="charge", observed="2+")
```

## Configuration

`RichFormatter` supports:

- `show_time`, `show_logger_name`, `show_extra` toggles
- `time_format` string (`strftime`)
- `markup` — enable Rich's inline `[bold]...[/bold]` markup in messages
- `highlighter` — swap the default `ReprHighlighter` used for extras
- `color_system` — `"truecolor"`, `"256"`, `"standard"`, or `None`
- `force_terminal` — force ANSI output even when the attached stream is
  not a tty

```python
from mollog import RichFormatter, StreamHandler

formatter = RichFormatter(
    show_time=False,
    color_system="256",
    markup=True,
)

handler = StreamHandler()
handler.set_formatter(formatter)
```

## Writing colored logs to files

Because Rich is a formatter, the same instance works with `FileHandler`
too — the file will contain ANSI escape codes, which tools like
`less -R` and most modern terminals can render:

```python
from mollog import FileHandler, RichFormatter

handler = FileHandler("/var/log/myapp.log")
handler.set_formatter(RichFormatter(color_system="256"))
```

To log to a file *without* ANSI codes (most production setups), just use
`TextFormatter` or `JSONFormatter` on the file handler and keep
`RichFormatter` on the stream handler.
