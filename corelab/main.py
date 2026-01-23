from core.nucleus import Nucleus, StudyRequest
from core.portfolio import StudentPortfolio


def main() -> None:
    print("=== Plataforma de Estudos (MVP) ===")

    topic = input("Tema: ").strip()
    level = input("Nível: ").strip()
    goal = input("Objetivo: ").strip()

    portfolio = StudentPortfolio()
    nucleus = Nucleus()

    request = StudyRequest(topic=topic, level=level, goal=goal)
    result = nucleus.start(request=request, portfolio=portfolio)

    session_id = result.session_id
    plan = result.plan
    step_index = result.current_step_index

    print("\n--- Plano de estudo ---")
    for i, step in enumerate(plan):
        title = getattr(step, "title", None) or getattr(step, "step_title", None) or str(step)
        print(f"{i}. {title}")

    print("\n--- Início ---")

    while True:
        step = plan[step_index]
        title = getattr(step, "title", None) or getattr(step, "step_title", None) or str(step)

        # agora o cliente pede ao NÚCLEO (não ao tutor diretamente)
        instruction = nucleus.explain_step(request=request, step=step)

        print(f"\n[Passo {step_index}] {title}")
        print(instruction)

        answer = input("> ")

        portfolio.record_step(
            session_id=session_id,
            step_index=step_index,
            student_answer=answer,
        )

        decision = nucleus.decide(
            portfolio=portfolio,
            session_id=session_id,
            current_step_index=step_index,
            total_steps=len(plan),
        )

        print(f"[decision] {decision.action} — {decision.reason}")

        if decision.action == "retry":
            continue

        if decision.next_step_index is None:
            print("\n✅ Plano finalizado.")
            break

        step_index = decision.next_step_index


if __name__ == "__main__":
    main()