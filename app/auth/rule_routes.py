from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.rate_limit_rule import RateLimitRule
from app.models.api_key import APIKey
from app.schemas.rule import RuleCreate, RuleResponse
from typing import List

router = APIRouter(prefix="/rules", tags=["rules"])

def get_tenant(api_key: str, db: Session = Depends(get_db)):
    key = db.query(APIKey).filter(
        APIKey.key == api_key,
        APIKey.is_active == True
    ).first()
    if not key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key

@router.post("/", response_model=RuleResponse)
def create_rule(
    rule: RuleCreate,
    db: Session = Depends(get_db),
    tenant: APIKey = Depends(get_tenant)
):
    db_rule = RateLimitRule(
        user_id=tenant.user_id,
        **rule.model_dump()
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.get("/", response_model=List[RuleResponse])
def list_rules(
    db: Session = Depends(get_db),
    tenant: APIKey = Depends(get_tenant)
):
    return db.query(RateLimitRule).filter(
        RateLimitRule.user_id == tenant.user_id,
        RateLimitRule.is_active == True
    ).all()

@router.delete("/{rule_id}")
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    tenant: APIKey = Depends(get_tenant)
):
    rule = db.query(RateLimitRule).filter(
        RateLimitRule.id == rule_id,
        RateLimitRule.user_id == tenant.user_id
    ).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    rule.is_active = False
    db.commit()
    return {"message": f"Rule {rule_id} deleted"}