from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from ..db import get_session
from ..schemas import (
    EvaluateAllRulesResponse,
    RuleCreate,
    RuleEnabledUpdate,
    RuleEvaluationResponse,
    RuleExecutionRead,
    RuleRead,
    RuleUpdate,
)
from ..services import rules as rule_service

router = APIRouter(prefix='/rules', tags=['rules'])


@router.post('/evaluate-all', response_model=EvaluateAllRulesResponse)
def evaluate_all_rules(
    dry_run: bool = Query(default=True),
    session: Session = Depends(get_session),
):
    return {'executions': rule_service.evaluate_all_rules(session, dry_run=dry_run)}


@router.get('', response_model=list[RuleRead])
def list_rules(session: Session = Depends(get_session)):
    return rule_service.list_rules(session)


@router.post('', response_model=RuleRead, status_code=status.HTTP_201_CREATED)
def create_rule(payload: RuleCreate, session: Session = Depends(get_session)):
    return rule_service.create_rule(session, payload)


@router.get('/executions', response_model=list[RuleExecutionRead])
def list_rule_executions(
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    return rule_service.list_rule_executions(session, limit=limit)


@router.get('/{rule_id}', response_model=RuleRead)
def get_rule(rule_id: int, session: Session = Depends(get_session)):
    return rule_service.get_rule_read(session, rule_id)


@router.put('/{rule_id}', response_model=RuleRead)
def update_rule(rule_id: int, payload: RuleUpdate, session: Session = Depends(get_session)):
    rule = rule_service.get_rule_or_404(session, rule_id)
    return rule_service.update_rule(session, rule, payload)


@router.patch('/{rule_id}/enabled', response_model=RuleRead)
def update_rule_enabled(rule_id: int, payload: RuleEnabledUpdate, session: Session = Depends(get_session)):
    rule = rule_service.get_rule_or_404(session, rule_id)
    return rule_service.update_rule_enabled(session, rule, payload)


@router.post('/{rule_id}/evaluate', response_model=RuleEvaluationResponse)
def evaluate_rule(
    rule_id: int,
    dry_run: bool = Query(default=True),
    session: Session = Depends(get_session),
):
    rule = rule_service.get_rule_or_404(session, rule_id)
    return rule_service.evaluate_rule(session, rule, dry_run=dry_run)


@router.get('/{rule_id}/executions', response_model=list[RuleExecutionRead])
def list_rule_executions_for_rule(
    rule_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    rule_service.get_rule_or_404(session, rule_id)
    return rule_service.list_rule_executions(session, rule_id=rule_id, limit=limit)
