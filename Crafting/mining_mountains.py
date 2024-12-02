from py_stealth.methods import *
from datetime import timedelta, datetime as dt
import math
import inspect
import pickle


#######################


# TODO:
# 1. разогнать, ибо сейчас в радиусе поиска тайлы, которые внутри горного массива, до которых ему
# никак не дойти. Либо статику лишнюю исключить из массива ли по-другому путь проверять
#
# 2. Унифицировать функции с ламбером: логгирование, перемещение, инструменты и т д
# сейчас оно просто тупо продублировано внутри этого, без импортов
#
# 3. Заход в банк переделать, ибо айди двери меняется
# 4. Открытие банка переделать, ибо айди банкбокса тоже, блядь, меняется
#
# 5. Приделать лошадь
#
# 6. Приделать еду из ламбера
#
# 7. Унифицировать для копки в шахте (вход/выход, регион, тайлы, статику)


#######################

REGION_BORDERS = {  'x_min' : 2320,
                    'x_max' : 2545,
                    'y_min' : 810,
                    'y_max' : 920,
}

# Can be changed
TILE_SEARCH_RANGE = 5
WEIGHT_TO_PACK = 450
WEIGHT_TO_UNLOAD = 200
WEIGHT_TO_SMELT = 200
INITIAL_LOCATION = (2349, 887)
FORGE_LOCATION = (2477, 888)
FORGE_POINT = (2479, 890)

BANK_ENTRY = (2476, 861)
BANK_ENTRY_DOOR = 0x40013D55  # 0x4000A9D1
BANK_INSIDE = (3438, 3422)
BANK_EXIT = (3445, 3442)
BANK_EXIT_DOOR = 0x400140BF

BANK_BOX_TYPE = 0x0436
BANK_BOX_ID = 0x40013FCE  # 0x4000AC58


GUMP_TINKER_TOOLS_CATEGORY_TOOLS = 29
GUMP_TINKER_TOOLS_TINKER_TOOLS_BUTTON = 128
GUMP_TINKER_TOOLS_SHOWEL_BUTTON = 100
GUMP_TINKER_ID = 0x7B28E708

POINTS = [
    (2488, 899),
    (2482, 902),
    (2476, 905),
    (2465, 907),
    (2457, 911),
    (2448, 911),
    (2437, 910),
    (2426, 907),
    (2411, 905),
    (2398, 909),
    (2390, 909),
    (2377, 905),
    (2362, 899),
    (2341, 872),
    (2369, 864),
    (2389, 849),
    (2383, 857),
    (2412, 848),
    (2415, 835),
    (2422, 830),
    (2432, 828),
    (2447, 822),
    (2455, 822),
    (2473, 826),
    (2481, 830),
    (2490, 833),
    (2499, 837),
    (2506, 840),
    (2516, 846),
    (2523, 855),
    (2522, 846),
    (2527, 866),
    (2532, 873),
    (2531, 867),
    (2526, 884),
    (2517, 888),
    (2510, 892),
    (2496, 897),
]
BAD_LOCATIONS = [
(2464, 821),
(2465, 821),
(2467, 821),
(2466, 821),
]
FORGE = 0x10DE
VERBOSE = True
# Generic types
GEMS = [0x0F10,
        0x0F13,
        0x0F25,
        0x0F15,
        0x0F16,
        0x0F26
]

INGOTS = 0x1BF2
#SHOVEL = 0x0F3A
SHOVEL = 0x0F39
MINING_BAG = 0x1C10
TINKER_TOOLS = 0x6708 #0x1EB8
ORE = 0x19B9


