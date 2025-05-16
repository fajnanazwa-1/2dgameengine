import tkinter as tk
import random
import json
from tkinter import filedialog

# GŁÓWNE OKNO
root = tk.Tk()
root.title("Game Engine")
root.geometry("1920x1080")

# ============================
# Panel menu – przewijalny, po lewej stronie
# ============================
menu_panel = tk.Frame(root, width=300, bg="#222222")
menu_panel.pack(side="left", fill="y")
menu_panel.pack_propagate(False)

menu_canvas = tk.Canvas(menu_panel, bg="#222222", highlightthickness=0)
menu_canvas.pack(side="left", fill="both", expand=True)

menu_scroll = tk.Scrollbar(menu_panel, orient="vertical", command=menu_canvas.yview)
menu_scroll.pack(side="right", fill="y")
menu_canvas.configure(yscrollcommand=menu_scroll.set)

menu_frame = tk.Frame(menu_canvas, bg="#222222")
menu_canvas.create_window((0, 0), window=menu_frame, anchor="nw")

def on_menu_frame_configure(event):
    menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))

menu_frame.bind("<Configure>", on_menu_frame_configure)

# ============================
# GŁÓWNY AREA RYSUNKOWY
# ============================
main_area = tk.Frame(root, bg="#333333")
main_area.pack(side="left", fill="both", expand=True)

canvas_width = 1280
canvas_height = 720
canvas = tk.Canvas(main_area, bg="white", width=canvas_width, height=canvas_height)
canvas.pack(padx=20, pady=20)

# ============================
# Zmienne globalne
# ============================
shapes = []
shape_names = {}
shape_codes = {}
shape_visibility = {}

selected_item = None
program_running = False
keys_pressed = set()
messages = set()

mouse_x, mouse_y = 0, 0
mouse_clicked = False

drag_data = {"item": None, "x": 0, "y": 0}

# ============================
# Funkcje do obsługi myszy
# ============================
def update_mouse_position(event):
    global mouse_x, mouse_y
    mouse_x, mouse_y = event.x, event.y

canvas.bind("<Motion>", update_mouse_position)

def on_mouse_down(event):
    global selected_item, mouse_clicked
    mouse_clicked = True
    item = None
    items = canvas.find_overlapping(event.x, event.y, event.x, event.y)
    if items:
        item = canvas.find_closest(event.x, event.y)[0]
        if item:
            drag_data["item"] = item
            drag_data["x"] = event.x
            drag_data["y"] = event.y
            selected_item = item

def on_mouse_move(event):
    if drag_data["item"]:
        dx = event.x - drag_data["x"]
        dy = event.y - drag_data["y"]
        canvas.move(drag_data["item"], dx, dy)
        drag_data["x"], drag_data["y"] = event.x, event.y

def on_mouse_up(event):
    global mouse_clicked
    drag_data["item"] = None
    mouse_clicked = False

canvas.bind("<ButtonPress-1>", on_mouse_down)
canvas.bind("<B1-Motion>", on_mouse_move)
canvas.bind("<ButtonRelease-1>", on_mouse_up)

# ============================
# Obsługa klawiatury
# ============================
def on_key_press(event):
    keys_pressed.add(event.keysym.lower())

def on_key_release(event):
    keys_pressed.discard(event.keysym.lower())

root.bind("<KeyPress>", on_key_press)
root.bind("<KeyRelease>", on_key_release)

# ============================
# Funkcje tworzące kształty
# ============================
def add_square():
    x = random.randint(0, canvas_width - 50)
    y = random.randint(0, canvas_height - 50)
    item = canvas.create_rectangle(x, y, x+50, y+50, fill="blue", outline="black")
    shapes.append(item)
    shape_names[item] = "Kwadrat"
    shape_codes[item] = ""
    shape_visibility[item] = True

def add_circle():
    x = random.randint(0, canvas_width - 50)
    y = random.randint(0, canvas_height - 50)
    item = canvas.create_oval(x, y, x+50, y+50, fill="red", outline="black")
    shapes.append(item)
    shape_names[item] = "Koło"
    shape_codes[item] = ""
    shape_visibility[item] = True

