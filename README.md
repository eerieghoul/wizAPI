# wizAPI

An API to interact and make bots in Wizard101

The wizAPI.py file contains a large number of functions to interact with Wizard101, Hopefully, you will find it useful :)

# How to run

- Make sure you have python version >= 3 installed and that you've configured your environment PATH variable to include the path to your python installation (Standard stuff, Python 3.6 even does it for you)
- Open the terminal of you choice (can be cmd) and cd into the project folder
- Run `python -m pip install -r requirements.txt` in the command line to install all dependencies
- To run farm_loremaster.py type in `python farm_loremaster.py` (It needs 2 w101 windows opened for this particular bot)
- Make your own bots! Looks at the code of `farm_loremaster.py` and get the sense on how this API is used. Go through each of the functions in `wizAPI.py` and look at what they do! THen build your own for your purpose.

# IMPORTANT

Make sure your windows are set to an 800 x 600 resolution and your interface size is Medium

To add your own spells, use the 'screenshot' function from the API when spell selection is opened.
Take this image and crop it so that only the image of the spell is visible (see spells folder for examples)
Rename it to the name of the spell, and add it to the spells folder.

I will probably add docs when I get the time.

# Syntax

I coded this library to be very intuitive and easy to use. Here's an example script:

```
import * from wizAPI
player = wizAPI().register_window()

(
  player.hold_key('s', 3)
  .face_arrow()
  .hold_key('w', 3)
)

player.wait_for_our_turn()
inFight = True

while inFight:
    (
      player.enchant('tempest', 'epic')
      .cast_spell('tempest-enchanted')
    )

    player.wait_for_end_of_round()

    if player.is_idle():
      inFight = False

# Fight complete!
```
