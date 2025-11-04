from aiogram import Router

from app.routers.onboarding import onboarding_router
from app.routers.qa import qa_router
from app.routers.quiz import quiz_router

router = Router()

router.include_router(onboarding_router)
router.include_router(qa_router)
router.include_router(quiz_router)
