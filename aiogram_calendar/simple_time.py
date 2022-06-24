import datetime
import calendar
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.types import CallbackQuery
from datetime import datetime, timedelta

time_callback = CallbackData('simple_time', 'action', 'hour', 'minute')
calendar_callback = CallbackData('simple_calendar', 'act', 'year', 'month', 'day')


class SimpleDateTime:
    async def start_calendar(
            self,
            year: int = datetime.now().year,
            month: int = datetime.now().month
    ) -> InlineKeyboardMarkup:
        """
        Creates an inline keyboard with the provided year and month
        :param int year: Year to use in the calendar, if None the current year is used.
        :param int month: Month to use in the calendar, if None the current month is used.
        :return: Returns InlineKeyboardMarkup object with the calendar.
        """
        inline_kb = InlineKeyboardMarkup(row_width=7)
        ignore_callback = calendar_callback.new("IGNORE", year, month, 0)  # for buttons with no answer
        # First row - Month and Year
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            "<<",
            callback_data=calendar_callback.new("PREV-YEAR", year, month, 1)
        ))
        inline_kb.insert(InlineKeyboardButton(
            f'{calendar.month_name[month]} {str(year)}',
            callback_data=ignore_callback
        ))
        inline_kb.insert(InlineKeyboardButton(
            ">>",
            callback_data=calendar_callback.new("NEXT-YEAR", year, month, 1)
        ))
        # Second row - Week Days
        inline_kb.row()
        for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
            inline_kb.insert(InlineKeyboardButton(day, callback_data=ignore_callback))

        # Calendar rows - Days of month
        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            inline_kb.row()
            for day in week:
                if day == 0:
                    inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
                    continue
                inline_kb.insert(InlineKeyboardButton(
                    str(day), callback_data=calendar_callback.new("DAY", year, month, day)
                ))

        # Last row - Buttons
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            "<", callback_data=calendar_callback.new("PREV-MONTH", year, month, day)
        ))
        inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
        inline_kb.insert(InlineKeyboardButton(
            ">", callback_data=calendar_callback.new("NEXT-MONTH", year, month, day)
        ))

        return inline_kb

    async def start_hour(self) -> InlineKeyboardMarkup:
        inline_kb = InlineKeyboardMarkup(row_width=6)
        ignore_callback = time_callback.new("IGNORE", 0, 0)
        inline_kb.row()
        time_matrix = \
            [
                ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00"],
                ["06:00", "07:00", "08:00", "09:00", "10:00", "11:00"],
                ["12:00", "13:00", "14:00", "15:00", "16:00", "17:00"],
                ["18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]
            ]
        for row in time_matrix:
            inline_kb.row()
            for time in row:
                inline_kb.insert(InlineKeyboardButton(
                    time, callback_data=time_callback.new("HOUR", time[:2], 0)  # sporno
                ))
        inline_kb.row()
        return inline_kb

    async def start_minute(self, hour: str = '00') -> InlineKeyboardMarkup:
        inline_kb = InlineKeyboardMarkup(row_width=4)
        minutes = \
            [
                [":00", ":05", ":10", ":15"],
                [":20", ":25", ":30", ":35"],
                [":40", ":45", ":50", ":55"]
            ]
        for row in minutes:
            inline_kb.row()
            for minute in row:
                time = hour + minute
                inline_kb.insert(InlineKeyboardButton(
                    time, callback_data=time_callback.new("MINUTE", time[:2], time[3:])
                ))
        return inline_kb

    async def process_selection_calendar(self, query: CallbackQuery, data: CallbackData) -> tuple:
        return_data = (False, None)
        temp_date = datetime(int(data['year']), int(data['month']), 1)
        # processing empty buttons, answering with no action
        if data['act'] == "IGNORE":
            await query.answer(cache_time=60)
        # user picked a day button, return date
        if data['act'] == "DAY":
            await query.message.delete_reply_markup()  # removing inline keyboard
            return_data = True, datetime(int(data['year']), int(data['month']), int(data['day']))
            # await query.message.edit_reply_markup(await self.start_hour())
        # user navigates to previous year, editing message with new calendar
        if data['act'] == "PREV-YEAR":
            prev_date = temp_date - timedelta(days=365)
            await query.message.edit_reply_markup(await self.start_calendar(int(prev_date.year), int(prev_date.month)))
        # user navigates to next year, editing message with new calendar
        if data['act'] == "NEXT-YEAR":
            next_date = temp_date + timedelta(days=365)
            await query.message.edit_reply_markup(await self.start_calendar(int(next_date.year), int(next_date.month)))
        # user navigates to previous month, editing message with new calendar
        if data['act'] == "PREV-MONTH":
            prev_date = temp_date - timedelta(days=1)
            await query.message.edit_reply_markup(await self.start_calendar(int(prev_date.year), int(prev_date.month)))
        # user navigates to next month, editing message with new calendar
        if data['act'] == "NEXT-MONTH":
            next_date = temp_date + timedelta(days=31)
            await query.message.edit_reply_markup(await self.start_calendar(int(next_date.year), int(next_date.month)))
        # at some point user clicks DAY button, returning date
        return return_data

    async def process_selection_time(self, query: CallbackQuery, data: CallbackData) -> tuple:
        return_data = (False, None)
        # actions for time selection
        if data['action'] == 'HOUR':
            hour = data['hour']
            await query.message.edit_reply_markup(await self.start_minute(hour=hour))
        if data['action'] == 'MINUTE':
            minutes = data['minute']
            hour = data['hour']
            await query.message.delete_reply_markup()
            return_data = True, ":".join([hour, minutes])

        return return_data


#
