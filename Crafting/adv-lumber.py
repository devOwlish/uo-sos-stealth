from time import time
from typing import Container, Tuple
from py_stealth.methods import *
from datetime import timedelta, datetime as dt

from adv_imports import *
from my_logger import logger
from adv_lumber_config import *

# initial
BAD_POINTS = []
chopped_trees = []
HUNGER_TIMESTAMP = dt.now()

def is_point_in_region(x, y):
    """
    returns True if cordinates are in rectangular region
    REGION_BORDERS defined in adv_imports
    """
    if x > REGION_BORDERS['x_max'] or x < REGION_BORDERS['x_min'] or y > REGION_BORDERS['y_max'] or y < REGION_BORDERS['y_min']:
        return False
    return True

def set_tree_chopped(tree):
    """
    appends global chopped_trees with coord and dt.now()
    """
    _tree = { 'x' : tree['x'],'y' : tree['y'] }
    _tree['resetTime'] = dt.now() + timedelta(minutes=20)
    chopped_trees.append(_tree)

def is_tree_chopped(tree):
    """
    returns True if tree is chopped and False respectively
    """
    for _tree in chopped_trees:
        if (_tree['x'] == tree['x']) and (_tree['y'] == tree['y']):
            if _tree['resetTime'] < dt.now():
                chopped_trees.remove(_tree)
                return False
            else:
                return True
    return False

def find_tree():
    logger.debug('Finding trees')
    Wait(100)
    for _r in range(1, 20):
        found_tiles = find_tiles(_r, GetX(Self()), GetY(Self()))
        for index in range(len(found_tiles)):
            tile, x, y, _ = found_tiles[index]
            if not is_tree_chopped({'x' : x, 'y' : y}) and is_point_in_region(x, y):
                logger.debug(f'r={_r}, tree at: {x}, {y}')
                return tile, x, y
    logger.debug('no ready trees at the point')
    return -1, -1, -1

def find_tiles(radius: int, center_x, center_y) -> list:
    _tiles_coordinates = []
    _tiles_coordinates += GetStaticTilesArray(center_x - radius, center_y - radius, center_x + radius,
                                                center_y + radius, WorldNum(), TREE_TILES)
    # for _tile in TREE_TILES:
        # logger.debug(f'tile {_tile}')
        #_tiles_coordinates += GetLandTilesArray(center_x - radius, center_y - radius, center_x + radius,
        #                                        center_y + radius, WorldNum(), _tile)
        #logger.debug(f"GetLandTilesArray {_tile} took {dt.now()-_stime}")
        # _tiles_coordinates += GetStaticTilesArray(center_x - radius, center_y - radius, center_x + radius,
        #                                         center_y + radius, WorldNum(), _tile)
        #logger.debug(f"GetStaticTilesArray {_tile} took {dt.now()-_stime}")
    return _tiles_coordinates

def to_bag() -> bool:
    logger.debug('packing stuff')
    if bag := FindType(LUMBER_BAG, Backpack()):
        while FindType(LOG, Backpack()):
            MoveItem(FindItem(), -1, bag, 0, 0, 0)
            Wait(1000)
        return True
    logger.error('ERROR: no bag skipping')
    return False

def get_coords(serial):
    return GetX(serial), GetY(serial)

def sell_mushrooms():
    # max gold with one sell operation is 15k
    pass

def to_ground() -> None:
    _i = 0
    logger.debug('shroning stuff')
    while FindType(PLANK, Backpack()):
        _planks_to_move = FindItem()
        SetFindDistance(3)
        SetFindVertical(25)
        if FindTypeEx(PLANK, GetColor(_planks_to_move), Ground(), False):
            for _stack in GetFoundList():
                if GetQuantity(_planks_to_move) + GetQuantity(_stack) > 60000 and get_coords(_stack) == DROP_POINT:
                    MoveItem(_stack, 0, Ground(), *DROP_POINT_FULL_STACKS, 0)
                    Wait(1500)
                    break
                elif get_coords(_stack) == DROP_POINT:
                    MoveItem(_planks_to_move, 0, _stack, 0,0,0)
                    break
                else:
                    pass
                    # MoveItem(_planks_to_move, 0, Ground(), *DROP_POINT, 0)
            if GetParent(_planks_to_move) == Backpack():
                MoveItem(_planks_to_move, 0, Ground(), *DROP_POINT, 0) # GetZ(Self())
            Wait(1500)
        # else:
        #     MoveItem(_planks_to_move, 0, Ground(), *DROP_POINT, 0) # GetZ(Self())

        _i += 1
        if _i > 20:
            while not Connected():
                Wait(5000)
            Wait(5000)


def cut(packing) -> None:
    goto_x_y(*SAW_MILL_POINT, 0)
    cancel_targets()
    while LastContainer() != Backpack():
        UseObject(Backpack())
        Wait(1000)
    if packing:
        while LastContainer() == Backpack(): # TODO: prolly endless loop if bag is lost
            UseType(LUMBER_BAG, 0xFFFF)
            Wait(1000)
    while FindType(LOG, LastContainer()):
        _log_stack = FindItem()
        cancel_targets()
        if not FindType(SAW_MILL, Ground()):
            logger.error(f"Saw mill not found")
            while not FindType(SAW_MILL, Ground()):
                Wait(10000)
        WaitTargetGround(SAW_MILL)
        UseObject(_log_stack)
        WaitJournalLine(dt.now(), "cut", 5000)
        Wait(1000)