def add_triangle():
    x = random.randint(0, canvas_width - 60)
    y = random.randint(0, canvas_height - 60)
    points = [x+30, y, x, y+60, x+60, y+60]
    item = canvas.create_polygon(points, fill="green", outline="black")
    shapes.append(item)
    shape_names[item] = "Trójkąt"
    shape_codes[item] = ""
    shape_visibility[item] = True

def add_rectangle():
    x = random.randint(0, canvas_width - 80)
    y = random.randint(0, canvas_height - 50)
    item = canvas.create_rectangle(x, y, x+80, y+50, fill="yellow", outline="black")
    shapes.append(item)
    shape_names[item] = "Prostokąt"
    shape_codes[item] = ""
    shape_visibility[item] = True

# ============================
# Funkcje pomocnicze
# ============================
def is_touching_mouse(item):
    bbox = canvas.bbox(item)
    if not bbox:
        return False
    x1, y1, x2, y2 = bbox
    return (mouse_x >= x1 and mouse_x <= x2 and mouse_y >= y1 and mouse_y <= y2)

def is_touching_color(item, target_color):
    bbox = canvas.bbox(item)
    if not bbox:
        return False
    x1, y1, x2, y2 = bbox
    overlapping = canvas.find_overlapping(x1, y1, x2, y2)
    for other in overlapping:
        if other != item:
            col = canvas.itemcget(other, "fill")
            if col and col.lower() == target_color.lower():
                return True
    return False

# ============================
# Funkcje do obsługi rozmiaru i usuwania
# ============================
def increase_size():
    if selected_item:
        coords = canvas.coords(selected_item)
        stype = canvas.type(selected_item)
        if stype in ["rectangle", "oval"]:
            canvas.coords(selected_item, coords[0]-5, coords[1]-5, coords[2]+5, coords[3]+5)
        elif stype == "polygon":
            cx = (coords[0] + coords[2]) / 2
            cy = (coords[1] + coords[3]) / 2
            new_coords = []
            for i in range(0, len(coords), 2):
                dx = coords[i] - cx
                dy = coords[i+1] - cy
                new_coords.append(cx + dx*1.1)
                new_coords.append(cy + dy*1.1)
            canvas.coords(selected_item, *new_coords)

def decrease_size():
    if selected_item:
        coords = canvas.coords(selected_item)
        stype = canvas.type(selected_item)
        if stype in ["rectangle", "oval"]:
            if (coords[2]-coords[0] > 10) and (coords[3]-coords[1] > 10):
                canvas.coords(selected_item, coords[0]+5, coords[1]+5, coords[2]-5, coords[3]-5)
        elif stype == "polygon":
            cx = (coords[0] + coords[2]) / 2
            cy = (coords[1] + coords[3]) / 2
            new_coords = []
            for i in range(0, len(coords), 2):
                dx = coords[i] - cx
                dy = coords[i+1] - cy
                new_coords.append(cx + dx*0.9)
                new_coords.append(cy + dy*0.9)
            canvas.coords(selected_item, *new_coords)

def delete_selected_shape():
    global selected_item
    if selected_item:
        canvas.delete(selected_item)
        if selected_item in shapes:
            shapes.remove(selected_item)
        shape_names.pop(selected_item, None)
        shape_codes.pop(selected_item, None)
        shape_visibility.pop(selected_item, None)
        selected_item = None

def show_shape(item):
    shape_visibility[item] = True
    canvas.itemconfig(item, state="normal")

def hide_shape(item):
    shape_visibility[item] = False
    canvas.itemconfig(item, state="hidden")

