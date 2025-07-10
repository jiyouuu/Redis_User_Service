import os 
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, HTTPException

USER_SERVICE_URL = os.getenv('USER_SERVICE_URL')


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print("🚀 서버 시작 중... DB 초기화 중")
    app.state.client = httpx.AsyncClient()   # 비동기 클라이언트 생성 ,app.state.client에 공유 http 클라이언트를 저장해서 이후 라우트에서 사용할 수 있게 함


    print("✅ DB 초기화 완료")

    yield  # 여기가 실행되면 FastAPI 앱이 본격적으로 실행됨

    # shutdown
    print("🛑 서버 종료!")
    await app.state.client.aclose()   # 리소스 정리

app = FastAPI(title="API Gateway", lifespan=lifespan)



# api_route: 모든 HTTP 메서드에 대해 경로를 처리할 수 있게 해주는 FastAPI의 데코레이터
# 즉, 전체 요청을 가로채는 "리버스 프록시" 역할을 하는 엔드포인트
# /{path:path}는 모든 경로를 받아옴
@app.api_route("/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"])
async def reverse_proxy(request: Request) :    # request: Request를 통해 클라이언트가 보낸 요청 정보(헤더, 본문 등)를 모두 받을 수 있음 
    path = request.url.path
    client: httpx.AsyncClient = request.app.state.client  # 다른 마이크로서비스에 요청을 보내는 비동기 HTTP 클라이언트 역할


# /api/users로 시작하는 요청이면 USER_SERVICE_URL로 보내고, # 그 외의 경로는 404 에러로 처리
# 즉, 지금은 유저 관련 요청만 Gateway에서 프록시하도록 제한하고 있는 상태
    if path.startswith("/api/users"):
        base_url = USER_SERVICE_URL
    else:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    url = f"{base_url}{path}?{request.url.query}"  # 마이크로서비스로 보낼 최종 URL을 만듦

    try:
        rp_resp = await client.request(   # 비동기 HTTP 요청을 날림
            method=request.method,
            url=url,
            headers=dict(request.headers),  # dict로 변환하여 httpx가 잘 인식하도록
            content= await request.body()   # content: 클라이언트가 보낸 body 내용을 비동기로 추출
        )
        return Response(    # httpx 응답 객체인 rp_resp에서 가져온 값을 그대로 FastAPI의 Response로 감싸서 리턴
            content=rp_resp.content,
            status_code=rp_resp.status_code,
            headers=dict(rp_resp.headers)  # FastAPI Response에 넣기 쉽게 변환
        )
    except httpx.ConnectError:  # 만약 마이크로서비스에 연결이 안 되면 httpx.ConnectError 예외가 발생
        raise HTTPException(status_code=503, detail="Service unavailable")