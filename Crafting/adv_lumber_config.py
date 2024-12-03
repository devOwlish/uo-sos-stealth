WEIGHT_TO_PACK = 575
WEIGHT_TO_UNLOAD = 320

CHOP_DELAY = 5000

BANK_ENTRY = (2476, 861)
BANK_ENTRY_DOOR = 0x40013D55
BANK_INSIDE = (3438, 3422)
BANK_EXIT = (3445, 3442)
BANK_EXIT_DOOR = 0x400140BF

BANK_BOX_TYPE = 0x0436
BANK_BOX_ID = 0x40013FCE

DRINK_REFILL_POINT = (2418, 867)

DRINK_REFILL_TILES = (0x22A1, 0x0B42)

# 0x0B42 2356 877 2

# 0x22A1 2356 876 2

# 0x22A1 2418 866 2

# Serial=0x4000AC58 Graphic=0x0436 Name=
# Count: 1  Color: 0x0000  Layer: 0
# X=3442 Y=3442 Z=0 C=0xFFFFFFFF F=0x00
# Properties:
# Bank Vault


# Common types
LUMBER_BAG = 0x1C10
AXE = 0x2D34  # 0x0F48 #0x0F4B #0x0F4B # 0x0F49 # 0x0F4B #  #0x0F43
AXES = [0x0F48, 0x265B, 0x0F47, 0x2660, # - battle axes
        0x265C, 0x2D28, 0x2D34,         # - barbarian axes
        0x0F43, 0x0F49, 0x2665                         # - hatchet
        ]
# 0x0F43 - hatchet
LOG = 0x1BE0
PLANK = 0x1BD7
SAW_MILL = 0x1BDA #0x0788
BOARDS = 0x1BD7

# Messages to skip current tile (depleted, etc0
# There's not enough wood here to harvest. {'x': 2304, 'y': 904, 'resetTime': datetime.datetime(2021, 9, 30, 0, 23, 22, 659782)}
SKIP_TILE_MESSAGES = [
                        "not enough",
                        "You cannot",
]
# Messages to continue chopping
NEXT_TRY_MESSAGES = [
                        "You hack at",
                        "You put",
                        "You chop",
                        "You have worn"
]
# Messages to mark tile as bad
BAD_POINT_MESSAGES = [
                        "You can't use",
                        "be seen",
                        "is too far",
                        "no line of",
                        "axe on that",
]

#################### YEW ####################
SHRON_BAG = 0x40053443
DROP_POINT = (2404, 857)
DROP_POINT_FULL_STACKS = (2406, 857)
POINTS = [
    (2375, 892, 5),
    (2409, 903, 5),
    (2450, 903, 5),
    (2473, 901, 5),
    (2501, 891, 5),
    (2522, 876, 5),
    (2501, 886, 5),
    (2500, 842, 5),
    (2473, 836, 5),
    (2446, 837, 5),
    (2424, 843, 5),
    (2388, 866, 5),
    (2364, 877, 5),
]
SAW_MILL_POINT = (2404, 856)
REGION_BORDERS = {  'x_min' : 2360,
                    'x_max' : 2533,
                    'y_min' : 820,
                    'y_max' : 920,
}
#################### YEW ####################



#################### EAST of britain ####################
# (stucks at houses smtimes)
# POINTS = [
#     (3131, 1108, 5),
#     (3136, 1078, 5),
#     (3167, 1076, 5),
#     (3165, 1105, 5),
#     (3166, 1138, 5),
#     (3139, 1140, 5),
# ]


#################### WEST of britain ####################
# SoVa's points
# POINTS = [
#     (2901, 870, 5),
#     (2896, 846, 5),
#     (2862, 838, 5),
#     (2889, 792, 5),
#     (2925, 769, 5),
#     (2947, 796, 5),
#     (2956, 828, 5)
# ]
# SAW_MILL_POINT = (2942, 1051) brit west

TREE_TILES = [
    0x0CCA,
    0x0CCB, 0x0CCC, 0x0CCD, 0x0CD0,
    0x0CD3, 0x0CD6, 0x0CD8, 0x0CDA,
    0x0CDD, 0x0CE0, 0x0CE3, 0x0CE6,
    0x0D42, 0x0D43, 0x0D59, 0x0D70,
    0x0D85, 0x0D94, 0x0D98, 0x0D9C,
    0x0DA0, 0x0DA4, 0x0DA8, 0x0C9E,
    0x0CA8, 0x0CAA, 0x0CAB, 0x0CC9,
    0x0CF8, 0x0CFB, 0x0CFE, 0x0D01,
    0x12B8, 0x12B9, 0x12BA, 0x12BB,
]

# TREE_TILES = [
#     2500, 2499, 2513, 2516,
#     2470, 2520, 2524,
#     2410,
#     3274, 3275, 3277, 3280,
#     3283, 3286, 3288, 3290,
#     3293, 3296, 3299, 3302,
#     3320, 3323, 3326, 3329,
#     3393, 3394, 3395, 3396,
#     3415, 3416, 3417, 3418,
#     3419, 3438, 3439, 3440,
#     3441, 3442, 3460, 3461,
#     3462, 3476, 3478, 3480,
#     3482, 3484, 3492, 3496
# ]