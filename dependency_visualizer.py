import os
import yaml
import subprocess
from graphviz import Digraph


def load_config(config_path):
    """
    Загрузка конфигурационного файла.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def get_commit_history(repo_path, file_path):
    """
    Получаем историю коммитов, связанных с файлом.
    """
    if not os.path.isdir(repo_path):
        raise ValueError(f"Invalid repository path: {repo_path}")

    cmd = ["git", "-C", repo_path, "log", "--pretty=format:%H", "--", file_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running git log: {e}")
        return []

    return result.stdout.splitlines()


def get_commit_message(repo_path, commit_hash):
    """
    Получаем сообщение коммита по его хешу.
    """
    cmd = ["git", "-C", repo_path, "log", "-n", "1", "--pretty=format:%s", commit_hash]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "No commit message"


def build_dependency_graph(repo_path, commits):
    """
    Строим граф зависимостей на основе коммитов.
    """
    dot = Digraph(comment='Dependency Graph', format='png')
    
    # Добавляем узлы с хешем и сообщением коммита
    for commit in commits:
        message = get_commit_message(repo_path, commit)
        label = f"{commit[:7]}: {message}"
        dot.node(commit[:7], label)
    
    # Добавляем рёбра между коммитами
    for child in commits:
        parent_cmd = ["git", "-C", repo_path, "log", "-n", "1", "--pretty=format:%P", child]
        try:
            parent_commit = subprocess.run(parent_cmd, capture_output=True, text=True, check=True).stdout.strip()
        except subprocess.CalledProcessError:
            continue

        if parent_commit:
            parents = parent_commit.split()
            for parent in parents:
                # Добавляем связь между коммитом и его родителем
                dot.edge(child[:7], parent[:7])
    
    return dot


def save_graph(dot, output_path):
    """
    Сохраняем граф в файл.
    """
    try:
        dot.render(output_path, cleanup=True)
        print(f"Dependency graph saved to {output_path}.png")
    except Exception as e:
        print(f"Error saving graph: {e}")


def main(config_path):
    config = load_config(config_path)
    
    repo_path = config.get('repo_path')
    output_path = config.get('output_path')
    file_path = config.get('target_file_hash')
    
    if not repo_path or not output_path or not file_path:
        print("Config file is missing required fields.")
        return

    # Найти все коммиты, связанные с файлом
    commits = get_commit_history(repo_path, file_path)
    if not commits:
        print("No commits found for the specified file.")
        return
    
    # Построить граф
    dot = build_dependency_graph(repo_path, commits)
    
    # Сохранить граф
    save_graph(dot, output_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python dependency_visualizer.py <config_path>")
    else:
        try:
            main(sys.argv[1])
        except Exception as e:
            print(f"An error occurred: {e}")
