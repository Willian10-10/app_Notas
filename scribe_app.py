# --- CÓDIGO FINAL CON BARRA DE HERRAMIENTAS FUNCIONAL ---
# Archivo: app.py

import customtkinter as ctk
from datetime import datetime
import json
import tkinter as tk # Importamos tkinter para manejar errores de selección

# --- DATOS INICIALES ---
ramos_data = [
    {"nombre": "MINERÍA DE DATOS", "color": "#16A085", "icon": "📊"},
    {"nombre": "FINANZAS", "color": "#27AE60", "icon": "📈"},
    {"nombre": "INGLÉS INICIAL", "color": "#C0392B", "icon": "💬"},
    {"nombre": "PROBABILIDAD", "color": "#D35400", "icon": "🎲"},
    {"nombre": "PROYECTO DE INTEGRACIÓN", "color": "#8E44AD", "icon": "⚙️"},
    {"nombre": "SEGURIDAD DE INFORMACIÓN", "color": "#2980B9", "icon": "🛡️"},
]

HIGHLIGHT_COLOR = "#3498DB"

# --- PANTALLAS PRINCIPALES ---

class DashboardScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=3); self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        self.ramos_container = ctk.CTkFrame(self, fg_color="transparent"); self.ramos_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.scrollable_frame = ctk.CTkScrollableFrame(self.ramos_container, fg_color="transparent", label_text="Mis Ramos"); self.scrollable_frame.pack(fill="both", expand=True); self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.exams_panel = ctk.CTkScrollableFrame(self, label_text="Pruebas Próximas"); self.exams_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    def refresh_dashboard(self):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        all_notes = self.controller.get_all_notes()
        for i, ramo in enumerate(ramos_data):
            notes_count = len(all_notes.get(ramo['nombre'], [])); card = RamoCard(self.scrollable_frame, ramo, notes_count, self.controller)
            card.grid(row=i, column=0, padx=15, pady=15, sticky="nsew")
        for widget in self.exams_panel.winfo_children(): widget.destroy()
        all_exams = self.controller.get_all_exams(); today = datetime.now().date(); sorted_exams = sorted(all_exams, key=lambda x: datetime.strptime(x['fecha'], "%d/%m/%Y").date())
        if not sorted_exams: ctk.CTkLabel(self.exams_panel, text="No hay pruebas agendadas.").pack(pady=20)
        for exam in sorted_exams:
            exam_date = datetime.strptime(exam['fecha'], "%d/%m/%Y").date(); days_until = (exam_date - today).days
            if days_until < 0: text_color, status = "gray", f"(Pasó hace {-days_until} días)"
            elif days_until <= 7: text_color, status = "#E74C3C", f"¡En {days_until} días!"
            elif days_until <= 14: text_color, status = "#F39C12", f"En {days_until} días"
            else: text_color, status = "#FFFFFF", f"En {days_until} días"
            exam_item = ctk.CTkFrame(self.exams_panel, fg_color="#333333", corner_radius=6); exam_item.pack(fill="x", padx=10, pady=6)
            label_text = f"{exam['nombre']} ({exam['ramo']})"; ctk.CTkLabel(exam_item, text=label_text, font=ctk.CTkFont(size=14, weight="bold"), text_color=text_color).pack(anchor="w", padx=15, pady=(10,0))
            ctk.CTkLabel(exam_item, text=f"{exam['fecha']} - {status}", font=ctk.CTkFont(size=12), text_color=text_color).pack(anchor="w", padx=15, pady=(0,10))

class NotesScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller; self.current_ramo = None; self.current_note = None; self.selected_note_widget = None
        self.grid_columnconfigure(0, weight=2); self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(1, weight=1)
        self.header = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=8); self.header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.ramo_icon = ctk.CTkLabel(self.header, text="", font=ctk.CTkFont(size=25)); self.ramo_icon.pack(side="left", padx=15)
        self.ramo_title = ctk.CTkLabel(self.header, text="Selecciona un Ramo", font=ctk.CTkFont(size=18, weight="bold")); self.ramo_title.pack(side="left", pady=15)
        self.manage_exams_button = ctk.CTkButton(self.header, text="📅 Pruebas", fg_color="transparent", border_width=1, command=self.show_add_exam_ui); self.manage_exams_button.pack(side="right", padx=15)
        self.add_note_button = ctk.CTkButton(self.header, text="➕ Nueva Nota", command=self.show_add_note_ui); self.add_note_button.pack(side="right")
        self.notes_list_frame = ctk.CTkScrollableFrame(self, label_text="Notas Recientes"); self.notes_list_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 15))
        self.preview_frame = ctk.CTkFrame(self, fg_color="#2B2B2B"); self.preview_frame.grid(row=1, column=1, sticky="nsew")
        self.overlay_frame_note = ctk.CTkFrame(self, fg_color="#242424", corner_radius=0)
        self.add_note_panel = ctk.CTkFrame(self.overlay_frame_note, fg_color="#333333", corner_radius=8); self.add_note_panel.pack(expand=True)
        panel_title = ctk.CTkLabel(self.add_note_panel, text="Crear Nueva Nota", font=ctk.CTkFont(size=16, weight="bold")); panel_title.pack(padx=50, pady=(20, 10))
        self.new_note_entry = ctk.CTkEntry(self.add_note_panel, placeholder_text="Título de la nota...", width=250); self.new_note_entry.pack(padx=20, pady=5)
        btn_frame_note = ctk.CTkFrame(self.add_note_panel, fg_color="transparent"); btn_frame_note.pack(padx=20, pady=(10, 20))
        save_btn_note = ctk.CTkButton(btn_frame_note, text="Crear Nota", command=self.save_new_note); save_btn_note.pack(side="left", padx=5)
        cancel_btn_note = ctk.CTkButton(btn_frame_note, text="Cancelar", fg_color="transparent", border_width=1, command=self.hide_add_note_ui); cancel_btn_note.pack(side="left", padx=5)
        self.overlay_frame_exam = ctk.CTkFrame(self, fg_color="#242424", corner_radius=0)
        self.add_exam_panel = ctk.CTkFrame(self.overlay_frame_exam, fg_color="#333333", corner_radius=8); self.add_exam_panel.pack(expand=True)
        exam_panel_title = ctk.CTkLabel(self.add_exam_panel, text="Añadir Nueva Prueba", font=ctk.CTkFont(size=16, weight="bold")); exam_panel_title.pack(padx=50, pady=(20, 10))
        self.new_exam_name_entry = ctk.CTkEntry(self.add_exam_panel, placeholder_text="Nombre (Ej: Parcial 1)", width=250); self.new_exam_name_entry.pack(padx=20, pady=5)
        self.new_exam_date_entry = ctk.CTkEntry(self.add_exam_panel, placeholder_text="Fecha (DD/MM/AAAA)", width=250); self.new_exam_date_entry.pack(padx=20, pady=5)
        btn_frame_exam = ctk.CTkFrame(self.add_exam_panel, fg_color="transparent"); btn_frame_exam.pack(padx=20, pady=(10, 20))
        save_btn_exam = ctk.CTkButton(btn_frame_exam, text="Guardar Prueba", command=self.save_new_exam); save_btn_exam.pack(side="left", padx=5)
        cancel_btn_exam = ctk.CTkButton(btn_frame_exam, text="Cancelar", fg_color="transparent", border_width=1, command=self.hide_add_exam_ui); cancel_btn_exam.pack(side="left", padx=5)
        
    def load_ramo_data(self, ramo_info): self.current_ramo = ramo_info; self.ramo_icon.configure(text=ramo_info["icon"]); self.ramo_title.configure(text=ramo_info["nombre"]); self.refresh_notes_list(); self.clear_preview(); self.hide_add_note_ui(); self.hide_add_exam_ui()
    def refresh_notes_list(self):
        self.selected_note_widget = None; [widget.destroy() for widget in self.notes_list_frame.winfo_children()]
        ramo_notes = self.controller.get_notes_for_ramo(self.current_ramo['nombre'])
        for note in ramo_notes: note_item = NoteListItem(self.notes_list_frame, note, self); note_item.pack(fill="x", padx=5, pady=5)
    def set_selected_note(self, note_widget):
        if self.selected_note_widget: self.selected_note_widget.configure(border_width=0)
        self.selected_note_widget = note_widget; self.selected_note_widget.configure(border_color=HIGHLIGHT_COLOR, border_width=2); self.show_note_preview(note_widget.note)
    def delete_note(self, note_to_delete):
        if self.current_note == note_to_delete: self.clear_preview(); self.current_note = None
        self.controller.delete_note_from_ramo(self.current_ramo['nombre'], note_to_delete); self.refresh_notes_list()
    def show_add_note_ui(self): self.overlay_frame_note.place(relx=0, rely=0, relwidth=1, relheight=1); self.new_note_entry.focus()
    def hide_add_note_ui(self): self.overlay_frame_note.place_forget(); self.new_note_entry.delete(0, "end")
    def save_new_note(self):
        title = self.new_note_entry.get()
        if title:
            new_note = {"titulo": title, "tipo": "apunte", "fecha": datetime.now().strftime("%d/%m/%Y"), "contenido": f"# {title}\n\n"}
            self.controller.add_note_to_ramo(self.current_ramo['nombre'], new_note); self.refresh_notes_list(); self.hide_add_note_ui()
            for widget in self.notes_list_frame.winfo_children():
                if isinstance(widget, NoteListItem) and widget.note == new_note: self.set_selected_note(widget); break

    def show_note_preview(self, note):
        self.current_note = note; self.clear_preview()
        self.preview_frame.grid_rowconfigure(2, weight=1); self.preview_frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(self.preview_frame, text=note['titulo'], font=ctk.CTkFont(size=20, weight="bold")); title.grid(row=0, column=0, pady=10, padx=15, sticky="w")
        
        # --- NUEVO: Barra de herramientas ---
        toolbar = ctk.CTkFrame(self.preview_frame, fg_color="transparent"); toolbar.grid(row=1, column=0, padx=10, sticky="ew")
        
        # Botones de la barra de herramientas
        ctk.CTkButton(toolbar, text="H1", width=40, command=lambda: self._apply_formatting("h1")).pack(side="left", padx=2)
        ctk.CTkButton(toolbar, text="B", width=40, font=ctk.CTkFont(weight="bold"), command=lambda: self._apply_formatting("bold")).pack(side="left", padx=2)
        ctk.CTkButton(toolbar, text="I", width=40, font=ctk.CTkFont(slant="italic"), command=lambda: self._apply_formatting("italic")).pack(side="left", padx=2)
        ctk.CTkButton(toolbar, text="•", width=40, command=lambda: self._apply_formatting("bullet")).pack(side="left", padx=2)
        
        self.content_box = ctk.CTkTextbox(self.preview_frame, font=ctk.CTkFont(size=14)); self.content_box.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0,10))
        self.content_box.insert("0.0", note.get("contenido", ""))
        
        save_button = ctk.CTkButton(self.preview_frame, text="Guardar Cambios", command=self.save_note_content); save_button.grid(row=3, column=0, padx=15, pady=10)
    
    # --- NUEVO: Función para aplicar formato desde la barra de herramientas ---
    def _apply_formatting(self, style):
        try:
            start, end = self.content_box.tag_ranges("sel")
            selected_text = self.content_box.get(start, end)
            
            if style == "bold": new_text = f"**{selected_text}**"
            elif style == "italic": new_text = f"*{selected_text}*"
            elif style == "h1": new_text = f"# {selected_text}"
            elif style == "bullet": new_text = f"- {selected_text}"
            else: new_text = selected_text
            
            self.content_box.delete(start, end)
            self.content_box.insert(start, new_text)
        except tk.TclError:
            # Esto ocurre si no hay nada seleccionado, lo ignoramos
            pass

    def save_note_content(self):
        if self.current_note: self.current_note["contenido"] = self.content_box.get("0.0", "end"); self.controller.save_all_data_to_file(); print(f"Nota '{self.current_note['titulo']}' guardada!")
    def clear_preview(self): [widget.destroy() for widget in self.preview_frame.winfo_children()]
    def show_add_exam_ui(self): self.overlay_frame_exam.place(relx=0, rely=0, relwidth=1, relheight=1); self.new_exam_name_entry.focus()
    def hide_add_exam_ui(self): self.overlay_frame_exam.place_forget(); self.new_exam_name_entry.delete(0, "end"); self.new_exam_date_entry.delete(0, "end")
    def save_new_exam(self):
        name, date_str = self.new_exam_name_entry.get(), self.new_exam_date_entry.get()
        if name and date_str:
            try:
                datetime.strptime(date_str, "%d/%m/%Y"); new_exam = {"nombre": name, "fecha": date_str, "ramo": self.current_ramo['nombre']}
                self.controller.add_exam(new_exam); self.hide_add_exam_ui()
            except ValueError: print("Formato de fecha inválido. Usar DD/MM/AAAA")