def unload_to_bank():
    """
    walks to bank, enters, and unloads PLANKS
    """
    logger.debug("Moving out to the bank...")

    goto_x_y(*BANK_ENTRY, 1)
    _point = (GetX(Self()), GetY(Self()))
    # while not wait_for_result((GetX(Self()), GetY(Self())) != _point):
    #     UseObject(BANK_ENTRY_DOOR)

    while ( (GetX(Self()), GetY(Self())) == _point):
        UseObject(BANK_ENTRY_DOOR)
        Wait(500)

    # TODO: no need to walk, just start using the fng bankbox
    # NewMoveXY(*BANK_INSIDE, True, 1, True)
    logger.debug("Opening the bank...")
    while LastContainer() != Backpack():
        UseObject(Backpack())
        Wait(1000)

    attempt = 0
    while LastContainer() != ObjAtLayer(BankLayer()):
        attempt += 1
        if attempt > 5:
            logger.error("Failed to open bank")
            exit()
        # UseFromGround(BANK_BOX_TYPE, 0xFFFF)
        UseObject(BANK_BOX_ID)
        Wait(500)
    logger.debug("Unloading...")
    while FindTypesArrayEx([PLANK], [0xFFFF], [Backpack()], [True]):
        MoveItem(FindItem(), -1, ObjAtLayer(BankLayer()), 0, 0, 0)
        Wait(2000)

    # TODO: repeat until really exited
    logger.debug("Leaving the bank...")

    NewMoveXY(*BANK_EXIT, True, 1, True)

    _point = (GetX(Self()), GetY(Self()))
    while ( (GetX(Self()), GetY(Self())) == _point):
        UseObject(BANK_EXIT_DOOR)
        Wait(500)

def lumberjacking(tile, x, y, packing): #: tuple[int, int, int, int]) -> None:

    if ([x, y] not in BAD_POINTS) and NewMoveXY(x, y, True, 1, True):
        _dead_timestamp = dt.now()
        while Dead():
            Wait(1000)
            if dt.now() - _dead_timestamp > timedelta(minutes=10):
                _dead_timestamp = dt.now()
                logger.error(f"Dead...")
        while not Dead():
            cancel_targets()
            if _tool_layer := check_and_equip_tool(AXES):
                # logger.debug(f"tool layer is {_tool_layer}")
                pass
            else:
                logger.error('tool problems')
                exit()
            if Weight() > WEIGHT_TO_PACK and packing:
                to_bag()
            if Weight() > WEIGHT_TO_UNLOAD:
                cut(packing)
                # newMoveXY(*SAW_MILL_POINT, True, 1, True)
                # exit()
                # to_ground()
                unload_to_bank()
                NewMoveXY(x, y, True, 1, True)
            _started_chopping = dt.now()
            UseObject(ObjAtLayer(_tool_layer))
            WaitForTarget(2000)
            if TargetPresent():
                WaitTargetTile(tile, x, y, GetZ(Self()))
                WaitJournalLine(_started_chopping, "|".join(NEXT_TRY_MESSAGES + SKIP_TILE_MESSAGES + BAD_POINT_MESSAGES),
                                CHOP_DELAY)
                # If WaitJournalLine timeout happened, then smth went po pizde
                if dt.now() >= _started_chopping+timedelta(milliseconds=CHOP_DELAY):
                    logger.debug(f"{tile}: {x}, {y} WaitJournalLine timeout exceeded, bad tree?")
                    break
                if InJournalBetweenTimes("|".join(BAD_POINT_MESSAGES), _started_chopping, dt.now()) > 0:
                    if [x, y] not in BAD_POINTS:
                        logger.debug(f"Added tree to bad points, trigger => {BAD_POINT_MESSAGES[FoundedParamID()]}")
                        BAD_POINTS.append([x, y])
                        break
                if InJournalBetweenTimes("|".join(SKIP_TILE_MESSAGES), _started_chopping, dt.now()) > 0:
                    # log("Tile depleted, skipping")
                    break
            else:
                logger.debug("No target present for some reason...")
            Wait(500)
    return True

# Start
ClearSystemJournal()
SetARStatus(True)
SetMoveOpenDoor(True)
SetMoveThroughNPC(True)
SetPauseScriptOnDisconnectStatus(True)
IgnoreReset()
SetFindDistance(25)

if __name__ == "__main__":
    coordsFile = 'adv_coords_lumber.dump'
    chopped_trees = load_pickle('chopped_'+coordsFile)
    logger.info(f'loaded {len(chopped_trees)} chopped trees')
    # unload_to_bank()
    if bag := FindType(LUMBER_BAG, Backpack()):
        packing = True
    else:
        packing = False

    while Connected():
        for point in POINTS:
            point_x, point_y, _ = point
            newMoveXY(point_x, point_y, True, 1, True)
            while True:
                tile, x, y = find_tree()
                if tile == -1 : break
                if lumberjacking(tile, x, y, packing):
                    set_tree_chopped({'x' : x, 'y' : y})
                    hh = handle_hunger(HUNGER_TIMESTAMP)
                    HUNGER_TIMESTAMP = hh['timestamp']
                    drinks_left = hh['drinks_left']
                    meal_left = hh['meal_left']
                save_pickle_to_file(chopped_trees, 'chopped_'+coordsFile)