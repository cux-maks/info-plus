from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/kakao", tags=["kakao"])

class KakaoRequest(BaseModel):
    intent: Dict[str, Any]
    userRequest: Dict[str, Any]
    bot: Dict[str, Any]
    action: Dict[str, Any]

class SimpleText(BaseModel):
    text: str

class QuickReply(BaseModel):
    label: str
    action: str
    messageText: str

class KakaoResponse(BaseModel):
    version: str = "2.0"
    template: Dict[str, Any]

@router.post("/message")
async def handle_message(request: KakaoRequest) -> KakaoResponse:
    """
    카카오톡 챗봇 기본 메시지 처리 엔드포인트
    """
    try:
        # 사용자 발화 추출
        user_utterance = request.userRequest.get("utterance", "").strip()

        # 기본 응답 생성
        response_text = "안녕하세요! 무엇을 도와드릴까요?"
        quick_replies = [
            QuickReply(
                label="도움말",
                action="message",
                messageText="도움말"
            ),
            QuickReply(
                label="안녕하세요",
                action="message",
                messageText="안녕하세요"
            )
        ]

        # 간단한 응답 분기 처리
        if "안녕" in user_utterance:
            response_text = "안녕하세요! 반갑습니다 😊"
        elif "도움말" in user_utterance:
            response_text = "다음과 같은 기능을 제공합니다:\n1. 인사하기\n2. 도움말 보기"

        # 응답 형식 생성
        response = KakaoResponse(
            template={
                "outputs": [
                    {
                        "simpleText": {
                            "text": response_text
                        }
                    }
                ],
                "quickReplies": [
                    quick_reply.dict() for quick_reply in quick_replies
                ]
            }
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
