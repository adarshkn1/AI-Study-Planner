from agent.memory import save_agent_decision, load_agent_decisions

class AgentDecisionLogger:
    """Helper class to format and store transparent agent reasoning per user."""

    @staticmethod
    def log(user_id: int, trigger_event: str, reason: str, decision: str, constraint_applied: str, result: str):
        save_agent_decision(
            user_id=user_id,
            trigger_event=trigger_event,
            reason=reason,
            decision=decision,
            constraint_applied=constraint_applied,
            result=result
        )

    @staticmethod
    def get_all_decisions(user_id: int):
        return load_agent_decisions(user_id)
