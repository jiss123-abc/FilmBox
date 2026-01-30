import random
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.strategy_experiment import StrategyExperiment

EXPERIMENT_GROUP = "phase14_ab"
STRATEGIES = ["collaborative-filtering", "content-based"]


def get_or_assign_strategy(user_id: int) -> str:
    session: Session = SessionLocal()

    record = (
        session.query(StrategyExperiment)
        .filter(
            StrategyExperiment.user_id == user_id,
            StrategyExperiment.experiment_group == EXPERIMENT_GROUP
        )
        .first()
    )

    if record:
        session.close()
        return record.strategy

    chosen = random.choice(STRATEGIES)

    new_record = StrategyExperiment(
        user_id=user_id,
        strategy=chosen,
        experiment_group=EXPERIMENT_GROUP
    )

    session.add(new_record)
    session.commit()
    session.close()

    return chosen
