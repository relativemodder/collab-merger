from base64 import b64encode
import copy
from typing import Dict
from typing import Tuple
from typing import List
import eel
import gd
import win32api
import win32con
from open_file_dialog import open_file_dialog
from win32gui import FindWindowEx
import xml.etree.ElementTree as ET
import gd_object
import gd_pipe

class App:

    def test(self):
        print("JS Called!")

    def do_game_injections(self):
        successfull_gdliveeditor_injection = self.mem.inject_dll('./dlls/GDLiveEditor.dll')
        if not successfull_gdliveeditor_injection: raise Exception('unsuccessfull_gdliveeditor_injection')

    def load_game_memory(self):
        self.mem: gd.memory.WindowsMemory = gd.memory.get_memory()

    def trigger_editor_callback(self, event: dict):
        eel.on_editor_trigger_callback(event)
    
    def trigger_loadlevel_callback(self, level_info):
        eel.on_level_load(level_info)

        try:
            result = self.__getattribute__("parts")
        except AttributeError:
            self.parts: List[gd.api.Editor] = list()
            

    def editor_checking_loop(self):
        last_editor_state = None

        while len(eel._websockets) > 0:
            is_in_editor = self.mem.is_in_editor()

            if is_in_editor != last_editor_state:
                editor_level_name = self.mem.get_editor_level_name()
                last_editor_state = is_in_editor

                print(f"Changed editor state: {is_in_editor} with level name {editor_level_name}")

                self.trigger_editor_callback({
                    'is_in_editor': is_in_editor,
                    'editor_level_name': editor_level_name if editor_level_name != "" else None
                })

            eel.sleep(1)
    
    def start_editor_checking_loop(self):
        eel.spawn(self.editor_checking_loop)
    
    def showSystemAlert(self, title, message, wnd=None):
        win32api.MessageBox(wnd, message, title, win32con.MB_OK)

    def showSystemFileOpenDialog(self, title: str, ext: List[Tuple[str, str]]):
        browserHwnd = FindWindowEx(None, None, None, 'Geometry Dash part merger')
        return open_file_dialog(hWnd=browserHwnd, title=title, ext=ext)
    
    def call_open_file_dialog(self, title: str, ext: List[Tuple[str, str]]):
        return self.showSystemFileOpenDialog(title, ext)

    def load_database(self):
        database = gd.api.save.load()
        self.db = database

    def load_level_by_name(self, level_name: str):
        self.levels = self.db.load_my_levels()
        self.current_level = self.levels.get_by_name(level_name)
        self.level_editor: gd.api.Editor = self.current_level.open_editor()

        objects = self.level_editor.get_objects()

        self.trigger_loadlevel_callback({
            'levelName': level_name,
            'levelLength': self.level_editor.get_length(),
            'levelObjectsCount': len(objects)
        })

    def parse_gmd_file(self, content: str) -> Dict[str, str]:
        tree = ET.fromstring(content)
        root = tree

        gmd_dict = {}

        next_child_is_value = False
        value_key = ""

        for child in root:
            if not next_child_is_value:
                value_key = child.text
                next_child_is_value = True
                continue

            gmd_dict[value_key] = child.text
            next_child_is_value = False

        return gmd_dict

    def put_and_merge_part(self, part_index: int, layer_setting: bool, color_convert_setting: bool):
        collab_objects = self.level_editor.get_objects()
        last_right_block = collab_objects[0].x

        print(collab_objects)

        for block in collab_objects:
            if last_right_block < block.x:
                last_right_block = block.x
        
        part_objects = self.parts[part_index].get_objects()
        first_left_block = part_objects[0].x

        for block in part_objects:
            if first_left_block > block.x:
                first_left_block = block.x
        
        # finally, drawing part

        new_objects_list: gd_object.gd_object_collection = gd_object.gd_object_collection()
        for block in part_objects:
            new_block: gd.api.Object = copy.copy(block)
            new_block.x = block.x + last_right_block

            if layer_setting:
                new_block.data['20'] = part_index

            if new_block.get('54') is not None:
                new_block.data['54'] = str(block.data['54'])

            if new_block.data.get('31') is not None:
                new_block.data['31'] = b64encode(str(block.data['31']).encode()).decode()

            new_objects_list.add_block(**new_block.data)
            self.level_editor.add_objects(new_block)
            print(new_block.data)

        color_converting_feature_in_development = True
        
        if color_convert_setting and not color_converting_feature_in_development:
            part_colors: List[gd.api.ColorChannel] = self.parts[part_index].header.colors
            color_y_offset = 0
            for color in part_colors:

                col:gd.Color = color.get_color()
                
                new_block = gd.api.Object(x=last_right_block + first_left_block, y=part_objects[0].y + 100 + color_y_offset)
                new_block.set_id('trigger:color')


                new_objects_list.add_block(**new_block.data)
                self.level_editor.add_objects(new_block)

                color_y_offset += 30

        gd_pipe.draw_object(new_objects_list)

    def load_part_by_path(self, path: str):
        with open(path) as fp:
            parsed_part = self.parse_gmd_file(fp.read())

            editor = gd.api.Editor.from_string(gd.Coder.unzip(parsed_part['k4']))
            self.parts.append(editor)

            return parsed_part

    def __init__(self):

        try:
            self.load_game_memory()
        except RuntimeError:
            self.showSystemAlert("Error!", "Run Geometry Dash first!")
            exit()

        self.do_game_injections()

        eel.init('ui')
        eel.start('templates/index.html', block=False, size=(1280, 720), jinja_templates='templates')

        eel.expose(self.start_editor_checking_loop)
        eel.expose(self.call_open_file_dialog)
        eel.expose(self.load_database)
        eel.expose(self.load_level_by_name)
        eel.expose(self.load_part_by_path)

        eel.expose(self.put_and_merge_part)

app: App = App()

while eel:
    eel.sleep(1.0)