import sqlite3
from collections.abc import Iterator
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.sse import EventSourceResponse, ServerSentEvent

from api.schemas.chat import ChatRequest, ChatResponse, HistoryMessage
from api.service.chat import ChatService
from db import get_db
from utils import get_timestamp

router = APIRouter(prefix="/chat", tags=["chat"])
chat_service = ChatService()
logger = logging.getLogger(__name__)

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, conn: sqlite3.Connection = Depends(get_db)):
    history = []
    if request.session_id is not None and request.session_id != "":
        session_exists = chat_service.get_session_by_id(conn, request.session_id)
        if not session_exists:
            raise HTTPException(status_code=404, detail="会话不存在")
        history = chat_service.get_messages_by_id(conn, request.session_id, 16)


    session_id = request.session_id or chat_service.create_session(conn)



    user_msg = HistoryMessage(session_id=session_id, role="user", content=request.prompt,
                              created_at=str(get_timestamp()))
    # 新增用户消息
    chat_service.add_message(conn, session_id, user_msg)

    response_data = chat_service.process_chat(request.prompt, history)

    system_msg = HistoryMessage(session_id=session_id, role="assistant", content=response_data,
                                created_at=str(get_timestamp()))
    chat_service.add_message(conn, session_id, system_msg)

    return ChatResponse(reply=response_data, status="ok", session_id=session_id)


@router.get("/history", response_model=list[HistoryMessage])
def get_history(session_id: str, limit: int = 10, offset: int = 0, conn: sqlite3.Connection = Depends(get_db)) -> list[
    HistoryMessage]:
    session_exists = chat_service.get_session_by_id(conn, session_id)

    if not session_exists:
        raise HTTPException(status_code=404, detail="会话不存在")

    history = chat_service.get_messages_by_id(conn, session_id, limit, offset)
    print("历史记录", history)
    return history


@router.post("/stream", response_class=EventSourceResponse)
def chat_request_stream(request: ChatRequest, conn: sqlite3.Connection = Depends(get_db)) -> Iterator[ServerSentEvent]:
    full_response = ""

    session_id = request.session_id or chat_service.create_session(conn)

    session_exists = chat_service.get_session_by_id(conn, session_id)
    if not session_exists:
        yield ServerSentEvent(data={"error": "无效的会话id"})
        return


    user_msg = HistoryMessage(session_id=session_id, role="user", content=request.prompt,
                              created_at=str(get_timestamp()))

    history = []
    if request.session_id is not None:
        history = chat_service.get_messages_by_id(conn, session_id, 16)
    print("历史记录", history)

    # 新增用户消息
    chat_service.add_message(conn, session_id, user_msg)
    print("新增用户消息", user_msg)

    try:
        for chunk in chat_service.process_chat_stream(request.prompt, history):
            full_response += chunk
            yield ServerSentEvent(data={"result": chunk, "session_id": session_id})

        system_msg = HistoryMessage(session_id=session_id, role="assistant", content=full_response,
                                    created_at=str(get_timestamp()))
        chat_service.add_message(conn, session_id, system_msg)
        print("新增系统消息")
        yield ServerSentEvent(raw_data="[DONE]")
    except Exception as exc:
        print("发生异常", )
        logger.exception("回复生成失败")
        yield ServerSentEvent(data={"error": "回复生成失败，请重试"})
