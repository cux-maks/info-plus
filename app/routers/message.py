"""카카오톡 챗봇 메시지 처리를 위한 라우터 모듈.

이 모듈은 카카오톡 챗봇의 메시지 처리를 위한 FastAPI 라우터를 구현합니다.
사용자의 메시지를 받아 적절한 응답을 생성하고 반환하는 기능을 제공합니다.
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/kakao", tags=["kakao"])

class KakaoRequest(BaseModel):
    """카카오톡 스킬 요청 데이터 모델.

    Attributes:
        intent: 사용자 발화에 대한 인텐트 정보를 담은 딕셔너리
        userRequest: 사용자 요청 정보를 담은 딕셔너리
        bot: 봇 정보를 담은 딕셔너리
        action: 스킬 실행 정보를 담은 딕셔너리
    """
    intent: Dict[str, Any]
    userRequest: Dict[str, Any]
    bot: Dict[str, Any]
    action: Dict[str, Any]

class SimpleText(BaseModel):
    """카카오톡 간단 텍스트 응답 모델.

    Attributes:
        text: 응답할 텍스트 메시지
    """
    text: str

class QuickReply(BaseModel):
    """카카오톡 빠른 응답 버튼 모델.

    Attributes:
        label: 버튼에 표시될 텍스트
        action: 버튼 동작 타입 (message 등)
        messageText: 버튼 클릭시 전송될 메시지
    """
    label: str
    action: str
    messageText: str

class KakaoResponse(BaseModel):
    """카카오톡 응답 데이터 모델.

    Attributes:
        version: 카카오톡 응답 프로토콜 버전
        template: 응답 템플릿 정보를 담은 딕셔너리
    """
    version: str = "2.0"
    template: Dict[str, Any]

@router.post("/message")
async def handle_message(request: KakaoRequest) -> KakaoResponse:
    """카카오톡 챗봇 기본 메시지 처리 엔드포인트.

    사용자의 발화를 분석하고 적절한 응답을 생성하여 반환합니다.

    Args:
        request: 카카오톡 스킬 요청 데이터

    Returns:
        KakaoResponse: 처리된 응답 데이터

    Raises:
        HTTPException: 메시지 처리 중 오류 발생시 500 에러 반환
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
        raise HTTPException(status_code=500, detail=str(e)) from e
