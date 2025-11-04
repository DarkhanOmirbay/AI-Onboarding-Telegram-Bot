from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.quiz import create_quiz, get_quiz, update_day
from app.data.questions import (
    questions_quiz_one,
    questions_quiz_three,
    questions_quiz_two,
)
from app.models.models import Quiz

quiz_router = Router()
user_sessions = {}


class AnswerCallback(CallbackData, prefix="ans"):  # ans:q_index:opt_index
    q_index: int
    opt_index: int
    quiz_day: int


def make_keyboard(questions: list, q_index: int, quiz_day: int) -> InlineKeyboardBuilder:
    q = questions[q_index]
    kb = InlineKeyboardBuilder()
    for i, opt in enumerate(q["options"]):
        kb.button(
            text=f"{chr(65+i)}",
            # text=f"{chr(65+i)}) {opt}"
            callback_data=AnswerCallback(q_index=q_index, opt_index=i, quiz_day=quiz_day).pack(),
        )
    kb.adjust(2)
    return kb.as_markup()


@quiz_router.message(Command("test"))
async def command_test_handler(message: Message, session: AsyncSession) -> None:
    user_id = message.from_user.id
    user_sessions[user_id] = {"score": 0, "current": 0}  # redis

    quiz: Quiz = await get_quiz(user_id=user_id, session=session)
    if quiz is None:
        quiz = Quiz(user_id=user_id)
        await create_quiz(quiz=quiz, session=session)

    day = quiz.day if quiz else 0

    match day:
        case 0:
            raise NotImplementedError("Quiz day 0 handler not implemented yet")
        case 1:
            q = questions_quiz_one[0]
            # text = f"<b>Вопрос 1/{len(questions_quiz_one)}</b>\n\n{q['text']}"
            text = f"Test for 1 day\n<b>Вопрос {0+ 1}/{len(questions_quiz_one)}</b>\n\n"
            text += f"{q['text']}\n\n"

            for i, opt in enumerate(q["options"]):
                text += f"{chr(65 + i)}) {opt}\n"
            await message.answer(
                text,
                reply_markup=make_keyboard(questions_quiz_one, 0, 1),
                parse_mode="HTML",
            )
        case 2:
            q = questions_quiz_two[0]
            # text = f"<b>Вопрос 1/{len(questions_quiz_two)}</b>\n\n{q['text']}"
            text = f"Test for 2 day\n<b>Вопрос {0+ 1}/{len(questions_quiz_two)}</b>\n\n"
            text += f"{q['text']}\n\n"

            for i, opt in enumerate(q["options"]):
                text += f"{chr(65 + i)}) {opt}\n"

            await message.answer(
                text,
                reply_markup=make_keyboard(questions_quiz_two, 0, 2),
                parse_mode="HTML",
            )
        case 3:
            q = questions_quiz_three[0]
            # text = f"<b>Вопрос 1/{len(questions_quiz_three)}</b>\n\n{q['text']}"
            text = f"Test for 3 day\n<b>Вопрос {0+ 1}/{len(questions_quiz_two)}</b>\n\n"
            text += f"{q['text']}\n\n"

            for i, opt in enumerate(q["options"]):
                text += f"{chr(65 + i)}) {opt}\n"
            await message.answer(
                text,
                reply_markup=make_keyboard(questions_quiz_three, 0, 3),
                parse_mode="HTML",
            )
        case 4:
            await message.answer("Вы успешно завершили все тесты!")


@quiz_router.callback_query(AnswerCallback.filter())
async def handle_answer(
    callback: CallbackQuery, callback_data: AnswerCallback, session: AsyncSession
) -> None:
    await callback.answer()  # for preventing double tap issues
    user_id = callback.from_user.id

    sessionDB = user_sessions.get(user_id)

    if not sessionDB:
        await callback.answer("Начни тест с /start", show_alert=True)
        return

    match callback_data.quiz_day:
        case 1:
            questions = questions_quiz_one
        case 2:
            questions = questions_quiz_two
        case 3:
            questions = questions_quiz_three

    q_idx = callback_data.q_index
    opt_idx = callback_data.opt_index
    correct_idx = questions[q_idx]["correct"]

    if opt_idx == correct_idx:
        sessionDB["score"] += 1
        await callback.answer("✅ Правильно!")
    else:
        await callback.answer("❌ Неправильно!")

    sessionDB["current"] += 1
    if sessionDB["current"] < len(questions):
        next_q = questions[sessionDB["current"]]
        new_text = f"<b>Вопрос {sessionDB['current'] + 1}/{len(questions)}</b>\n\n"
        new_text += f"{next_q['text']}\n\n"
        for i, opt in enumerate(next_q["options"]):
            new_text += f"{chr(65+i)}) {opt}\n"
        await callback.message.edit_text(
            new_text,
            reply_markup=make_keyboard(
                questions=questions,
                q_index=sessionDB["current"],
                quiz_day=callback_data.quiz_day,
            ),
        )
    else:
        total = len(questions)
        score = sessionDB["score"]

        # Минимальный порог для прохождения
        match callback_data.quiz_day:
            case 1:
                required_score = 13
            case 2:
                required_score = 8
            case 3:
                required_score = total // 2
            case _:
                required_score = total // 2  # на случай неизвестного дня

        passed = score >= required_score

        if passed:
            quiz: Quiz = await get_quiz(user_id=user_id, session=session)
            current_day = quiz.day

            if current_day == callback_data.quiz_day:
                await update_day(quiz=quiz, session=session)

            new_day = quiz.day

            if new_day > 3:
                result_text = (
                    f"\n\n🎉 <b>Поздравляем!</b>\n"
                    f"Вы успешно прошли все тесты программы! 🏆\n"
                    f"Ваш результат за последний день: <b>{score}/{total}</b>."
                )
            else:
                result_text = (
                    f"\n\n🚀 <b>Отлично!</b>\n"
                    f"Вы прошли тест {current_day}-го дня, набрав <b>{score}</b> из <b>{total}</b> баллов. 🎯\n"
                    f"Теперь можете перейти к тесту {new_day}-го дня, используя команду <b>/test</b>."
                )
        else:
            result_text = (
                f"\n\n🏁 <b>Тест завершён!</b>\n\n"
                f"Ваш результат: <b>{score}/{total}</b>\n"
                f"😞 К сожалению, вы не прошли тест {callback_data.quiz_day}-го дня.\n"
                f"Чтобы пройти, необходимо набрать минимум <b>{required_score}</b> из <b>{total}</b> баллов.\n\n"
                f"📘 Повторите материалы и попробуйте снова с помощью команды <b>/test</b>."
            )
        await callback.message.edit_text(result_text)
        user_sessions.pop(user_id, None)
