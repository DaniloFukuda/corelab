from dataclasses import dataclass

@dataclass(frozen=True)
class StudyStep:
    title: str
    prompt: str

class SimplePlannerAgent:
    """
    Agente planejador.
    Divide o objetivo de estudo em passos.
    """
    def build_plan(self, topic: str, level: str, goal: str) -> list[StudyStep]:
        t = topic.strip().lower()
        return [
            StudyStep("Diagnóstico rápido", f"O que você já sabe sobre {t} e onde costuma errar?"),
            StudyStep("Conceito base", f"Explique com suas palavras o que é {t}."),
            StudyStep("Exemplo guiado", f"Vamos resolver 1 exemplo de {t} passo a passo."),
            StudyStep("Prática controlada", f"Resolva 3 exercícios curtos de {t}."),
            StudyStep("Checagem de domínio", f"Crie um exercício novo de {t} e explique a solução."),
        ]
