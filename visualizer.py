import os
import subprocess
import argparse


def get_commit_dependencies(repo_path, file_name):
    """
    Получает список зависимостей (родительские коммиты) для каждого коммита, который затрагивает указанный файл.
    :param repo_path: Путь к репозиторию.
    :param file_name: Имя файла, для которого строится граф зависимостей.
    :return: Список кортежей (commit_hash, [parent_hashes]).
    """
    try:
        # Получаем лог изменений для файла (формат: хеш коммита и хеши его родителей)
        result = subprocess.run(
            ["git", "-C", repo_path, "log", "--pretty=format:%H %P", "--", file_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Ошибка выполнения команды git: {result.stderr}")

        dependencies = []
        for line in result.stdout.strip().split("\n"):
            parts = line.split()
            commit = parts[0]
            parents = parts[1:] if len(parts) > 1 else []
            dependencies.append((commit, parents))

        return dependencies

    except Exception as e:
        raise RuntimeError(f"Не удалось получить зависимости: {e}")


def generate_dot_code(dependencies):
    """
    Генерирует код Graphviz в формате .dot на основе зависимостей коммитов.
    :param dependencies: Список зависимостей в формате (commit, [parent1, parent2, ...]).
    :return: Строка с кодом Graphviz.
    """
    dot_code = "digraph G {\n"
    for commit, parents in dependencies:
        for parent in parents:
            dot_code += f'    "{parent}" -> "{commit}";\n'  # Ребро от родителя к коммиту
    dot_code += "}\n"
    return dot_code


def main():
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(description="Визуализатор графа зависимостей коммитов.")
    parser.add_argument("--graphviz_path", required=True, help="Путь к утилите Graphviz (dot.exe).")
    parser.add_argument("--repo_path", required=True, help="Путь к анализируемому репозиторию.")
    parser.add_argument("--output_file", required=True, help="Путь к выходному файлу для сохранения графа.")
    parser.add_argument("--file_name", required=True, help="Имя файла для анализа зависимостей.")

    args = parser.parse_args()

    # Проверяем, что репозиторий существует
    if not os.path.exists(args.repo_path):
        raise FileNotFoundError(f"Репозиторий не найден: {args.repo_path}")

    # Получаем зависимости для указанного файла
    dependencies = get_commit_dependencies(args.repo_path, args.file_name)

    # Генерация .dot кода
    dot_code = generate_dot_code(dependencies)

    # Сохраняем .dot код в файл
    with open(args.output_file, 'w') as f:
        f.write(dot_code)

    print(f"Граф зависимостей сохранён в файл: {args.output_file}")
    print("\nСодержимое графа .dot:\n")
    print(dot_code)


if __name__ == "__main__":
    main()