class RamoCard(ctk.CTkFrame):
    def __init__(self, parent, ramo_info, notes_count, controller):
        super().__init__(parent, fg_color=ramo_info["color"], corner_radius=15)
        self.ramo_info = ramo_info; self.controller = controller; self.bind("<Button-1>", lambda e: self.controller.show_notes_screen(self.ramo_info)); self.grid_rowconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1); self.grid_columnconfigure(0, weight=1)
        top_frame = ctk.CTkFrame(self, fg_color="transparent"); top_frame.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="nsew"); top_frame.bind("<Button-1>", lambda e: self.controller.show_notes_screen(self.ramo_info))
        icon = ctk.CTkLabel(top_frame, text=ramo_info["icon"], font=ctk.CTkFont(size=30)); icon.pack(side="left", padx=(0, 10)); icon.bind("<Button-1>", lambda e: self.controller.show_notes_screen(self.ramo_info))
        title = ctk.CTkLabel(top_frame, text=ramo_info["nombre"], font=ctk.CTkFont(size=18, weight="bold")); title.pack(side="left"); title.bind("<Button-1>", lambda e: self.controller.show_notes_screen(self.ramo_info))
        bottom_frame = ctk.CTkFrame(self, fg_color="#333333", corner_radius=12); bottom_frame.grid(row=1, column=0, padx=8, pady=8, sticky="nsew"); bottom_frame.bind("<Button-1>", lambda e: self.controller.show_notes_screen(self.ramo_info))
        notes_count_label = ctk.CTkLabel(bottom_frame, text=f"{notes_count} Notes", text_color="#EAEAEA", font=ctk.CTkFont(size=14, weight="bold")); notes_count_label.pack(anchor="w", padx=15, pady=(10, 0)); notes_count_label.bind("<Button-1>", lambda e: self.controller.show_notes_screen(self.ramo_info))
        last_note = ctk.CTkLabel(bottom_frame, text="Last Note: --/--/----", text_color="#A0A0A0", font=ctk.CTkFont(size=12)); last_note.pack(anchor="w", padx=15, pady=(0, 10)); last_note.bind("<Button-1>", lambda e: self.controller.show_notes_screen(self.ramo_info))
