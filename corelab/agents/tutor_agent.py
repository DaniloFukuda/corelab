class PlaceholderTutorAgent:
    """
    Agente tutor (placeholder).
    Depois será substituído por IA.
    """
    def explain(self, topic: str, level: str, goal: str, step_title: str, step_prompt: str) -> str:
        return (
            "Tutor (placeholder)\n"
            f"Tema: {topic}\n"
            f"Nível: {level}\n"
            f"Objetivo: {goal}\n\n"
            f"Passo atual: {step_title}\n"
            f"Instrução: {step_prompt}\n\n"
            "Responda com honestidade. Se travar, diga exatamente onde."
        )
