import sqlite3
import time
import uuid
from utils import get_timestamp
from api.schemas.chat import HistoryMessage
from llm_client import LLMClient

SYSTEM_PROMPT = "你是发制品 MES 助手，简要回答。"
MAX_TURNS = 8  # 一轮 = user + assistant 两条


class ChatService:
    def __init__(self):
        self.client = LLMClient("DEEPSEEK")

    def _build_messages(self, prompt: str, history: list[HistoryMessage]) -> list[dict]:
        recent = history[-MAX_TURNS * 2:]
        return (
                [{"role": "system", "content": SYSTEM_PROMPT}]
                + [{"role": m.role, "content": m.content} for m in recent]
                + [{"role": "user", "content": prompt}]
        )

    def process_chat(self, prompt: str, history) -> str:
        reply = self.client.chat(self._build_messages(prompt, history))
        if reply is None:
            raise Exception("生成失败")
        return reply

    def process_chat_stream(self, prompt: str, history):
        yield from self.client.stream_chat(self._build_messages(prompt, history))

    def get_session_by_id(self, conn: sqlite3.Connection, session_id: str) -> bool:
        cursor = conn.execute("""
                              SELECT *
                              FROM sessions
                              WHERE id = ?
                              """, (session_id,))
        return cursor.fetchone() is not None

    def create_session(self, conn: sqlite3.Connection) -> str:
        print("开始创建会话")
        session_id = str(uuid.uuid4())
        created_at = str(get_timestamp())
        result = conn.execute(
            '''INSERT INTO sessions (id, created_at)
               VALUES (?, ?)''',
            (session_id, created_at)
        )
        conn.commit()
        print("会话创建完成", session_id, created_at, result)
        return session_id

    def add_message(self, conn: sqlite3.Connection, session_id: str, msg: HistoryMessage):
        try:
            conn.execute('''INSERT INTO messages
                                (session_id, role, content, created_at)
                            VALUES (?, ?, ?, ?)''', (session_id, msg.role, msg.content, msg.created_at))
            conn.commit()
            print("信息新增成功")
        except Exception as exc:
            print(exc)
            raise

    def get_messages_by_id(self, conn: sqlite3.Connection, session_id: str, limit: int = 10, offset: int = 0) -> list[
        HistoryMessage]:
        rows = conn.execute('''SELECT *
                               FROM messages
                               WHERE session_id = ?
                               ORDER BY id DESC
                               LIMIT ? OFFSET ?''', (session_id, limit, offset))

        messages = [HistoryMessage(**dict(row)) for row in rows]
        messages.reverse()
        return messages
