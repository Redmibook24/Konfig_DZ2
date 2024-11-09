import os
import unittest
from graphviz import Digraph
from dependency_visualizer import (
    load_config,
    get_commit_history,
    build_dependency_graph,
    save_graph
)


class TestDependencyVisualizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Определяем текущий каталог, где находится тестовый файл
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Настройка абсолютного пути к репозиторию и выходному файлу
        cls.repo_path = os.path.abspath(os.path.join(current_dir, "../test-repo"))
        cls.output_path = os.path.abspath(os.path.join(current_dir, "output/graph"))
        
        # Абсолютный путь к конфигурационному файлу
        cls.config_path = os.path.abspath(os.path.join(current_dir, "../test-repo/config.yaml"))
        
        # Создаем папку output, если она не существует
        os.makedirs(os.path.dirname(cls.output_path), exist_ok=True)

    def test_load_config(self):
        # Тестируем загрузку конфигурации из файла YAML
        print(f"Загружаем конфигурацию из: {self.config_path}")
        config = load_config(self.config_path)
        self.assertIn('repo_path', config)
        self.assertIn('output_path', config)
        self.assertIn('target_file_hash', config)

    def test_get_commit_history(self):
        # Тестируем получение истории коммитов для файла
        commits = get_commit_history(self.repo_path, 'file1.txt')
        self.assertGreater(len(commits), 0)
        self.assertIsInstance(commits, list)

    def test_build_dependency_graph(self):
        # Тестируем построение графа зависимостей
        commits = get_commit_history(self.repo_path, 'file1.txt')
        dot = build_dependency_graph(self.repo_path, commits)
        self.assertIsInstance(dot, Digraph)
        self.assertGreater(len(dot.body), 0)

    def test_save_graph(self):
        # Тестируем сохранение графа в файл
        commits = get_commit_history(self.repo_path, 'file1.txt')
        dot = build_dependency_graph(self.repo_path, commits)
        save_graph(dot, self.output_path)
        # Убедимся, что файл создан с расширением .png
        self.assertTrue(os.path.exists(f"{self.output_path}.png"), f"Файл {self.output_path}.png не найден")

    @classmethod
    def tearDownClass(cls):
        # Очистка после тестов
        if os.path.exists(f"{cls.output_path}.png"):
            os.remove(f"{cls.output_path}.png")


if __name__ == "__main__":
    unittest.main()
