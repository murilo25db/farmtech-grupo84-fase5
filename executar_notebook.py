"""Executa o relatório com o mesmo Python usado para chamar este arquivo."""
import os
import sys
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from jupyter_client import KernelManager


if __name__ == '__main__':
    pasta = Path(__file__).resolve().parent
    arquivo = pasta / 'MuriloDiasBrandao_rm573633_pbl_fase4.ipynb'
    notebook = nbformat.read(arquivo, as_version=4)
    os.environ['MPLBACKEND'] = 'module://matplotlib_inline.backend_inline'
    kernel = KernelManager(kernel_name='python3')
    kernel.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
    executor = NotebookClient(notebook, km=kernel, timeout=600, startup_timeout=60,
                              resources={'metadata': {'path': str(pasta)}})
    # O arquivo só é sobrescrito depois que todas as células executarem sem erro.
    executor.execute()
    nbformat.write(notebook, arquivo)
    html, _ = HTMLExporter().from_notebook_node(notebook)
    (pasta / 'relatorio_notebook.html').write_text(html, encoding='utf-8')
    print('Notebook e versão HTML atualizados com sucesso.')
