from py_stealth.methods import *
from datetime import datetime as dt, timedelta
from typing import Tuple
import inspect
# Can be changed
TILE_SEARCH_RANGE = 15

INITIAL_LOCATION = (2978, 3607)
FORGE_LOCATION = (2971, 3613)
FORGE = 0x0FB1
VERBOSE = True
# Generic types
SHOVEL = 0x0F39
TINKER_TOOLS = 0x6708
ORE = 0x19B9
GEMS = [0x0F10,
        0x0F13,
        0x0F25,
        0x0F15,
        0x0F16,
        0x0F26
        ]

INGOTS = 0x1BF2

BANK_ENTRY = (2476, 861)
BANK_ENTRY_DOOR = 0x40013D55  # 0x4000A9D1
BANK_INSIDE = (3438, 3422)
BANK_EXIT = (3445, 3442)
BANK_EXIT_DOOR = 0x400140BF

BANK_BOX_TYPE = 0x0436
BANK_BOX_ID = 0x40013FCE  # 0x4000AC58

GUMP_TINKER_TOOLS_CATEGORY_TOOLS = 29
GUMP_TINKER_TOOLS_TINKER_TOOLS_BUTTON = 128
GUMP_TINKER_TOOLS_SHOVEL_BUTTON = 100
GUMP_TINKER_ID = 0x7B28E708
EXIT_MINE_COORDINATES = (3023,3648)
ENTER_MINE_COORDINATES = (2466,821)
# Generic messages and tiles
SKIP_TILE_MESSAGES = ["no metal", "far away"]
NEXT_TRY_MESSAGES = ["loosen", "You dig some", "You dig up"]
CAVE_TILES = range(1339, 1358)

##########

def log(message = ""):
    if VERBOSE:
        AddToSystemJournal(f"[{inspect.stack()[1].function}] {message}")
        print(f"[{inspect.stack()[1].function}] {message}")

def cancel_targets():
    CancelWaitTarget()
    if TargetPresent():
        CancelTarget()

def find_tiles(center_x: int, center_y: int, radius: int) -> set[int, int, int, int]:
    _min_x, _min_y = center_x-radius, center_y-radius
    _max_x, _max_y = center_x+radius, center_y+radius
    _tiles_coordinates = []
    for _tile in CAVE_TILES:
        _tiles_coordinates += GetStaticTilesArray(
            _min_x, _min_y, _max_x, _max_y, WorldNum(), _tile)
    log(f"Found {str(len(_tiles_coordinates))} tiles")
    return _tiles_coordinates

def smelt():
    IgnoreReset()
    forge_x, forge_y = FORGE_LOCATION
    newMoveXY(forge_x, forge_y, True, 1, True)

    while FindType(ORE, Backpack()):
        # You can't smelt 1 ore =\
        if GetQuantity(FindItem()) > 1:
            WaitTargetTile(FORGE, forge_x, forge_y, GetZ(Self()))
            UseObject(FindItem())
            WaitJournalLine(dt.now(), "You smelt|You burn", 5000)
            Wait(1000)
        else:
            Ignore(FindItem())

def craft_item(tool_category: int, tool_button: int, tool_type: int, item_type: int, required_qty: int) -> None:
    if Count(item_type) < required_qty - 1:
        log(f"Crafting, {Count(item_type)=}/{required_qty}")
        unequip()

        for _gump_counter in range(0, GetGumpsCount()):
            CloseSimpleGump(_gump_counter)
            log("equipped the tool...")

        while Count(item_type) < required_qty:
            if FindType(tool_type, Backpack()):
                log("equipping tool...")
                while not GetType(ObjAtLayer(RhandLayer())) == TINKER_TOOLS:
                    Equip(RhandLayer(), FindItem())
                    Wait(500)

            UseObject(ObjAtLayer(RhandLayer()))
            Wait(500)
            log("waiting for gump...")
            wait_for_gump(tool_category)
            wait_for_gump(tool_button)
            wait_for_gump(0)


def find_gump(gump_id: int) -> bool:
    for _gump in range(0, GetGumpsCount()):
        if GetGumpID(_gump) == gump_id:
            return True
    return False


def wait_for_gump(button: int) -> None:
    _try = 0
    while not find_gump(GUMP_TINKER_ID):
        _try += 1
        Wait(500)
        if _try > 30:
            log("wat_for_gump timeout")
            return

    WaitGump(button)
    Wait(2000)

def unequip():
    for layer in [LhandLayer(), RhandLayer()]:
        while ObjAtLayer(layer):
            UnEquip(layer)
            Wait(500)

