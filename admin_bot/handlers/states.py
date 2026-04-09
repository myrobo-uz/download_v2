from aiogram.fsm.state import StatesGroup, State

class UploadStates(StatesGroup):
    waiting_title   = State()
    waiting_code    = State()
    waiting_caption = State()
    waiting_file    = State()   # bir nechta media yuborish mumkin

class EditStates(StatesGroup):
    waiting_code        = State()
    choosing_field      = State()
    waiting_new_code    = State()
    waiting_new_title   = State()
    waiting_new_caption = State()
    waiting_new_file    = State()

class CooldownState(StatesGroup):
    waiting_seconds = State()

class BroadcastState(StatesGroup):
    waiting_target  = State()
    waiting_content = State()

class PanelManageState(StatesGroup):
    waiting_add_admin_id = State()
    waiting_del_admin_id = State()
    waiting_add_super_id = State()
    waiting_del_super_id = State()

class ChannelPanelState(StatesGroup):
    waiting_add    = State()
    waiting_remove = State()
