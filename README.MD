# EmeACE

A payload built on top of [the 0x611 Hall of Fame ACE](https://www.youtube.com/watch?v=NiFAKMtCO4w) to [switch to GBC mode](https://github.com/AntonioND/gba-switch-to-gbc) from Pok‚mon Emerald.

While this repo is pointless for most people, those who can't afford a GBA flashcart yet still somehow own Pok‚mon Emerald can run simple payloads using this setup.

This code was originally made to test the behavior of bit3 in undocumented register 0x04000800 without owning a GBA flashcart.

## Repo layout

- payload.S contains the actual payload written into the savefile
- chkfix.py fixes up the box area checksum after modifying it with [ARMIPS](https://github.com/Kingcom/armips)
- pokecontest.sav is a premade savefile I used, but if you have 0x611 ACE already working then you may use your own savefile as well, I think. I hope. See header of payload.S

## Recommended use

While this repo was built for personal use, it's still faster than tediously (mis)typing box names using my method.

- Dump Emerald .sav with GBA Save Tool on a DS or DSLite
- Insert flashcart SD into your computer
- Copy and rename your savefile next to payload.S as "pokecontest.sav"
- Run `armips payload.S`
- Copy "pokecontest.sav" back to your flashcart SD into the same folder you found it
- Flash back the newly modified .sav to your Emerald cartridge
- Trigger the ACE

## Credits

TODO: gather *all* credits

- "merrp" for the ACE setup
- "CasualPokePlayer" for the savefile
- "Kingcom" for [ARMIPS](https://github.com/Kingcom/armips)
- "AntonioND" for [gba-switch-to-gbc](https://github.com/AntonioND/gba-switch-to-gbc)
- "ChickasaurusGL"/"Evie" for [the video showing how to use the ACE](https://www.youtube.com/watch?v=NiFAKMtCO4w)
- "Shiny Quagsire"/"shinyquagsire23" for bringing my attention to the undocumented reg
- "nocash"/"Martin" for [gbatek](https://problemkaputt.de/gbatek.htm)
- Bulbagarden for [the Bulbapedia article describing savefile documentation](https://bulbapedia.bulbagarden.net/wiki/Save_data_structure_(Generation_III))
