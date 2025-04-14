# Play music with AY8913 and SN76489 replicas on Tiny Tapeout 05

This is a testing code for AY-3-8913 and SN76489 implementations on [Tiny Tapeout 05](https://tinytapeout.com/runs/tt05), running on micropython on the RP2040.

* [tt_um_rejunity_ay8913](https://tinytapeout.com/runs/tt05/tt_um_rejunity_ay8913) is an implementation of the AY-3-8913, a 3-voice programmable sound generator chip from General Instruments and
* [tt_um_rejunity_sn76489](https://tinytapeout.com/runs/tt05/tt_um_rejunity_sn76489) is an impleentation of the SN76489, a 4-voice programmable sound generator chip from Texas Instruments

This will let you either play with the AY8913 / SN76489 interface directly or just call functions to play tunes.

NOTE: this all assumes you're running a Tiny Tapeout 5 demoboard, with [the SDK](https://github.com/TinyTapeout/tt-micropython-firmware/) and [micropython](https://www.micropython.org) installed.

## Install
Installation basically involves copying over the `tt_um_rejunity_ay8913` and `tt_um_rejunity_sn76489` directories onto the micropython FS under `examples/`.

```
mpremote cp -r sample :/examples/
mpremote cp -r tt_um_rejunity_sn76489 :/examples/
mpremote cp -r tt_um_rejunity_ay8913 :/examples/
```

## Play tunes with AY8913

You'll need a file, such as that found in samples/ here, of the right format or to figure out how to get the register values to set for each time tick on your own.

The "psym" format is a derivative of YM files, such as those [found here](http://antarctica.no/stuff/atari/YM2/).  There's some complexity and processing involved in these things, which we don't have time for on the RP2040.  So I wrote [convertym](https://github.com/psychogenic/convertym) that takes in a ym file, uses the pretty sweet [StSoundLibrary](https://github.com/arnaud-carre/StSound/tree/main/StSoundLibrary) and dumps out a file that's just an uncompressed sequence of register settings.

To use the player, you can simply load your psym file onto the RP2040 fs and then do:

```
import examples.tt_um_rejunity_ay8913.play_psym as player

player.run('examples/sample/doubledragon.psym')

```

## Play tunes with SN76489

Similar to "psym" format, the "binsn" is a simplification of VGM files, such as those [found here](https://www.stairwaytohell.com/music/index.html?page=vgmarchive). Use [vgm-converter](https://github.com/simondotm/vgm-converter) that takes vgm and dumps out a file that's just an uncompressed sequence of register settings.

To use the player, you can simply load your music file onto the RP2040 fs and then do:

```
import examples.tt_um_rejunity_sn76489.play_binsn as player

player.run('examples/sample/mission76496.rawsn')

```


## Set registers manually

There are two implementations of the API -- a pure python and a PIO-based.  The PIO is fast (like 40us to set a register vs close to 8ms using the pure Python SDK).  Both support a simple

```
    set_register(regid, value)
```

method that does the right thing.  


There's also a way to just send over a list of registers to set, per sample, e.g.
```
      Data = [
              [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,255),(8,0),(9,0),(10,0),(11,0),(12,0),(13,0),(14,0),(15,0)]
              [(4,255),(7,251),(10,8),(13,15)]
              [(0,214),(7,250),(8,9)],
              # ...
      ]
```
Then, `tt_um_rejunity_ay8913.play_array` has a `run(data_list, sample_rate:int=50)` you may call to feed in each list of registers at the right beat.

For more, use the source.

