import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State


import markups as nav
import api as api
from db import Database
import keys

storage = MemoryStorage()
bot = Bot(token=keys.TOKEN)
dp = Dispatcher(bot, storage=storage)

db = Database('database.db')

#состояния пустышки
class ForAdminPacifier1(StatesGroup):
    waiting_from = State()
    waiting_phone = State()
    waiting_msg = State()

#состояния пустышки
class ForAdminPacifier2(StatesGroup):
    waiting_from = State()
    waiting_phone = State()
    waiting_msg = State()

#состояния пустышки
class ForAdminPacifier3(StatesGroup):
    waiting_from = State()
    waiting_phone = State()
    waiting_msg = State()

#состояния специальной функции
class ForAdminSpecialStates(StatesGroup):
    waiting_from = State()
    waiting_phone = State()
    waiting_msg = State()

class ForAdminStates(StatesGroup):
    waiting_msg = State()

class ForAdminPurchaseStates(StatesGroup):
    waiting_id = State()

class ForAdminUserBalance(StatesGroup):
    waiting_id = State()

class ForAdminPrice(StatesGroup):
    waiting_name = State()
    waiting_spec = State()
    waiting_price = State()

class ForAdminBalanceStates(StatesGroup):
    waiting_id = State()
    waiting_balance = State()

class ImeiStates(StatesGroup):
    waiting_imei_fOn1 = State()
    waiting_imei_fOn2 = State()
    waiting_imei_сLo1 = State()
    waiting_imei_сLo2 = State()
    waiting_imei_bInf = State()
    waiting_imei_sBy = State()
    waiting_serial_findMac = State()
    waiting_serial_clo_Mac = State()
    waiting_imei_all_in = State()
    waiting_sim_lock = State()
    waiting_mdm_status = State()
    waiting_model_storage = State()
    waiting_allInCar = State()
    waiting_convertImei = State()
    waiting_partNum = State()
    waiting_fullGsx = State()
    waiting_idinFogsx = State()

class PhoneStates(StatesGroup):
    waiting_phone_ping = State()
    waiting_hlr_ping = State()

class DhruStates(StatesGroup):
    waiting_imei = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    username = 'Добро пожаловать, ' + str(message.from_user.username) + '!'
    full_message = f'📱{username}\n\n Авторизируйтесь для дальнейшей работы!'
    await bot.send_message(message.from_user.id, full_message, reply_markup=nav.mainMenu)

@dp.message_handler(text_contains= '⚙ Услуги', state='*')
async def services(message: types.Message, state: FSMContext):
    if message.text == '⚙ Услуги':
            await bot.send_message(message.from_user.id, '⚙ Услуги\n\nВыберите интересующую Вас услугу из списка ниже.', reply_markup=nav.choice)
            await state.finish()


@dp.message_handler(text_contains= '🙋‍♂️Войти!', state='*')
async def start(message: types.Message, state: FSMContext):
    if message.text == '🙋‍♂️Войти!':
        await state.finish()
        if not db.user_exists(message.from_user.id) and not db.user_admin(message.from_user.id):
            username = 'Уважаемый, ' + str(message.from_user.username)
            full_message = f'📱{username}\n\n ⚠ Для начала создайте аккаунт для дальнейшей работы!'
            await bot.send_message(message.from_user.id,
                                   full_message,
                                   reply_markup=nav.mainMenu)

        elif db.user_exists(message.from_user.id) and db.user_admin(message.from_user.id):
            username = 'Добро пожаловать, ' + str(message.from_user.username) + '!'
            full_message = f'📱{username}\n\n Рады приветствовать Вас, админ! Выберите необходимый вам пункт меню и начинайте работу!'
            await bot.send_message(message.from_user.id,
                                   full_message,
                                   reply_markup=nav.adminMenu)
        else:
            username = 'Добро пожаловать, ' + str(message.from_user.username) + '!'
            full_message = f'📱{username}\n\n Рады видеть Вас снова! Выберите необходимый вам пункт меню и начинайте работу!'
            await bot.send_message(message.from_user.id,
                                   full_message,
                                   reply_markup=nav.profileMenu)

@dp.message_handler(state=ImeiStates.waiting_mdm_status)
async def clean_lost_mac_message(message: types.Message, state: FSMContext):
    await state.update_data(imei=message.text)
    service_id = 10
    service_name = db.get_service_name(service_id)
    check = await message.answer(f'📱{service_name}\n\n💵Отлично, ваша проверка выполняется!',reply_markup=nav.cancelSolo)
    answer = api.mdm_status(message.text, message.from_user.id, message.date)
    if db.user_special(message.from_user.id):
        service_price = db.get_price_special(service_name)
    else:
        service_price = db.get_price(service_name)
    await message.reply(f'✅Ваша проверка выполнена!\n📱{service_name}\n\n{answer}\n\n💵Ваш баланс: {round(db.get_balance(message.from_user.id) + service_price, 2)} => {round(db.get_balance(message.from_user.id), 2)}')
    await check.delete()
    if 'неправильный' not in answer:
        db.user_pay(message.from_user.id, service_price)
        db.add_purchase(message.from_user.id, service_name, message.text,message.date)
    else:
        await message.answer(f'❌Ваша проверка не выполнена!\n\nВаши средства за проверку не будут списаны!\n\n💵Ваш баланс: {round(db.get_balance(message.from_user.id), 2)}',
        reply_markup=nav.cancelSolo)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


