from time import time
from py_stealth.methods import *
import pickle
from my_logger import logger
from datetime import timedelta, datetime as dt
import re


CRAFTING_GUMP = 0x38920ABD
MAKE_LAST_BUTTON = 21

DRINKABLES = [
    0x65BA, #Name=Decanter Of Water # Of Milk
    0x4CEF, #Flagon
]

FOOD = [
        0x1608, #  Name= Chicken Leg
        0x09F2, # Name=3 Cut Of Ribs
        0x09B7, # Name=3 Cooked Bird
        0x103B, # Bread
    ]


def goto_x_y(x: int, y: int, accuracy=1) -> bool:
    logger.debug(f"Moving out towards {x}, {y}")
    _try = 0
    while not newMoveXY(x, y, True, accuracy, True):
        if newMoveXY(x, y, True, accuracy, True):
            return True
        else:
            logger.debug(f"Failed to reach point {x}, {y}")
            _try += 1
            Wait(100)
            if _try > 10:
                return False

    logger.debug(f"Reached point {x}, {y}")
    return True

def get_craft_status_message(gump_info):
    # You failed to create the item, and some of your materials are lost.
    try:
        msg = GetClilocByID(gump_info['XmfHTMLGumpColor'][9]['ClilocID'])
    except:
        msg = 'exception'
    if not (msg == 'LAST TEN'):
        return msg
    return ''

def eat(bag=Backpack()):
    '''
        eat food once from backpack or specified bag
        FOOD array is defined in adv_imports
    '''
    logger.debug('Need to eat!')
    _started_meal = dt.now()
    while Connected():
        if FindTypesArrayEx(FOOD,[0xFFFF],[bag],False):
            UseObject(GetFoundList()[0])
            Wait(1000)
        else:
            break
        if InJournalBetweenTimes('You manage to eat the food, but you are stuffed!|You are simply too full to eat any more!', _started_meal, dt.now()) > 0:
            logger.debug('Fulfilled my hunger.')
            break

def count_waterskin_drinks(array_of_waterskins):
    total_drinks = 0
    for _item in array_of_waterskins:
        _props = GetCliloc(_item).split("|")
        try:
            _drinks = int(re.split('Drink', _props[2])[0].upper().strip())
            total_drinks += _drinks
        except:
            print('failed converting drinks to int')
    return total_drinks

def wait_for_result(a,wait_step=100, timeout=5000):
    _t=0
    while (not a) and (_t<timeout):
        _t += wait_step
        Wait(wait_step)
    if a:
        return True
    return False

def drink(bag=Backpack()) -> int:
    """
    drink from various bottles in backpack or specified bag
    returns amount of drinks avaliable
    """
    drinks_left = 0
    logger.debug('Need to drink!')
    _started_meal = dt.now()
    while Connected():
        if FindTypesArrayEx(DRINKABLES,[0xFFFF],[bag], False):
            _found = True
            UseObject(GetFoundList()[0])
            Wait(1000)
            if InJournalBetweenTimes('fill', _started_meal, dt.now()) > 0:
                break
        else:
            break

        if InJournalBetweenTimes('You drink the water and are no longer thirsty|You are simply too quenched to drink any more', _started_meal, dt.now()) > 0:
            logger.debug(f'Fulfilled my thirst.')
            break

        if _found:
            drinks_left = count_waterskin_drinks(GetFoundList())

        return drinks_left

def handle_hunger(previous_check):
    """
        eat and drink if certain messages found since the prev check
    """
    drinks_left = -1
    meal_left = -1
    if InJournalBetweenTimes('hungry', previous_check, dt.now()) > 0:
        meal_left = eat()
    if InJournalBetweenTimes('thirsty', previous_check, dt.now()) > 0:
        drinks_left = drink()
    return {'timestamp' : dt.now()+timedelta(seconds=1),
            'drinks_left' : drinks_left,
            'meal_left' : meal_left}

def cancel_targets() -> None:
    CancelWaitTarget()
    if TargetPresent():
        CancelTarget()
    Wait(10)


def find_string_in_cliloc(item: id, string: str) -> str:
    """
        parses item cliloc,
        returning found string
    """
    _props = GetCliloc(item).split("|")
    result = None
    for _prop in _props:
        if string in _prop:
            result = _prop
    return result

def check_and_equip_tool(tool) -> None:
    """
    Checks whether gump_serial has button
    """
    if GetType(ObjAtLayer(LhandLayer())) in tool:
        # logger.debug("Tool is in Lhand")
        return LhandLayer()
    elif GetType(ObjAtLayer(RhandLayer())) in tool:
        # logger.debug("Tool is in Rhand")
        return RhandLayer()
    else:
        if FindTypesArrayEx(tool, [0xFFFF], [Backpack()], False):
            logger.debug("Tool found, what is the layer?")
            _props = GetCliloc(FindItem()).split("|")
            if _equipment := find_string_in_cliloc(FindItem(), 'Equipment'):
                _equipment = _equipment.split('Equipment: ')[1]
            else:
                logger.error(f"Error parsing cliloc for layer info")
                exit()

            if 'Right' in _equipment:
                _layer = RhandLayer()
            else:
                _layer = LhandLayer()
            logger.debug(f"Tool found, the layer is {_layer}")

            Equip(_layer, FindItem())
            Wait(500)
        elif Connected():
            logger.error("No more tools left in pack!")
            exit()
    return _layer

def find_gump(gump_serial: int) -> int:
    """
    return gump index by gump_serial
    returns -1 if gump has not been found
    """
    log_str = ""
    for gump in range(0, GetGumpsCount()+1):
        # log_str += (f"gump#{gump}, id = {hex(GetGumpID(gump))} != {hex(gump_serial)}\n")
        if GetGumpID(gump) == gump_serial:
            return gump
    # logger.debug(log_str)
    return -1

def gump_has_button(button, gump_serial=CRAFTING_GUMP) -> bool:
    """
    Checks whether gump_serial has button
    """
    _gump_id = find_gump(gump_serial)
    # print(f"debug _gump_id {_gump_id}")
    if _gump_id >= 0:
        # print("DEBUG GUMP FOUND")
        _buttons_info = GetGumpInfo(_gump_id)['GumpButtons']
        for _i, _button in enumerate(_buttons_info):
            if button == _button['ReturnValue']:
                return True
    logger.debug(f"button {button} not found!")
    return False

def wait_for_gump(button: int = -1, gump_serial = CRAFTING_GUMP, delay:int = 750) -> bool:
    """
    finds gump and checks whether it has button if provided
    returns False if gump found but button has not been found
    """
    attempt = 0
    while find_gump(gump_serial) < 0:
        attempt += 1
        Wait(500)
        if attempt > 15:
            logger.debug("wait_for_gump timeout")
            return False
    if button > -1 and gump_has_button(button, gump_serial):
        WaitGump(button)
        # logger.debug(f"button {button} pressed")
        Wait(delay)
        return True
    elif button < 0:
        return True
    return False

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