# ============================
# Funkcja do przełączania na tryb kodu
# ============================
def switch_to_code_editor():
    global in_code_editor
    in_code_editor = True
    # Ukrywamy główne menu i obszar rysunku
    for widget in root.winfo_children():
        widget.pack_forget()
    # Tworzymy nowy obszar kodu
    code_area = tk.Frame(root, bg="#333333")
    code_area.pack(side="left", fill="both", expand=True)

    # Globalnie
    global selected_item

    if selected_item:
        name = shape_names.get(selected_item, "Nieznany")
        saved_code = shape_codes.get(selected_item, "")
    else:
        name = "Brak zaznaczenia"
        saved_code = ""

    top_frame = tk.Frame(code_area, bg="#333333")
    top_frame.pack(side="top", fill="x")
    lbl = tk.Label(top_frame, text="Wybrany obiekt: " + name, bg="#333333", fg="white", font=("Arial", 12))
    lbl.pack(side="left", padx=10, pady=10)

    code_text = tk.Text(code_area, bg="#444444", fg="white", height=30, width=135, font=("Arial", 12))
    code_text.pack(padx=10, pady=10, fill="both", expand=True)
    code_text.insert("1.0", saved_code)

    def save_and_return():
        if selected_item:
            shape_codes[selected_item] = code_text.get("1.0", tk.END)
        switch_to_visual_editor()

    tk.Button(top_frame, text="Przejdź do wizualnego", bg="#444444", fg="white", command=save_and_return).pack(side="left", padx=10, pady=10)

def switch_to_visual_editor():
    global in_code_editor
    in_code_editor = False
    # Przywracamy główne menu i główny obszar
    for widget in root.winfo_children():
        widget.pack_forget()
    menu_panel.pack(side="left", fill="y")
    main_area.pack(side="left", fill="both", expand=True)
    main_area.config(bg="#333333")
    # Ustaw widoczność
    for item in shapes:
        if shape_visibility.get(item, True):
            canvas.itemconfig(item, state="normal")
        else:
            canvas.itemconfig(item, state="hidden")
    canvas.pack(padx=20, pady=20)

# ============================
# Funkcje parsowania i oceniania warunków
# ============================

def parse_startpos(command):
    command = command.strip()
    if not command.startswith("startpos:"):
        return None
    params = command[len("startpos:"):].strip()
    parts = params.split()
    pos = {}
    for part in parts:
        if "=" in part:
            k, v = part.split("=", 1)
            try:
                pos[k.strip().lower()] = float(v.strip())
            except:
                pass
    if "x" in pos and "y" in pos:
        return (pos["x"], pos["y"])
    return None

def parse_code(command):
    cmd = command.strip()
    if "if " in cmd and " else?:" in cmd:
        parts = cmd.split("else?:")
        condition_part = parts[0].strip()
        else_part = parts[1].strip() if len(parts) > 1 else ""
        condition_str = condition_part[3:].strip()  # po "if "
        true_action = condition_str.split("?:")[1].strip() if "?: " in condition_str else ""
        false_action = else_part
        return ("if_else", condition_str, true_action, false_action)

    if "touching colors:" in cmd and "and" in cmd:
        return ("touching_colors", cmd)

    if cmd.startswith("startpos:"):
        return ("startpos", parse_startpos(cmd))
    if cmd.startswith("setcolor="):
        col = cmd[len("setcolor="):].strip()
        return ("setcolor", col)
    if cmd == "show":
        return ("show",)
    if cmd == "hide":
        return ("hide",)
    return None

def evaluate_condition(condition_str, item):
    c = condition_str.lower()
    if "touching mouse?" in c:
        return is_touching_mouse(item)
    elif "touching colors:" in c:
        return evaluate_touching_colors(c, item)
    elif "touching" in c:
        if "color=" in c:
            col = c.split("color=")[1].replace("?", "").strip()
            return is_touching_color(item, col)
        else:
            return False
    elif "mouse click?" in c:
        return mouse_clicked
    return False

def evaluate_touching_colors(condition_str, item):
    import re
    pattern = r"touching\s+colors:\s+(.+)\?"
    m = re.match(pattern, condition_str)
    if not m:
        return False
    conditions_part = m.group(1)
    color_matches = re.findall(r"color=([a-zA-Z0-9]+)", conditions_part)
    if not color_matches:
        return False
    for col in color_matches:
        if not is_touching_color(item, col):
            return False
    return True