# Generic messages and tiles
BAD_TILE_MESSAGES = ["far away", "cannot be seen", "can't mine"]
DEPLETED_TILE_MESSAGES = ["no metal"]
NEXT_TRY_MESSAGES = ["loosen", "You dig some", "You dig up"]
# From UA sources
CAVE_TILES = [
    220, 221, 222, 223, 224, 225, 226, 227, 228, 229,
    230, 231, 236, 237, 238, 239, 240, 241, 242, 243,
    244, 245, 246, 247, 252, 253, 254, 255, 256, 257,
    258, 259, 260, 261, 262, 263, 268, 269, 270, 271,
    272, 273, 274, 275, 276, 277, 278, 279, 286, 287,
    288, 289, 290, 291, 292, 293, 294, 296, 296, 297,
    321, 322, 323, 324, 467, 468, 469, 470, 471, 472,
    473, 474, 476, 477, 478, 479, 480, 481, 482, 483,
    484, 485, 486, 487, 492, 493, 494, 495, 543, 544,
    545, 546, 547, 548, 549, 550, 551, 552, 553, 554,
    555, 556, 557, 558, 559, 560, 561, 562, 563, 564,
    565, 566, 567, 568, 569, 570, 571, 572, 573, 574,
    575, 576, 577, 578, 579, 581, 582, 583, 584, 585,
    586, 587, 588, 589, 590, 591, 592, 593, 594, 595,
    596, 597, 598, 599, 600, 601, 610, 611, 612, 613,

    1010, 1741, 1742, 1743, 1744, 1745, 1746, 1747, 1748, 1749,
    1750, 1751, 1752, 1753, 1754, 1755, 1756, 1757, 1771, 1772,
    1773, 1774, 1775, 1776, 1777, 1778, 1779, 1780, 1781, 1782,
    1783, 1784, 1785, 1786, 1787, 1788, 1789, 1790, 1801, 1802,
    1803, 1804, 1805, 1806, 1807, 1808, 1809, 1811, 1812, 1813,
    1814, 1815, 1816, 1817, 1818, 1819, 1820, 1821, 1822, 1823,
    1824, 1831, 1832, 1833, 1834, 1835, 1836, 1837, 1838, 1839,
    1840, 1841, 1842, 1843, 1844, 1845, 1846, 1847, 1848, 1849,
    1850, 1851, 1852, 1853, 1854, 1861, 1862, 1863, 1864, 1865,
    1866, 1867, 1868, 1869, 1870, 1871, 1872, 1873, 1874, 1875,
    1876, 1877, 1878, 1879, 1880, 1881, 1882, 1883, 1884, 1981,
    1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991,
    1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001,
    2002, 2003, 2004, 2028, 2029, 2030, 2031, 2032, 2033, 2100,
    2101, 2102, 2103, 2104, 2105,

    0x453B, 0x453C, 0x453D, 0x453E, 0x453F, 0x4540, 0x4541,
    0x4542, 0x4543, 0x4544,	0x4545, 0x4546, 0x4547, 0x4548,
    0x4549, 0x454A, 0x454B, 0x454C, 0x454D, 0x454E,	0x454F
]
##########

Bad_points = []
Mined_tiles = []

def load_pickle(filepath):
    """
    safe loads pickle file by filepath
    returns empty array if failed to load the file
    """
    try:
        loaded = pickle.load(open(filepath, 'rb'))
        return loaded
    except:
        return []

def save_pickle_to_file(mytuple, filepath):
    pickle.dump(mytuple, open(filepath, 'wb'))

def set_tile_mined(tile):
# append Mined_tiles with coord and dt.now()
    _tile = { 'x' : tile['x'],'y' : tile['y'] }
    _tile['resetTime'] = dt.now() + timedelta(minutes=20)
    Mined_tiles.append(_tile)

def is_tile_mined(tile):
# returns True if mined and False respectively
    # log(f"is tile mined? {tile}")
    # Wait(100)
    for _tile in Mined_tiles:
        if (_tile['x'] == tile['x']) and (_tile['y'] == tile['y']):
            if _tile['resetTime'] < dt.now():
                Mined_tiles.remove(_tile)
                return False
            else:
                # log(f"point is in mined tiles {_tile['x']}, {_tile['y']}")
                # Wait(100)
                return True
    for _x,_y,_ in Bad_points: # shitty but fast workaround TODO: refactor
        if (_x == tile['x']) and (_y == tile['y']):
            # log(f"point is in Bad tiles {_x}, {_y}")
            # Wait(100)
            return True

    return False

def log(message=""):
    if VERBOSE:
        AddToSystemJournal(f"[{inspect.stack()[1].function}] {message}")
        print(f"[{inspect.stack()[1].function}] {message}")

def cancel_targets():
    CancelWaitTarget()
    if TargetPresent():
        CancelTarget()


def find_tiles(radius: int, center_x: int, center_y: int) -> set[int, int, int, int]:
    _min_x, _min_y = center_x-radius, center_y-radius
    _max_x, _max_y = center_x+radius, center_y+radius
    _tiles_coordinates = []
    # log(f"Looking for tiles")
    # _dt_started=dt.now()

    _tiles_coordinates += GetStaticTilesArray(
            _min_x, _min_y, _max_x, _max_y, WorldNum(), CAVE_TILES)
    _tiles_coordinates += GetLandTilesArray(
            _min_x, _min_y, _max_x, _max_y, WorldNum(), CAVE_TILES)
    # for tile in CAVE_TILES:
    #     # print(f"tile {tile}")

    #     _tiles_coordinates += GetStaticTilesArray(
    #         _min_x, _min_y, _max_x, _max_y, WorldNum(), tile)
    #     log(GetLandTileData())
    #     _tiles_coordinates += GetLandTilesArray(
    #         _min_x, _min_y, _max_x, _max_y, WorldNum(), tile)

    # log(f"Found {str(len(_tiles_coordinates))} tiles in {dt.now()-_dt_started}")
    return _tiles_coordinates


