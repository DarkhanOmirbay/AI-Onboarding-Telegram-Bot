from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.core.state import QAStates
from app.data.qdrant_helper import qdrant_helper
from app.core.config import settings

from openai import AsyncOpenAI


qa_router = Router()


@qa_router.message(Command("qa"))
async def qa(message: Message, state: FSMContext):

    await state.set_state(QAStates.waiting_for_question)
    await message.answer("write a question")


@qa_router.message(QAStates.waiting_for_question)
async def process_question(message: Message, state: FSMContext):
    user_question = message.text

    context = await qdrant_helper.retrieve_context(user_question=user_question)
    print(context)

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.responses.create(
        model="gpt-4o",
        input=f"{user_question}\n\n\n\n{context}",
    )

    await message.answer(response.output_text)
