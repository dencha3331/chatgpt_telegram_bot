from aiogram.filters.state import State, StatesGroup


# StatesGroup-derived class for a group of states
class FSMRegistrationFillForm(StatesGroup):
    # registration state
    fill_name = State()  # Name
    fill_surname = State()  # Surname
    fill_age = State()  # Age
    fill_gender = State()  # Gender
    fill_wish_news = State()  # Whether to receive news
    fill_update_reg_data = State()  # Registration data update


class WeatherState(StatesGroup):
    get_weather = State()


class VoiceState(StatesGroup):
    correct_text = State()


class PayWMState(StatesGroup):
    fill_method = State()
    fill_price = State()
    fill_end = State()


class CommandState(StatesGroup):
    change_model = State()
    choice_dial = State()
    delete_all_dialogs = State()


class TextHandChangeOrLeaveModel(StatesGroup):
    change_model = State()

