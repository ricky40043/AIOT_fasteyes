from fastapi import APIRouter, Depends, HTTPException

from app.api.routes import user, authentication, fasteyes_device, fasteyes_uuid, staff, fasteyes_observation, department, \
    bulletin, device, device_model, group, observation, area, face_recognition

router = APIRouter()
#
router.include_router(authentication.router, tags=["authentication"])
router.include_router(user.router, tags=["user"])
router.include_router(fasteyes_device.router, tags=["fasteyes_device"])
router.include_router(staff.router, tags=["staff"])
router.include_router(fasteyes_uuid.router, tags=["DeviceUuid"])
router.include_router(department.router, tags=["Department"])
router.include_router(fasteyes_observation.router, tags=["fasteyes_observation"])
router.include_router(observation.router, tags=["Observation"])
router.include_router(group.router, tags=["Group"])
router.include_router(device.router, tags=["Device"])
router.include_router(device_model.router, tags=["Device_model"])
router.include_router(bulletin.router, tags=["bulletin"])
router.include_router(area.router, tags=["area"])
router.include_router(face_recognition.router, tags=["face_recognition"])