def process_action(action_str, item):
    ac = action_str.strip().lower()
    if ac.startswith("setcolor="):
        color = ac[len("setcolor="):]
        canvas.itemconfig(item, fill=color)
    elif ac.startswith("setpos:"):
        pos = parse_startpos("startpos:" + ac[len("setpos:"):].strip())
        if pos:
            bbox = canvas.bbox(item)
            if bbox:
                cur_x, cur_y = bbox[0], bbox[1]
                dx = pos[0] - cur_x
                dy = pos[1] - cur_y
                canvas.move(item, dx, dy)
    elif ac == "show":
        show_shape(item)
    elif ac == "hide":
        hide_shape(item)

# ============================
# Główna funkcja wykonująca program
# ============================
def execute_program():
    global messages, mouse_clicked
    if not program_running:
        return
    # Debug: print("Executing program cycle")
    messages = set()
    for item in shapes:
        code_str = shape_codes.get(item, "").strip()
        if code_str:
            for line in code_str.splitlines():
                line = line.strip()
                if not line:
                    continue
                parsed = parse_code(line)
                if parsed:
                    if parsed[0] == "if_else":
                        cond_str = parsed[1]
                        true_act = parsed[2]
                        false_act = parsed[3]
                        if evaluate_condition(cond_str, item):
                            process_action(true_act, item)
                        else:
                            process_action(false_act, item)
                    elif parsed[0] == "touching_colors":
                        cond_str = parsed[1]
                        if evaluate_condition(cond_str, item):
                            pass
                    elif parsed[0] == "touching":
                        target = parsed[1]
                        if target == "mouse":
                            if is_touching_mouse(item):
                                pass
                        else:
                            if is_touching_color(item, target):
                                pass
                    elif parsed[0] == "setcolor":
                        process_action(parsed[1], item)
                    elif parsed[0] == "show":
                        show_shape(item)
                    elif parsed[0] == "hide":
                        hide_shape(item)
    mouse_clicked = False

# ============================
# Start/Stop funkcje
# ============================
def start_program():
    global program_running
    if not program_running:
        print("Program started")
        program_running = True
        # Ustawienia początkowe
        for item in shapes:
            for line in shape_codes.get(item, "").splitlines():
                line = line.strip()
                if line.startswith("startpos:"):
                    pos = parse_startpos(line)
                    if pos:
                        bbox = canvas.bbox(item)
                        if bbox:
                            cur_x, cur_y = bbox[0], bbox[1]
                            dx = pos[0] - cur_x
                            dy = pos[1] - cur_y
                            canvas.move(item, dx, dy)
                elif line.startswith("setcolor="):
                    col = line[len("setcolor="):]
                    canvas.itemconfig(item, fill=col)
                elif line == "hide":
                    hide_shape(item)
                elif line == "show":
                    show_shape(item)
        execute_program()

def stop_program():
    global program_running
    print("Program stopped")
    program_running = False

# ============================
# Zapis i odczyt plików
# ============================
def save_shapes_to_file():
    filename = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON files", "*.json")],
                                            title="Zapisz plik")
    if filename:
        data = []
        for item in shapes:
            bbox = canvas.bbox(item)
            if bbox:
                x1, y1, x2, y2 = bbox
                pos = {"x": x1, "y": y1}
                size = {"width": x2 - x1, "height": y2 - y1}
            else:
                pos = {"x": 0, "y": 0}
                size = {"width": 50, "height": 50}
            data.append({
                "type": shape_names.get(item, "Nieznany"),
                "position": pos,
                "size": size,
                "color": canvas.itemcget(item, "fill"),
                "visible": shape_visibility.get(item, True),
                "code": shape_codes.get(item, "")
            })
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

