.3ds
.arm

; Download "Pokemon Emerald ACE contest Poke 1.sav" as "pokecontest.sav"
; https://sites.google.com/site/torchickens2/pokemon-save-files
.open "pokecontest.sav",0

; Overwrite existing ARM code in the premade savefile
.org 0xDB1C

NOP
NOP

; Fix ARM7 PC bit1 bug caused by the Thumb instruction in the original savefile
BIC PC, PC, #3

NOP
NOP

; Above BIC should skip the two NOPs above
NOP
NOP

; Prepare for copying the payload to IWRAM,
;  as the 5V switch (in the cartridge port)
;  disables EWRAM as soon as it's pressed

ADR r0, payload_start
ADR r1, payload_end

MOV r2, #0x03000000 ; IWRAM
MOV r4, r2          ; Payload entry address == IWRAM


copy_loop:
LDR r3, [r0], #4
STR r3, [r2], #4

CMP r0, r1
BNE copy_loop

BX r4 ; Jump to payload

NOP
NOP

payload_start:

; Setup few registers to contain necessary hardware addresses

MOV r4, #0x04000000
ORR r5, r4, #0x200
ORR r6, r4, #0x130

MOV r0, #0
STRH r0, [r5, #8] ; 0x208 IME = 0 ; Disable all interrupts


LDRH r2, [r5, #0] ; 0x200 IE
LDRH r3, [r5, #2] ; 0x202 IF
AND r1, r3, r2
STRH r1, [r5, #2] ; 0x202 IF - clear pending interrupts

MOV r0, #0
STRH r0, [r5, #0] ; 0x200 IE = 0 - Disable all interrupts

MOV r0, #0
STRH r0, [r6, #2] ; 0x132 KEYCNT = 0 - Disable key interrupts


MSR CPSR_c, #0xDF ; Disable CPU interrupts


MOV r0, #8
STRH r0, [r4, #4] ; 0x004 DISPSTAT - VBlank IRQ enable


; Clear all sound registers (should also stop GBA crash sound)

MOV r1, #0

ORR r7, r4, #0x60

STRH r1, [r7, #0]
STRH r1, [r7, #2]
STRH r1, [r7, #4]
STRH r1, [r7, #8]
STRH r1, [r7, #12]

ORR r7, r4, #0x70

STRH r1, [r7, #0]
STRH r1, [r7, #2]
STRH r1, [r7, #4]
STRH r1, [r7, #8]
STRH r1, [r7, #12]

ORR r7, r4, #0x80

STRH r1, [r7, #0]
STRH r1, [r7, #2]
STRH r1, [r7, #4]


; Initialize sound registers to what the BIOS initializes them to
; from https://github.com/AntonioND/gba-switch-to-gbc

MOV r2, #0x8800
ORR r2, #0xC2
STRH r2, [r7, #2]

MOV r2, #0xC200
STRH r2, [r7, #8]


; Wait option 1 - wait for key held
; Note: only L and R works, as the rest of the buttons
;  return 0 upon the 5V switch is pressed in
ORR r6, r4, #0x130
lol:
LDRH r1, [r6]     ; 0x130 KEYINPUT
TST r1, #(1 << 8) ; Check for R pressed
BNE lol

/*
; Wait option 2 - wait for 5V switch (unreliable)
ORR r6, r4, #0x200
lol:
LDR r1, [r6, #4] ; 0x204 WAITCNT
TST r1, #0x8000 ; Check for CGB cart
BEQ lol
*/


ORR r5, r4, #0x200
MOV r0, #1
STRH r0, [r5, #0] ; 0x200 IE = 1 - Enable VBlank interrupt (needed for BIOS switch routine)

/*
ORR r7, r4, #0x800
LDR r8, [r7]
ORR r8, #(1 << 3)
STR r8, [r7] ; 0x800 undocumented - Enable the skip CGB BootROM bit
*/

MOV r0, #0x280
ADD r0, #5
BLX r0 ; (0x284 | 1) - BIOS CGB mode switch routine


B .
B .
B .
B .
B .
B .

B .
B .
.pool

payload_end:

.close
