import tkinter as tk
from tkinter import ttk
import requests
import json
from tkinter import messagebox

class StepsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Steps")
        self.root.geometry("1400x600")

        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar a tabela
        self.tree = ttk.Treeview(main_frame, columns=(
            "MissionId",
            "State", 
            "Priority",
            "StepIndex",
            "StepType",
            "StepStatus",
            "CurrentTargetId",
            "AllowedTargets",
            "SortingRules",
            "WaitForExtension"
        ), show='headings')
        
        # Definir as colunas
        self.tree.heading("MissionId", text="ID da Missão")
        self.tree.heading("State", text="State da Missão")
        self.tree.heading("Priority", text="Prioridade")
        self.tree.heading("StepIndex", text="StepIndex")
        self.tree.heading("StepType", text="Tipo do Step")
        self.tree.heading("StepStatus", text="Status")
        self.tree.heading("CurrentTargetId", text="Target Atual")
        self.tree.heading("AllowedTargets", text="Targets Permitidos")
        self.tree.heading("SortingRules", text="Regras de Ordenação")
        self.tree.heading("WaitForExtension", text="Aguarda Extensão")

        # Configurar larguras das colunas
        self.tree.column("MissionId", width=80)
        self.tree.column("State", width=150)
        self.tree.column("Priority", width=70)
        self.tree.column("StepIndex", width=60)
        self.tree.column("StepType", width=100)
        self.tree.column("StepStatus", width=100)
        self.tree.column("CurrentTargetId", width=100)
        self.tree.column("AllowedTargets", width=120)
        self.tree.column("SortingRules", width=150)
        self.tree.column("WaitForExtension", width=120)

        # Adicionar scrollbars
        scrolly = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollx = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)

        # Posicionar elementos na grid
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrolly.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollx.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Botão de atualizar
        ttk.Button(main_frame, text="Atualizar", command=self.fetch_steps).grid(row=2, column=0, pady=10)

        # Frame para edição
        edit_frame = ttk.LabelFrame(main_frame, text="Editar Step", padding="10")
        edit_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # Campos de edição
        row = 0
        ttk.Label(edit_frame, text="ID da Missão:").grid(row=row, column=0, pady=5)
        self.mission_id_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.mission_id_var, state='readonly').grid(row=row, column=1, pady=5)

        row += 1
        ttk.Label(edit_frame, text="State da Missão:").grid(row=row, column=0, pady=5)
        self.mission_State = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.mission_State).grid(row=row, column=1, pady=5)

        row += 1
        ttk.Label(edit_frame, text="StepIndex:").grid(row=row, column=0, pady=5)
        self.stepindex_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.stepindex_var).grid(row=row, column=1, pady=5)

        row += 1
        ttk.Label(edit_frame, text="Status:").grid(row=row, column=0, pady=5)
        self.status_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.status_var).grid(row=row, column=1, pady=5)

        row += 1
        ttk.Label(edit_frame, text="Target Atual:").grid(row=row, column=0, pady=5)
        self.target_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.target_var).grid(row=row, column=1, pady=5)

        row += 1
        ttk.Label(edit_frame, text="Aguarda Extensão:").grid(row=row, column=0, pady=5)
        self.wait_extension_var = tk.BooleanVar()
        ttk.Checkbutton(edit_frame, variable=self.wait_extension_var).grid(row=row, column=1, pady=5)

        # Botões de ação
        button_frame = ttk.Frame(edit_frame)
        button_frame.grid(row=row+1, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Salvar", command=self.save_step).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpar", command=self.clear_form).pack(side=tk.LEFT, padx=5)

        # Bind para seleção na tabela
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # Configurar expansão da grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Carregar dados iniciais
        self.fetch_steps()

    def fetch_steps(self):
        try:
            response = requests.get('http://localhost:1234/api/GetMissions')
            missions = response.json()
            
            # Limpar tabela atual
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Inserir dados atualizados
            for mission in missions:
                mission_id = mission['ExternalId']
                mission_State = mission.get('State', '')
                priority = mission.get('Options', {}).get('Priority', '')
                
                for i, step in enumerate(mission['Steps']):
                    # Formatar AllowedTargets para exibição
                    allowed_targets = ', '.join(str(target['Id']) for target in step['AllowedTargets'])
                    sorting_rules = ', '.join(step['Options'].get('SortingRules', []))
                    
                    self.tree.insert('', tk.END, values=(
                        mission_id,
                        mission_State,
                        priority,
                        i,
                        step.get('StepType', ''),
                        step['StepStatus'],
                        step['CurrentTargetId'],
                        allowed_targets,
                        sorting_rules,
                        'Sim' if step['Options'].get('WaitForExtension', False) else 'Não'
                    ))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar steps: {str(e)}")

    def on_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # Pegar valores da linha selecionada
        values = self.tree.item(selected_items[0])['values']
        
        # Atualizar campos de edição
        self.mission_id_var.set(values[0])
        self.mission_State.set(values[1])
        self.stepindex_var.set(values[3])
        self.status_var.set(values[5])
        self.target_var.set(values[6])
        self.wait_extension_var.set(values[9] == 'Sim')

    def save_step(self):
        try:
            # Primeiro, buscar a missão completa
            response = requests.get('http://localhost:1234/api/GetMissions')
            missions = response.json()
            
            mission_id = self.mission_id_var.get()
            mission = next((m for m in missions if str(m['ExternalId']) == str(mission_id)), None)
            
            if not mission:
                messagebox.showerror("Erro", "Missão não encontrada")
                return

            # Atualizar o step selecionado
            selected_items = self.tree.selection()
            if not selected_items:
                return

            step_index = int(self.tree.item(selected_items[0])['values'][3])
            
            # Atualizar os valores do step
            mission['State'] = self.mission_State.get()
            mission['StepIndex'] = int(self.stepindex_var.get())
            mission['Steps'][step_index]['StepStatus'] = self.status_var.get()
            mission['Steps'][step_index]['CurrentTargetId'] = int(self.target_var.get())
            mission['Steps'][step_index]['Options']['WaitForExtension'] = self.wait_extension_var.get()

            print(mission)
            # Enviar missão atualizada
            response = requests.post(
                'http://localhost:1234/api/missioncreate',
                json=mission
            )

            if response.ok:
                messagebox.showinfo("Sucesso", "Step atualizado com sucesso!")
                self.fetch_steps()
                self.clear_form()
            else:
                messagebox.showerror("Erro", "Erro ao salvar step")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar step: {str(e)}")

    def clear_form(self):
        self.mission_id_var.set("")
        self.mission_State.set("")
        self.stepindex_var.set("")
        self.status_var.set("")
        self.target_var.set("")
        self.wait_extension_var.set(False)

def main():
    root = tk.Tk()
    app = StepsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()