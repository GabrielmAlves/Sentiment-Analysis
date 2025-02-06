import time
import os
import subprocess
import webbrowser
from collections import deque
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 📝 Configuração do repositório GitHub
GITHUB_REPO = "GabrielmAlves/Sentiment-Analysis"  # Exemplo: "meuUsuario/meuRepo"
BRANCH_ATUAL = "master"  # Branch principal
BRANCH_NOVA = "feature-auto-update"  # Nome da branch do PR
REPO_DIR = r"C:\Users\Usuario\OneDrive\Documentos\Projetos\AnaliseSentimentos\SentimentAnalysisApp\SentimentAnalysis\Sentiment-Analysis"  # Diretório do repositório

# Classe para armazenar histórico de versões (Linked List)
class LinkedList:
    def __init__(self):
        self.history = deque()

    def add_version(self, content):
        if content.strip() and (not self.history or self.history[-1] != content):
            self.history.append(content)
            return True
        return False

    def get_latest_version(self):
        return self.history[-1] if self.history else None

# Hash table para armazenar históricos de cada arquivo
conteudo_anterior = {}

class MeuManipulador(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.processados = set()
        self.arquivos_modificados = set()

    def process_file(self, caminho_arquivo):
        """Processa um arquivo para verificar mudanças e registrar para possível PR."""
        if os.path.exists(caminho_arquivo):
            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                    novo_conteudo = arquivo.read()

                    if not novo_conteudo.strip():
                        return  # Ignora arquivos vazios

                    if caminho_arquivo in conteudo_anterior:
                        nova_versao = conteudo_anterior[caminho_arquivo].add_version(novo_conteudo)
                    else:
                        conteudo_anterior[caminho_arquivo] = LinkedList()
                        nova_versao = conteudo_anterior[caminho_arquivo].add_version(novo_conteudo)

                    if nova_versao:
                        self.arquivos_modificados.add(caminho_arquivo)

            except Exception as e:
                print(f'Erro ao ler o arquivo {caminho_arquivo}: {e}')

    def on_modified(self, event):
        """Dispara quando um arquivo é modificado."""
        if not event.is_directory:
            caminho_arquivo = event.src_path

            if caminho_arquivo in self.processados:
                return  # Evita múltiplos eventos para a mesma modificação

            self.processados.add(caminho_arquivo)
            time.sleep(0.5)  # Garante que o arquivo foi salvo antes de processar
            self.process_file(caminho_arquivo)

            time.sleep(1)
            self.processados.remove(caminho_arquivo)

            if self.arquivos_modificados:
                self.perguntar_criacao_pr()

    def perguntar_criacao_pr(self):
        """Pergunta ao usuário se deseja criar um Pull Request."""
        while True:
            resposta = input("\n❓ Deseja criar um Pull Request com as modificações? (s/n): ").strip().lower()
            if resposta in ["s", "n"]:
                break
            print("❌ Resposta inválida! Digite 's' para sim ou 'n' para não.")

        if resposta == "s":
            self.commit_push_pull_request()
        else:
            print("⏳ As alterações continuarão armazenadas, mas sem criar PR.")

    def commit_push_pull_request(self):
        """Adiciona arquivos ao Git, faz commit e cria um PR."""
        os.chdir(REPO_DIR)  # Garante que estamos no repositório correto
        print("\n🔄 Adicionando arquivos ao Git...")
        for arquivo in self.arquivos_modificados:
            subprocess.run(["git", "add", arquivo])

        # Solicita a mensagem do commit ao usuário
        mensagem_commit = input("\n📝 Digite a mensagem do commit: ")

        if not mensagem_commit.strip():
            print("❌ Mensagem do commit não pode ser vazia!")
            return

        # Realiza o commit
        subprocess.run(["git", "commit", "-m", mensagem_commit])

        # Verifica se a branch já existe e cria se necessário
        branches = subprocess.run(["git", "branch"], capture_output=True, text=True).stdout
        if BRANCH_NOVA not in branches:
            subprocess.run(["git", "checkout", "-B", BRANCH_NOVA])  # Cria nova branch
        else:
            subprocess.run(["git", "checkout", BRANCH_NOVA])  # Muda para a branch existente

        # Envia as mudanças para o repositório remoto
        print("\n🚀 Enviando mudanças para o GitHub...")
        subprocess.run(["git", "push", "--set-upstream", "origin", BRANCH_NOVA])

        # Cria um pull request usando a API do GitHub
        print("\n🔀 Criando Pull Request...")
        subprocess.run(["gh", "pr", "create", "--base", BRANCH_ATUAL, "--head", BRANCH_NOVA, "--title", mensagem_commit, "--body", "Este PR foi criado automaticamente após modificações nos arquivos."])

        # Obtém a URL do PR para abrir no navegador
        pr_url = subprocess.run(["gh", "pr", "view", "--json", "url", "--jq", ".url"], capture_output=True, text=True).stdout.strip()
        
        if pr_url:
            print(f"\n✅ Pull Request criado com sucesso! Acesse: {pr_url}")
            webbrowser.open(pr_url)  # Abre o PR no navegador
        else:
            print("\n❌ Falha ao obter a URL do Pull Request.")

        # Limpa a lista de arquivos modificados
        self.arquivos_modificados.clear()

# 📂 Caminho da pasta a ser monitorada
caminho = r"C:\Users\Usuario\OneDrive\Documentos\Projetos\AnaliseSentimentos\SentimentAnalysisApp\SentimentAnalysis\Sentiment-Analysis"

# 🔍 Criando o observador
observer = Observer()
event_handler = MeuManipulador()
observer.schedule(event_handler, caminho, recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)  # Mantém o programa rodando
except KeyboardInterrupt:
    observer.stop()
observer.join()