def to_bag() -> None:
    log("Packing...")
    if bag := FindType(MINING_BAG, Backpack()):
        # Can't use while cuz of item limit in bag
        if FindType(ORE, Backpack()):
            for ore in GetFoundList():
                MoveItem(ore, -1, bag, 0, 0, 0)
                Wait(1500)


def smelt():
    log("Smelting...")
    IgnoreReset()
    forge_x, forge_y = FORGE_LOCATION
    move_x_y(forge_x, forge_y)

    if FindType(MINING_BAG, Backpack()):
        UseObject(FindItem())
        Wait(1000)

    while FindTypeEx(ORE, 0xFFFF, Backpack(), True):
        # You can't smelt 1 ore =\
        if GetQuantity(FindItem()) > 1:
            WaitTargetTile(FORGE, forge_x, forge_y, GetZ(Self()))
            UseObject(FindItem())
            WaitJournalLine(dt.now(), "You smelt|You burn", 5000)
            Wait(1000)
        else:
            Ignore(FindItem())


def craft_item(tool_category: int, tool_button: int, tool_type: int, item_type: int, required_qty: int) -> None:
    log("Crafting... TODO: FIX qty checks, tinker tools worn out during craft")
    while Count(item_type) < required_qty:
        for _gump_counter in range(0, GetGumpsCount()):
            CloseSimpleGump(_gump_counter)

        if FindType(tool_type, Backpack()):
            _tool_obj = FindItem()
            log("equipping tool...")
            while not ObjAtLayer(RhandLayer())==_tool_obj:
                Equip(RhandLayer(), FindItem())
                Wait(500)
            log("equipped the tool...")
            while True:
                UseObject(_tool_obj)
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


def mine(tile):
    tile, x, y, z = tile
    _bad = False
    _start = dt.now()

    if [x,y,tile] in Bad_points:
        log("Skipping bad tile")
        return

    if newMoveXY(x, y, True, 2, True):
        while not Dead():
            ClearJournal()
            # Smelt and return back to mining point
            if Weight() > WEIGHT_TO_PACK:
                Wait(1000)
                to_bag()
            if Weight() > WEIGHT_TO_SMELT:
                smelt()
            # if Weight() > WEIGHT_TO_UNLOAD:
                unload_to_bank()
                move_x_y(x, y)

            cancel_targets()


            if not GetType( ObjAtLayer(LhandLayer()))==SHOVEL:
                while ObjAtLayer(LhandLayer()):
                    UnEquip(LhandLayer())
                    Wait(500)
                while ObjAtLayer(RhandLayer()):
                    UnEquip(RhandLayer())
                    Wait(500)

                if FindType(SHOVEL, Backpack()):
                    log("Tool found, equipping!")
                    Equip(LhandLayer(), FindItem())
                    Wait(500)
                elif Connected():
                    log("No more tools left in pack! Trying to craft...")

                    craft_item(GUMP_TINKER_TOOLS_CATEGORY_TOOLS, GUMP_TINKER_TOOLS_TINKER_TOOLS_BUTTON, TINKER_TOOLS, TINKER_TOOLS, 1)
                    craft_item(GUMP_TINKER_TOOLS_CATEGORY_TOOLS, GUMP_TINKER_TOOLS_SHOWEL_BUTTON, TINKER_TOOLS, SHOVEL, 2)
                    if not FindType(SHOVEL, Backpack()):
                        log(f"Didn\'t manage to craft a tool...")
                        exit()

            UseObject(ObjAtLayer(LhandLayer()))

            WaitForTarget(2000)
            if TargetPresent():
                WaitTargetXYZ(x, y, z)
                WaitJournalLine(_start, "|".join(
                    BAD_TILE_MESSAGES + DEPLETED_TILE_MESSAGES + NEXT_TRY_MESSAGES), 15000)
                Wait(1000)


            if InJournalBetweenTimes("|".join(BAD_TILE_MESSAGES), _start, dt.now()) > 0:
                Bad_points.append([x, y, tile])
                Wait(500)
                log("Bad tile")
                break

            if InJournalBetweenTimes("|".join(DEPLETED_TILE_MESSAGES), _start, dt.now()) > 0:
                for _x in range(x-2,x+2):
                    for _y in range(y-2,y+2):
                        # log(f"setting tile mined {_x}, {_y}")
                        # Wait(50)
                        set_tile_mined({'x' : _x, 'y' : _y})
                Wait(500)
                log("Depleted tile")
                break
    else:
        Bad_points.append([x, y, tile])
        print(f"Can't reach X: {x} Y: {y}")


