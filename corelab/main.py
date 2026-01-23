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
        print(f"{i}. {step.title}")

    print("\n--- Início ---")

    while True:
        step = plan[step_index]

        # instrução do tutor (agente)
        instruction = nucleus.tutor_agent.explain(step)
        print(f"\n[Passo {step_index}] {step.title}")
        print(instruction)

        # resposta do aluno
        answer = input("> ")

        # registra no portfólio
        portfolio.record_step(
            session_id=session_id,
            step_index=step_index,
            student_answer=answer,
        )

        # decisão do núcleo (camada 3)
        decision = nucleus.decide(
            portfolio=portfolio,
            session_id=session_id,
            current_step_index=step_index,
            total_steps=len(plan),
        )

        print(f"[decision] {decision.action} — {decision.reason}")

        if decision.action == "retry":
            # repete o mesmo passo
            continue

        if decision.next_step_index is None:
            print("\n✅ Plano finalizado.")
            break

        step_index = decision.next_step_index


if __name__ == "__main__":
    main()