class NoteListItem(ctk.CTkFrame):
    def __init__(self, parent, note, screen):
        super().__init__(parent, fg_color="#333333", corner_radius=6, border_width=0)
        self.note = note; self.screen = screen; self.grid_columnconfigure(1, weight=1)
        content_frame = ctk.CTkFrame(self, fg_color="transparent"); content_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5); content_frame.grid_columnconfigure(1, weight=1)
        icon_map = {"apunte": "📝", "audio": "🎤", "pdf": "📄", "repaso": "⭐"}
        icon = ctk.CTkLabel(content_frame, text=icon_map.get(note["tipo"], "❔"), font=ctk.CTkFont(size=20)); icon.grid(row=0, column=0, rowspan=2, padx=5, pady=5)
        title_label = ctk.CTkLabel(content_frame, text=note["titulo"], font=ctk.CTkFont(size=14, weight="bold"), anchor="w"); title_label.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        date_label = ctk.CTkLabel(content_frame, text=note["fecha"], font=ctk.CTkFont(size=12), text_color="gray", anchor="w"); date_label.grid(row=1, column=1, sticky="ew", padx=(0, 10))
        delete_button = ctk.CTkButton(self, text="🗑️", width=30, height=30, fg_color="transparent", text_color="gray", hover_color="#555555", command=self.delete_this_note); delete_button.grid(row=0, column=1, sticky="e", padx=10)
        content_frame.bind("<Button-1>", self.on_click); [child.bind("<Button-1>", self.on_click) for child in content_frame.winfo_children()]
    def on_click(self, event=None): self.screen.set_selected_note(self)
    def delete_this_note(self): self.screen.delete_note(self.note)
class SidebarFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, width=200, corner_radius=0, fg_color="#2B2B2B")
        self.controller = controller; self.buttons = {}
        dashboard_button = ctk.CTkButton(self, text="🏠 inicio", anchor="w", fg_color="transparent", command=controller.show_dashboard_screen); dashboard_button.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(self, text="APUNTES").pack(fill="x", padx=10, pady=5)
        for ramo in ramos_data:
            btn = ctk.CTkButton(self, text=f"{ramo['icon']}  {ramo['nombre']}", anchor="w", fg_color="transparent", command=lambda r=ramo: self.controller.show_notes_screen(r)); btn.pack(fill="x", padx=10); self.buttons[ramo['nombre']] = btn
    def update_selection(self, ramo_nombre=None):
        for btn in self.buttons.values(): btn.configure(fg_color="transparent")
        if ramo_nombre and ramo_nombre in self.buttons: self.buttons[ramo_nombre].configure(fg_color="#555555")
class App(ctk.CTk):
    def __init__(self):
        super().__init__(); self.title("ClassNotes Pro"); self.geometry("1200x750"); ctk.set_appearance_mode("Dark")
        self.grid_rowconfigure(0, weight=1); self.grid_columnconfigure(1, weight=1); self.load_all_data_from_file()
        container = ctk.CTkFrame(self, fg_color="transparent"); container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20); container.grid_rowconfigure(0, weight=1); container.grid_columnconfigure(0, weight=1)
        self.sidebar = SidebarFrame(self, self); self.sidebar.grid(row=0, column=0, sticky="ns")
        self.frames = {};
        for F in (DashboardScreen, NotesScreen): frame = F(container, self); self.frames[F] = frame; frame.grid(row=0, column=0, sticky="nsew")
        self.show_dashboard_screen()
    def show_dashboard_screen(self): self.sidebar.update_selection(); self.frames[DashboardScreen].refresh_dashboard(); self.frames[DashboardScreen].tkraise()
    def show_notes_screen(self, ramo_info): self.sidebar.update_selection(ramo_info['nombre']); self.frames[NotesScreen].load_ramo_data(ramo_info); self.frames[NotesScreen].tkraise()
    def get_all_notes(self): return self.app_data.get("notes", {})
    def get_notes_for_ramo(self, ramo_nombre): return self.get_all_notes().get(ramo_nombre, [])
    def add_note_to_ramo(self, ramo_nombre, note_data):
        if ramo_nombre in self.app_data["notes"]: self.app_data["notes"][ramo_nombre].insert(0, note_data); self.save_all_data_to_file()
    def delete_note_from_ramo(self, ramo_nombre, note_data):
        if ramo_nombre in self.app_data["notes"] and note_data in self.app_data["notes"][ramo_nombre]:
            self.app_data["notes"][ramo_nombre].remove(note_data); self.save_all_data_to_file(); print(f"Nota '{note_data['titulo']}' eliminada.")
    def get_all_exams(self): return self.app_data.get("exams", [])
    def add_exam(self, exam_data): self.app_data["exams"].append(exam_data); self.save_all_data_to_file()
    def save_all_data_to_file(self):
        with open("app_data.json", "w", encoding="utf-8") as f: json.dump(self.app_data, f, indent=4, ensure_ascii=False); print("Datos guardados en app_data.json")
    def load_all_data_from_file(self):
        try:
            with open("app_data.json", "r", encoding="utf-8") as f: self.app_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): self.app_data = {"notes": {ramo['nombre']: [] for ramo in ramos_data}, "exams": []}

if __name__ == "__main__":
    app = App()
    app.mainloop()