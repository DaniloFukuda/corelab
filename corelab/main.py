# main.py
# main.py
from core.nucleus import Nucleus, StudyRequest
from core.storage import load_portfolio, save_portfolio

PORTFOLIO_PATH = "data/portfolio.json"


def print_header() -> None:
    print("=== Plataforma de Estudos (MVP) ===")


def print_plan(plan) -> None:
    print("\n--- Plano de estudo ---")
    for i, step in enumerate(plan):
        title = getattr(step, "title", None) or getattr(step, "step_title", None) or str(step)
        print(f"{i}. {title}")


def step_title(step) -> str:
    return getattr(step, "title", None) or getattr(step, "step_title", None) or str(step)


def print_context(request: StudyRequest, current_step_index: int, title: str) -> None:
    print(f"\n[Passo {current_step_index}] {title}")
    print("Tutor (placeholder)")
    print(f"Tema: {request.topic}")
    print(f"Nível: {request.level}")
    print(f"Objetivo: {request.goal}\n")


def print_instruction(title: str, instruction: str) -> None:
    print(f"Passo atual: {title}")
    print(f"Instrução: {instruction}\n")
    print("Responda com honestidade. Se travar, diga exatamente onde.")


def main() -> None:
    print_header()

    topic = input("Tema: ").strip()
    level = input("Nível: ").strip()
    goal = input("Objetivo: ").strip()

    nucleus = Nucleus()

    # NOVO: carrega histórico (se existir)
    portfolio = load_portfolio(PORTFOLIO_PATH)

    request = StudyRequest(topic=topic, level=level, goal=goal)
    result = nucleus.start(request=request, portfolio=portfolio)

    plan = result.plan
    session_id = result.session_id
    current_step_index = result.current_step_index

    # Estado local (em vez de recriar `result`)
    instruction = result.instruction

    print_plan(plan)
    print("\n--- Início ---")

    while True:
        current_step = plan[current_step_index]
        title = step_title(current_step)

        # UI (cliente)
        print_context(request, current_step_index, title)
        print_instruction(title, instruction)

        # Resposta do aluno
        answer = input("> ")

        # Registro no portfólio (estado/histórico)
        portfolio.record_step(
            session_id=session_id,
            step_index=current_step_index,
            student_answer=answer,
        )

        # NOVO: salva depois de cada resposta (nunca perde histórico)
        save_portfolio(portfolio, PORTFOLIO_PATH)

        # Decisão do núcleo (delegando para a policy)
        decision = nucleus.decide(
            portfolio=portfolio,
            session_id=session_id,
            current_step_index=current_step_index,
            total_steps=len(plan),
        )

        # Decisão + fricção
        print(f"[decision] {decision.action} — {decision.reason}")
        friction_message = getattr(decision, "friction_message", None)
        if friction_message:
            print(f"[friction] {friction_message}")

        # Próximo índice (robusto)
        if decision.action == "retry":
            next_index = current_step_index
        else:
            next_index = decision.next_step_index

        # Encerramento
        if next_index is None:
            print("\n=== Fim do plano ===")
            break

        current_step_index = next_index

        # Próxima instrução
        next_step = plan[current_step_index]
        instruction = nucleus.explain_step(request=request, step=next_step)

    # Salva no final também (segurança extra)
    save_portfolio(portfolio, PORTFOLIO_PATH)


if __name__ == "__main__":
    main()