def load_shapes_from_file():
    filename = filedialog.askopenfilename(defaultextension=".json",
                                          filetypes=[("JSON files", "*.json")],
                                          title="Wczytaj plik")
    if filename:
        with open(filename, "r") as f:
            data = json.load(f)
        # Usuwamy stare kształty
        for item in shapes:
            canvas.delete(item)
        shapes.clear()
        shape_names.clear()
        shape_codes.clear()
        shape_visibility.clear()
        # Tworzymy nowe
        for s in data:
            t = s.get("type", "Nieznany")
            pos = s.get("position", {"x":0,"y":0})
            size = s.get("size", {"width":50,"height":50})
            color = s.get("color", "black")
            visible = s.get("visible", True)
            code = s.get("code", "")
            x, y = pos.get("x",0), pos.get("y",0)
            w, h = size.get("width",50), size.get("height",50)
            if t.lower() in ["kwadrat", "prostokąt"]:
                item = canvas.create_rectangle(x, y, x+w, y+h, fill=color, outline="black")
            elif t.lower() == "koło":
                item = canvas.create_oval(x, y, x+w, y+h, fill=color, outline="black")
            elif t.lower() == "trójkąt":
                item = canvas.create_polygon(x+w/2, y, x, y+h, x+w, y+h, fill=color, outline="black")
            else:
                item = canvas.create_rectangle(x, y, x+w, y+h, fill=color, outline="black")
            shapes.append(item)
            shape_names[item] = t
            shape_codes[item] = code
            shape_visibility[item] = visible
            if not visible:
                canvas.itemconfig(item, state="hidden")

# ============================
# Aktualizacja współrzędnych
# ============================
coord_label = tk.Label(menu_frame, text="X: -     Y: -", font=("Arial", 10), bg="#222222", fg="white")
coord_label.pack(side="bottom", pady=10)

def update_coords():
    if selected_item:
        bbox = canvas.bbox(selected_item)
        if bbox:
            x, y = bbox[0], bbox[1]
            coord_label.config(text=f"X: {x:.0f} Y: {y:.0f}")
        else:
            coord_label.config(text="X: - Y: -")
    else:
        coord_label.config(text="X: - Y: -")
    root.after(50, update_coords)

update_coords()

# ============================
# Funkcja do dodawania sekcji (zapobiegamy powtarzaniu)
# ============================
added_sections = {}

def add_section(header, buttons):
    if header in added_sections:
        return
    lbl = tk.Label(menu_frame, text=header, bg="#222222", fg="white", font=("Arial", 10, "bold"))
    lbl.pack(anchor="w", padx=5, pady=(10,2))
    for btn in buttons:
        btn.configure(width=25)
        btn.pack(fill="x", padx=10, pady=2)
    added_sections[header] = True

# ============================
# Tworzymy sekcje menu tylko raz
# ============================
add_section("1. Dodaj", [
    tk.Button(menu_frame, text="Dodaj kwadrat", command=add_square, bg="#444444", fg="white"),
    tk.Button(menu_frame, text="Dodaj koło", command=add_circle, bg="#444444", fg="white"),
    tk.Button(menu_frame, text="Dodaj trójkąt", command=add_triangle, bg="#444444", fg="white"),
    tk.Button(menu_frame, text="Dodaj prostokąt", command=add_rectangle, bg="#444444", fg="white")
])

add_section("2. Zarządzaj obiektami", [
    tk.Button(menu_frame, text="Przejdź do kodu", command=switch_to_code_editor, bg="#444444", fg="white"),
    tk.Button(menu_frame, text="Powiększ", command=increase_size, bg="#444444", fg="white"),
    tk.Button(menu_frame, text="Zmniejsz", command=decrease_size, bg="#444444", fg="white"),
    tk.Button(menu_frame, text="Usuń", command=delete_selected_shape, bg="#444444", fg="white")
])

add_section("3. Zarządzaj plikiem", [
    tk.Button(menu_frame, text="Start", command=start_program, bg="#444444", fg="white"),
    tk.Button(menu_frame, text="Stop", command=stop_program, bg="#444444", fg="white"),
    tk.Button(menu_frame, text="Zapisz plik", command=save_shapes_to_file, bg="#444444", fg="white"),
    tk.Button(menu_frame, text="Wczytaj plik", command=load_shapes_from_file, bg="#444444", fg="white")
])

# ============================
# Dodaj przycisk "Uruchom program"
# ============================
tk.Button(root, text="Uruchom program", command=start_program, bg="#444444", fg="white").pack(side="top", padx=10, pady=10)

# ============================
# Automatyczne cykliczne wywoływanie
# ============================
def auto_run():
    global program_running
    if program_running:
        execute_program()
    root.after(100, auto_run)

auto_run()

# ============================
# Uruchom główną pętlę
# ============================
root.mainloop()