"""
backend/app/routers/friends.py
Friend system endpoints.
  GET  /api/friends                          - List accepted friends
  GET  /api/friends/requests                 - Pending incoming requests
  POST /api/friends/request/{user_id}        - Send a friend request
  PUT  /api/friends/request/{req_id}/accept  - Accept a request
  PUT  /api/friends/request/{req_id}/decline - Decline a request
  DELETE /api/friends/{user_id}              - Remove a friend
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.friends import FriendRequest, FriendRequestStatus
from app.schemas.user import UserPublicOut

router = APIRouter(prefix="/friends", tags=["Friends"])


@router.get("")
def get_friends(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    accepted = db.query(FriendRequest).filter(
        and_(FriendRequest.status == FriendRequestStatus.accepted,
             or_(FriendRequest.sender_id == current_user.id, FriendRequest.receiver_id == current_user.id))
    ).all()
    friends = []
    for req in accepted:
        friend = req.receiver if str(req.sender_id) == str(current_user.id) else req.sender
        friends.append(UserPublicOut.model_validate(friend).model_dump())
    return {"friends": friends, "total": len(friends)}


@router.get("/requests")
def get_incoming_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reqs = db.query(FriendRequest).filter(
        and_(FriendRequest.receiver_id == current_user.id, FriendRequest.status == FriendRequestStatus.pending)
    ).all()
    result = []
    for r in reqs:
        result.append({"id": str(r.id), "sender": UserPublicOut.model_validate(r.sender).model_dump(),
                       "status": r.status.value, "created_at": r.created_at.isoformat()})
    return {"requests": result, "total": len(result)}


@router.post("/request/{user_id}", status_code=201)
def send_request(user_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot add yourself")
    target = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    existing = db.query(FriendRequest).filter(
        or_(and_(FriendRequest.sender_id == current_user.id, FriendRequest.receiver_id == user_id),
            and_(FriendRequest.sender_id == user_id, FriendRequest.receiver_id == current_user.id))
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Request already exists or already friends")
    req = FriendRequest(sender_id=current_user.id, receiver_id=user_id)
    db.add(req)
    db.commit()
    db.refresh(req)
    return {"message": "Friend request sent", "request_id": str(req.id)}


@router.put("/request/{req_id}/accept")
def accept_request(req_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    req = db.query(FriendRequest).filter(
        FriendRequest.id == req_id, FriendRequest.receiver_id == current_user.id,
        FriendRequest.status == FriendRequestStatus.pending
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    req.status = FriendRequestStatus.accepted
    db.commit()
    return {"message": "Accepted"}


@router.put("/request/{req_id}/decline")
def decline_request(req_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    req = db.query(FriendRequest).filter(
        FriendRequest.id == req_id, FriendRequest.receiver_id == current_user.id,
        FriendRequest.status == FriendRequestStatus.pending
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    req.status = FriendRequestStatus.declined
    db.commit()
    return {"message": "Declined"}


@router.delete("/{user_id}")
def remove_friend(user_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    req = db.query(FriendRequest).filter(
        FriendRequest.status == FriendRequestStatus.accepted,
        or_(and_(FriendRequest.sender_id == current_user.id, FriendRequest.receiver_id == user_id),
            and_(FriendRequest.sender_id == user_id, FriendRequest.receiver_id == current_user.id))
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Friendship not found")
    db.delete(req)
    db.commit()
    return {"message": "Removed"}
