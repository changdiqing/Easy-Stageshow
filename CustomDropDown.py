from kivy.uix.dropdown import DropDown

class DropDownDelegate():

    def dropdown_item_selected(self, item_id):
        pass

class CustomDropDown(DropDown):
    delegate = DropDownDelegate()

    def select_item(self,item_id):
        self.delegate.dropdown_item_selected(item_id)