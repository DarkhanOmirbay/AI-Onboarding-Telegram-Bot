from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.state import QAStates
from app.crud.chat import add_msg_and_rspnse
from app.data.qdrant_helper import qdrant_helper
from app.keyboards.keyboards import stop
from app.models.models import Message as MessageModel, Response

qa_router = Router()
db = {}


@qa_router.message(Command("qa"))
async def qa(message: Message, state: FSMContext):
    user_id = message.from_user.id
    db[user_id] = {"questions": [], "answers": []}
    await state.set_state(QAStates.waiting_for_question)
    await message.answer("write a question", reply_markup=stop)


@qa_router.message(QAStates.waiting_for_question)
async def process_question(message: Message, state: FSMContext, session: AsyncSession):
    user_question = message.text
    user_id = message.from_user.id
    user_questions = db[user_id]["questions"]
    user_answers = db[user_id]["answers"]
    user_questions.append(user_question)
    context, point_ids = await qdrant_helper.retrieve_context(user_question=user_question)
    print(context)

    # Собираем историю диалога в виде текста
    conversation_history = "\n".join(
        [
            f"Q{i+1}: {q}\nA{i+1}: {a}"
            for i, (q, a) in enumerate(zip(user_questions, user_answers, strict=False))
        ]
    )

    # Формируем финальный prompt
    input_text = (
        f"{user_question}\n\n\n\n"
        f"{context}\n\n\n\n"
        f"User's conversation history:\n{conversation_history}\n\nA:"
    )

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.responses.create(
        model="gpt-4o",
        instructions=(
            "Вы — внутренний корпоративный ассистент компании TrustMe. "
            "Ваша роль — помогать сотрудникам и стажёрам, отвечая на все вопросы, "
            "связанные с внутренними материалами компании TrustMe. "
            "Вы имеете доступ к корпоративной информации из предоставленного контекста, "
            "включая имена сотрудников, контакты, Telegram-теги, отделы, расписание, Wi-Fi и пароли. "
            "Если пользователь спрашивает, например, 'дай номер по тэгу @darkhvnn' или 'какой пароль Wi-Fi для отдела маркетинга', "
            "Вы спокойно и точно отвечаете, используя данные из контекста. "
            "Не добавляйте фраз вроде 'я не могу', 'мне жаль' или 'похоже, это внутренний документ'. "
            "Отвечайте чётко, по делу, уважительно и уверенно. "
            "Всегда обращайтесь к пользователю на 'Вы' и сохраняйте вежливый, деловой стиль."
        ),
        input=input_text,
        temperature=0,
        max_output_tokens=500,
    )
    answer = response.output_text
    user_answers.append(answer)
    msg: MessageModel = MessageModel(
        id=message.message_id,
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        text=user_question,
    )
    rspnse: Response = Response(message_id=message.message_id, answer=answer, retrieved=point_ids)
    await add_msg_and_rspnse(session=session, msg=msg, rspnse=rspnse)
    await message.answer(answer, reply_markup=stop)


@qa_router.callback_query(F.data == "stop_qa")
async def stop_qa_callback(callback: CallbackQuery, state: FSMContext):
    print(f"db : {', '.join(f'{k}={v}' for k, v in db.items())}")
    user_id = callback.from_user.id
    db.pop(user_id, None)
    await state.clear()
    print(f"db : {', '.join(f'{k}={v}' for k, v in db.items())}")
    await callback.message.answer(
        "Привет! Я бот для проведения тестов по знанию компании TrustMe.\nЧтобы начать тест, используй команду /test. Удачи!,\n/qa - вопросы и ответы,\n/me - информация о вас",
    )
    await callback.answer()