def distance_from_player(target_x: int, target_y: int) -> int:

    self_x = GetX(Self())
    self_y = GetY(Self())
    _dt_started=dt.now()
    # res = Dist(self_x,self_y,target_x,target_y)
    res = math.hypot(target_x - self_x, target_y - self_y)
    log(f"distance_calc took {dt.now()-_dt_started}")
    return res


def move_x_y(x: int, y: int) -> bool:
    log(f"Heading to point {x}, {y}")
    _try = 0
    while not newMoveXY(x, y, True, 1, True):
        if newMoveXY(x, y, True, 1, True):
            return True
        else:
            log(f"Failed to reach point {x}, {y}")
            _try += 1
            if _try > 10:
                return False

    log(f"Reached point {x}, {y}")
    return True


def goto_x_y(x: int, y: int, accuracy=1) -> bool:
    log(f"Moving out towards {x}, {y}")
    _try = 0
    while not newMoveXY(x, y, True, accuracy, True):
        if newMoveXY(x, y, True, accuracy, True):
            return True
        else:
            log(f"Failed to reach point {x}, {y}")
            _try += 1
            Wait(100)
            if _try > 10:
                return False

    log(f"Reached point {x}, {y}")
    return True

def unload_to_bank():
    """
    walks to bank, enters, and unloads PLANKS
    """
    log("Moving out to the bank...")

    goto_x_y(*BANK_ENTRY, 1)
    _point = (GetX(Self()), GetY(Self()))
    # while not wait_for_result((GetX(Self()), GetY(Self())) != _point):
    #     UseObject(BANK_ENTRY_DOOR)

    while ( (GetX(Self()), GetY(Self())) == _point):
        UseObject(BANK_ENTRY_DOOR)
        Wait(500)

    # TODO: no need to walk, just start using the fng bankbox
    # NewMoveXY(*BANK_INSIDE, True, 1, True)
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
        # UseFromGround(BANK_BOX_TYPE, 0xFFFF)
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
    while ( (GetX(Self()), GetY(Self())) == _point):
        UseObject(BANK_EXIT_DOOR)
        Wait(500)

def is_point_in_region(x, y):
    """
    returns True if cordinates are in rectangular region
    REGION_BORDERS defined in adv_imports
    """
    if x > REGION_BORDERS['x_max'] or x < REGION_BORDERS['x_min'] or y > REGION_BORDERS['y_max'] or y < REGION_BORDERS['y_min']:
        # log(f"Point is not in region {x},{y}")
        # Wait(100)
        return False
    return True

def find_vein():
    log('Searching for avaliable veins...')
    Wait(100)

    _self_x, _self_y = GetX(Self()), GetY(Self())
    found_tiles = find_tiles(5, _self_x, _self_y)
    for index in range(len(found_tiles)):
        tile, x, y, z = found_tiles[index]
        # if is_tile_mined({'x' : x, 'y' : y}):
        #     log(f"tile is mined, {x,y}")
        #     Wait(100)
        # if not is_point_in_region(x, y):
        #     log(f"point is not in region {x,y}")
        #     Wait(100)

        if not is_tile_mined({'x' : x, 'y' : y}) and is_point_in_region(x, y) and not [x,y,tile] in Bad_points:
            log(f'vein at: {x}, {y}')
            return tile, x, y, z

    log('no ready veins at the point')
    return -1, _self_x, _self_y, z

if __name__ == "__main__":
    for location in BAD_LOCATIONS:
        SetBadLocation(*location)
    log("Bad location loaded")
    coordsFile = 'sos_coords_mining.dump'
    Mined_tiles = load_pickle('mined_'+coordsFile)
    log(f'Loaded {len(Mined_tiles)} mined tiles')

    bad_points_file = 'sos_bad_points.dump'
    Bad_points = load_pickle(bad_points_file)

    SetMoveOpenDoor(True)
    SetMoveThroughNPC(True)

    while not Dead():
        for point in POINTS:
            point_x, point_y = point
            log(f"Point: {point_x}, {point_y}")
            move_x_y(point_x, point_y)
            log("Looking for tiles...")
            # tiles = find_tiles(GetX(Self()), GetY(Self()), TILE_SEARCH_RANGE)
            # log("Sorting tile...")
            # self_x = GetX(Self())
            # self_y = GetY(Self())
            # sorted_tiles = sorted(
            #     tiles, key=lambda tile: Dist(tile[1], tile[2], self_x, self_y))
            # for tile_counter in range(0, len(sorted_tiles), 4):
            # for tile_counter in range(0, len(sorted_tiles)):
            while True:
                tile, x, y, z = find_vein()
                if tile == -1:
                    break
                mine((tile,x,y,z))
                save_pickle_to_file(Mined_tiles, 'mined_'+coordsFile)
                save_pickle_to_file(Bad_points, bad_points_file)
                Wait(100)

