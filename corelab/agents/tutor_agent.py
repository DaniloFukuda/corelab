# agents/tutor_agent.py

class PlaceholderTutorAgent:
    """
    Agente tutor (placeholder).
    Depois será substituído por IA.

    Importante: este agente devolve APENAS o texto da instrução do passo.
    Cabeçalho/ritual ficam no cliente (main).
    """

    def explain(self, topic: str, level: str, goal: str, step_title: str, step_prompt: str) -> str:
        # Por enquanto, retornamos só o prompt do passo.
        # Depois, com IA, você pode enriquecer isso (sem incluir cabeçalho fixo do CLI).
        return step_prompt
