from core.core import Core, CoreResult


def step_echo(ctx) -> CoreResult:
    return CoreResult(ok=True, data={"echo": ctx["message"]})


def main():
    core = Core()
    core.register_step(step_echo)

    result = core.run({"message": "teste do núcleo"})
    print("OK:", result.ok)
    print("ERROR:", result.error)
    print("DATA:", result.data)


if __name__ == "__main__":
    main()
