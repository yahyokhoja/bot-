from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()

class BookingForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_description = State()

@router.message(F.text == "📝 Оставить заявку")
async def booking_start(message: Message, state: FSMContext):
    print("🔥 Кнопка 'Оставить заявку' сработала")
    await message.answer("Пожалуйста, введите ваше имя:")
    await state.set_state(BookingForm.waiting_for_name)

@router.message(BookingForm.waiting_for_name)
async def booking_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите номер телефона:")
    await state.set_state(BookingForm.waiting_for_phone)

@router.message(BookingForm.waiting_for_phone)
async def booking_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Опишите, что именно вам нужно:")
    await state.set_state(BookingForm.waiting_for_description)

@router.message(BookingForm.waiting_for_description)
async def booking_description(message: Message, state: FSMContext):
    user_data = await state.get_data()
    description = message.text
    await state.clear()
    await message.answer(
        "✅ Заявка отправлена!\n\n"
        f"Имя: {user_data['name']}\n"
        f"Телефон: {user_data['phone']}\n"
        f"Описание: {description}"
    )
