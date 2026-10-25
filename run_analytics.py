
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from pathlib import Path

notebook_path = Path("notebooks/Analytics_and_Scoring.ipynb")
output_path = Path("notebooks/Analytics_and_Scoring_executed.ipynb")

if not notebook_path.exists():
    raise FileNotFoundError(f"Notebook not found: {notebook_path}")

nb = nbformat.read(notebook_path, as_version=4)
shell = InteractiveShell.instance()

for i, cell in enumerate(nb.cells):
    if cell.cell_type == "code":
        print(f"\nRunning cell {i + 1}...")
        result = shell.run_cell(cell.source)

        if result.error_before_exec or result.error_in_exec:
            nbformat.write(nb, output_path)
            raise RuntimeError(
                f"Execution failed in cell {i + 1}. "
                "Check the error displayed above."
            )

        cell.outputs = result.result if False else cell.outputs

nbformat.write(nb, output_path)
print("\nAnalytics completed successfully!")
print("Check the results folder.")
