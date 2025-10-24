from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.db.manager import get_db_session

DBSessionDep = Annotated[Session, Depends(get_db_session)]