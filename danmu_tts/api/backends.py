"""Backend management and status endpoints."""

from fastapi import APIRouter, HTTPException
from typing import List

from ..models.responses import BackendInfo, StatsResponse, GPUUsage, GPUDevice
from ..manager import tts_manager

router = APIRouter(tags=["backends"])


@router.get("/backends", response_model=List[BackendInfo])
async def get_backends():
    """Get status of all TTS backends."""
    try:
        backend_info_list = []
        
        for backend in tts_manager.backends.values():
            status = await backend.get_status()
            backend_info = BackendInfo(
                name=status.name,
                enabled=status.enabled,
                available=status.available,
                load=status.load,
                queue_size=status.queue_size
            )
            backend_info_list.append(backend_info)
        
        return backend_info_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get backend status: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get comprehensive server statistics."""
    try:
        # Get backend status
        backend_status = []
        for backend in tts_manager.backends.values():
            status = await backend.get_status()
            backend_info = BackendInfo(
                name=status.name,
                enabled=status.enabled,
                available=status.available,
                load=status.load,
                queue_size=status.queue_size
            )
            backend_status.append(backend_info)
        
        # Basic GPU info (simplified for MVP)
        gpu_usage = None
        try:
            # This is a placeholder - in a full implementation you'd use
            # libraries like nvidia-ml-py to get real GPU information
            gpu_usage = GPUUsage(
                available=False,
                devices=[]
            )
        except Exception:
            # GPU monitoring not available
            pass
        
        return StatsResponse(
            uptime=tts_manager.uptime,
            total_requests=tts_manager.total_requests,
            cache_hit_rate=0.0,  # No caching implemented in MVP
            active_connections=0,  # Not tracked in MVP
            backend_status=backend_status,
            gpu_usage=gpu_usage
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get server statistics: {str(e)}")