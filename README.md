# cdlpto

This is a command line application that will fill out CDL's PTO request form for you.

```bash
cdlpto 2023-06-26 --n-days 5 --comment "Summer Vacation"
```

After writing the PDF, the program will pop it open in Preview. It also opens an email draft in the Gmail web interface. Drag the document proxy icon from Preview's title bar to the compose window and hit send.

## Installation

Use [pipx](https://pypa.github.io/pipx/):

```bash
pipx install cdlpto
```

Plain old `pip` will work too.

Or, if you want a development version, use:

```bash
pip install --editable git+https://github.com/baldwint/cdlpto#egg=cdlpto
```

## Configuration

On first run, a config file is put in `~/Library/Application Support/cdlpto`. This is where you configure your name, email signature, and the person you send the form to. You should also put a blank, *signed* copy of the [PDF form](https://drive.google.com/file/d/1FtK2zw4tXpKm31RZnl6Tmjk4VkCMO8uT/view?usp=sharing) in this folder for use as a template.

## Usage

Run `cdlpto --help` to see the options. It can also do sick leave, floating holidays, etc.

## Limitations

It doesn't know about weekends or the CDL holiday schedule. So don't give it any multi-week spans, or spans that include days you don't need to take PTO for.