def mine(tile):
    tile, x, y, z = tile
    log(f"{x=}, {y=}")
    craft_item(GUMP_TINKER_TOOLS_CATEGORY_TOOLS,
                GUMP_TINKER_TOOLS_TINKER_TOOLS_BUTTON, TINKER_TOOLS, TINKER_TOOLS, 2)
    craft_item(GUMP_TINKER_TOOLS_CATEGORY_TOOLS,
                GUMP_TINKER_TOOLS_SHOVEL_BUTTON, TINKER_TOOLS, SHOVEL, 2)
    if newMoveXY(x, y, True, 1, True):
        while not Dead():
            started = dt.now() - timedelta(seconds=1)

            if not GetType(ObjAtLayer(LhandLayer())) == SHOVEL:
                unequip()

                if FindType(SHOVEL, Backpack()):
                    log("Tool found, equipping!")
                    Equip(LhandLayer(), FindItem())
                    Wait(500)

            # Smelt and return back to mining point
            if Weight() > 250:
                smelt()
                if Weight() > 200:
                    change_location(EXIT_MINE_COORDINATES, ENTER_MINE_COORDINATES)
                    unload_to_bank()
                    change_location(ENTER_MINE_COORDINATES, EXIT_MINE_COORDINATES)
                newMoveXY(x, y, True, 1, True)

            cancel_targets()
            UseObject(ObjAtLayer(LhandLayer()))

            WaitForTarget(2000)
            if TargetPresent():
                WaitTargetTile(tile, x, y, z)
                Wait(1000)
                WaitJournalLine(started, "|".join(SKIP_TILE_MESSAGES + NEXT_TRY_MESSAGES), 15000)


            if InJournalBetweenTimes("|".join(SKIP_TILE_MESSAGES), started, dt.now()) > 0:
                log("Skipping the tile")
                break
    else:
        print(f"Can't reach X: {x} Y: {y}")


def change_location(_from: Tuple[int, int], _to: Tuple[int, int]):
    attempt = 0
    while GetX(Self()) != _to[0] and GetY(Self()) != _to[1]:
        log(f"Changing location. {attempt}/10")

        NewMoveXY(_from[0], _from[1], True, 0, True)
        Wait(1000)
        attempt += 1
        if attempt > 10:
            log("Failed to change the location!")
            exit()
    log("Changed the location")


def unload_to_bank():
    """
    walks to bank, enters, and unloads PLANKS
    """
    log("Moving out to the bank...")

    NewMoveXY(*BANK_ENTRY, True, 0, True)
    _point = (GetX(Self()), GetY(Self()))

    while ((GetX(Self()), GetY(Self())) == _point):
        UseObject(BANK_ENTRY_DOOR)
        Wait(500)

    log("Opening the bank...")
    while LastContainer() != Backpack():
        UseObject(Backpack())
        Wait(1000)

    attempt = 0
    while LastContainer() != ObjAtLayer(BankLayer()):
        attempt += 1
        if attempt > 5:
            log("Failed to open bank")
            exit()
        UseObject(BANK_BOX_ID)
        Wait(500)
    log("Unloading...")
    while FindTypesArrayEx([INGOTS] + GEMS, [0xFFFF], [Backpack()], [True]):
        MoveItem(FindItem(), -1, ObjAtLayer(BankLayer()), 0, 0, 0)
        Wait(2000)

    log("Loading with ingots for tools production...")
    # We have to keep some Iron ingots to craft shovels\tools
    if not FindTypeEx(INGOTS, 0x0000, Backpack()):
        FindTypeEx(INGOTS, 0x0000, ObjAtLayer(BankLayer()))
        Grab(FindItem(), 80)
        Wait(2000)

    # TODO: repeat until really exited
    log("Leaving the bank...")

    NewMoveXY(*BANK_EXIT, True, 1, True)

    _point = (GetX(Self()), GetY(Self()))
    while ((GetX(Self()), GetY(Self())) == _point):
        UseObject(BANK_EXIT_DOOR)
        Wait(500)

if __name__ == "__main__":

    init_x, init_y = INITIAL_LOCATION
    newMoveXY(init_x, init_y, True, 1, True)
    tiles = find_tiles(GetX(Self()), GetY(Self()), TILE_SEARCH_RANGE)
    while not Dead() and Connected():
        for tile in range(0, len(tiles), 4):
            log(f"Tile: {tile}/{len(tiles)}")
            mine(tiles[tile])
