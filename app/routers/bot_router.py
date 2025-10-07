from aiogram import Router

from .onboarding import onboarding_router
from .qa import qa_router

router = Router()

router.include_router(onboarding_router)
router.include_router(qa_router)
