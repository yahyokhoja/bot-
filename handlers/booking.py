from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp

router = Router()

class BookingForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_description = State()
    waiting_for_address = State()
    waiting_for_quantity = State()
    waiting_for_confirmation = State()
    waiting_for_payment_method = State()

async def send_order_to_app(user_id, item_name, quantity):
    async with aiohttp.ClientSession() as session:
        payload = {
            "user_id": user_id,
            "item_name": item_name,
            "quantity": quantity
        }
        try:
            async with session.post("http://localhost:5000/api/orders", json=payload) as resp:
                data = await resp.json()
                return {
                    "success": resp.status == 200,
                    "data": data,
                    "status": resp.status
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# --- START ---
@router.message(F.text == "📝 Оставить заявку")
async def booking_start(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите ваше имя:")
    await state.set_state(BookingForm.waiting_for_name)

# --- NAME ---
@router.message(BookingForm.waiting_for_name)
async def booking_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите номер телефона (пример: +992123456789):")
    await state.set_state(BookingForm.waiting_for_phone)

# --- PHONE ---
@router.message(BookingForm.waiting_for_phone)
async def booking_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not phone.startswith("+") or not phone[1:].isdigit() or len(phone) < 10:
        await message.answer("❌ Неверный формат. Введите номер в формате +992123456789")
        return
    await state.update_data(phone=phone)
    await message.answer("Опишите, что именно вам нужно:")
    await state.set_state(BookingForm.waiting_for_description)

# --- DESCRIPTION ---
@router.message(BookingForm.waiting_for_description)
async def booking_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите адрес доставки:")
    await state.set_state(BookingForm.waiting_for_address)

# --- ADDRESS ---
@router.message(BookingForm.waiting_for_address)
async def booking_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Введите количество товара:")
    await state.set_state(BookingForm.waiting_for_quantity)

# --- QUANTITY ---
@router.message(BookingForm.waiting_for_quantity)
async def booking_quantity(message: Message, state: FSMContext):
    quantity = message.text.strip()
    if not quantity.isdigit() or int(quantity) <= 0:
        await message.answer("❌ Введите корректное количество (целое число больше 0).")
        return
    await state.update_data(quantity=quantity)

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Да", callback_data="confirm_yes")
    kb.button(text="❌ Нет", callback_data="confirm_no")
    await message.answer("Подтвердите заказ:", reply_markup=kb.as_markup())
    await state.set_state(BookingForm.waiting_for_confirmation)

# --- CONFIRMATION ---
@router.callback_query(F.data.in_({"confirm_yes", "confirm_no"}))
async def booking_confirmation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.data == "confirm_no":
        await state.clear()
        await callback.message.answer("❌ Заказ отменён.")
        return

    kb = InlineKeyboardBuilder()
    kb.button(text="💵 Наличные", callback_data="pay_cash")
    kb.button(text="💳 Карта", callback_data="pay_card")
    await callback.message.answer("Выберите способ оплаты:", reply_markup=kb.as_markup())
    await state.set_state(BookingForm.waiting_for_payment_method)

# --- PAYMENT ---
@router.callback_query(F.data.in_({"pay_cash", "pay_card"}))
async def booking_payment(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    payment = "Наличные" if callback.data == "pay_cash" else "Карта"

    user_data = await state.get_data()

    # Отправляем заказ на внешний API
    response = await send_order_to_app(
        user_id=callback.from_user.id,
        item_name=user_data.get("description", "не указано"),
        quantity=int(user_data.get("quantity", 1))
    )

    if response.get("success", False):
        await callback.message.answer(
            "✅ Заявка отправлена!\n\n"
            f"👤 Имя: {user_data['name']}\n"
            f"📞 Телефон: {user_data['phone']}\n"
            f"📝 Описание: {user_data['description']}\n"
            f"📍 Адрес: {user_data['address']}\n"
            f"📦 Количество: {user_data['quantity']}\n"
            f"💰 Оплата: {payment}"
        )
    else:
        debug_info = ""
        if "error" in response:
            debug_info = f"\n\n🪛 Ошибка: {response['error']}"
        elif "status" in response:
            debug_info = f"\n\n🪛 Код ответа: {response['status']}, данные: {response.get('data')}"
        await callback.message.answer("❌ Ошибка при отправке заявки. Попробуйте позже." + debug_info)

    await state.clear()
