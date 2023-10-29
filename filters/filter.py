from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery

from db import Crud, Users, Dialog


class ChoiceDialogFilter(BaseFilter):

    async def __call__(self, callback: CallbackQuery) -> bool | dict:
        userid: int = callback.from_user.id
        data: str = callback.data
        if data == "no_choice":
            choice_message = data
            return {"choice_message": choice_message}
        choice_message: str | bool = await Crud.change_current_dialog(userid, int(data))
        return {"choice_message": choice_message}
