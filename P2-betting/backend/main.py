PREDICTION_EVENTS = {
    "tomorrow-rain": {
        "question": "明天会下雨吗？",
        "options": ["yes", "no"],
        "pool": {"yes": 0.0, "no": 0.0},
        "deadline": "2026-12-31 23:59:59",
        "bets_count": 0
    },
    "typhoon": {
        "question": "台风会经过这里吗？",
        "options": ["yes", "no"],
        "pool": {"yes": 0.0, "no": 0.0},
        "deadline": "2026-12-31 23:59:59",
        "bets_count": 0
    }
}
from fastapi import FastAPI, HTTPException
from typing import Annotated
from pydantic import Field,BaseModel
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# GET /api/v1/predictions/{event_id}：获取特定竞猜事件当前的奖池与状态。
@app.get('/predictions/{event_id}')
async def get_evens(event_id : str):
    try:
        event = PREDICTION_EVENTS[event_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
'''
POST /api/v1/predictions/{event_id}/bet
提交下注，接收查询参数 user_id: str、option
str (如 "yes" 或 "no")与 amount: float。
'''
class OptionEnum(str, Enum):
    yes = "yes"
    no = "no"
class put_bet(BaseModel):
    user_id: int
    option: OptionEnum
    amount: float = Field(..., gt=0)
@app.post('/predictions/{event_id}/bet')
async def bet(event_id : str, bet_data: put_bet):
    try:
        event = PREDICTION_EVENTS[event_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Event not found")
    if bet_data.option not in event["options"]:
        raise HTTPException(status_code=400, detail="Invalid option")  
    if bet_data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")  
    event["pool"][bet_data.option] += bet_data.amount
    event["bets_count"] += 1
    return {"message": "Bet placed successfully", "event": event}
