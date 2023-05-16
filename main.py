import nbtlib
from nbtlib.tag import Int, List, Compound, String, Byte, Short, Long, Float, Double, ByteArray, IntArray, LongArray
import os
import sys
import mido

notesX ={
    'C':"tconstruct:ender_slime_sapling",
    "C#":"minecraft:dark_oak_sapling",
    "D":"croptopia:cinnamon_sapling",
    "D#":"minecraft:birch_sapling",
    "E":"pioneer:baobab_sapling",
    "F":"pioneer:aspen_sapling",
    "F#":"minecraft:acacia_sapling",
    "G":"quark:pink_blossom_sapling",
    "G#":"minecraft:jungle_sapling",
    "A":"terraincognita:hazel_sapling",
    "A#":"quark:blue_blossom_sapling",
    "B":"quark:red_blossom_sapling"
}

octavesX = {
    "2":"tconstruct:greenheart_log",
    "3":"minecraft:dark_oak_log",
    "4":"minecraft:oak_log",
    "5":"minecraft:birch_log",
}


file=sys.argv[1]


# Define mapping from MIDI note numbers to note names
notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']



# Load MIDI file
mid = mido.MidiFile(f'midi/{file}')

# Keep track of currently active notes
active_notes = set()

# Iterate through all messages in the MIDI file
melody=[]

print("Loading MIDI file...")

for msg in mid.play():

    # Check if the message is a note on or off event
    if msg.type == 'note_on' and msg.velocity > 0:

        # Add the note to the set of active notes
        active_notes.add(msg.note)
        # print(' '.join(notes[note % 12] + str(note // 12 - 1) for note in sorted(active_notes)), end=' ')

        # Convert MIDI note number to note name
        # note_name = notes[msg.note % 12]+ str(msg.note // 12 - 1)

        # Print all active notes
        # print(note_name)
        #add active notes to melody


        melody.append(','.join(notes[note % 12]+" " + str(note // 12 - 1) for note in sorted(active_notes)))

    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):

        # Remove the note from the set of active notes
        active_notes.discard(msg.note)
        # print(' '.join(notes[note % 12] + str(note // 12 - 1) for note in sorted(active_notes)), end=' ')

        # Convert MIDI note number to note name
        # note_name = notes[msg.note % 12]+ str(msg.note // 12 - 1)

        # Print all active notes
        # print(note_name)

        #add active notes to melody
        melody.append(','.join(notes[note % 12]+" " + str(note // 12 -1 ) for note in sorted(active_notes)))

melody2 = melody.copy()

for i in range(len(melody2)):
    if melody2[i] != "":
        for j in range(len(melody2[i].split(','))):
            octave = melody2[i].split(',')[j].split(' ')[1]
            if int(octave) > 5:
                #change to 5
                melody2[i] = melody2[i].replace(melody2[i].split(',')[j], melody2[i].split(',')[j].replace(octave, "5"))

            if int(octave) < 2:
                #change to 2
                melody2[i] = melody2[i].replace(melody2[i].split(',')[j], melody2[i].split(',')[j].replace(octave, "2"))
    


#get biggest ammount of notes at the same time
maxNotes = 0
for i in range(len(melody)):
    if len(melody[i].split(',')) > maxNotes:
        maxNotes = len(melody[i].split(','))
        # print(maxNotes)

#get max time
maxTime = len(melody)

print("Creating Schematic...")

schematic = nbtlib.nbt.File()

schematic['DataVersion'] = Int(2975)
schematic['entities'] = List[Compound]()
schematic['palette'] = List[Compound]()
schematic['blocks'] = List[Compound]()
schematic['size'] = List[Int]([Int(maxNotes), Int(2), Int(maxTime+2)])


#add palette
redstoneContactPallete = Compound({
    "Name": String("create:redstone_contact"),
    "Properties": Compound({
        "facing": String("up"),
        "powered": String("false")
    }),
})
redstoneLinkPallete = Compound({
    "Name": String("create:redstone_link"),
    "Properties": Compound({
        "facing": String("up"),
        "powered": String("false"),
        "reciver": String("false")
    }),

})

stonePallete = Compound({
    "Name": String("minecraft:stone"),
})

schematic['palette'].append(redstoneContactPallete)
schematic['palette'].append(redstoneLinkPallete)
schematic['palette'].append(stonePallete)

stoneBlock = Compound({
    "pos": List[Int]([Int(0), Int(0), Int(0)]),
    "state": Int(2),
})

print("Adding blocks...")

for i in range(len(melody2)):
    for j in range(len(melody2[i].split(','))):

        if melody2[i]!="":

            note = melody2[i].split(',')[j].split(' ')[0]
            octave = str(int(melody2[i].split(',')[j].split(' ')[1])-1)
            time = i
            noteBlock = notesX[note]
            # print(note, noteBlock)
            octaveBlock = octavesX[octave]


            redstoneLink = Compound({
                "nbt": Compound({
                    "FrequencyFirst": Compound({
                        "Count": Byte(1),
                        "id": String(f"{noteBlock}"),
                        "tag": Compound({
                            "display": Compound({
                                "Name": String('{"text":"'+str(note)+'"}')
                            })
                        })
                    }),

                    "FrequencyLast": Compound({
                        "Count": Byte(1),
                        "id": String(f"{octaveBlock}"),
                        "tag": Compound({
                            "display": Compound({
                                "Name": String('{"text":"'+str(octave)+'"}')
                            })
                        })
                    }),
                    "Receive": Int(0),
                    "ReceivedChanged": Byte(0),
                    "Transmit": Int(0),
                    "Transmitter": Byte(1),
                    "id": String("create:redstone_link"),
                }),
                "pos": List[Int]([Int(j), Int(0), Int(time+1)]),
                "state": Int(1)
            })

            redstoneContact = Compound({
                "pos": List[Int]([Int(j), Int(1), Int(time+1)]),
                "state": Int(0),
            })



            schematic['blocks'].append(redstoneLink)
            schematic['blocks'].append(redstoneContact)

print("Saving schematic...")
schematic.save(f"output/{file}.nbt", gzipped=True)