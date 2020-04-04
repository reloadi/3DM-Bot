# 3dmeltdown

This is a custom bot made for 3DMeltdown.

Python 3 is required.

## Features
CMD|Description
-------------------|---
!gcode some_text | Return result from marlin documentation
!convert 100 usd| Convert 100 usd to common currencies
!google some text |Search google for some text and display first result
!thing some text | Search thingiverse (using google for now) for some text and display first result
!tweet link [user] | Link your discord user to a twitter account for tagging when posting. If [user] is ommited, display current link
!tweet unlink [user] |Remove link between discord account and twitter account
!tweet top | Show top twitted members
!tweet [list|delete|ID] [pos] short text (restricted) | Post a user's message (ID) to the twitter account.

## Configuration

See config.cfg for configuration of various api and paths

The bot use a local sqlite.

To install the module run `pip3 install -r req.lst`

