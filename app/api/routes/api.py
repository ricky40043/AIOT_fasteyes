from fastapi import APIRouter, Depends, HTTPException

from app.api.routes import user, authentication, fasteyes_device, fasteyes_uuid, staff, fasteyes_observation, department

router = APIRouter()
#
router.include_router(authentication.router, tags=["authentication"])
router.include_router(user.router, tags=["user"])
router.include_router(fasteyes_device.router, tags=["Device"])
router.include_router(staff.router, tags=["staff"])
router.include_router(fasteyes_uuid.router, tags=["DeviceUuid"])
router.include_router(department.router, tags=["Department"])
router.include_router(fasteyes_observation.router, tags=["Observation"])
