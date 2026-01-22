# main.py
from core.nucleus import Nucleus, StudyRequest


def main():
    print("=== Plataforma de Matemática (MVP) ===")

    # 1) Coleta de dados iniciais (cliente)
    topic = input("Tema (ex: frações): ").strip()
    level = input("Nível (ex: fundamental/médio): ").strip()
    goal = input("Objetivo (ex: somar frações): ").strip()

    # 2) Cria o núcleo (autoridade)
    nucleus = Nucleus()

    # 3) Inicia o estudo (cria sessão + plano + instrução)
    result = nucleus.start(
        StudyRequest(
            topic=topic,
            level=level,
            goal=goal
        )
    )

    # 4) Mostra o plano gerado
    print("\n--- Plano de Estudo ---")
    for i, step in enumerate(result["plan"], start=1):
        print(f"{i}. {step['title']} — {step['prompt']}")

    # 5) Mostra a instrução do passo atual
    print("\n--- Tutor ---")
    print(result["tutor_output"])

    # 6) Recebe a resposta do aluno
    print("\n--- Sua resposta ---")
    user_answer = input("> ")

    # 7) Registra a resposta no Portfólio via Núcleo
    nucleus.receive_answer(
        step_title=result["current_step"]["title"],
        prompt=result["current_step"]["prompt"],
        answer=user_answer
    )

    # 8) Debug mínimo (apenas para validar o MVP)
    current_session = nucleus.portfolio.current_session()

    print("\n--- Resposta registrada no Portfólio ---")
    print(f"ID da sessão: {current_session.session_id}")
    print(f"Total de sessões no portfólio: {len(nucleus.portfolio.sessions)}")
    print(f"Passos registrados nesta sessão: {len(current_session.steps)}")
    print(f"Última resposta: {current_session.steps[-1].student_answer}")



if __name__ == "__main__":
    main()