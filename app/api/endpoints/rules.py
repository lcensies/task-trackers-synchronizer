from fastapi import APIRouter
from app.core.db import DocumentDatabase
from app.core.rule import RuleDTO
from fastapi import Depends
from app.core.db import get_db
import app.api.crud as crud

router = APIRouter(prefix="/api")


# project id reserved for specific trackers which might
# have differnet fields per project
@router.get("/rule_list")
def get_rules(db: DocumentDatabase = Depends(get_db)):
    return crud.get_rules(db)


@router.post("/add_rule")
def add_rule(rule: RuleDTO, db: DocumentDatabase = Depends(get_db)):
    return crud.add_rule(rule, db)


@router.delete("/remove_rule")
def remove_rule(rule: RuleDTO, db: DocumentDatabase = Depends(get_db)):
    return crud.remove_rule(rule, db)


# TODO: error on POSt when rule with  source / dest fields exist
